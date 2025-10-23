# Critical Monitoring Paths

Quick reference for the most important DBus paths for AI agent monitoring.

**Source**: Extracted from QUICK_REFERENCE_DIAGNOSTIC_PATHS.json
**Systems**: Tested on Cerbo GX v3.70~33

---

## Battery Monitoring (Priority 1)

### State of Charge (SOC)

**Path**: `/Dc/Battery/Soc`
**Service**: `com.victronenergy.system`
**Type**: float
**Unit**: %
**Poll Interval**: 10 seconds

**Thresholds**:
- Critical: <10%
- Warning: <20%
- Normal: 20-100%

**User Story**: "Alert me when battery drops below 20%"

**Conversational Query**:
```
User: "What's the battery level?"
Agent: "Battery is at 73%, discharging at 15A. About 4 hours remaining at current load."
```

---

### State of Health (SOH)

**Path**: `/Soh`
**Service**: `com.victronenergy.battery.socketcan_can0`
**Type**: float
**Unit**: %
**Poll Interval**: 3600 seconds (1 hour)

**Thresholds**:
- Critical: <70% (replace immediately)
- Warning: <85% (plan replacement)
- Good: 85-95%
- Excellent: >95%

**User Story**: "Detect battery degradation early"

**Conversational Query**:
```
User: "How healthy is the battery?"
Agent: "Battery SOH is 82% (Warning). It's lost 6% in the last month—faster than normal.
        I predict it'll reach the 70% replacement threshold in about 8 months."
```

---

### Battery Voltage

**Path**: `/Dc/Battery/Voltage`
**Service**: `com.victronenergy.system`
**Type**: float
**Unit**: V
**Poll Interval**: 10 seconds

**Safe Range** (48V system):
- Minimum: 45V
- Maximum: 58V
- Nominal: 48-52V

**User Story**: "Monitor voltage stability"

---

### Battery Current

**Path**: `/Dc/Battery/Current`
**Service**: `com.victronenergy.system`
**Type**: float
**Unit**: A
**Poll Interval**: 10 seconds

**Note**:
- Negative = Discharging
- Positive = Charging

**User Story**: "Track charge/discharge rate"

**Conversational Query**:
```
User: "Is the battery charging?"
Agent: "Yes, charging at 28A (1,470W). Currently in Bulk mode, will switch to Absorption at 52V."
```

---

### Battery Power

**Path**: `/Dc/Battery/Power`
**Service**: `com.victronenergy.system`
**Type**: float
**Unit**: W
**Poll Interval**: 10 seconds

**Note**:
- Negative = Discharging (battery → loads)
- Positive = Charging (grid/solar → battery)

---

## Grid Monitoring (Priority 2)

### Grid Power

**Path**: `/Ac/Grid/L1/Power`
**Service**: `com.victronenergy.system`
**Type**: int
**Unit**: W
**Poll Interval**: 10 seconds

**User Story**: "Monitor grid import/export"

**Conversational Query**:
```
User: "Am I exporting to grid?"
Agent: "Yes, exporting 450W to the grid. Solar is producing 2.1kW,
        battery is full (100%), so excess is being fed back."
```

---

### Grid Frequency

**Path**: `/Ac/ActiveIn/L1/F`
**Service**: `com.victronenergy.vebus.ttyS4`
**Type**: float
**Unit**: Hz
**Poll Interval**: 10 seconds

**Thresholds** (50Hz grid):
- Critical Low: <49.5Hz
- Critical High: >50.5Hz
- Normal: 49.8-50.2Hz

**User Story**: "Detect grid stability issues"

---

### Grid Voltage

**Path**: `/Ac/ActiveIn/L1/V`
**Service**: `com.victronenergy.vebus.ttyS4`
**Type**: float
**Unit**: V
**Poll Interval**: 10 seconds

**Thresholds** (230V grid):
- Critical Low: <207V
- Critical High: >253V
- Warning Low: <220V
- Warning High: >240V
- Normal: 220-240V

---

## Critical Alarms (Priority 3)

### Grid Lost

**Path**: `/Alarms/GridLost`
**Service**: `com.victronenergy.vebus.ttyS4`
**Type**: bool
**Poll Interval**: 5 seconds

**Critical**: Yes - System running on battery

**Conversational Alert**:
```
Agent: "⚠️ ALERT: Grid connection lost at Site 5. System switched to battery backup.
        Estimated runtime: 6 hours at current load (530W)."
```

---

### BMS Connection Lost

**Path**: `/Alarms/BmsConnectionLost`
**Service**: `com.victronenergy.vebus.ttyS4`
**Type**: bool
**Poll Interval**: 5 seconds

**Critical**: Yes - Battery monitor offline

**Conversational Alert**:
```
Agent: "⚠️ CRITICAL: Battery monitor offline at Site 3. Cannot read SOC/voltage safely.
        System may shut down to protect battery. Check CAN-bus connection immediately."
```

---

### High DC Voltage

