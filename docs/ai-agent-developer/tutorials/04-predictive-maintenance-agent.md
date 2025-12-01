# Tutorial 04: Build a Predictive Maintenance Agent

Build an AI agent that predicts hardware failures 30-90 days in advance using risk scoring and trend analysis.

**Time Required**: 120 minutes
**Difficulty**: Advanced
**Prerequisites**: Completed Tutorial 02 (Battery Health Agent)

---

## Learning Objectives

By the end of this tutorial, you will:
- Calculate failure risk scores for batteries, inverters, and grid connectivity
- Predict maintenance needs 30-180 days in advance
- Generate conversational maintenance recommendations
- Schedule preventive maintenance based on risk analysis
- Estimate maintenance costs and prioritize interventions

---

## User Story

**As an AI Agent Developer**, I want my fleet agent to predict hardware failures before they happen, so I can schedule maintenance during customer off-hours and avoid $10k+ emergency service calls.

**Business Value**:
- Avoid emergency service premiums (save $5k-15k per incident)
- Schedule maintenance during low-impact windows
- Order replacement parts in advance (avoid expedited shipping)
- Reduce customer downtime from days to hours
- Improve customer satisfaction through proactive communication

---

## What We're Building

A predictive maintenance agent that:

1. **Analyzes historical trends** (30-90 days of data)
2. **Calculates risk scores** (0-100 for each component)
3. **Predicts failure dates** (with confidence intervals)
4. **Generates maintenance schedules** (prioritized by risk)
5. **Estimates costs** (labor + parts + urgency premium)
6. **Communicates proactively** ("Battery at Site Alpha needs replacement in 6 months")

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                 Predictive Maintenance Agent             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │  Battery   │  │  Inverter  │  │   Grid     │       │
│  │  Risk      │  │  Risk      │  │   Risk     │       │
│  │  Scorer    │  │  Scorer    │  │   Scorer   │       │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘       │
│        │                │                │              │
│        └────────────────┴────────────────┘              │
│                         │                               │
│                  ┌──────▼──────┐                        │
│                  │  Risk       │                        │
│                  │  Aggregator │                        │
│                  └──────┬──────┘                        │
│                         │                               │
│        ┌────────────────┴────────────────┐             │
│        │                                  │             │
│  ┌─────▼──────┐              ┌───────────▼─────┐      │
│  │ Maintenance │              │  Cost Estimator │      │
│  │  Scheduler  │              │                 │      │
│  └─────┬───────┘              └───────────┬─────┘      │
│        │                                   │            │
│        └──────────┬────────────────────────┘            │
│                   │                                     │
│            ┌──────▼──────┐                             │
│            │ Conversational                            │
│            │  Response   │                             │
│            │  Generator  │                             │
│            └─────────────┘                             │
└─────────────────────────────────────────────────────────┘
         │
         │ Time-Series Database (InfluxDB/PostgreSQL)
         │  - 30-90 days historical data
         │  - SOH trends, error logs, temperature
         │  - Alarm history, cycle counts
         └──────────────────────────────────────────────────
