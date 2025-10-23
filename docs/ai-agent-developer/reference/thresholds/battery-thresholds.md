# Battery Thresholds Reference

Consolidated reference of all battery health thresholds for AI agent decision-making.

---

## State of Health (SOH)

| Range | Status | Action | Urgency |
|-------|--------|--------|---------|
| **95-100%** | Excellent | Monitor quarterly | None |
| **90-95%** | Good | Monitor monthly | None |
| **85-90%** | Fair | Monitor weekly, plan replacement in 12-24 months | Low |
| **70-85%** | Warning | Monitor daily, plan replacement in 3-12 months | Medium |
| **<70%** | Critical | Replace within 1 month | High |

**API Path**: `/Soh` (battery service)

---

## State of Charge (SOC)

| Range | Status | Typical Use | Notes |
|-------|--------|-------------|-------|
| **90-100%** | Full | After charging | Avoid storage at 100% |
| **60-90%** | Normal | Daily operation | Optimal range |
| **30-60%** | Moderate | Acceptable | Monitor if trending down |
| **10-30%** | Low | Charge soon | Avoid deep discharge |
| **<10%** | Critical | Charge immediately | Risk of cell damage |

**API Path**: `/Soc` (battery service)

---

## Cell Voltage Spread

| Spread (V) | Spread (%) | Status | Action |
|------------|------------|--------|--------|
| **<0.05** | <1.5% | Balanced | No action |
| **0.05-0.10** | 1.5-3.0% | Minor Imbalance | Enable balancing, monitor weekly |
| **0.10-0.15** | 3.0-4.5% | Warning | Check BMS, inspect cells, monitor daily |
| **>0.15** | >4.5% | Critical | Reduce discharge, inspect urgently, plan replacement |

**API Paths**:
- `/System/MaxCellVoltage` (battery service)
- `/System/MinCellVoltage` (battery service)

**Calculation**: `spread = max_cell_voltage - min_cell_voltage`

---

## Cell Voltage Ranges (LiFePO4)

| Voltage | Status | Notes |
|---------|--------|-------|
| **<3.00V** | Critical Low | Stop discharge immediately, risk of damage |
| **3.00-3.20V** | Low | Weak cell, discharge cautiously |
| **3.20-3.25V** | Normal Low | Healthy low end |
| **3.25-3.35V** | Normal | Optimal operating range |
| **3.35-3.40V** | High | Near full charge |
| **3.40-3.45V** | Very High | At full charge, balancing occurs |
| **>3.45V** | Critical High | Overvoltage, stop charging |

---

## Pack Voltage (48V System)

| Voltage | Status | SOC Estimate | Notes |
|---------|--------|--------------|-------|
| **<45V** | Critical Low | <10% | Stop discharge |
| **45-48V** | Low | 10-40% | Charge soon |
| **48-51V** | Normal | 40-80% | Optimal range |
| **51-53V** | High | 80-95% | Near full |
| **53-54V** | Charging | 95-100% | Absorption/float |
| **>54V** | Too High | - | Check charger settings |

**API Path**: `/Dc/0/Voltage` (battery service)

---

## Temperature

| Temperature (°C) | Status | Aging Rate | Action |
|------------------|--------|------------|--------|
| **<0°C** | Too Cold | 0.5× | Reduce charge rate, wait to warm |
| **0-15°C** | Cold | 0.7× | Reduced charge acceptance |
| **15-25°C** | Optimal | 1× | No action |
| **25-35°C** | Warm | 1.5× | Monitor, acceptable |
| **35-40°C** | Hot | 2× | Check cooling |
| **40-50°C** | Very Hot | 2.5× | Reduce charge rate, improve cooling |
| **>50°C** | Critical | 4× | Alert immediately, may block charging |

**API Path**: `/Dc/0/Temperature` (battery service)

**Aging Rate**: For every 10°C above 25°C, aging rate approximately doubles

---

## Current (C-Rate)

| C-Rate | Current (174Ah) | Status | Lifespan Impact |
|--------|-----------------|--------|-----------------|
| **<0.2C** | <35A | Very Low | Optimal (+20%) |
| **0.2-0.5C** | 35-87A | Normal | Baseline (100%) |
| **0.5-1.0C** | 87-174A | High | Reduced (-20%) |
| **1.0-2.0C** | 174-348A | Very High | Significantly reduced (-50%) |
| **>2.0C** | >348A | Critical | Risk of damage |

**API Path**: `/Dc/0/Current` (battery service)

**Calculation**: `c_rate = abs(current) / capacity_ah`

---

## Degradation Rate

| Rate (%/month) | Status | Expected Lifespan | Action |
|----------------|--------|-------------------|--------|
| **<0.2** | Normal | 10+ years | Monitor quarterly |
| **0.2-0.5** | Elevated | 7-10 years | Monitor monthly |
| **0.5-1.0** | Concerning | 4-7 years | Investigate cause, monitor weekly |
| **>1.0** | Critical | <4 years | Immediate intervention |

