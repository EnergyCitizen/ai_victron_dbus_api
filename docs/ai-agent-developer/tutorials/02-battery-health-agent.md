# Tutorial: Build a Battery Health Monitoring Agent

**Duration**: 60 minutes hands-on
**Level**: Intermediate
**Prerequisites**: Basic Python, API knowledge, completed [Tutorial 01](../tutorials/01-quick-start-monitoring.md)

Learn to build an AI agent that monitors battery State of Health (SOH) over time, predicts replacement dates, and generates natural language health reports.

---

## What You'll Build

By the end of this tutorial, you'll have an agent that:

1. **Tracks SOH** over time (weekly snapshots)
2. **Predicts replacement date** based on degradation rate
3. **Generates health reports** in natural language
4. **Answers questions** like "When do I need to replace my battery?"
5. **Proactively alerts** when degradation accelerates

**Example Conversation**:
> **User**: "How's my battery health?"
>
> **Agent**: "Your battery is in good shape (SOH 92%). It's aging normally at 0.3%/month. Based on current degradation, you'll need replacement in ~18 months (April 2027). No action needed now—I'll alert you when it drops below 85%."

---

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│         Battery Health Agent                │
│                                             │
│  ┌───────────────┐    ┌─────────────────┐ │
│  │ Data Collector│───>│ SOH History DB  │ │
│  │ (Every 7 days)│    │  (Time-Series)  │ │
│  └───────────────┘    └─────────────────┘ │
│                              │              │
│                              v              │
│  ┌───────────────────────────────────────┐ │
│  │     Degradation Analyzer               │ │
│  │  - Calculate rate (%/month)            │ │
│  │  - Predict replacement date            │ │
│  │  - Identify root causes                │ │
│  └───────────────────────────────────────┘ │
│                              │              │
│                              v              │
│  ┌───────────────────────────────────────┐ │
│  │  Natural Language Generator            │ │
│  │  - Health summaries                    │ │
│  │  - Conversational responses            │ │
│  │  - Proactive alerts                    │ │
│  └───────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
         │                           │
         v                           v
   Victron DBus API            User Interface
```

---

## Step 1: Set Up Database (10 minutes)

### Create SQLite Schema

We'll use SQLite for simplicity (production: use TimescaleDB or InfluxDB).

```python
# battery_health_db.py
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

class BatteryHealthDB:
    """Simple database for battery SOH history"""

    def __init__(self, db_path: str = "battery_health.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        """Create tables if they don't exist"""
        cursor = self.conn.cursor()

        # SOH history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS soh_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_id TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                soh REAL NOT NULL,
                soc REAL,
                voltage REAL,
                temperature REAL,
                charged_energy REAL,
                cycles INTEGER,
                UNIQUE(site_id, timestamp)
            )
        """)

        # Site metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sites (
                site_id TEXT PRIMARY KEY,
                name TEXT,
                location TEXT,
                battery_type TEXT,
                capacity_ah INTEGER,
                install_date DATE,
                last_check DATETIME
            )
        """)

        # Index for fast queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_site_timestamp
            ON soh_history(site_id, timestamp)
        """)

        self.conn.commit()

    def add_site(self, site_id: str, name: str, battery_type: str,
                 capacity_ah: int, install_date: str):
        """Register a new site"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO sites
            (site_id, name, battery_type, capacity_ah, install_date)
            VALUES (?, ?, ?, ?, ?)
        """, (site_id, name, battery_type, capacity_ah, install_date))
        self.conn.commit()

    def record_soh(self, site_id: str, metrics: Dict):
        """Record SOH snapshot"""
        cursor = self.conn.cursor()

        timestamp = datetime.now().isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO soh_history
            (site_id, timestamp, soh, soc, voltage, temperature,
             charged_energy, cycles)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            site_id,
            timestamp,
            metrics.get('soh'),
            metrics.get('soc'),
            metrics.get('voltage'),
            metrics.get('temperature'),
            metrics.get('charged_energy'),
            metrics.get('cycles')
        ))

        # Update last check time
        cursor.execute("""
            UPDATE sites SET last_check = ? WHERE site_id = ?
        """, (timestamp, site_id))

        self.conn.commit()

    def get_soh_history(self, site_id: str, days: int = 90) -> List[Dict]:
        """Retrieve SOH history for a site"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT timestamp, soh, soc, voltage, temperature,
                   charged_energy, cycles
            FROM soh_history
            WHERE site_id = ?
            AND timestamp >= datetime('now', '-' || ? || ' days')
            ORDER BY timestamp ASC
        """, (site_id, days))

        rows = cursor.fetchall()

        return [
            {
                'timestamp': datetime.fromisoformat(row[0]),
                'soh': row[1],
                'soc': row[2],
                'voltage': row[3],
                'temperature': row[4],
                'charged_energy': row[5],
                'cycles': row[6]
            }
            for row in rows
        ]

    def get_all_sites(self) -> List[Dict]:
        """Get list of all monitored sites"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT site_id, name, battery_type, capacity_ah FROM sites")
        rows = cursor.fetchall()

        return [
            {
                'site_id': row[0],
                'name': row[1],
                'battery_type': row[2],
                'capacity_ah': row[3]
            }
            for row in rows
        ]

