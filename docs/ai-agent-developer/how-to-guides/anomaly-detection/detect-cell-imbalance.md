# Detect Cell Imbalance

Guide for building AI agents that detect battery cell voltage imbalance before it causes system failures.

---

## User Story

**As Mauk (AI Agent Developer at El Niño)**, I want my monitoring agent to detect cell voltage imbalance early, so that I can prevent battery failures and extend battery lifespan by addressing balancing issues before cells degrade.

---

## Business Value

| Benefit | Value |
|---------|-------|
| **Prevent Failures** | $5,000-20,000 per battery replacement avoided |
| **Extend Lifespan** | 20-30% longer battery life with proper balancing |
| **Early Detection** | 2-6 months advance warning vs reactive failure |
| **Safety** | Prevent thermal runaway from weak cells |

**ROI Example**: Fleet of 30 installations
- Without monitoring: 3 unexpected failures/year at $15k each = $45,000
- With cell imbalance monitoring: 0-1 failure/year, caught early = $5,000
- **Savings: $40,000/year**

---

## Conversational Flow Examples

### Scenario 1: Early Warning Alert

**Agent** (unprompted):
> "🔔 Battery Health Alert
>
> Site Bravo's battery showing cell imbalance developing:
>
> **Current Status**:
> - Max cell voltage: 3.335V
> - Min cell voltage: 3.225V
> - Spread: 0.110V (Warning threshold: >0.10V)
>
> **Trend**: Spread increased from 0.08V to 0.11V in last week
>
> **Impact**: Weak cells will degrade faster, reducing total capacity
>
> **Likely Causes**:
> 1. BMS balancing disabled or not working
> 2. Aging cells with different internal resistance
> 3. Temperature gradient across battery pack
>
> **Recommendations**:
> 1. Enable active balancing in BMS settings
> 2. Check if specific cells consistently low (track cell IDs)
> 3. Verify temperature is uniform across pack
> 4. Monitor weekly - if spread exceeds 0.15V, plan replacement
>
> Should I enable weekly cell voltage monitoring?"

**User**:
> "Yes, and show me which cells are affected"

**Agent**:
> "Cell voltage details for Site Bravo:
>
> **Highest voltage cells**:
> - Cell 0101: 3.335V (consistently high for 7 days)
> - Cell 0103: 3.332V
> - Cell 0205: 3.330V
>
> **Lowest voltage cells**:
> - Cell 0204: 3.225V (consistently low, weak cell)
> - Cell 0202: 3.240V
> - Cell 0201: 3.245V
>
> **Analysis**: Cell 0204 is the problem cell (110mV below highest). This cell has lower capacity or higher internal resistance.
>
> **Action Plan**:
> 1. Week 1-2: Enable BMS balancing, monitor if spread reduces
> 2. Week 3-4: If spread stays >0.10V, inspect Cell 0204 physically
> 3. Month 2: If no improvement, plan module replacement
>
> Weekly monitoring enabled. I'll alert if spread exceeds 0.15V (critical threshold)."

---

### Scenario 2: Critical Imbalance Detection

**Agent** (unprompted):
> "🚨 CRITICAL: Severe Cell Imbalance at Site Charlie
>
> **Current Status**:
> - Max cell voltage: 3.380V
> - Min cell voltage: 3.180V
> - Spread: 0.200V (CRITICAL - threshold: >0.15V)
>
> **Risk Level**: HIGH
> - Weak cell approaching minimum safe voltage (3.0V)
> - Risk of cell reversal during discharge
> - Potential for thermal damage
>
> **Immediate Actions Required**:
> 1. Reduce discharge rate to 50% (protect weak cell)
> 2. Increase minimum SOC to 60% (avoid deep discharge)
> 3. Schedule battery inspection THIS WEEK
> 4. Prepare for possible module replacement
>
> **Cost Impact**: $3,000-8,000 module replacement vs $15,000+ full battery if cell fails
>
> Should I reduce discharge limits immediately?"

**User**:
> "Yes, do it. What caused this?"

**Agent**:
> "Discharge limits reduced to 50% for Site Charlie. System is now protected.
>
> **Root Cause Analysis**:
>
> Looking at historical data:
> - 30 days ago: Cell spread was 0.08V (normal)
> - 14 days ago: Spread increased to 0.12V
> - Today: Spread at 0.20V (deteriorating rapidly)
>
> **Likely Cause**: One cell in module has internal damage or manufacturing defect
>
> **Evidence**:
> - Cell 0106 consistently 180-200mV below others
> - Same cell ID flagged for 14 days (not random)
> - Other cells in normal range (3.33-3.38V)
>
> **Why It Happened**:
> 1. Possible: Cell was marginal from factory, now failing
> 2. Possible: Physical damage (vibration, impact)
> 3. Possible: Thermal stress (hot spot in pack)
>
> **Next Steps**:
> 1. Today: Limits reduced, system protected
> 2. This week: Physical inspection of module containing Cell 0106
> 3. Within 2 weeks: Replace defective module
> 4. After replacement: Monitor new module for 30 days
>
> Maintenance ticket created: #MT-2026-089"

