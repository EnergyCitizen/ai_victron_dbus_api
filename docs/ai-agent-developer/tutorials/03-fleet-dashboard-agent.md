# Tutorial 03: Fleet Dashboard Agent

Build an AI agent that monitors 10+ Victron installations simultaneously, compares performance, and identifies sites needing attention.

**Duration**: 90 minutes
**Difficulty**: Intermediate
**Prerequisites**: [Tutorial 01: First Monitoring Agent](./01-first-monitoring-agent.md), [Tutorial 02: Battery Health Agent](./02-battery-health-agent.md)

---

## What You'll Build

An AI agent that:
- Monitors 10+ sites in parallel
- Aggregates health scores across fleet
- Compares site performance with conversational queries
- Identifies outliers and underperformers
- Generates executive dashboards

**Example Conversation**:

**User**: "Which sites need attention this week?"

**Agent**:
> "I've analyzed all 12 sites. Here's what needs attention:
>
> **URGENT** (1 site):
> - Site Alpha: Battery SOH 68% (below threshold), replace within 7 days
>
> **WARNING** (3 sites):
> - Site Beta: Grid frequency unstable (49.3Hz avg), investigate utility connection
> - Site Gamma: Cell imbalance 0.12V, check BMS balancing
> - Site Delta: Temperature 45°C consistently high, improve cooling
>
> **HEALTHY** (8 sites): No action needed
>
> Total estimated cost: $8,500 (1 battery + 2 service calls)
>
> Would you like me to create maintenance tickets?"

---

## Architecture Overview

```
Fleet Monitor Agent
    |
    +---> Site Discovery (from config/API)
    |        - Read site list
    |        - Verify connectivity
    |        - Track online/offline status
    |
    +---> Parallel Data Collection
    |        - Query all sites simultaneously
    |        - 10s timeout per site
    |        - Aggregate results
    |
    +---> Health Scoring Engine
    |        - Battery: 40% weight
    |        - Grid: 30% weight
    |        - Solar: 20% weight
    |        - Connectivity: 10% weight
    |
    +---> Comparative Analytics
    |        - Rank sites by performance
    |        - Identify outliers (±2σ)
    |        - Detect common issues
    |
    +---> Natural Language Interface
             - Answer "which sites..." queries
             - Generate summaries
             - Proactive alerts
```

---

## Step 1: Site Configuration (15 min)

### 1.1 Define Site Registry

Create `sites.json`:

```json
{
  "sites": [
    {
      "id": "site_alpha",
      "name": "Site Alpha - Main Office",
      "location": "Building A, Floor 2",
      "api_endpoint": "http://192.168.1.100:8088",
      "battery_type": "Pylontech US3000C",
      "capacity_kwh": 56,
      "solar_capacity_kw": 12,
      "priority": "high",
      "contact": {
        "name": "John Doe",
        "phone": "+1234567890"
      }
    },
    {
      "id": "site_beta",
      "name": "Site Beta - Warehouse",
      "location": "Industrial Park, Unit 5",
      "api_endpoint": "http://192.168.1.101:8088",
      "battery_type": "BYD LVS 20.0",
      "capacity_kwh": 20,
      "solar_capacity_kw": 8,
      "priority": "medium"
    }
    // ... more sites
  ],
  "thresholds": {
    "battery_soh_warning": 85,
    "battery_soh_critical": 70,
    "grid_frequency_min": 49.5,
    "grid_frequency_max": 50.5,
    "temperature_max": 45
  }
}
```

### 1.2 Site Discovery Class

```python
import json
import requests
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

class SiteRegistry:
    """Manage multi-site configuration"""

    def __init__(self, config_path: str = "sites.json"):
        with open(config_path) as f:
            self.config = json.load(f)
        self.sites = self.config['sites']
        self.thresholds = self.config['thresholds']

    def get_all_sites(self) -> List[Dict]:
        """Return list of all configured sites"""
        return self.sites

    def get_site(self, site_id: str) -> Dict:
        """Get specific site config"""
        return next((s for s in self.sites if s['id'] == site_id), None)

    def verify_connectivity(self, timeout: int = 3) -> Dict[str, bool]:
        """Check which sites are reachable"""
        results = {}

        for site in self.sites:
            try:
                response = requests.get(
                    f"{site['api_endpoint']}/services",
                    timeout=timeout
                )
                results[site['id']] = response.status_code == 200
            except:
                results[site['id']] = False

        return results
```