**Calculation**: `rate = (soh_old - soh_new) / months_elapsed`

---

## Charge Cycles

| Cycles | Typical Age | Status | Action |
|--------|-------------|--------|--------|
| **0-1000** | <2 years | New | No action |
| **1000-3000** | 2-5 years | Healthy | Monitor SOH |
| **3000-5000** | 5-8 years | Aging | Plan replacement in 2-3 years |
| **5000-6000** | 8-10 years | End of Life | Plan replacement in 6-12 months |
| **>6000** | >10 years | Beyond Design Life | Replace soon |

**API Path**: `/History/ChargeCycles` (battery service)

**Note**: LiFePO4 typically rated for 6,000 cycles to 80% capacity

---

## Module Status

| Metric | Threshold | Status | Action |
|--------|-----------|--------|--------|
| Modules Online | = Total | OK | No action |
| Modules Online | < Total | Problem | Check CAN connections |
| Modules Blocking Charge | > 0 | Warning | Check module health |
| Modules Blocking Discharge | > 0 | Warning | Check module health |
| Modules Offline | > 0 | Critical | Inspect failed module |

**API Paths**:
- `/System/NrOfModulesOnline` (battery service)
- `/System/NrOfModulesOffline` (battery service)
- `/System/NrOfModulesBlockingCharge` (battery service)
- `/System/NrOfModulesBlockingDischarge` (battery service)

---

## Decision Tree for Battery Health

```
START
  |
  v
Is SOH < 70%?
  |
  +-- YES --> Critical: Replace immediately
  |
  +-- NO --> Is SOH < 85%?
      |
      +-- YES --> Warning: Plan replacement in 3-12 months
      |           Check degradation rate:
      |           - >1%/month: Accelerated, investigate
      |           - 0.5-1%/month: Elevated, monitor weekly
      |           - <0.5%/month: Normal, monitor monthly
      |
      +-- NO --> Is cell spread > 0.10V?
          |
          +-- YES --> Warning: Cell imbalance
          |           - Enable BMS balancing
          |           - Monitor weekly
          |           - If >0.15V: Urgent inspection
          |
          +-- NO --> Is temperature > 40°C?
              |
              +-- YES --> Warning: Overheating
              |           - Check cooling
              |           - Reduce charge rate
              |
              +-- NO --> Healthy
                          - Monitor quarterly
                          - No action needed
```

---

## Agent Implementation Example

```python
def assess_battery_health(metrics):
    """Comprehensive battery health assessment"""

    soh = metrics.get('soh', 100)
    cell_spread = metrics.get('cell_spread', 0)
    temp = metrics.get('temperature', 25)
    degradation_rate = metrics.get('degradation_rate', 0)

    alerts = []

    # SOH check
    if soh < 70:
        alerts.append({
            'level': 'critical',
            'message': f'SOH {soh:.0f}% - Replace immediately',
            'action': 'Schedule replacement this week'
        })
    elif soh < 85:
        alerts.append({
            'level': 'warning',
            'message': f'SOH {soh:.0f}% - Plan replacement',
            'action': f'Budget for replacement in 3-12 months'
        })

    # Cell spread check
    if cell_spread > 0.15:
        alerts.append({
            'level': 'critical',
            'message': f'Cell spread {cell_spread:.3f}V - Severe imbalance',
            'action': 'Inspect cells immediately, plan module replacement'
        })
    elif cell_spread > 0.10:
        alerts.append({
            'level': 'warning',
            'message': f'Cell spread {cell_spread:.3f}V - Imbalance developing',
            'action': 'Enable BMS balancing, monitor weekly'
        })

    # Temperature check
    if temp > 50:
        alerts.append({
            'level': 'critical',
            'message': f'Temperature {temp:.0f}°C - Too hot',
            'action': 'Check cooling immediately, may block charging'
        })
    elif temp > 40:
        alerts.append({
            'level': 'warning',
            'message': f'Temperature {temp:.0f}°C - Hot',
            'action': 'Improve cooling, reduce charge rate'
        })

    # Degradation rate check
    if degradation_rate > 1.0:
        alerts.append({
            'level': 'warning',
            'message': f'Degradation {degradation_rate:.1f}%/month - Accelerated',
            'action': 'Investigate cause (temperature, cycling, etc.)'
        })

    return {
        'overall_status': 'critical' if any(a['level'] == 'critical' for a in alerts) else 'warning' if alerts else 'healthy',
        'alerts': alerts
    }
```

---

## Related Documentation

**How-To Guides**:
- [Detect Battery Degradation](../../how-to-guides/anomaly-detection/detect-battery-degradation.md)
- [Detect Cell Imbalance](../../how-to-guides/anomaly-detection/detect-cell-imbalance.md)

**Concepts**:
- [Battery Degradation Patterns](../../concepts/battery-degradation-patterns.md)
- [Why Monitor Batteries](../../concepts/why-monitor-batteries.md)

---

**Made in Ukraine 🇺🇦 with love by EnergyCitizen**
