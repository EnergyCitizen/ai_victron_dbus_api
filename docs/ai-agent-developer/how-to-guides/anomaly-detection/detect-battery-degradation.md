# Detect Battery Degradation

Guide for building AI agents that detect battery aging early and predict replacement needs.

---

## User Story

**As Mauk (AI Agent Developer at El Niño)**, I want my fleet monitoring agent to detect battery degradation early, so that I can schedule replacements 3-6 months in advance and avoid $5k-20k emergency replacements.

---

## Business Value

| Benefit | Value |
|---------|-------|
| **Cost Savings** | $5,000-20,000 per battery (avoid emergency replacement premium) |
| **Uptime** | Prevent unexpected outages and customer downtime |
| **Planning** | 3-6 month lead time for procurement and scheduling |
| **Customer Satisfaction** | Proactive maintenance vs reactive firefighting |

**ROI Example**: Fleet of 50 installations
- Average: 2 batteries degrade to replacement threshold per year
- Reactive cost: $40,000 (2 × $20k emergency)
- Proactive cost: $10,000 (2 × $5k planned)
- **Savings: $30,000/year**

---

## Conversational Flow Examples

### Scenario 1: Proactive Agent Alert

**Agent** (unprompted):
> "🔔 Battery Health Alert
>
> Site Alpha's battery SOH dropped from 88% to 82% in the last month—that's 3× faster than normal degradation.
>
> **Prediction**: Will reach 70% replacement threshold in ~8 months (June 2026)
>
> **Likely Cause**: Average temperature 42°C (8° above optimal)
>
> **Recommendations**:
> 1. Check cooling system airflow
> 2. Reduce peak discharge rate (lower inverter limit)
> 3. Plan battery replacement for Q2 2026
>
> Should I create a maintenance ticket?"

**User**:
> "Yes, and show me the degradation chart"

**Agent**:
> "[Shows graph: SOH trending from 88% → 82% over 30 days, projection to 70% in 8 months]
>
> Maintenance ticket created: #MT-2026-042
> Assigned to: Installation team
> Due date: May 2026
> Estimated cost: $7,500 (planned replacement)"

---

### Scenario 2: User-Initiated Query

**User**:
> "Check battery health across all my sites"

**Agent Thinks** (internal reasoning, not shown to user):
```
1. Identify "battery health" metrics:
   - SOH (State of Health)
   - SOC (current charge level)
   - Cell voltage spread (imbalance indicator)
   - Temperature (stress indicator)
   - Degradation rate (trending)

2. Query all 12 sites in parallel

3. Apply thresholds:
   - SOH <70% = Critical (replace now)
   - SOH <85% = Warning (plan replacement)
   - Degradation rate >0.5%/month = Accelerated (investigate)
   - Cell spread >0.10V = Imbalance (monitor closely)

4. Calculate health scores (0-100, weighted)

5. Rank sites by urgency

6. Generate natural language summary
```

**Agent Says**:
> "Battery health summary across 12 sites:
>
> **HEALTHY** (10 sites): SOC 60-95%, SOH 90-99%
> - All batteries aging normally (<0.2%/month)
> - No immediate concerns
>
> **WARNING** (2 sites):
>
> 🟡 **Site Alpha**: SOH 82% (↓6% last month)
>    - Health Score: 72/100
>    - Degradation: 2.0%/month (10× normal)
>    - Prediction: Replace in ~8 months
>    - Action: Check cooling, reduce discharge rate
>
> 🟡 **Site Beta**: SOH 94%, Cell spread 0.12V
>    - Health Score: 78/100
>    - Issue: Cell imbalance developing
>    - Prediction: Monitor weekly, may need balancing
>    - Action: Check BMS configuration
>
> **CRITICAL** (0 sites)
>
> **Cost Estimate**: $15,000 (2 batteries, planned replacements)
>
> Would you like:
> 1. Detailed analysis of Site Alpha?
> 2. Historical SOH charts?
> 3. Create maintenance schedule?"

**User**:
> "Show me Site Alpha details"