```

---

## Phase 1: Battery Failure Risk Scoring (30 min)

### Step 1.1: Define Risk Factors

Battery failure risks come from multiple sources:

| Risk Factor | Weight | Threshold | Points |
|-------------|--------|-----------|--------|
| **SOH Degradation** | 40% | <70% SOH | 0-40 |
| **Cell Imbalance** | 25% | >0.10V spread | 0-25 |
| **Module Offline** | 20% | Any offline | 0-20 |
| **Thermal Stress** | 10% | Avg >40°C | 0-10 |
| **Cycle Count** | 5% | >4000 cycles | 0-5 |

**Total Score**: 0-100 (higher = more likely to fail)

### Step 1.2: Implement Battery Risk Calculator

<details>
<summary>Click to expand Python implementation (~250 lines)</summary>

```python
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class BatteryRiskScorer:
    """
    Calculate battery failure risk score (0-100)
    """

    def __init__(self, history_db):
        self.db = history_db

    def calculate_risk(self, site_id: str, current_metrics: Dict) -> Dict:
        """
        Calculate comprehensive battery risk score

        Returns:
            {
                'total_score': float (0-100),
                'risk_level': str ('LOW'|'MEDIUM'|'HIGH'|'CRITICAL'),
                'risk_factors': [...],
                'predicted_failure_date': datetime,
                'confidence': float (0-1)
            }
        """

        risk_factors = []

        # Factor 1: SOH Degradation (40 points max)
        soh = current_metrics.get('soh', 100)
        soh_points = self._score_soh(soh)
        if soh_points > 0:
            risk_factors.append({
                'factor': 'SOH Degradation',
                'points': soh_points,
                'severity': 'CRITICAL' if soh < 70 else 'HIGH' if soh < 80 else 'MEDIUM',
                'value': f"{soh}%",
                'explanation': f"Battery health at {soh}% (threshold: 70%)",
                'recommendation': "Plan replacement" if soh < 80 else "Monitor closely"
            })

        # Factor 2: Cell Imbalance (25 points max)
        cell_spread = current_metrics.get('cell_spread', 0)
        imbalance_points = self._score_cell_imbalance(cell_spread)
        if imbalance_points > 0:
            risk_factors.append({
                'factor': 'Cell Imbalance',
                'points': imbalance_points,
                'severity': 'HIGH' if cell_spread > 0.15 else 'MEDIUM',
                'value': f"{cell_spread:.3f}V spread",
                'explanation': f"Cell voltage spread {cell_spread}V (threshold: 0.10V)",
                'recommendation': "Inspect cells, check BMS balancing"
            })

        # Factor 3: Module Offline (20 points max)
        modules_offline = current_metrics.get('modules_offline', 0)
        module_points = self._score_modules(modules_offline)
        if module_points > 0:
            risk_factors.append({
                'factor': 'Module Offline',
                'points': module_points,
                'severity': 'CRITICAL',
                'value': f"{modules_offline} module(s)",
                'explanation': f"{modules_offline} battery modules not responding",
                'recommendation': "Inspect battery module connections immediately"
            })

        # Factor 4: Thermal Stress (10 points max)
        temp_history = self.db.get_temperature_history(site_id, days=7)
        thermal_points = self._score_thermal(temp_history)
        if thermal_points > 0:
            avg_temp = sum(temp_history) / len(temp_history) if temp_history else 0
            risk_factors.append({
                'factor': 'Thermal Stress',
                'points': thermal_points,
                'severity': 'MEDIUM',
                'value': f"{avg_temp:.1f}°C avg",
                'explanation': f"Battery running hot (avg {avg_temp}°C, optimal: 20-35°C)",
                'recommendation': "Improve cooling, reduce charge/discharge rate"
            })

        # Factor 5: Cycle Count (5 points max)
        cycles = current_metrics.get('cycles', 0)
        cycle_points = self._score_cycles(cycles)
        if cycle_points > 0:
            risk_factors.append({
                'factor': 'High Cycle Count',
                'points': cycle_points,
                'severity': 'LOW',
                'value': f"{cycles} cycles",
                'explanation': f"Battery at {cycles} cycles (design life: 6000)",
                'recommendation': "Normal aging, plan replacement within 12 months"
            })

        # Calculate total score
        total_score = sum(rf['points'] for rf in risk_factors)

        # Determine risk level
        risk_level = self._score_to_level(total_score)

        # Predict failure date
        prediction = self._predict_failure_date(
            site_id,
            total_score,
            risk_factors
        )

        return {
            'total_score': total_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'predicted_failure_date': prediction['date'],
            'confidence': prediction['confidence'],
            'months_until_failure': prediction['months']
        }

    def _score_soh(self, soh: float) -> float:
        """Score SOH (0-40 points)"""
        if soh >= 90:
            return 0
        elif soh >= 85:
            return 5
        elif soh >= 80:
            return 10
        elif soh >= 75:
            return 20
        elif soh >= 70:
            return 30
        else:
            return 40

    def _score_cell_imbalance(self, spread: float) -> float:
        """Score cell voltage spread (0-25 points)"""
        if spread < 0.05:
            return 0
        elif spread < 0.10:
            return 5
        elif spread < 0.15:
            return 15
        else:
            return 25

    def _score_modules(self, offline_count: int) -> float:
        """Score offline modules (0-20 points)"""
        return min(20, offline_count * 20)  # 20 points per offline module

    def _score_thermal(self, temp_history: List[float]) -> float:
        """Score thermal stress (0-10 points)"""
        if not temp_history:
            return 0

        avg_temp = sum(temp_history) / len(temp_history)

        if avg_temp < 35:
            return 0
        elif avg_temp < 40:
            return 2
        elif avg_temp < 45:
            return 5
        elif avg_temp < 50:
            return 7
        else:
            return 10

    def _score_cycles(self, cycles: int) -> float:
        """Score cycle count (0-5 points)"""
        if cycles < 3000:
            return 0
        elif cycles < 4000:
            return 1
        elif cycles < 5000:
            return 3
        else:
            return 5

    def _score_to_level(self, score: float) -> str:
        """Convert score to risk level"""
        if score >= 60:
            return "CRITICAL"
        elif score >= 40:
            return "HIGH"
        elif score >= 20:
            return "MEDIUM"
        else:
            return "LOW"

    def _predict_failure_date(
        self,
        site_id: str,
        risk_score: float,
        risk_factors: List[Dict]
    ) -> Dict:
        """
        Predict when failure will occur

        Uses risk score and degradation rate to estimate
        """

        # Get historical SOH data
        soh_history = self.db.get_soh_history(site_id, days=90)

        if len(soh_history) < 2:
            return {
                'date': None,
                'confidence': 0.0,
                'months': None
            }

        # Calculate degradation rate
        oldest = soh_history[0]
        newest = soh_history[-1]

        soh_delta = oldest['soh'] - newest['soh']
        days_elapsed = (newest['date'] - oldest['date']).days

        if days_elapsed == 0 or soh_delta <= 0:
            return {
                'date': None,
                'confidence': 0.0,
                'months': None
            }

        # Degradation rate per day
        rate_per_day = soh_delta / days_elapsed

        # Current SOH
        current_soh = newest['soh']

        # Days until 70% threshold (failure point)
        threshold = 70.0
        soh_remaining = current_soh - threshold
        days_until_failure = soh_remaining / rate_per_day if rate_per_day > 0 else float('inf')

        # Adjust by risk score (higher risk = sooner failure)
        risk_multiplier = 1.0 - (risk_score / 200.0)  # 0-100 score → 0.5-1.0 multiplier
        adjusted_days = days_until_failure * risk_multiplier

        # Convert to months
        months_until_failure = adjusted_days / 30.0

        # Calculate confidence based on data points
        confidence = min(1.0, len(soh_history) / 30.0)  # Full confidence at 30+ data points

        # Failure date
        failure_date = datetime.now() + timedelta(days=adjusted_days)

        return {
            'date': failure_date,
            'confidence': confidence,
            'months': months_until_failure
        }