---

## Step 2: Parallel Data Collection (20 min)

### 2.1 Multi-Site Collector

```python
from datetime import datetime
import time

class FleetDataCollector:
    """Collect data from multiple sites in parallel"""

    def __init__(self, registry: SiteRegistry):
        self.registry = registry
        self.battery_service = "com.victronenergy.battery.socketcan_can0"
        self.system_service = "com.victronenergy.system"

    def collect_site_metrics(self, site: Dict) -> Dict:
        """Collect key metrics from a single site"""
        start_time = time.time()

        try:
            base_url = site['api_endpoint']

            # Query critical services in parallel
            metrics = {
                'site_id': site['id'],
                'site_name': site['name'],
                'timestamp': datetime.utcnow().isoformat(),
                'online': True,
                'collection_time_ms': 0
            }

            # Battery metrics
            battery_paths = ['/Soc', '/Soh', '/Dc/0/Voltage', '/Dc/0/Current',
                           '/Dc/0/Temperature', '/System/MaxCellVoltage',
                           '/System/MinCellVoltage']

            for path in battery_paths:
                try:
                    response = requests.get(
                        f"{base_url}/value",
                        params={'service': self.battery_service, 'path': path},
                        timeout=2
                    )
                    if response.status_code == 200:
                        key = path.split('/')[-1].lower()
                        metrics[f'battery_{key}'] = response.json().get('value')
                except:
                    pass

            # System metrics
            system_response = requests.get(
                f"{base_url}/value",
                params={'service': self.system_service, 'path': '/'},
                timeout=5
            )

            if system_response.status_code == 200:
                sys_data = system_response.json().get('value', {})
                metrics.update({
                    'grid_power': sys_data.get('Ac/Grid/L1/Power'),
                    'grid_frequency': sys_data.get('Ac/ActiveIn/L1/F'),
                    'consumption': sys_data.get('Ac/Consumption/L1/Power'),
                    'solar_power': sys_data.get('Dc/Pv/Power'),
                    'system_state': sys_data.get('SystemState/State')
                })

            # Calculate cell spread
            if metrics.get('battery_maxcellvoltage') and metrics.get('battery_mincellvoltage'):
                metrics['cell_spread'] = (
                    metrics['battery_maxcellvoltage'] -
                    metrics['battery_mincellvoltage']
                )

            metrics['collection_time_ms'] = int((time.time() - start_time) * 1000)
            return metrics

        except Exception as e:
            return {
                'site_id': site['id'],
                'site_name': site['name'],
                'timestamp': datetime.utcnow().isoformat(),
                'online': False,
                'error': str(e),
                'collection_time_ms': int((time.time() - start_time) * 1000)
            }

    def collect_all(self, max_workers: int = 10) -> List[Dict]:
        """Collect data from all sites in parallel"""
        sites = self.registry.get_all_sites()
        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_site = {
                executor.submit(self.collect_site_metrics, site): site
                for site in sites
            }

            for future in as_completed(future_to_site):
                try:
                    result = future.result(timeout=10)
                    results.append(result)
                except Exception as e:
                    site = future_to_site[future]
                    results.append({
                        'site_id': site['id'],
                        'site_name': site['name'],
                        'online': False,
                        'error': f'Collection timeout: {str(e)}'
                    })

        return results
```

---

## Step 3: Health Scoring Engine (20 min)

### 3.1 Site Health Calculator