**Agent**:
> "Site Alpha - Detailed Analysis:
>
> **Current State**:
> - SOH: 82% (Warning)
> - SOC: 67% (Normal)
> - Voltage: 49.2V (Normal)
> - Temperature: 42°C (High, 8° above optimal 20-35°C)
> - Cell Spread: 0.08V (OK)
>
> **30-Day Trend**:
> - SOH lost: 6 percentage points
> - Rate: 2.0%/month (vs normal 0.2%/month)
> - Temperature avg: 42°C (consistently high)
>
> **Root Cause Analysis**:
> High temperature is accelerating degradation. Each 10°C above 25°C doubles aging rate.
>
> **Immediate Actions**:
> 1. ✅ Verify cooling fan operation
> 2. ✅ Check battery enclosure ventilation
> 3. ✅ Reduce max charge current by 20% (less heat)
> 4. ✅ Lower discharge C-rate limit
>
> **Long-Term Plan**:
> - Monitor SOH weekly
> - If rate stays >1%/month → Replace in 6 months
> - If rate drops to <0.5%/month → Extend to 12 months
>
> Shall I monitor temperature and alert if it stays >40°C?"

---

## Agent Capabilities Required

### 1. Data Collection

**Primary Metrics** (query for each site):

| Metric | DBus Path | Service | Purpose |
|--------|-----------|---------|---------|
| SOH | `/Soh` | battery.socketcan_can0 | Degradation indicator |
| SOC | `/Soc` | battery.socketcan_can0 | Current charge level |
| Voltage | `/Dc/0/Voltage` | battery.socketcan_can0 | Operating voltage |
| Current | `/Dc/0/Current` | battery.socketcan_can0 | Charge/discharge rate |
| Temperature | `/Dc/0/Temperature` | battery.socketcan_can0 | Thermal stress |
| Max Cell V | `/System/MaxCellVoltage` | battery.socketcan_can0 | Cell balance (high) |
| Min Cell V | `/System/MinCellVoltage` | battery.socketcan_can0 | Cell balance (low) |
| Charged Energy | `/History/ChargedEnergy` | battery.socketcan_can0 | Lifetime throughput |
| Cycles | `/History/ChargeCycles` | battery.socketcan_can0 | Cycle count |

**API Call Pattern**:
```
GET http://192.168.88.77:8088/value?service=com.victronenergy.battery.socketcan_can0&path=/Soh
```

---

### 2. Historical Trending

**Requirement**: Store SOH values over time (minimum 30 days, recommend 12 months)

**Data Structure**:
```json
{
  "site_alpha": {
    "soh_history": [
      {"date": "2025-09-23", "soh": 88.0, "temp_avg": 41.5},
      {"date": "2025-09-30", "soh": 86.5, "temp_avg": 42.1},
      {"date": "2025-10-07", "soh": 85.0, "temp_avg": 43.0},
      {"date": "2025-10-14", "soh": 83.5, "temp_avg": 42.8},
      {"date": "2025-10-23", "soh": 82.0, "temp_avg": 42.3}
    ],
    "metadata": {
      "battery_type": "Pylontech US3000C",
      "capacity_ah": 174,
      "install_date": "2023-04-15"
    }
  }
}
```

**Storage Options**:
- Time-series database: InfluxDB, TimescaleDB
- Simple: SQLite with indexed timestamps
- Cloud: Firebase, Supabase

---

### 3. Degradation Rate Calculation

**Algorithm**:
```
degradation_rate = (SOH_baseline - SOH_current) / months_elapsed

Example:
  Baseline (30 days ago): 88%
  Current: 82%
  Elapsed: 1 month
  Rate: (88 - 82) / 1 = 6%/month
```

**Normal vs Abnormal**:
- Normal: 0.1-0.3%/month (LiFePO4)
- Concerning: 0.5-1.0%/month
- Critical: >1.0%/month

---

### 4. Replacement Date Prediction

**Algorithm**:
```
months_to_replacement = (SOH_current - 70) / degradation_rate

Example:
  Current SOH: 82%
  Threshold: 70%
  Rate: 2.0%/month
  Months: (82 - 70) / 2.0 = 6 months
```

**Confidence Levels**:
- High (>90%): 30+ days of data, stable rate
- Medium (70-90%): 14-30 days of data
- Low (<70%): <14 days, use conservative estimate

---

### 5. Root Cause Analysis

**Common Degradation Causes**:

| Cause | Indicator | DBus Path | Resolution |
|-------|-----------|-----------|------------|
| **High Temperature** | Temp >40°C | `/Dc/0/Temperature` | Check cooling, reduce charge rate |
| **Deep Cycling** | SOC <20% frequently | `/Dc/Battery/Soc` | Increase SOC limit |
| **High C-Rate** | Current >0.5C | `/Dc/0/Current` | Lower power limits |
| **Cell Imbalance** | Spread >0.10V | `/System/MaxCellVoltage` - `/System/MinCellVoltage` | BMS balancing, check cells |
| **Age** | 5+ years old | Install date metadata | Normal wear, plan replacement |

