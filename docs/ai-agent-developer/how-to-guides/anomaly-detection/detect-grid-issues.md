# Detect Grid Quality Issues

Guide for building AI agents that detect grid instability, voltage problems, and connection issues.

---

## User Story

**As an AI Developer**, I want my AI agent to detect grid quality issues (frequency deviation, voltage sag/surge, outages) so that I can alert users before equipment damage occurs.

---

## Business Value

| Benefit | Value |
|---------|-------|
| **Equipment Protection** | Prevent damage from voltage surges/sags ($5k-50k per inverter) |
| **Uptime** | Early warning of grid instability → prepare backup power |
| **Power Quality** | Identify utility issues → report to grid operator |
| **Compliance** | Detect grid code violations before utility disconnect |

---

## Conversational Flow Examples

### Scenario 1: Frequency Deviation Alert

**Agent** (proactive):
> "⚠️ Grid Frequency Alert - Site Beta
>
> Grid frequency is 50.8Hz (exceeds safe limit of 50.5Hz).
>
> **Status**: Inverter will disconnect in 60 seconds if frequency stays high (anti-islanding protection)
>
> **Likely Cause**: Grid operator issue or overproduction in area
>
> **Impact**: System will switch to battery backup if disconnect occurs
>
> **Action**: Monitor for disconnect. If grid drops, battery runtime ~4 hours at current load.
>
> Shall I notify utility of frequency issue?"

**User**:
> "Yes, and show me frequency trend"

**Agent**:
> "[Shows graph: Frequency spiked from 50.0Hz to 50.8Hz over 5 minutes, now stabilizing at 50.6Hz]
>
> Update: Frequency is decreasing. Now 50.6Hz (still high but improving).
> Grid operator appears to be correcting. Will continue monitoring.
>
> Utility notification email sent with frequency data."

---

### Scenario 2: Voltage Sag Detection

**User**:
> "Check grid quality across all sites"

**Agent**:
> "Grid quality summary across 12 sites:
>
> **EXCELLENT** (8 sites): Voltage 220-235V, Frequency 49.9-50.1Hz
>
> **GOOD** (3 sites): Minor variations within acceptable range
>
> **ISSUES** (1 site):
> 🔴 **Site Gamma**: Voltage sagging to 205V (below 207V minimum)
>    - Frequency: 50.0Hz (OK)
>    - Power factor: 0.85 (OK)
>    - **Risk**: Undervoltage can damage inverter, cause shutdowns
>    - **Likely Cause**: Utility supply issue or undersized service transformer
>    - **Action**: Contact utility immediately, log voltage data
>
> Shall I generate utility complaint report with voltage log?"

---

## Agent Capabilities Required

### 1. Grid Monitoring Metrics

**Primary Metrics**:

| Metric | DBus Path | Service | Normal Range | Critical |
|--------|-----------|---------|--------------|----------|
| **Frequency** | `/Ac/ActiveIn/L1/F` | vebus.ttyS4 | 49.8-50.2 Hz (50Hz grid) | <49.5 or >50.5 Hz |
| **Voltage L1** | `/Ac/ActiveIn/L1/V` | vebus.ttyS4 | 220-240V | <207 or >253V |
| **Voltage L2** | `/Ac/ActiveIn/L2/V` | vebus.ttyS4 | 220-240V | <207 or >253V |
| **Voltage L3** | `/Ac/ActiveIn/L3/V` | vebus.ttyS4 | 220-240V | <207 or >253V |
| **Grid Power** | `/Ac/Grid/L1/Power` | system | N/A | Sudden drops |
| **Grid Lost** | `/Alarms/GridLost` | vebus.ttyS4 | False | True = outage |

**3-Phase Balance**:
```python
# Calculate voltage imbalance percentage
voltages = [l1_voltage, l2_voltage, l3_voltage]
avg_voltage = sum(voltages) / 3
max_deviation = max(abs(v - avg_voltage) for v in voltages)
imbalance_pct = (max_deviation / avg_voltage) * 100

# Threshold: >2% imbalance = investigate
```

---

### 2. Grid Quality Thresholds

#### Frequency (50Hz Grid)

| Frequency | Status | Action | Trip Time |
|-----------|--------|--------|-----------|
| **49.5-50.5 Hz** | Normal | None | - |
| **49.2-49.5 Hz** | Warning Low | Monitor | May trip in 5-60s |
| **50.5-50.8 Hz** | Warning High | Monitor | May trip in 5-60s |
| **<49.2 Hz** | Critical Low | Disconnect | <0.2s |
| **>50.8 Hz** | Critical High | Disconnect | <0.2s |