```python
class HealthScoreCalculator:
    """Calculate comprehensive health scores for each site"""

    def __init__(self, thresholds: Dict):
        self.thresholds = thresholds

    def calculate_battery_score(self, metrics: Dict) -> Dict:
        """Battery health: 0-100 score"""
        score = 100
        issues = []

        # SOH check (50% of battery score)
        soh = metrics.get('battery_soh', 100)
        if soh < self.thresholds['battery_soh_critical']:
            score -= 50
            issues.append(f"SOH {soh}% critical")
        elif soh < self.thresholds['battery_soh_warning']:
            score -= 20
            issues.append(f"SOH {soh}% low")

        # Temperature check (20% of battery score)
        temp = metrics.get('battery_temperature')
        if temp and temp > self.thresholds['temperature_max']:
            score -= 20
            issues.append(f"Temperature {temp}°C high")

        # Cell spread check (20% of battery score)
        cell_spread = metrics.get('cell_spread', 0)
        if cell_spread > 0.15:
            score -= 20
            issues.append(f"Cell imbalance {cell_spread:.3f}V")
        elif cell_spread > 0.10:
            score -= 10
            issues.append(f"Cell spread {cell_spread:.3f}V elevated")

        # SOC check (10% of battery score)
        soc = metrics.get('battery_soc', 50)
        if soc < 10:
            score -= 10
            issues.append(f"SOC {soc}% critical")

        return {
            'score': max(0, score),
            'issues': issues,
            'status': self._score_to_status(score)
        }

    def calculate_grid_score(self, metrics: Dict) -> Dict:
        """Grid quality: 0-100 score"""
        score = 100
        issues = []

        freq = metrics.get('grid_frequency')
        if freq:
            if freq < self.thresholds['grid_frequency_min'] or \
               freq > self.thresholds['grid_frequency_max']:
                score -= 40
                issues.append(f"Frequency {freq}Hz out of range")
            elif abs(freq - 50.0) > 0.1:
                score -= 15
                issues.append(f"Frequency {freq}Hz unstable")

        # Grid power fluctuation (placeholder - needs historical data)
        # In real implementation, check grid power variance

        return {
            'score': max(0, score),
            'issues': issues,
            'status': self._score_to_status(score)
        }

    def calculate_solar_score(self, metrics: Dict, site_config: Dict) -> Dict:
        """Solar performance: 0-100 score"""
        score = 100
        issues = []

        solar_power = metrics.get('solar_power', 0)
        capacity_kw = site_config.get('solar_capacity_kw', 10)

        # During daylight, check if producing (placeholder - needs time/irradiance)
        # In real implementation, compare with expected based on time/weather

        return {
            'score': score,
            'issues': issues,
            'status': self._score_to_status(score)
        }

    def calculate_overall_score(self, metrics: Dict, site_config: Dict) -> Dict:
        """Weighted overall health score"""

        if not metrics.get('online'):
            return {
                'overall_score': 0,
                'overall_status': 'OFFLINE',
                'battery': {'score': 0, 'issues': ['Site offline']},
                'grid': {'score': 0, 'issues': []},
                'solar': {'score': 0, 'issues': []},
                'connectivity': {'score': 0, 'issues': ['Site unreachable']}
            }

        battery = self.calculate_battery_score(metrics)
        grid = self.calculate_grid_score(metrics)
        solar = self.calculate_solar_score(metrics, site_config)
        connectivity = {'score': 100, 'issues': [], 'status': 'HEALTHY'}

        # Weighted average
        overall = (
            battery['score'] * 0.40 +
            grid['score'] * 0.30 +
            solar['score'] * 0.20 +
            connectivity['score'] * 0.10
        )

        return {
            'overall_score': int(overall),
            'overall_status': self._score_to_status(overall),
            'battery': battery,
            'grid': grid,
            'solar': solar,
            'connectivity': connectivity
        }

    def _score_to_status(self, score: float) -> str:
        """Convert numeric score to status string"""
        if score >= 90:
            return 'HEALTHY'
        elif score >= 70:
            return 'GOOD'
        elif score >= 50:
            return 'WARNING'
        else:
            return 'CRITICAL'
```

---

## Step 4: Comparative Analytics (15 min)

### 4.1 Fleet Analyzer