**Agent Analysis Pattern**:
```
IF degradation_rate > 0.5%/month AND temperature > 40°C:
    likely_cause = "High temperature accelerating aging"
    recommendation = "Improve cooling, reduce charge current"
ELIF degradation_rate > 0.5%/month AND cell_spread > 0.10V:
    likely_cause = "Cell imbalance causing uneven aging"
    recommendation = "Check BMS balancing, inspect cell voltages"
ELIF degradation_rate > 0.5%/month AND cycles > 4000:
    likely_cause = "Normal end-of-life wear"
    recommendation = "Battery approaching design lifetime, plan replacement"
ELSE:
    likely_cause = "Unknown - requires investigation"
    recommendation = "Review charge/discharge patterns, check BMS logs"
```

---

### 6. Natural Language Generation

**Response Templates**:

**Healthy Battery**:
```
"Battery at {site} is healthy:
 - SOH: {soh}% (Excellent)
 - Aging normally at {rate}%/month
 - No action needed, continue monitoring"
```

**Warning**:
```
"Battery at {site} needs attention:
 - SOH: {soh}% (Warning)
 - Degrading {rate}%/month (faster than normal)
 - Predicted replacement: {months} months ({date})
 - Likely cause: {root_cause}
 - Recommended action: {recommendation}"
```

**Critical**:
```
"🚨 URGENT: Battery at {site} requires immediate replacement:
 - SOH: {soh}% (below 70% threshold)
 - System may shut down unexpectedly
 - Schedule replacement THIS WEEK
 - Estimated cost: ${cost}"
```

---

## API Implementation

<details>
<summary>Click to expand Python implementation</summary>