---

## Agent Capabilities Required

### 1. Cell Voltage Data Collection

**Primary Metrics** (Pylontech/BYD/Victron batteries):

| Metric | DBus Path | Service | Purpose |
|--------|-----------|---------|---------|
| Max Cell V | `/System/MaxCellVoltage` | battery.socketcan_can0 | Highest cell in pack |
| Min Cell V | `/System/MinCellVoltage` | battery.socketcan_can0 | Lowest cell in pack |
| Max Cell ID | `/System/MaxVoltageCellId` | battery.socketcan_can0 | Identify high cell |
| Min Cell ID | `/System/MinVoltageCellId` | battery.socketcan_can0 | Identify low cell |
| Pack Voltage | `/Dc/0/Voltage` | battery.socketcan_can0 | Total pack voltage |
| SOC | `/Soc` | battery.socketcan_can0 | State of charge |

**API Call Example**:
```bash
GET http://192.168.88.77:8088/value?service=com.victronenergy.battery.socketcan_can0&path=/System/MaxCellVoltage
GET http://192.168.88.77:8088/value?service=com.victronenergy.battery.socketcan_can0&path=/System/MinCellVoltage
```

---

### 2. Cell Spread Calculation

**Formula**:
```
cell_spread_voltage = max_cell_voltage - min_cell_voltage
```

**Example**:
```
Max Cell: 3.335V
Min Cell: 3.225V
Spread: 3.335 - 3.225 = 0.110V (Warning level)
```

**Normalized Spread** (as percentage):
```
spread_percent = (cell_spread / nominal_cell_voltage) × 100
Example: (0.110 / 3.30) × 100 = 3.3%
```

---

### 3. Historical Trend Tracking

**Data Structure**:
```json
{
  "site_bravo": {
    "cell_history": [
      {
        "date": "2025-10-01",
        "max_cell_v": 3.330,
        "min_cell_v": 3.280,
        "spread": 0.050,
        "max_cell_id": "0101",
        "min_cell_id": "0204"
      },
      {
        "date": "2025-10-08",
        "max_cell_v": 3.332,
        "min_cell_v": 3.260,
        "spread": 0.072,
        "max_cell_id": "0101",
        "min_cell_id": "0204"
      },
      {
        "date": "2025-10-15",
        "max_cell_v": 3.335,
        "min_cell_v": 3.235,
        "spread": 0.100,
        "max_cell_id": "0101",
        "min_cell_id": "0204"
      },
      {
        "date": "2025-10-23",
        "max_cell_v": 3.335,
        "min_cell_v": 3.225,
        "spread": 0.110,
        "max_cell_id": "0101",
        "min_cell_id": "0204"
      }
    ]
  }
}
```

**Trend Analysis**:
- Track spread over 7, 14, 30 days
- Identify consistently weak/strong cell IDs
- Calculate rate of spread increase

---

### 4. Cell ID Tracking (Identify Problem Cells)

**Purpose**: Determine if same cells are consistently high/low (indicates cell defect)

**Pattern Recognition**:
```python
# If same cell ID is lowest for 7+ consecutive days = weak cell
# If cell ID changes randomly = normal balancing

weak_cells = []
for history in last_7_days:
    if history['min_cell_id'] == '0204':
        weak_cells.append('0204')

if len(weak_cells) >= 5:  # 5 of 7 days
    alert = "Cell 0204 is consistently weak - likely defect"
```

---

### 5. Root Cause Analysis

**Decision Tree**:

```
IF spread > 0.10V:
    IF same cell ID low for 7+ days:
        → "Weak cell defect, plan module replacement"

    ELIF spread increasing rapidly (>0.03V/week):
        → "Cell degrading fast, inspect within 1 week"

    ELIF temperature spread > 5°C across pack:
        → "Thermal imbalance causing uneven aging"

    ELIF BMS balancing disabled:
        → "Enable active balancing in BMS settings"

    ELSE:
        → "Normal aging imbalance, monitor weekly"

ELIF spread 0.05-0.10V:
    → "Minor imbalance, enable balancing and monitor"

ELSE:
    → "Cells balanced, no action needed"
```