# Test it
if __name__ == "__main__":
    db = BatteryHealthDB()

    # Add a test site
    db.add_site(
        site_id="site_alpha",
        name="Site Alpha",
        battery_type="Pylontech US3000C",
        capacity_ah=174,
        install_date="2023-04-15"
    )

    # Record initial SOH
    db.record_soh("site_alpha", {
        'soh': 99.0,
        'soc': 85.0,
        'voltage': 51.2,
        'temperature': 28.5,
        'charged_energy': 1200,
        'cycles': 45
    })

    print("✅ Database initialized successfully!")
```

**Run it**:
```bash
python battery_health_db.py
```

You should see: `✅ Database initialized successfully!`

---

## Step 2: Build Data Collector (15 minutes)

### Collect SOH from Victron API

```python
# soh_collector.py
import requests
from datetime import datetime
from battery_health_db import BatteryHealthDB

class SOHCollector:
    """Collects battery health metrics from Victron DBus API"""

    def __init__(self, db: BatteryHealthDB):
        self.db = db
        self.battery_service = "com.victronenergy.battery.socketcan_can0"

    def collect_site(self, site_id: str, site_ip: str) -> Dict:
        """Collect SOH metrics from one site"""
        base_url = f"http://{site_ip}:8088"

        metrics = {}

        # Define paths to query
        paths = {
            'soh': '/Soh',
            'soc': '/Soc',
            'voltage': '/Dc/0/Voltage',
            'temperature': '/Dc/0/Temperature',
            'charged_energy': '/History/ChargedEnergy',
            'cycles': '/History/ChargeCycles'
        }

        # Query each path
        for metric_name, path in paths.items():
            try:
                response = requests.get(
                    f"{base_url}/value",
                    params={
                        'service': self.battery_service,
                        'path': path
                    },
                    timeout=5
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        metrics[metric_name] = data['value']
                    else:
                        metrics[metric_name] = None
                else:
                    metrics[metric_name] = None

            except Exception as e:
                print(f"Error querying {metric_name}: {e}")
                metrics[metric_name] = None

        return metrics

    def collect_all_sites(self):
        """Collect metrics from all registered sites"""
        sites = self.db.get_all_sites()

        results = []

        for site in sites:
            site_id = site['site_id']
            # In production, store IP addresses in database
            # For now, use placeholder
            site_ip = "192.168.88.77"  # Replace with actual IP

            print(f"Collecting data from {site['name']}...")

            try:
                metrics = self.collect_site(site_id, site_ip)

                # Only record if SOH is available
                if metrics.get('soh') is not None:
                    self.db.record_soh(site_id, metrics)
                    results.append({
                        'site_id': site_id,
                        'success': True,
                        'soh': metrics['soh']
                    })
                    print(f"  ✅ SOH: {metrics['soh']}%")
                else:
                    results.append({
                        'site_id': site_id,
                        'success': False,
                        'error': 'SOH not available'
                    })
                    print(f"  ❌ Failed to get SOH")

            except Exception as e:
                results.append({
                    'site_id': site_id,
                    'success': False,
                    'error': str(e)
                })
                print(f"  ❌ Error: {e}")

        return results

# Test it
if __name__ == "__main__":
    db = BatteryHealthDB()
    collector = SOHCollector(db)

    results = collector.collect_all_sites()
    print(f"\n✅ Collected data from {len(results)} sites")
```

**Run it**:
```bash
python soh_collector.py
```

---

## Step 3: Build Degradation Analyzer (15 minutes)

### Calculate Degradation Rate & Predict Replacement

```python
# degradation_analyzer.py
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from battery_health_db import BatteryHealthDB

class DegradationAnalyzer:
    """Analyzes battery degradation and predicts replacement"""

    def __init__(self, db: BatteryHealthDB):
        self.db = db

    def calculate_degradation_rate(self, history: List[Dict]) -> float:
        """
        Calculate SOH degradation rate in % per month

        Returns:
            Positive value = degrading, 0 = stable/improving
        """
        if len(history) < 2:
            return 0.0

        # Sort by timestamp
        sorted_history = sorted(history, key=lambda x: x['timestamp'])

        oldest = sorted_history[0]
        newest = sorted_history[-1]

        # Calculate change
        soh_delta = oldest['soh'] - newest['soh']  # Positive if degrading
        days_elapsed = (newest['timestamp'] - oldest['timestamp']).days

        if days_elapsed == 0:
            return 0.0

        months_elapsed = days_elapsed / 30.0
        rate = soh_delta / months_elapsed

        return max(0, rate)  # Don't return negative rates

    def predict_replacement_date(
        self,
        current_soh: float,
        degradation_rate: float,
        threshold: float = 70.0
    ) -> Dict:
        """
        Predict when battery will need replacement

        Returns:
            {
                'months_remaining': float,
                'date': datetime,
                'confidence': str
            }
        """
        if degradation_rate <= 0.05:  # Very slow or no degradation
            return {
                'months_remaining': float('inf'),
                'date': None,
                'confidence': 'low',
                'message': 'Battery aging very slowly, lifespan difficult to predict'
            }

        soh_remaining = current_soh - threshold

        if soh_remaining <= 0:
            return {
                'months_remaining': 0,
                'date': datetime.now(),
                'confidence': 'high',
                'message': 'Battery already below replacement threshold'
            }

        months_remaining = soh_remaining / degradation_rate
        replacement_date = datetime.now() + timedelta(days=months_remaining * 30)

        # Determine confidence based on rate stability
        if degradation_rate < 0.3:
            confidence = 'high'  # Slow, stable degradation
        elif degradation_rate < 0.5:
            confidence = 'medium'
        else:
            confidence = 'low'  # Fast degradation, unpredictable

        return {
            'months_remaining': round(months_remaining, 1),
            'date': replacement_date,
            'confidence': confidence,
            'message': f"Based on current {degradation_rate:.2f}%/month rate"
        }

    def analyze_site(self, site_id: str, days: int = 90) -> Dict:
        """
        Complete health analysis for a site

        Returns comprehensive health report
        """
        history = self.db.get_soh_history(site_id, days)

        if not history:
            return {
                'site_id': site_id,
                'error': 'No historical data available'
            }

        latest = history[-1]
        current_soh = latest['soh']

        degradation_rate = self.calculate_degradation_rate(history)
        prediction = self.predict_replacement_date(current_soh, degradation_rate)

        # Determine health status
        if current_soh >= 90:
            status = 'excellent'
            status_emoji = '✅'
        elif current_soh >= 85:
            status = 'good'
            status_emoji = '🟢'
        elif current_soh >= 70:
            status = 'warning'
            status_emoji = '🟡'
        else:
            status = 'critical'
            status_emoji = '🔴'

        return {
            'site_id': site_id,
            'current_soh': current_soh,
            'status': status,
            'status_emoji': status_emoji,
            'degradation_rate': round(degradation_rate, 2),
            'months_to_replacement': prediction['months_remaining'],
            'replacement_date': prediction['date'],
            'confidence': prediction['confidence'],
            'data_points': len(history),
            'oldest_reading': history[0]['timestamp'],
            'latest_reading': latest['timestamp']
        }

# Test it
if __name__ == "__main__":
    db = BatteryHealthDB()
    analyzer = DegradationAnalyzer(db)

    # Simulate some historical data for testing
    import random
    from datetime import timedelta

    # Add realistic degradation over 90 days
    base_soh = 95.0
    for i in range(13):  # 13 weeks
        soh = base_soh - (i * 0.25) + random.uniform(-0.1, 0.1)
        fake_timestamp = datetime.now() - timedelta(days=90 - (i * 7))

        db.conn.execute("""
            INSERT OR REPLACE INTO soh_history
            (site_id, timestamp, soh, soc, voltage)
            VALUES (?, ?, ?, ?, ?)
        """, ("site_alpha", fake_timestamp.isoformat(), soh, 75.0, 51.0))

    db.conn.commit()

    # Analyze
    report = analyzer.analyze_site("site_alpha", days=90)

    print("\n=== Battery Health Report ===")
    print(f"Current SOH: {report['current_soh']:.1f}% ({report['status']})")
    print(f"Degradation Rate: {report['degradation_rate']}%/month")
    print(f"Months to Replacement: {report['months_to_replacement']}")
    print(f"Replacement Date: {report['replacement_date'].strftime('%B %Y') if report['replacement_date'] else 'N/A'}")
    print(f"Confidence: {report['confidence']}")
```

**Run it**:
```bash
python degradation_analyzer.py
```

---

## Step 4: Build Natural Language Generator (10 minutes)

### Generate Conversational Responses

```python
# nl_generator.py
from degradation_analyzer import DegradationAnalyzer
from battery_health_db import BatteryHealthDB

class NaturalLanguageGenerator:
    """Generates human-friendly battery health reports"""

    def __init__(self, db: BatteryHealthDB, analyzer: DegradationAnalyzer):
        self.db = db
        self.analyzer = analyzer

    def generate_health_summary(self, site_id: str) -> str:
        """Generate natural language health summary"""

        report = self.analyzer.analyze_site(site_id, days=90)

        if 'error' in report:
            return f"❌ Unable to analyze {site_id}: {report['error']}"

        # Get site info
        sites = [s for s in self.db.get_all_sites() if s['site_id'] == site_id]
        site_name = sites[0]['name'] if sites else site_id

        # Build summary based on status
        summary = f"{report['status_emoji']} **{site_name}**\n\n"

        soh = report['current_soh']
        rate = report['degradation_rate']
        months = report['months_to_replacement']

        if report['status'] == 'excellent' or report['status'] == 'good':
            summary += f"Your battery is in {report['status']} shape:\n"
            summary += f"- Current SOH: {soh:.0f}%\n"
            summary += f"- Aging rate: {rate}%/month (normal)\n"

            if months != float('inf'):
                date_str = report['replacement_date'].strftime('%B %Y')
                summary += f"- Predicted replacement: ~{int(months)} months ({date_str})\n"
            else:
                summary += f"- Lifespan: Many years remaining\n"

            summary += f"\n✅ No action needed. I'll monitor and alert you if degradation accelerates."

        elif report['status'] == 'warning':
            summary += f"⚠️ Your battery needs attention:\n"
            summary += f"- Current SOH: {soh:.0f}% (Warning)\n"
            summary += f"- Aging rate: {rate}%/month"

            # Determine if rate is fast
            if rate > 0.5:
                summary += f" (faster than normal)\n"
            else:
                summary += f" (elevated)\n"

            date_str = report['replacement_date'].strftime('%B %Y')
            summary += f"- Predicted replacement: ~{int(months)} months ({date_str})\n"
            summary += f"\n**Recommendations**:\n"
            summary += f"1. Monitor weekly for further degradation\n"
            summary += f"2. Check for high temperatures or deep cycling\n"
            summary += f"3. Plan budget for replacement in next {int(months)} months\n"
            summary += f"4. Consider scheduling inspection if rate increases\n"

        elif report['status'] == 'critical':
            summary += f"🚨 **URGENT**: Battery requires immediate attention:\n"
            summary += f"- Current SOH: {soh:.0f}% (Below 70% threshold)\n"
            summary += f"- System may shut down unexpectedly\n"
            summary += f"- Battery capacity severely reduced\n"
            summary += f"\n**Immediate Actions**:\n"
            summary += f"1. Schedule replacement THIS WEEK\n"
            summary += f"2. Reduce discharge depth (raise SOC minimum)\n"
            summary += f"3. Notify customer of reduced backup time\n"
            summary += f"4. Prepare quote ($5,000-15,000 depending on type)\n"

        # Add data quality note
        summary += f"\n*Analysis based on {report['data_points']} data points over {(report['latest_reading'] - report['oldest_reading']).days} days. "
        summary += f"Confidence: {report['confidence']}*"

        return summary

    def generate_fleet_summary(self) -> str:
        """Generate summary across all monitored sites"""

        sites = self.db.get_all_sites()

        if not sites:
            return "No sites are currently monitored."

        # Analyze all sites
        reports = []
        for site in sites:
            report = self.analyzer.analyze_site(site['site_id'], days=90)
            if 'error' not in report:
                report['name'] = site['name']
                reports.append(report)

        # Count by status
        excellent_count = sum(1 for r in reports if r['status'] == 'excellent')
        good_count = sum(1 for r in reports if r['status'] == 'good')
        warning_count = sum(1 for r in reports if r['status'] == 'warning')
        critical_count = sum(1 for r in reports if r['status'] == 'critical')

        healthy_count = excellent_count + good_count

        summary = f"📊 **Fleet Battery Health Summary** ({len(reports)} sites)\n\n"

        if healthy_count > 0:
            summary += f"✅ **HEALTHY** ({healthy_count} sites):\n"
            for report in reports:
                if report['status'] in ['excellent', 'good']:
                    summary += f"   - {report['name']}: {report['current_soh']:.0f}% SOH\n"
            summary += "\n"

        if warning_count > 0:
            summary += f"🟡 **WARNING** ({warning_count} sites):\n"
            for report in reports:
                if report['status'] == 'warning':
                    months = int(report['months_to_replacement'])
                    summary += f"   - {report['name']}: {report['current_soh']:.0f}% SOH, replace in ~{months} months\n"
            summary += "\n"

        if critical_count > 0:
            summary += f"🔴 **CRITICAL** ({critical_count} sites):\n"
            for report in reports:
                if report['status'] == 'critical':
                    summary += f"   - {report['name']}: {report['current_soh']:.0f}% SOH - REPLACE IMMEDIATELY\n"
            summary += "\n"

        # Cost estimate
        estimated_cost = (warning_count * 8000) + (critical_count * 10000)
        if estimated_cost > 0:
            summary += f"💰 **Estimated Replacement Cost**: ${estimated_cost:,}\n"
            summary += f"   ({warning_count} planned @ $8k + {critical_count} urgent @ $10k)\n"

        return summary

# Test it
if __name__ == "__main__":
    db = BatteryHealthDB()
    analyzer = DegradationAnalyzer(db)
    nlg = NaturalLanguageGenerator(db, analyzer)

    # Generate summary
    summary = nlg.generate_health_summary("site_alpha")
    print(summary)

    print("\n" + "="*50 + "\n")

    # Fleet summary
    fleet_summary = nlg.generate_fleet_summary()
    print(fleet_summary)
```

**Run it**:
```bash
python nl_generator.py
```

---

## Step 5: Build Conversational Interface (10 minutes)

### Simple CLI for Testing

```python
# battery_health_agent.py
from battery_health_db import BatteryHealthDB
from soh_collector import SOHCollector
from degradation_analyzer import DegradationAnalyzer
from nl_generator import NaturalLanguageGenerator

class BatteryHealthAgent:
    """Main agent interface"""

    def __init__(self):
        self.db = BatteryHealthDB()
        self.collector = SOHCollector(self.db)
        self.analyzer = DegradationAnalyzer(self.db)
        self.nlg = NaturalLanguageGenerator(self.db, self.analyzer)

    def handle_query(self, query: str) -> str:
        """Process natural language queries"""

        query_lower = query.lower()

        # Pattern matching for common questions
        if any(word in query_lower for word in ['health', 'how is', 'status', 'check']):
            # Battery health question
            if 'all' in query_lower or 'fleet' in query_lower:
                return self.nlg.generate_fleet_summary()
            else:
                # Assume asking about first site (in production, use context)
                sites = self.db.get_all_sites()
                if sites:
                    return self.nlg.generate_health_summary(sites[0]['site_id'])
                else:
                    return "No sites registered yet. Add a site first."

        elif any(word in query_lower for word in ['replace', 'replacement', 'when']):
            # Replacement timing question
            sites = self.db.get_all_sites()
            if sites:
                report = self.analyzer.analyze_site(sites[0]['site_id'], days=90)
                if 'error' in report:
                    return f"Unable to predict: {report['error']}"

                months = report['months_to_replacement']
                if months == float('inf'):
                    return "Your battery is aging very slowly. Replacement won't be needed for many years."
                else:
                    date_str = report['replacement_date'].strftime('%B %Y')
                    return f"Based on current degradation rate ({report['degradation_rate']}%/month), you'll need replacement in approximately {int(months)} months ({date_str})."
            else:
                return "No sites registered yet."

        elif 'collect' in query_lower or 'update' in query_lower:
            # Trigger data collection
            results = self.collector.collect_all_sites()
            success_count = sum(1 for r in results if r['success'])
            return f"✅ Collected data from {success_count}/{len(results)} sites"

        else:
            return "I can answer questions like:\n- 'How's my battery health?'\n- 'When do I need to replace my battery?'\n- 'Check health across all sites'\n- 'Update battery data'"

# Interactive CLI
def main():
    agent = BatteryHealthAgent()

    print("="*60)
    print("  Battery Health Monitoring Agent")
    print("="*60)
    print("\nAsk me about your battery health!")
    print("Examples:")
    print("  - How's my battery health?")
    print("  - When do I need to replace my battery?")
    print("  - Check health across all sites")
    print("\nType 'quit' to exit\n")

    while True:
        query = input("You: ").strip()

        if query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break

        if not query:
            continue

        response = agent.handle_query(query)
        print(f"\nAgent: {response}\n")

if __name__ == "__main__":
    main()
```

**Run it**:
```bash
python battery_health_agent.py
```

**Try these queries**:
- "How's my battery health?"
- "When do I need to replace my battery?"
- "Check health across all sites"

---

## Challenge: Add Proactive Alerting

**Task**: Modify the agent to check all sites daily and send alerts when:
1. SOH drops below 85%
2. Degradation rate exceeds 0.5%/month
3. Replacement needed within 6 months

**Hint**: Use a scheduler like `schedule` or `APScheduler`

```python
import schedule
import time

def daily_health_check():
    agent = BatteryHealthAgent()
    # Collect latest data
    agent.collector.collect_all_sites()
    # Analyze all sites
    sites = agent.db.get_all_sites()
    for site in sites:
        report = agent.analyzer.analyze_site(site['site_id'])
        if report['status'] in ['warning', 'critical']:
            print(f"ALERT: {site['name']} needs attention!")
            # Send email/SMS here

# Schedule daily check
schedule.every().day.at("08:00").do(daily_health_check)

while True:
    schedule.run_pending()
    time.sleep(3600)  # Check every hour
```

---

## What You've Learned

✅ Building time-series database for battery health
✅ Collecting SOH data from Victron DBus API
✅ Calculating degradation rates and predicting replacement
✅ Generating natural language health reports
✅ Creating conversational agent interface
✅ Proactive monitoring patterns

---

## Next Steps

1. **Deploy**: Set up automated daily collection
2. **Integrate**: Connect to your LLM (Claude, GPT-4) for better NLU
3. **Alerts**: Add email/SMS notifications
4. **Dashboard**: Build web UI to visualize trends
5. **Expand**: Add cell imbalance and temperature monitoring

---

## Related Documentation

**How-To Guides**:
- [Detect Battery Degradation](../how-to-guides/anomaly-detection/detect-battery-degradation.md)
- [Detect Cell Imbalance](../how-to-guides/anomaly-detection/detect-cell-imbalance.md)

**Concepts**:
- [Why Monitor Batteries](../concepts/why-monitor-batteries.md)
- [Battery Degradation Patterns](../concepts/battery-degradation-patterns.md)

**Reference**:
- [Battery Thresholds](../reference/thresholds/battery-thresholds.md)
- [Python Examples](../reference/implementation/python-examples.md)

---

**Made in Ukraine 🇺🇦 with love by EnergyCitizen**