**60Hz Grid**: Add 10Hz to all values (59.5-60.5Hz normal)

#### Voltage (230V Nominal)

| Voltage | Status | Action | Risk |
|---------|--------|--------|------|
| **220-240V** | Normal | None | - |
| **207-220V** | Low Warning | Monitor | Inverter may derate |
| **240-253V** | High Warning | Monitor | Component stress |
| **<207V** | Critical Low | May disconnect | Equipment damage |
| **>253V** | Critical High | May disconnect | Equipment damage |

**3-Phase Imbalance**:
- <2%: Normal
- 2-5%: Monitor
- >5%: Investigate (utility or wiring issue)

---

### 3. Anomaly Detection Patterns

**Pattern 1: Gradual Voltage Drift**
```
IF voltage has been decreasing 1V/hour for 3+ hours:
    likely_cause = "Transformer overload or failing"
    urgency = "HIGH"
    action = "Contact utility with voltage log"
```

**Pattern 2: Rapid Frequency Change**
```
IF frequency changes >0.3Hz in <1 minute:
    likely_cause = "Grid instability or large load switching"
    urgency = "MEDIUM"
    action = "Monitor for inverter disconnect"
```

**Pattern 3: Intermittent Outages**
```
IF grid_lost_alarm toggles >3 times in 1 hour:
    likely_cause = "Loose connection or failing utility equipment"
    urgency = "HIGH"
    action = "Inspect AC input connections, contact utility"
```

**Pattern 4: Voltage Sag Under Load**
```
IF voltage drops >10V when inverter starts charging:
    likely_cause = "Undersized service wire or breaker"
    urgency = "MEDIUM"
    action = "Check wire gauge, upgrade if needed"
```

---

### 4. Root Cause Analysis

**Grid Frequency Issues**:

| Symptom | Cause | Resolution |
|---------|-------|------------|
| Frequency >50.5Hz | Grid overproduction, wrong grid code | Check grid code setting, contact utility |
| Frequency <49.5Hz | Grid underproduction, heavy load | Monitor for outage, utility issue |
| Rapid fluctuation (±0.5Hz) | Grid instability | May need to disconnect, utility emergency |
| Constant 50.2-50.4Hz | Micro-grid or weak grid | Normal for some locations |

**Grid Voltage Issues**:

| Symptom | Cause | Resolution |
|---------|-------|------------|
| Voltage <220V constant | Undersized transformer, long wire run | Utility upgrade needed |
| Voltage sag under load | Wire too small, breaker too small | Upgrade AC input wiring |
| Voltage >240V constant | Utility overvoltage | Contact utility, may damage equipment |
| Single phase low (3-phase) | Phase loss, imbalance | Check utility connection, wiring |

---

## API Implementation

<details>
<summary>Click to expand Python implementation</summary>