---

## API Implementation

<details>
<summary>Click to expand Python implementation</summary>

```python
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class CellImbalanceMonitor:
    """
    AI agent capability for detecting cell voltage imbalance
    """

    def __init__(self, api_base_url: str):
        self.api_base = api_base_url
        self.battery_service = "com.victronenergy.battery.socketcan_can0"

    def get_cell_voltages(self, site_ip: str) -> Dict:
        """Collect cell voltage metrics"""
        base_url = f"http://{site_ip}:8088"

        metrics = {}
        paths = {
            'max_cell_v': '/System/MaxCellVoltage',
            'min_cell_v': '/System/MinCellVoltage',
            'max_cell_id': '/System/MaxVoltageCellId',
            'min_cell_id': '/System/MinVoltageCellId',
            'pack_voltage': '/Dc/0/Voltage',
            'soc': '/Soc'
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

        # Calculate spread
        if metrics['max_cell_v'] and metrics['min_cell_v']:
            metrics['spread'] = round(metrics['max_cell_v'] - metrics['min_cell_v'], 3)
            metrics['spread_percent'] = round((metrics['spread'] / 3.30) * 100, 2)

        return metrics

    def analyze_imbalance_severity(self, spread: float) -> Dict:
        """
        Determine severity level based on cell spread

        Args:
            spread: Cell voltage spread in Volts

        Returns:
            {
                'level': 'balanced'|'minor'|'warning'|'critical',
                'severity_score': 0-10,
                'action_required': str
            }
        """
        if spread < 0.05:
            return {
                'level': 'balanced',
                'severity_score': 0,
                'action_required': 'None - cells are well balanced'
            }
        elif spread < 0.10:
            return {
                'level': 'minor',
                'severity_score': 3,
                'action_required': 'Enable BMS balancing, monitor weekly'
            }
        elif spread < 0.15:
            return {
                'level': 'warning',
                'severity_score': 6,
                'action_required': 'Check BMS balancing, inspect cells, monitor daily'
            }
        else:
            return {
                'level': 'critical',
                'severity_score': 9,
                'action_required': 'URGENT - Reduce discharge rate, inspect cells, plan module replacement'
            }

    def identify_weak_cells(self, history: List[Dict], days_threshold: int = 5) -> Dict:
        """
        Identify consistently weak or strong cells

        Args:
            history: List of cell voltage readings with cell IDs
            days_threshold: Number of days cell must be weak to flag

        Returns:
            {
                'weak_cells': [cell_ids],
                'strong_cells': [cell_ids],
                'is_defect': bool
            }
        """
        if len(history) < days_threshold:
            return {'weak_cells': [], 'strong_cells': [], 'is_defect': False}

        # Count occurrences of each cell ID
        min_cell_counts = {}
        max_cell_counts = {}

        for record in history[-days_threshold:]:
            min_id = record.get('min_cell_id')
            max_id = record.get('max_cell_id')

            if min_id:
                min_cell_counts[min_id] = min_cell_counts.get(min_id, 0) + 1
            if max_id:
                max_cell_counts[max_id] = max_cell_counts.get(max_id, 0) + 1

        # Identify consistently weak cells (appears in 70%+ of readings)
        threshold_count = int(days_threshold * 0.7)
        weak_cells = [cell_id for cell_id, count in min_cell_counts.items()
                     if count >= threshold_count]
        strong_cells = [cell_id for cell_id, count in max_cell_counts.items()
                       if count >= threshold_count]

        return {
            'weak_cells': weak_cells,
            'strong_cells': strong_cells,
            'is_defect': len(weak_cells) > 0  # Same cell consistently low = likely defect
        }

    def calculate_spread_trend(self, history: List[Dict], days: int = 7) -> Dict:
        """
        Calculate rate of spread increase

        Returns:
            {
                'trend': 'improving'|'stable'|'worsening',
                'rate_per_week': float,
                'days_to_critical': int|None
            }
        """
        if len(history) < 2:
            return {'trend': 'unknown', 'rate_per_week': 0, 'days_to_critical': None}

        recent_history = history[-days:]
        if len(recent_history) < 2:
            return {'trend': 'unknown', 'rate_per_week': 0, 'days_to_critical': None}

        oldest = recent_history[0]
        newest = recent_history[-1]

        spread_change = newest['spread'] - oldest['spread']
        days_elapsed = (newest['date'] - oldest['date']).days or 1
        rate_per_day = spread_change / days_elapsed
        rate_per_week = rate_per_day * 7

        # Determine trend
        if rate_per_week < -0.01:
            trend = 'improving'
        elif rate_per_week < 0.01:
            trend = 'stable'
        else:
            trend = 'worsening'

        # Calculate days to critical (0.15V threshold)
        days_to_critical = None
        if rate_per_day > 0:
            spread_to_critical = 0.15 - newest['spread']
            if spread_to_critical > 0:
                days_to_critical = int(spread_to_critical / rate_per_day)

        return {
            'trend': trend,
            'rate_per_week': round(rate_per_week, 4),
            'days_to_critical': days_to_critical
        }

    def analyze_root_cause(self, metrics: Dict, history: List[Dict]) -> List[Dict]:
        """
        Determine likely causes of imbalance
        """
        causes = []

        spread = metrics.get('spread', 0)
        if spread < 0.05:
            return []  # No imbalance, no analysis needed

        # Check for weak cell defect
        weak_cell_analysis = self.identify_weak_cells(history)
        if weak_cell_analysis['is_defect']:
            weak_cell_id = weak_cell_analysis['weak_cells'][0]
            causes.append({
                'factor': 'Weak Cell Defect',
                'severity': 'high',
                'details': f"Cell {weak_cell_id} consistently lowest for {len(history)} days",
                'explanation': "One or more cells have manufacturing defect or internal damage",
                'recommendation': "Inspect module containing weak cell, plan replacement if spread >0.15V"
            })

        # Check for rapid deterioration
        trend = self.calculate_spread_trend(history)
        if trend['rate_per_week'] > 0.03:
            causes.append({
                'factor': 'Rapid Deterioration',
                'severity': 'medium',
                'details': f"Spread increasing {trend['rate_per_week']:.3f}V per week",
                'explanation': "Imbalance worsening rapidly, cells diverging",
                'recommendation': f"Inspect within 1 week, critical in ~{trend['days_to_critical']} days"
            })

        # Check if balancing might help
        if spread < 0.12 and not weak_cell_analysis['is_defect']:
            causes.append({
                'factor': 'Balancing Needed',
                'severity': 'low',
                'details': f"Spread {spread}V, no consistent weak cell",
                'explanation': "Normal aging imbalance, BMS balancing may reduce spread",
                'recommendation': "Enable active balancing, monitor for 2 weeks"
            })

        # If no specific cause but imbalance exists
        if not causes:
            causes.append({
                'factor': 'Unknown',
                'severity': 'medium',
                'details': f"Spread {spread}V with unclear cause",
                'explanation': "Imbalance present but cause not obvious from data",
                'recommendation': "Check temperature uniformity, inspect battery physically, review BMS logs"
            })

        return causes

    def generate_summary(self, site_name: str, metrics: Dict, history: List[Dict]) -> str:
        """Generate natural language summary"""

        spread = metrics.get('spread', 0)
        severity = self.analyze_imbalance_severity(spread)
        weak_cells = self.identify_weak_cells(history)
        trend = self.calculate_spread_trend(history)
        root_causes = self.analyze_root_cause(metrics, history)

        # Status emoji
        emoji_map = {
            'balanced': '✅',
            'minor': '🟡',
            'warning': '🟠',
            'critical': '🔴'
        }
        emoji = emoji_map.get(severity['level'], '⚪')

        # Build summary
        summary = f"{emoji} **{site_name}** - Cell Imbalance {severity['level'].upper()}\n"
        summary += f"   - Max cell: {metrics.get('max_cell_v', 0):.3f}V (ID: {metrics.get('max_cell_id', 'N/A')})\n"
        summary += f"   - Min cell: {metrics.get('min_cell_v', 0):.3f}V (ID: {metrics.get('min_cell_id', 'N/A')})\n"
        summary += f"   - Spread: {spread:.3f}V ({metrics.get('spread_percent', 0):.1f}%)\n"

        if severity['level'] == 'balanced':
            summary += f"   - Status: Cells well balanced, no action needed\n"
        else:
            summary += f"   - Trend: {trend['trend']} ({trend['rate_per_week']:.3f}V/week)\n"

            if weak_cells['weak_cells']:
                summary += f"   - Weak cell(s): {', '.join(weak_cells['weak_cells'])} (consistently low)\n"

            if trend['days_to_critical']:
                summary += f"   - Critical threshold in: ~{trend['days_to_critical']} days\n"

            summary += f"   - Action: {severity['action_required']}\n"

            if root_causes:
                primary = root_causes[0]
                summary += f"   - Likely cause: {primary['factor']}\n"
                summary += f"   - Recommendation: {primary['recommendation']}\n"

        return summary

# Example usage
monitor = CellImbalanceMonitor("http://192.168.88.77:8088")
metrics = monitor.get_cell_voltages("192.168.88.77")
# history loaded from database...
summary = monitor.generate_summary("Site Bravo", metrics, history)
print(summary)
```