```python
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class BatteryDegradationMonitor:
    """
    AI agent capability for detecting battery degradation
    """

    def __init__(self, api_base_url: str):
        self.api_base = api_base_url
        self.battery_service = "com.victronenergy.battery.socketcan_can0"

    def get_current_metrics(self, site_ip: str) -> Dict:
        """Collect current battery health metrics"""
        base_url = f"http://{site_ip}:8088"

        metrics = {}
        paths = {
            'soh': '/Soh',
            'soc': '/Soc',
            'voltage': '/Dc/0/Voltage',
            'current': '/Dc/0/Current',
            'power': '/Dc/0/Power',
            'temperature': '/Dc/0/Temperature',
            'max_cell_v': '/System/MaxCellVoltage',
            'min_cell_v': '/System/MinCellVoltage',
            'charged_energy': '/History/ChargedEnergy',
            'cycles': '/History/ChargeCycles'
        }

        for key, path in paths.items():
            try:
                response = requests.get(
                    f"{base_url}/value",
                    params={'service': self.battery_service, 'path': path},
                    timeout=2
                )
                if response.json().get('success'):
                    metrics[key] = response.json()['value']
            except:
                metrics[key] = None

        # Calculate cell spread
        if metrics['max_cell_v'] and metrics['min_cell_v']:
            metrics['cell_spread'] = metrics['max_cell_v'] - metrics['min_cell_v']

        return metrics

    def calculate_degradation_rate(self, history: List[Dict]) -> float:
        """
        Calculate SOH degradation rate in % per month

        Args:
            history: List of {'date': datetime, 'soh': float} dicts

        Returns:
            float: Degradation rate in %/month (positive = degrading)
        """
        if len(history) < 2:
            return 0.0

        # Sort by date
        sorted_history = sorted(history, key=lambda x: x['date'])

        oldest = sorted_history[0]
        newest = sorted_history[-1]

        soh_delta = oldest['soh'] - newest['soh']  # Positive if degrading
        days_elapsed = (newest['date'] - oldest['date']).days
        months_elapsed = days_elapsed / 30.0

        if months_elapsed == 0:
            return 0.0

        return soh_delta / months_elapsed

    def predict_replacement_date(
        self,
        current_soh: float,
        degradation_rate: float,
        threshold: float = 70.0
    ) -> Dict:
        """
        Predict when battery SOH will drop below threshold

        Returns:
            {
                'months_remaining': float,
                'date': datetime,
                'confidence': str ('high'|'medium'|'low')
            }
        """
        if degradation_rate <= 0:
            return {
                'months_remaining': float('inf'),
                'date': None,
                'confidence': 'unknown'
            }

        soh_remaining = current_soh - threshold
        months_remaining = soh_remaining / degradation_rate

        replacement_date = datetime.now() + timedelta(days=months_remaining * 30)

        # Confidence based on data points (from context)
        # High: 30+ days, Medium: 14-30 days, Low: <14 days
        confidence = 'medium'  # Placeholder, calculate from history length

        return {
            'months_remaining': max(0, months_remaining),
            'date': replacement_date,
            'confidence': confidence
        }

    def analyze_root_cause(self, metrics: Dict, degradation_rate: float) -> Dict:
        """
        Determine likely cause of degradation
        """
        causes = []

        # High temperature?
        if metrics.get('temperature', 0) > 40:
            causes.append({
                'factor': 'High Temperature',
                'severity': 'high',
                'value': f"{metrics['temperature']}°C",
                'explanation': f"Temperature is {metrics['temperature'] - 35}°C above optimal (35°C). Each 10°C doubles aging rate.",
                'recommendation': "Check cooling system, improve ventilation, reduce charge current"
            })

        # Cell imbalance?
        cell_spread = metrics.get('cell_spread', 0)
        if cell_spread > 0.10:
            causes.append({
                'factor': 'Cell Imbalance',
                'severity': 'medium',
                'value': f"{cell_spread:.3f}V spread",
                'explanation': "Cell voltage difference indicates uneven aging or balancing issues",
                'recommendation': "Check BMS balancing settings, inspect individual cells"
            })

        # High C-rate?
        capacity_ah = metrics.get('capacity', 174)  # Example
        current = abs(metrics.get('current', 0))
        c_rate = current / capacity_ah if capacity_ah > 0 else 0

        if c_rate > 0.5:
            causes.append({
                'factor': 'High C-Rate',
                'severity': 'medium',
                'value': f"{c_rate:.2f}C",
                'explanation': f"Charging/discharging at {c_rate:.2f}C (recommended <0.5C for longevity)",
                'recommendation': "Reduce inverter power limits, limit discharge depth"
            })

        # High cycle count?
        cycles = metrics.get('cycles', 0)
        if cycles > 4000:
            causes.append({
                'factor': 'High Cycle Count',
                'severity': 'low',
                'value': f"{cycles} cycles",
                'explanation': "Battery approaching design lifetime (typically 6,000 cycles for LiFePO4)",
                'recommendation': "Normal end-of-life wear, plan replacement"
            })

        # If no specific cause but degradation is fast
        if not causes and degradation_rate > 0.5:
            causes.append({
                'factor': 'Unknown',
                'severity': 'medium',
                'value': f"{degradation_rate:.1f}%/month",
                'explanation': "Degradation is faster than normal but specific cause unclear",
                'recommendation': "Review charge/discharge patterns, check BMS error logs, inspect battery physically"
            })

        return {
            'causes': causes,
            'primary_cause': causes[0] if causes else None
        }

    def generate_summary(self, site_name: str, metrics: Dict, history: List[Dict]) -> str:
        """Generate natural language summary"""

        soh = metrics.get('soh', 0)
        rate = self.calculate_degradation_rate(history)
        prediction = self.predict_replacement_date(soh, rate)
        root_cause = self.analyze_root_cause(metrics, rate)

        # Status determination
        if soh >= 90:
            status = "HEALTHY"
            emoji = "✅"
        elif soh >= 85:
            status = "GOOD"
            emoji = "🟢"
        elif soh >= 70:
            status = "WARNING"
            emoji = "🟡"
        else:
            status = "CRITICAL"
            emoji = "🔴"

        # Build summary
        summary = f"{emoji} **{site_name}**: SOH {soh:.0f}% ({status})\n"

        if status == "HEALTHY" or status == "GOOD":
            summary += f"   - Aging normally at {rate:.1f}%/month\n"
            summary += f"   - No action needed"

        elif status == "WARNING":
            months = prediction['months_remaining']
            summary += f"   - Degrading at {rate:.1f}%/month (faster than normal)\n"
            summary += f"   - Predicted replacement: ~{int(months)} months ({prediction['date'].strftime('%b %Y')})\n"

            if root_cause['primary_cause']:
                cause = root_cause['primary_cause']
                summary += f"   - Likely cause: {cause['factor']} ({cause['value']})\n"
                summary += f"   - Action: {cause['recommendation']}"

        elif status == "CRITICAL":
            summary += f"   - 🚨 URGENT: Replace immediately\n"
            summary += f"   - System may shut down unexpectedly\n"
            summary += f"   - Estimated cost: $7,500"

        return summary

# Example usage
monitor = BatteryDegradationMonitor("http://192.168.88.77:8088")
metrics = monitor.get_current_metrics("192.168.88.77")
# history loaded from database...
summary = monitor.generate_summary("Site Alpha", metrics, history)
print(summary)
```