```python
import statistics

class FleetAnalyzer:
    """Analyze fleet-wide patterns and outliers"""

    def __init__(self, health_calculator: HealthScoreCalculator):
        self.health_calc = health_calculator

    def analyze_fleet(self, site_metrics: List[Dict],
                     site_configs: List[Dict]) -> Dict:
        """Generate fleet-wide analysis"""

        # Calculate health scores
        site_health = []
        for metrics, config in zip(site_metrics, site_configs):
            health = self.health_calc.calculate_overall_score(metrics, config)
            health['site_id'] = metrics['site_id']
            health['site_name'] = metrics['site_name']
            health['metrics'] = metrics
            site_health.append(health)

        # Sort by overall score (worst first)
        site_health.sort(key=lambda x: x['overall_score'])

        # Categorize sites
        critical = [s for s in site_health if s['overall_status'] == 'CRITICAL']
        warning = [s for s in site_health if s['overall_status'] == 'WARNING']
        good = [s for s in site_health if s['overall_status'] == 'GOOD']
        healthy = [s for s in site_health if s['overall_status'] == 'HEALTHY']
        offline = [s for s in site_health if s['overall_status'] == 'OFFLINE']

        # Calculate fleet statistics
        online_scores = [s['overall_score'] for s in site_health
                        if s['overall_status'] != 'OFFLINE']

        return {
            'timestamp': datetime.utcnow().isoformat(),
            'total_sites': len(site_health),
            'online_sites': len(online_scores),
            'offline_sites': len(offline),
            'fleet_health_avg': int(statistics.mean(online_scores)) if online_scores else 0,
            'fleet_health_median': int(statistics.median(online_scores)) if online_scores else 0,
            'categorized': {
                'critical': critical,
                'warning': warning,
                'good': good,
                'healthy': healthy,
                'offline': offline
            },
            'all_sites': site_health
        }

    def identify_outliers(self, site_metrics: List[Dict]) -> List[Dict]:
        """Identify sites with anomalous metrics"""
        outliers = []

        # Collect SOH values
        soh_values = [m.get('battery_soh') for m in site_metrics
                     if m.get('battery_soh') is not None]

        if len(soh_values) > 3:
            mean_soh = statistics.mean(soh_values)
            stdev_soh = statistics.stdev(soh_values)

            for metrics in site_metrics:
                soh = metrics.get('battery_soh')
                if soh and abs(soh - mean_soh) > 2 * stdev_soh:
                    outliers.append({
                        'site_id': metrics['site_id'],
                        'site_name': metrics['site_name'],
                        'metric': 'battery_soh',
                        'value': soh,
                        'fleet_mean': mean_soh,
                        'deviation': soh - mean_soh,
                        'severity': 'high' if soh < mean_soh else 'low'
                    })

        return outliers

    def rank_sites(self, site_health: List[Dict],
                  metric: str = 'overall_score') -> List[Dict]:
        """Rank sites by specified metric"""

        ranked = sorted(site_health,
                       key=lambda x: x.get(metric, 0),
                       reverse=True)

        return [{
            'rank': i + 1,
            'site_name': site['site_name'],
            'score': site.get(metric, 0),
            'status': site.get('overall_status', 'UNKNOWN')
        } for i, site in enumerate(ranked)]
```

---

## Step 5: Natural Language Interface (20 min)

### 5.1 Conversational Agent