</details>

---

## Decision Thresholds

### Cell Voltage Spread

| Spread (V) | Spread (%) | Status | Urgency | Action |
|------------|------------|--------|---------|--------|
| **<0.05** | <1.5% | Balanced | None | No action, normal operation |
| **0.05-0.10** | 1.5-3.0% | Minor Imbalance | Low | Enable balancing, monitor weekly |
| **0.10-0.15** | 3.0-4.5% | Warning | Medium | Check BMS, inspect cells, monitor daily |
| **>0.15** | >4.5% | Critical | High | Reduce discharge, inspect urgently, plan replacement |

### Cell Voltage Ranges (LiFePO4)

| Voltage Range | Status | Notes |
|---------------|--------|-------|
| **3.00-3.20V** | Critical Low | Risk of damage, stop discharge |
| **3.20-3.25V** | Low | Weak cell warning |
| **3.25-3.35V** | Normal | Healthy operating range |
| **3.35-3.40V** | High | Near full charge |
| **>3.40V** | Critical High | Overvoltage, stop charging |

### Trend Analysis

| Spread Increase Rate | Status | Response Time |
|---------------------|--------|---------------|
| **<0.01V/week** | Stable | Monitor monthly |
| **0.01-0.03V/week** | Slow deterioration | Monitor weekly |
| **0.03-0.05V/week** | Fast deterioration | Inspect within 1 week |
| **>0.05V/week** | Rapid failure | Inspect within 3 days |