</details>

---

## Decision Thresholds

### SOH (State of Health)

| Range | Status | Action | Timeline |
|-------|--------|--------|----------|
| **95-100%** | Excellent | Monitor quarterly | No action |
| **90-95%** | Good | Monitor monthly | No action |
| **85-90%** | Fair | Monitor weekly | Plan replacement in 12-24 months |
| **70-85%** | Warning | Monitor daily | Plan replacement in 3-12 months |
| **<70%** | Critical | Alert immediately | Replace within 1 month |

### Degradation Rate

| Rate (%/month) | Status | Severity | Investigation |
|----------------|--------|----------|---------------|
| **<0.2** | Normal | None | No action |
| **0.2-0.5** | Elevated | Low | Monitor for trend |
| **0.5-1.0** | Concerning | Medium | Investigate cause |
| **>1.0** | Critical | High | Immediate intervention |

### Cell Voltage Spread

| Spread (V) | Status | Urgency | Action |
|------------|--------|---------|--------|
| **<0.05** | Balanced | None | No action |
| **0.05-0.10** | Minor Imbalance | Low | Monitor weekly |
| **0.10-0.15** | Imbalanced | Medium | Check BMS balancing |
| **>0.15** | Severe | High | Inspect cells, possible replacement |

### Temperature Impact

| Temperature (°C) | Aging Rate Multiplier | Status |
|------------------|----------------------|--------|
| **20-30** | 1× (baseline) | Optimal |
| **30-40** | 1.5× | Acceptable |
| **40-50** | 2.5× | Concerning |
| **>50** | 4× | Critical |

**Formula**: For every 10°C above 25°C, aging rate approximately doubles.

---

## Testing Your Implementation

### Test Case 1: Healthy Battery
```
Expected Input:
  SOH: 96%
  Rate: 0.15%/month
  Temperature: 28°C

Expected Agent Response:
  "Battery at Site Test is healthy (SOH 96%). Aging normally at 0.15%/month. No action needed."
```

### Test Case 2: Warning - Fast Degradation
```
Expected Input:
  SOH: 82%
  Rate: 2.0%/month
  Temperature: 42°C
  History: 30 days of data

Expected Agent Response:
  "Battery at Site Test needs attention (SOH 82%, Warning). Degrading at 2.0%/month—10× normal rate.
   Predicted replacement: ~6 months (April 2026).
   Likely cause: High temperature (42°C, 7° above optimal).
   Recommendation: Check cooling system, reduce charge rate."
```

### Test Case 3: Critical - Immediate Replacement
```
Expected Input:
  SOH: 68%
  Rate: 1.5%/month

Expected Agent Response:
  "🚨 URGENT: Battery at Site Test requires immediate replacement (SOH 68%, below 70% threshold).
   System may shut down unexpectedly. Schedule replacement THIS WEEK. Estimated cost: $7,500."
```

---

## Related Documentation

### Tutorials
- [Tutorial 02: Battery Health Agent](../../tutorials/02-battery-health-agent.md) - Complete implementation walkthrough

### How-To Guides
- [Detect Cell Imbalance](./detect-cell-imbalance.md) - Deeper dive on cell voltage monitoring
- [Proactive Alerts](../conversational-patterns/proactive-alerts.md) - Agent-initiated notifications
- [Compare Site Performance](../fleet-monitoring/compare-site-performance.md) - Identify worst performers

### Concepts
- [Battery Degradation Patterns](../../concepts/battery-degradation-patterns.md) - Why batteries age
- [Why Monitor Batteries](../../concepts/why-monitor-batteries.md) - Business case and ROI

### Reference
- [Battery Thresholds](../../reference/thresholds/battery-thresholds.md) - All threshold values
- [Critical Paths](../../reference/api/critical-paths.md) - Essential API paths
- [Python Examples](../../reference/implementation/python-examples.md) - Code snippets library

---

## Next Steps

1. **Implement**: Build this capability into your agent
2. **Test**: Use test cases above to validate
3. **Learn More**: Read [Battery Degradation Patterns](../../concepts/battery-degradation-patterns.md) concept
4. **Expand**: Add [Cell Imbalance Detection](./detect-cell-imbalance.md)

---

**Made in Ukraine 🇺🇦 with love by EnergyCitizen**