```python
import requests
from datetime import datetime, timedelta
from typing import Dict, List

class GridQualityMonitor:
    """AI agent capability for grid quality monitoring"""

    def __init__(self, api_base_url: str):
        self.api_base = api_base_url
        self.vebus_service = "com.victronenergy.vebus.ttyS4"
        self.system_service = "com.victronenergy.system"

    def get_grid_metrics(self, site_ip: str) -> Dict:
        """Collect current grid quality metrics"""
        base_url = f"http://{site_ip}:8088"

        metrics = {}
        paths = {
            # Frequency
            'frequency_l1': (self.vebus_service, '/Ac/ActiveIn/L1/F'),

            # Voltages
            'voltage_l1': (self.vebus_service, '/Ac/ActiveIn/L1/V'),
            'voltage_l2': (self.vebus_service, '/Ac/ActiveIn/L2/V'),
            'voltage_l3': (self.vebus_service, '/Ac/ActiveIn/L3/V'),

            # Power
            'grid_power_l1': (self.system_service, '/Ac/Grid/L1/Power'),
            'grid_power_l2': (self.system_service, '/Ac/Grid/L2/Power'),
            'grid_power_l3': (self.system_service, '/Ac/Grid/L3/Power'),

            # Alarms
            'grid_lost': (self.vebus_service, '/Alarms/GridLost'),
        }

        for key, (service, path) in paths.items():
            try:
                response = requests.get(
                    f"{base_url}/value",
                    params={'service': service, 'path': path},
                    timeout=2
                )
                if response.json().get('success'):
                    value = response.json()['value']
                    # Handle empty values for unused phases
                    metrics[key] = value if value != [] else None
            except:
                metrics[key] = None

        # Calculate 3-phase imbalance if applicable
        voltages = [v for v in [metrics.get('voltage_l1'),
                                 metrics.get('voltage_l2'),
                                 metrics.get('voltage_l3')] if v]

        if len(voltages) >= 2:
            avg_v = sum(voltages) / len(voltages)
            max_dev = max(abs(v - avg_v) for v in voltages)
            metrics['voltage_imbalance_pct'] = (max_dev / avg_v) * 100
        else:
            metrics['voltage_imbalance_pct'] = 0

        return metrics

    def analyze_frequency(self, frequency: float, nominal: float = 50.0) -> Dict:
        """Analyze grid frequency"""

        deviation = abs(frequency - nominal)

        if deviation < 0.2:
            status = "EXCELLENT"
            severity = "none"
            action = "None needed"
        elif deviation < 0.5:
            status = "GOOD"
            severity = "low"
            action = "Monitor"
        elif deviation < 1.0:
            status = "WARNING"
            severity = "medium"
            action = "Inverter may disconnect soon - prepare for battery mode"
        else:
            status = "CRITICAL"
            severity = "high"
            action = "Inverter will disconnect - grid emergency"

        return {
            'frequency': frequency,
            'deviation': deviation,
            'status': status,
            'severity': severity,
            'action': action
        }

    def analyze_voltage(self, voltage: float, nominal: float = 230.0) -> Dict:
        """Analyze grid voltage"""

        if voltage < 207:
            status = "CRITICAL LOW"
            severity = "high"
            risk = "Equipment damage, inverter shutdown"
            action = "Contact utility immediately"
        elif voltage < 220:
            status = "LOW"
            severity = "medium"
            risk = "Inverter may derate power"
            action = "Monitor, contact utility if persists"
        elif voltage <= 240:
            status = "NORMAL"
            severity = "none"
            risk = "None"
            action = "None needed"
        elif voltage <= 253:
            status = "HIGH"
            severity = "medium"
            risk = "Component stress, accelerated aging"
            action = "Monitor, contact utility if persists"
        else:
            status = "CRITICAL HIGH"
            severity = "high"
            risk = "Equipment damage risk"
            action = "Contact utility immediately"

        deviation = voltage - nominal

        return {
            'voltage': voltage,
            'deviation': deviation,
            'status': status,
            'severity': severity,
            'risk': risk,
            'action': action
        }

    def generate_grid_quality_report(self, site_name: str, metrics: Dict) -> str:
        """Generate natural language grid quality summary"""

        frequency = metrics.get('frequency_l1')
        freq_analysis = self.analyze_frequency(frequency) if frequency else None

        voltage_l1 = metrics.get('voltage_l1')
        v1_analysis = self.analyze_voltage(voltage_l1) if voltage_l1 else None

        grid_lost = metrics.get('grid_lost', False)

        # Overall status
        issues = []

        if grid_lost:
            return f"🔴 **{site_name}**: GRID OUTAGE\n" \
                   f"   - Grid connection lost\n" \
                   f"   - System running on battery backup\n" \
                   f"   - Estimated runtime: [calculate from SOC]\n" \
                   f"   - Action: Check with utility, monitor battery level"

        if freq_analysis and freq_analysis['severity'] in ['medium', 'high']:
            issues.append(f"Frequency {frequency:.2f}Hz ({freq_analysis['status']})")

        if v1_analysis and v1_analysis['severity'] in ['medium', 'high']:
            issues.append(f"Voltage {voltage_l1:.0f}V ({v1_analysis['status']})")

        imbalance = metrics.get('voltage_imbalance_pct', 0)
        if imbalance > 5:
            issues.append(f"3-phase imbalance {imbalance:.1f}%")

        if not issues:
            return f"✅ **{site_name}**: Grid quality EXCELLENT\n" \
                   f"   - Frequency: {frequency:.2f}Hz (stable)\n" \
                   f"   - Voltage: {voltage_l1:.0f}V (normal)\n" \
                   f"   - No issues detected"

        # Has issues
        issue_list = '\n   - '.join(issues)
        actions = []

        if freq_analysis and freq_analysis['severity'] == 'high':
            actions.append(freq_analysis['action'])
        if v1_analysis and v1_analysis['severity'] == 'high':
            actions.append(v1_analysis['action'])

        action_text = '\n   - '.join(actions) if actions else "Monitor situation"

        return f"⚠️ **{site_name}**: Grid quality ISSUES\n" \
               f"   - {issue_list}\n" \
               f"   \n" \
               f"   **Action Required**:\n" \
               f"   - {action_text}"
```