# Example usage
scorer = BatteryRiskScorer(history_db)

current_metrics = {
    'soh': 82,
    'cell_spread': 0.12,
    'modules_offline': 0,
    'cycles': 3200,
    'temperature': 42
}

risk = scorer.calculate_risk("site_alpha", current_metrics)

print(f"Risk Score: {risk['total_score']}/100")
print(f"Risk Level: {risk['risk_level']}")
print(f"Predicted Failure: {risk['months_until_failure']:.1f} months")
```

</details>

### Step 1.3: Test Battery Risk Scoring

Test cases to validate implementation:

**Test 1: Healthy Battery**
```python
test_metrics = {
    'soh': 96,
    'cell_spread': 0.04,
    'modules_offline': 0,
    'cycles': 2000,
    'temperature': 28
}
# Expected: Risk score <10, Level: LOW
```

**Test 2: Warning Battery**
```python
test_metrics = {
    'soh': 82,
    'cell_spread': 0.12,
    'modules_offline': 0,
    'cycles': 3800,
    'temperature': 42
}
# Expected: Risk score 30-50, Level: MEDIUM-HIGH
```

**Test 3: Critical Battery**
```python
test_metrics = {
    'soh': 68,
    'cell_spread': 0.16,
    'modules_offline': 1,
    'cycles': 5200,
    'temperature': 47
}
# Expected: Risk score 70-90, Level: CRITICAL
```

---

## Phase 2: Inverter & Grid Risk Scoring (25 min)

### Step 2.1: Inverter Risk Factors

| Risk Factor | Weight | Threshold | Points |
|-------------|--------|-----------|--------|
| **Frequent Errors** | 35% | >5 errors/week | 0-35 |
| **Overheating** | 30% | >50°C avg | 0-30 |
| **Overload Events** | 20% | >3 overloads/week | 0-20 |
| **High Runtime** | 10% | >5 years | 0-10 |
| **Voltage Issues** | 5% | Frequent HV/LV | 0-5 |

### Step 2.2: Grid/Connectivity Risk Factors

| Risk Factor | Weight | Threshold | Points |
|-------------|--------|-----------|--------|
| **VRM Connection Failures** | 40% | >3 failures/week | 0-40 |
| **CAN Bus Errors** | 30% | >100 errors/day | 0-30 |
| **Grid Lost Events** | 20% | >2 events/week | 0-20 |
| **WiFi Signal Weak** | 10% | <40% strength | 0-10 |

Implementation follows same pattern as battery risk scorer (see full code in repository).

---

## Phase 3: Aggregate Risk & Conversational Output (40 min)

### Step 3.1: Generate Maintenance Report

Conversational output example:

```
🔧 Predictive Maintenance Report: Site Alpha