```python
class FleetDashboardAgent:
    """Natural language interface to fleet data"""

    def __init__(self, registry: SiteRegistry,
                 collector: FleetDataCollector,
                 analyzer: FleetAnalyzer):
        self.registry = registry
        self.collector = collector
        self.analyzer = analyzer

    def answer_query(self, query: str) -> str:
        """Process natural language query and return answer"""

        query_lower = query.lower()

        # Collect fresh data
        site_metrics = self.collector.collect_all()
        site_configs = self.registry.get_all_sites()
        fleet_analysis = self.analyzer.analyze_fleet(site_metrics, site_configs)

        # Route query to appropriate handler
        if 'which sites need attention' in query_lower or \
           'sites with problems' in query_lower:
            return self._sites_needing_attention(fleet_analysis)

        elif 'best performing' in query_lower or 'healthiest' in query_lower:
            return self._best_performing_sites(fleet_analysis)

        elif 'fleet summary' in query_lower or 'overview' in query_lower:
            return self._fleet_summary(fleet_analysis)

        elif 'compare' in query_lower:
            return self._compare_sites(fleet_analysis, query)

        elif 'rank' in query_lower:
            return self._rank_all_sites(fleet_analysis)

        else:
            return self._fleet_summary(fleet_analysis)

    def _sites_needing_attention(self, analysis: Dict) -> str:
        """Generate summary of sites needing attention"""

        critical = analysis['categorized']['critical']
        warning = analysis['categorized']['warning']

        response = f"Fleet Status ({analysis['timestamp']}):\n\n"

        if critical:
            response += f"**URGENT** ({len(critical)} sites):\n"
            for site in critical[:5]:  # Top 5
                issues = self._collect_all_issues(site)
                response += f"- {site['site_name']}: {', '.join(issues[:2])}\n"
            response += "\n"

        if warning:
            response += f"**WARNING** ({len(warning)} sites):\n"
            for site in warning[:5]:
                issues = self._collect_all_issues(site)
                response += f"- {site['site_name']}: {', '.join(issues[:2])}\n"
            response += "\n"

        healthy_count = len(analysis['categorized']['healthy']) + \
                       len(analysis['categorized']['good'])
        response += f"**HEALTHY** ({healthy_count} sites): No action needed\n"

        return response

    def _fleet_summary(self, analysis: Dict) -> str:
        """Generate executive summary"""

        response = f"Fleet Health Report\n"
        response += f"{'=' * 40}\n\n"
        response += f"Total Sites: {analysis['total_sites']}\n"
        response += f"Online: {analysis['online_sites']}\n"
        response += f"Offline: {analysis['offline_sites']}\n"
        response += f"Fleet Health Score: {analysis['fleet_health_avg']}/100\n\n"

        response += f"Status Breakdown:\n"
        response += f"  Critical: {len(analysis['categorized']['critical'])} sites\n"
        response += f"  Warning: {len(analysis['categorized']['warning'])} sites\n"
        response += f"  Good: {len(analysis['categorized']['good'])} sites\n"
        response += f"  Healthy: {len(analysis['categorized']['healthy'])} sites\n"

        return response

    def _best_performing_sites(self, analysis: Dict) -> str:
        """Show top performers"""

        ranked = self.analyzer.rank_sites(analysis['all_sites'])

        response = "Top 5 Performing Sites:\n\n"
        for site in ranked[:5]:
            response += f"{site['rank']}. {site['site_name']}: "
            response += f"{site['score']}/100 ({site['status']})\n"

        return response

    def _collect_all_issues(self, site_health: Dict) -> List[str]:
        """Collect all issues from a site"""
        issues = []
        issues.extend(site_health['battery']['issues'])
        issues.extend(site_health['grid']['issues'])
        issues.extend(site_health['solar']['issues'])
        return issues
```

---

## Step 6: Dashboard Visualization (Optional)

### 6.1 Simple Text Dashboard

```python
def print_dashboard(analysis: Dict):
    """Print ASCII dashboard"""

    print("\n" + "=" * 60)
    print("VICTRON FLEET DASHBOARD".center(60))
    print("=" * 60 + "\n")

    # Fleet summary
    print(f"Total Sites: {analysis['total_sites']:>3}  |  " +
          f"Online: {analysis['online_sites']:>3}  |  " +
          f"Offline: {analysis['offline_sites']:>3}")
    print(f"Fleet Health: {analysis['fleet_health_avg']:>3}/100\n")

    # Status bars
    critical_count = len(analysis['categorized']['critical'])
    warning_count = len(analysis['categorized']['warning'])
    good_count = len(analysis['categorized']['good'])
    healthy_count = len(analysis['categorized']['healthy'])

    print("Status Distribution:")
    print(f"  Critical: {'█' * critical_count} {critical_count}")
    print(f"  Warning:  {'█' * warning_count} {warning_count}")
    print(f"  Good:     {'█' * good_count} {good_count}")
    print(f"  Healthy:  {'█' * healthy_count} {healthy_count}")
    print()

    # Sites needing attention
    if critical_count > 0 or warning_count > 0:
        print("Sites Needing Attention:")
        print("-" * 60)

        for site in analysis['categorized']['critical'][:3]:
            print(f"🔴 {site['site_name']:30} Score: {site['overall_score']:>3}")
            for issue in site['battery']['issues'][:2]:
                print(f"   → {issue}")

        for site in analysis['categorized']['warning'][:3]:
            print(f"🟡 {site['site_name']:30} Score: {site['overall_score']:>3}")
            for issue in site['battery']['issues'][:1]:
                print(f"   → {issue}")

    print("\n" + "=" * 60 + "\n")

# Usage
analysis = analyzer.analyze_fleet(site_metrics, site_configs)
print_dashboard(analysis)
```