**Path**: `/Alarms/HighDcVoltage`
**Service**: `com.victronenergy.vebus.ttyS4`
**Type**: int
**Poll Interval**: 5 seconds

**Values**:
- 0: OK
- 1: Warning
- 2: Alarm

**User Story**: "Detect overvoltage conditions"

---

## Inverter Monitoring (Priority 4)

### Inverter Mode

**Path**: `/Mode`
**Service**: `com.victronenergy.vebus.ttyS4`
**Type**: int
**Poll Interval**: 30 seconds

**Values**:
- 1: Charger Only
- 2: Inverter Only
- 3: On (Charger + Inverter)
- 4: Off

**User Story**: "Check if inverter is enabled"

---

### Inverter State

**Path**: `/State`
**Service**: `com.victronenergy.vebus.ttyS4`
**Type**: int
**Poll Interval**: 30 seconds

**Values**:
- 0: Off
- 1: Low Power Mode
- 2: Fault
- 3: Bulk Charging
- 4: Absorption Charging
- 5: Float Charging
- 9: Inverting

**User Story**: "Monitor charge cycle progress"

**Conversational Query**:
```
User: "What's the inverter doing?"
Agent: "Inverter is in Absorption mode (State 4), charging battery at 12A.
        Will switch to Float in about 30 minutes when voltage stabilizes at 52V."
```

---

## Solar Production (Priority 5)

### Solar Power

**Path**: `/Yield/Power`
**Service**: `com.victronenergy.solarcharger.*`
**Type**: int
**Unit**: W
**Poll Interval**: 30 seconds

**User Story**: "Monitor solar production"

**Multi-MPPT**: Query each solarcharger service and sum for total

---

### Daily Solar Yield

**Path**: `/History/Daily/0/Yield`
**Service**: `com.victronenergy.solarcharger.*`
**Type**: float
**Unit**: kWh
**Poll Interval**: 300 seconds (5 min)

**User Story**: "Track daily solar production"

**Conversational Query**:
```
User: "How much solar today?"
Agent: "Today's solar production: 18.4 kWh across 4 MPPT trackers.
        That's 92% of yesterday (19.8 kWh). Slightly cloudy."
```

---

## ESS Control (Priority 6)

### ESS SOC Limit

**Path**: `/Settings/CGwacs/BatteryLife/SocLimit`
**Service**: `com.victronenergy.settings`
**Type**: float
**Unit**: %
**Poll Interval**: 300 seconds

**Range**: 10-100%

**User Story**: "Check ESS battery protection settings"

---

### Grid Setpoint

**Path**: `/Settings/CGwacs/AcPowerSetPoint`
**Service**: `com.victronenergy.settings`
**Type**: float
**Unit**: W
**Poll Interval**: 60 seconds

**User Story**: "Monitor ESS grid feed-in target"

**Conversational Query**:
```
User: "What's the grid setpoint?"
Agent: "Grid setpoint is 0W (zero feed-in mode). System is keeping grid power near zero
        by adjusting battery charge/discharge. Currently at -15W (slight export)."
```

---

## Polling Strategy

### High-Priority (5-10 seconds)
- Battery SOC, Voltage, Current, Power
- Grid Power, Voltage, Frequency
- Critical Alarms

### Medium-Priority (30-60 seconds)
- Inverter Mode, State
- Solar Power
- Grid Setpoint

### Low-Priority (5-60 minutes)
- Battery SOH (hourly)
- Daily Yield (5 min)
- Settings (on change only)
- Firmware Version (daily)

## Batch Query Optimization

Instead of individual requests, query parent path:

```python
# Inefficient: 4 requests
soc = get_value("/Dc/Battery/Soc")
voltage = get_value("/Dc/Battery/Voltage")
current = get_value("/Dc/Battery/Current")
power = get_value("/Dc/Battery/Power")

# Efficient: 1 request
battery = get_value("/Dc/Battery")  # Returns all sub-paths
# Extract: battery['Soc'], battery['Voltage'], etc.
```

---

## Related Documentation

**How-To Guides**:
- [Detect Battery Degradation](../../how-to-guides/anomaly-detection/detect-battery-degradation.md)
- [Detect Grid Issues](../../how-to-guides/anomaly-detection/detect-grid-issues.md)
- [Natural Language Queries](../../how-to-guides/conversational-patterns/natural-language-queries.md)

**Concepts**:
- [Why Monitor Batteries](../../concepts/why-monitor-batteries.md)
- [Grid Quality Metrics](../../concepts/grid-quality-metrics.md)

**Reference**:
- [All Thresholds](../thresholds/battery-thresholds.md)
- [Complete API](../../../shared/api-specification/http-api-reference.md)

**Original Data**: [QUICK_REFERENCE_DIAGNOSTIC_PATHS.json](../../../../QUICK_REFERENCE_DIAGNOSTIC_PATHS.json)

---

**Made in Ukraine 🇺🇦 with love by EnergyCitizen**