🟠 **Overall Risk: HIGH**
Risk Score: 52/100

**Component Health:**
  - Battery: HIGH (65/100)
    → Predicted replacement: 8 months
  - Inverter: MEDIUM (28/100)
  - Connectivity: LOW (12/100)

**Maintenance Schedule:**

🔴 **1. Replace battery pack**
   - Component: Battery
   - Urgency: Within 3-6 months
   - Reason: Risk score 65/100
   - Estimated Cost: $5,000
   - Key Issues:
     • SOH Degradation: 82%
     • Cell Imbalance: 0.120V spread

🟡 **2. Service/replace inverter**
   - Component: Inverter
   - Urgency: Within 1-2 months
   - Reason: Risk score 28/100
   - Estimated Cost: $500
   - Key Issues:
     • Frequent Errors: 8 errors/week

🟢 **3. Improve connectivity**
   - Component: Network/Connectivity
   - Urgency: Within 1 month
   - Reason: Communication issues affecting monitoring
   - Estimated Cost: $150
   - Key Issues:
     • Weak WiFi Signal: 45%

**Cost Estimate:**
  - Planned Maintenance: $5,650
  - **Total: $5,650**

💡 **Proactive Savings:**
By scheduling maintenance in advance, you avoid:
  - Emergency service premiums: $5,000-15,000
  - Expedited shipping: $500-2,000
  - Customer downtime losses: $1,000-10,000
```

---

## Testing Your Implementation

### Test Scenario 1: Low Risk Site

```python
test_metrics = {
    'soh': 96,
    'cell_spread': 0.03,
    'modules_offline': 0,
    'cycles': 1500,
    'temperature': 28,
    'inverter_temp': 42,
    'wifi_signal': 75
}
# Expected: Overall risk LOW, no urgent recommendations
```

### Test Scenario 2: High Risk Site

```python
test_metrics = {
    'soh': 78,
    'cell_spread': 0.14,
    'modules_offline': 0,
    'cycles': 4200,
    'temperature': 44,
    'inverter_temp': 52,
    'wifi_signal': 38
}
# Expected: Overall risk HIGH, battery + inverter recommendations
```

---

## Success Criteria

After completing this tutorial, you should be able to:

- ✅ Calculate risk scores for battery, inverter, and connectivity
- ✅ Predict failure dates with confidence levels
- ✅ Generate prioritized maintenance schedules
- ✅ Estimate maintenance costs (planned vs emergency)
- ✅ Communicate proactively with natural language reports
- ✅ Identify early warning signs 30-90 days before failure

---

## What's Next

### Expand Your Agent

1. **Add More Components**: Solar chargers, grid meters, temperature sensors
2. **ML Integration**: Train models on historical failure data
3. **Cost Optimization**: Find optimal maintenance timing (balance cost vs risk)
4. **Multi-Site Comparison**: Identify highest-risk sites across fleet

### Related Tutorials

- [Tutorial 02: Battery Health Agent](./02-battery-health-agent.md) - Battery-specific diagnostics
- [Tutorial 03: Fleet Dashboard Agent](./03-fleet-dashboard-agent.md) - Multi-site monitoring

### Related How-To Guides

- [Detect Battery Degradation](../how-to-guides/anomaly-detection/detect-battery-degradation.md) - Deep dive on battery analysis
- [Compare Site Performance](../how-to-guides/fleet-monitoring/compare-site-performance.md) - Identify problem sites
- [Proactive Alerts](../how-to-guides/conversational-patterns/proactive-alerts.md) - Agent-initiated communication

---

## Summary

You've built a predictive maintenance agent that:

1. **Scores failure risk** across battery, inverter, and connectivity (0-100 scale)
2. **Predicts failure dates** using trend analysis and historical data
3. **Generates maintenance schedules** prioritized by urgency and cost
4. **Estimates costs** including emergency premiums
5. **Communicates proactively** with natural language reports

**Business Impact**:
- Avoid $5k-15k emergency service premiums
- Schedule maintenance during customer off-hours
- Order parts in advance (no expedited shipping)
- Reduce downtime from days to hours
- Improve customer satisfaction through proactive communication

**Next Steps**: Deploy to production, monitor accuracy, refine risk thresholds based on real failures.

---

**Made in Ukraine 🇺🇦 with love by EnergyCitizen**