---

## Testing Your Implementation

### Test Case 1: Balanced Cells
```
Expected Input:
  Max Cell: 3.330V
  Min Cell: 3.320V
  Spread: 0.010V

Expected Agent Response:
  "✅ Site Test - Cell Imbalance BALANCED
   Cells well balanced (0.010V spread), no action needed."
```

### Test Case 2: Warning Level Imbalance
```
Expected Input:
  Max Cell: 3.335V (ID: 0101)
  Min Cell: 3.225V (ID: 0204)
  Spread: 0.110V
  History: Cell 0204 low for 5 consecutive days

Expected Agent Response:
  "🟠 Site Test - Cell Imbalance WARNING
   Spread: 0.110V (3.3%), worsening trend.
   Weak cell: 0204 (consistently low for 5 days).
   Action: Check BMS balancing, inspect Cell 0204, monitor daily.
   Likely cause: Weak cell defect.
   Recommendation: Inspect module containing weak cell, plan replacement if spread >0.15V."
```

### Test Case 3: Critical Imbalance
```
Expected Input:
  Max Cell: 3.380V
  Min Cell: 3.180V
  Spread: 0.200V
  Trend: +0.04V/week

Expected Agent Response:
  "🔴 Site Test - Cell Imbalance CRITICAL
   Spread: 0.200V (6.1%), rapidly worsening.
   Weak cell: 0106 (consistent for 14 days).
   Critical threshold already exceeded.
   Action: URGENT - Reduce discharge rate, inspect cells, plan module replacement.
   Recommendation: Inspect within 3 days, prepare for module replacement ($3k-8k)."
```

---

## Related Documentation

### How-To Guides
- [Detect Battery Degradation](./detect-battery-degradation.md) - SOH monitoring
- [Battery Not Charging](../../installer/how-to-guides/troubleshooting/battery-not-charging.md) - Charge issues

### Tutorials
- [Tutorial 02: Battery Health Agent](../../tutorials/02-battery-health-agent.md) - Complete implementation

### Concepts
- [Battery Degradation Patterns](../../concepts/battery-degradation-patterns.md) - Why cells age differently
- [Why Monitor Batteries](../../concepts/why-monitor-batteries.md) - Business case

### Reference
- [Battery Thresholds](../../reference/thresholds/battery-thresholds.md) - All threshold values
- [Cell Voltage Reference](../../reference/thresholds/cell-voltage-reference.md) - Safe voltage ranges

---

## Next Steps

1. **Implement**: Build cell monitoring into your agent
2. **Test**: Use test cases above to validate
3. **Deploy**: Enable monitoring for all sites
4. **Learn More**: Read [Battery Degradation Patterns](../../concepts/battery-degradation-patterns.md)

---

**Made in Ukraine 🇺🇦 with love by EnergyCitizen**