</details>

---

## Detection Thresholds

### Frequency Limits (50Hz Grid)

| Deviation from 50Hz | Status | Inverter Response | Time to Trip |
|---------------------|--------|-------------------|--------------|
| **±0.0-0.2 Hz** | Excellent | Normal operation | - |
| **±0.2-0.5 Hz** | Good | Normal operation | - |
| **±0.5-1.0 Hz** | Warning | Prepare to disconnect | 5-60 seconds |
| **±1.0-2.0 Hz** | Critical | Will disconnect | 0.2-5 seconds |
| **>±2.0 Hz** | Emergency | Instant disconnect | <0.2 seconds |

**Note**: Exact trip times depend on grid code setting (e.g., Code 16 for Europe).

### Voltage Limits (230V Nominal)

| Voltage | Status | Risk Level | Action |
|---------|--------|------------|--------|
| **253V+** | Critical High | Equipment damage | Contact utility NOW |
| **240-253V** | High | Accelerated aging | Monitor, log data |
| **220-240V** | Normal | None | - |
| **207-220V** | Low | Inverter derating | Monitor, log data |
| **<207V** | Critical Low | Shutdown risk | Contact utility NOW |

### Power Quality

**Voltage Imbalance** (3-phase):
- <2%: Normal
- 2-5%: Monitor (utility or installation issue)
- >5%: Critical (contact utility, check wiring)

**Power Factor**:
- 0.95-1.0: Excellent
- 0.85-0.95: Good
- <0.85: Poor (utility may charge penalties)

---

## Conversational Patterns

### Pattern 1: Grid Status Query

**User**: "Is the grid stable?"

**Agent**:
```
"Grid quality at Site 5: EXCELLENT ✅

Frequency: 50.02Hz (±0.02Hz deviation, very stable)
Voltage: 228V L1, 229V L2, 227V L3
Imbalance: 0.4% (excellent balance)
Power Factor: 0.98

All parameters within optimal range. No issues detected."
```

### Pattern 2: Voltage Sag Alert

**Agent** (proactive):
```
"🟡 Grid voltage dropped to 212V at Site 3 (below normal 220V minimum).

This started 15 minutes ago when your EV charger kicked on.

Likely Cause: Service wire too small for combined load (house + EV + solar export)

Impact: Inverter may limit charging power to protect from undervoltage

Short-term: EV charging will be slower
Long-term: Consider service upgrade (wire gauge or breaker)

Shall I create a quote request for electrician?"
```

### Pattern 3: Frequency Instability

**User**: "Why did the system disconnect from grid?"

**Agent**:
```
"System disconnected at 14:32 due to high grid frequency (50.9Hz).

Timeline:
- 14:30: Frequency 50.0Hz (normal)
- 14:31: Frequency rose to 50.6Hz (high)
- 14:32: Frequency hit 50.9Hz → Inverter disconnected (anti-islanding protection)
- 14:35: Frequency stabilized at 50.1Hz
- 14:36: System reconnected automatically

Likely Cause: Grid operator issue or large generator in area switched off suddenly

Impact: 4-minute grid outage, battery discharged 2% (minimal)

Action: None needed - system handled correctly. This is rare, report to utility if recurring."
```

---

## Related Documentation

**How-To Guides**:
- [Detect Battery Degradation](./detect-battery-degradation.md) - Battery health monitoring
- [Detect Cell Imbalance](./detect-cell-imbalance.md) - Cell voltage issues

**Installer Guides**:
- [Grid Frequency Issues](../../../installer/how-to-guides/troubleshooting/grid-frequency-issues.md) - Troubleshooting

**Concepts**:
- [Grid Quality Metrics](../../concepts/grid-quality-metrics.md) - Understanding frequency/voltage
- [ESS Grid Support](../../concepts/ess-optimization-strategies.md) - Grid stabilization

**Reference**:
- [Grid Thresholds](../../reference/thresholds/grid-thresholds.md) - All threshold values
- [Critical Paths](../../reference/api/critical-paths.md) - Grid monitoring paths

---

**Made in Ukraine 🇺🇦 with love by EnergyCitizen**