---

## Testing Your Implementation

### Test Case 1: All Sites Healthy

```python
# Mock data with all sites healthy
test_metrics = [
    {'site_id': 'site_1', 'battery_soh': 95, 'battery_soc': 75,
     'grid_frequency': 50.0, 'online': True},
    {'site_id': 'site_2', 'battery_soh': 93, 'battery_soc': 68,
     'grid_frequency': 50.05, 'online': True},
]

analysis = analyzer.analyze_fleet(test_metrics, site_configs)
assert len(analysis['categorized']['healthy']) == 2
assert analysis['fleet_health_avg'] > 90
```

### Test Case 2: Mixed Fleet Health

```python
test_metrics = [
    {'site_id': 'site_1', 'battery_soh': 65, 'online': True},  # Critical
    {'site_id': 'site_2', 'battery_soh': 82, 'online': True},  # Warning
    {'site_id': 'site_3', 'battery_soh': 95, 'online': True},  # Healthy
]

analysis = analyzer.analyze_fleet(test_metrics, site_configs)
assert len(analysis['categorized']['critical']) == 1
assert len(analysis['categorized']['warning']) == 1
assert len(analysis['categorized']['healthy']) == 1
```

### Test Case 3: Offline Sites

```python
test_metrics = [
    {'site_id': 'site_1', 'online': False, 'error': 'Timeout'},
    {'site_id': 'site_2', 'online': True, 'battery_soh': 95},
]

analysis = analyzer.analyze_fleet(test_metrics, site_configs)
assert len(analysis['categorized']['offline']) == 1
assert analysis['offline_sites'] == 1
```

---

## Production Deployment

### Recommended Architecture

```
Cloud/Server:
  - FastAPI or Flask REST API
  - PostgreSQL (site configs + history)
  - InfluxDB (time-series metrics)
  - Redis (caching)

Data Collection:
  - Celery beat (scheduled tasks every 30s)
  - Worker pool (parallel site queries)

Dashboard:
  - React/Vue frontend
  - Real-time WebSocket updates
  - Chart.js for visualizations

AI Agent:
  - OpenAI/Anthropic API integration
  - Natural language query processing
  - Proactive alert generation
```

### Scaling Considerations

**100+ Sites**:
- Use connection pooling (max 10 connections per site)
- Implement exponential backoff for failed sites
- Cache site configs (refresh hourly)
- Store only deltas in time-series DB

**1000+ Sites**:
- Shard by geographic region
- Deploy regional collectors
- Use message queue (RabbitMQ/Kafka)
- Implement lazy loading on dashboard

---

## Next Steps

1. **Add Historical Trending**: Store health scores over time
2. **Implement Alerts**: Proactive notifications when sites degrade
3. **Build Web Dashboard**: Interactive visualizations
4. **Add Predictive Models**: Forecast future failures

---

## Related Documentation

### Tutorials
- [Tutorial 04: Predictive Maintenance Agent](./04-predictive-maintenance-agent.md) - Add ML forecasting

### How-To Guides
- [Compare Site Performance](../how-to-guides/fleet-monitoring/compare-site-performance.md) - Deep dive comparisons
- [Aggregate Alerts](../how-to-guides/fleet-monitoring/aggregate-alerts.md) - Fleet-wide alerting
- [Identify Underperformers](../how-to-guides/fleet-monitoring/identify-underperformers.md) - Find problem sites

### Concepts
- [Fleet Monitoring Patterns](../concepts/fleet-monitoring-patterns.md) - Best practices
- [Health Scoring Methodology](../concepts/health-scoring-methodology.md) - Scoring algorithms

### Reference
- [Fleet API Examples](../reference/implementation/fleet-examples.md) - Code library
- [Performance Benchmarks](../reference/performance-benchmarks.md) - Expected metrics

---

**Made in Ukraine 🇺🇦 with love by EnergyCitizen**
