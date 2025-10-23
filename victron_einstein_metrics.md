# Victron Einstein System - Critical Metrics & Monitoring Reference

## Device Identification & NAD Addressing

### VE.Can Devices (socketcan:can0)

#### Grid & Load Metering
| Device | NAD | Instance | Service | Serial | Key Metric |
|--------|-----|----------|---------|--------|-----------|
| VM-3P75CT Grid Meter | 64 | 0 | grid | 0449643 | -33.92W total power |
| Carlo Gavazzi Load Meter | - | 41 | acload | BX18600620015 | 747.2W L3 consumption |

#### Inverter/Chargers (Multi Units)
| Device | NAD | Instance | Service | Serial | Key Metric |
|--------|-----|----------|---------|--------|-----------|
| MultiRS1 (Primary) | 67 | 1 | multi | 0488085 | -46W output (supplying) |
| MultiRS2 (Secondary) | 66 | 2 | multi | 0382989 | +413W output (demanding) |
| MultiRS PV | 68 | 0 | pvinverter | 0487020 | -2.0W AC output |

#### Solar Chargers
| Device | NAD | Instance | Service | Serial | Key Metric |
|--------|-----|----------|---------|--------|-----------|
| MPPT RS 450/200 | 65 | 5 | solarcharger | 0431531 | 0.0W (offline) |
| MPPT VE.Can 150/70 | 36 | 7 | solarcharger | 0283819 | 0.0W (night) |

#### Battery Management
| Device | NAD | Instance | Service | Serial | Key Metric |
|--------|-----|----------|---------|--------|-----------|
| Lynx Smart BMS 500 | 41 | 6 | battery | 0317637 | 66.39% SOC, -698W |

---

## Critical Real-Time Monitoring Parameters

### Battery Voltage & Current (PRIMARY)
```
Path: /value?service=com.victronenergy.battery.socketcan_can0_vi6_uc317637&path=/Dc/0/Voltage
Current: 52.55V (nominal 48V)
Range: 41.6V (min) - 54.0V (max)
Alert if: <41.6V or >54.5V

Path: /value?service=com.victronenergy.battery.socketcan_can0_vi6_uc317637&path=/Dc/0/Current
Current: -13.3A (discharging)
Alert if: >600A (discharge) or current asymmetry >20A between units
```

### Battery State of Charge
```
Path: /value?service=com.victronenergy.battery.socketcan_can0_vi6_uc317637&path=/Soc
Current: 66.39%
Critical: <20% (low battery)
Warning: <40%
Optimal: 40-80%
```

### Inverter AC Output Load Sharing
```
Path RS1: /value?service=com.victronenergy.multi.socketcan_can0_vi1_uc488085&path=/Ac/Out/L3/P
Current: -46W (supplying)

Path RS2: /value?service=com.victronenergy.multi.socketcan_can0_vi2_uc382989&path=/Ac/Out/L3/P
Current: +413W (demanding)

Alert if: Load difference >50% (currently 89% on one unit)
```

### Grid Power Flow Direction
```
Path: /value?service=com.victronenergy.grid.socketcan_can0_vi0_uc449643&path=/Ac/Power
Current: -33.92W (EXPORTING to grid)
Positive: Importing from grid
Negative: Exporting to grid
```

### System Frequency Lock
```
Path: /value?service=com.victronenergy.grid.socketcan_can0_vi0_uc449643&path=/Ac/Frequency
Current: 50.04Hz
Alert if: <49.5Hz or >50.5Hz (grid instability)
```

---

## Daily Monitoring Checklist

### Morning (6:00 AM)
- [ ] SOC trending (should be rising with dawn)
- [ ] Solar yield starting (PV voltage increase)
- [ ] Load distribution (verify 50% each inverter ideally)
- [ ] Grid frequency (should be stable 50.0Hz)

### Midday (12:00 PM)
- [ ] Peak solar production (maximum kW)
- [ ] Battery charge current (should be highest)
- [ ] Grid export direction (should be exporting)
- [ ] Phase voltage balance (3-phase check)

### Evening (18:00)
- [ ] Solar yield daily total
- [ ] Battery SOC at sunset (target: 80%+)
- [ ] Grid transition (import/export change)
- [ ] Load distribution during transition

### Night (22:00)
- [ ] Battery discharge rate (amps)
- [ ] Time to empty calculation
- [ ] Grid import (should be steady)
- [ ] Error codes (all should be 0)

---

## Critical Voltage Points

### Battery Voltage Thresholds
| State | Voltage | Meaning |
|-------|---------|---------|
| 54.0V | Max Charge | BMS will stop charging |
| 53.0V | Float/Maintain | Bulk charging complete |
| 52.5V | Normal Operating | Battery absorbing power |
| 41.6V | Low Voltage Alarm | Critical, discharge disable |
| 50.6V | Historical Min | Lowest ever seen |
| 64.1V | Historical Max | Highest ever seen |

### AC Grid Voltage per Phase
| Phase | Current | Range OK | Alert |
|-------|---------|----------|-------|
| L1 | 224.32V | 207-253V | >253V or <207V |
| L2 | 223.66V | 207-253V | >253V or <207V |
| L3 | 226.65V | 207-253V | >253V or <207V |
| Imbalance | 3.0V | <10V | >15V between phases |

---

## Current Distribution (Parallel Inverters)

### Expected vs. Actual
```
Expected (50/50 load sharing):
  RS1: 1.4A each
  RS2: 1.4A each
  Total: 2.8A

Actual (IMBALANCED):
  RS1: -0.5A (supplying/negative)
  RS2: +3.3A (demanding)
  Total: 2.8A (current correct, distribution wrong)
  
Imbalance: 3.8A (270% of per-unit expected)
Root Cause: ESS Mode 1 vs Mode 3 configuration
```

### Current Ripple (DC Side)
| Device | Ripple | Status | Alert |
|--------|--------|--------|-------|
| RS1 | 17.99mV | GOOD | >50mV |
| RS2 | 32.99mV | GOOD | >50mV |
| BMS | N/A | N/A | - |

---

## Energy Flows (Cumulative Historical)

### MultiRS1 Energy Routing
| Path | kWh | Direction | Comment |
|------|-----|-----------|---------|
| SolarToAcOut | 6.64 | Solar to load | Low (2% of routes) |
| SolarToBattery | 267.93 | Solar to battery | Primary solar use |
| SolarToAcIn1 | 288.23 | Solar to grid | Feedback to grid |
| AcIn1ToInverter | 1037.81 | Grid to battery | Primary grid use |
| InverterToAcOut | 2.01 | Battery to load | Very low |
| **Total In** | 1600.62 | All inputs | - |

### MultiRS2 Energy Routing
| Path | kWh | Direction | Comment |
|------|-----|-----------|---------|
| SolarToAcOut | 254.37 | Solar to load | Primary solar output |
| SolarToBattery | 443.65 | Solar to battery | Strong solar charging |
| InverterToAcOut | 1363.11 | Battery to load | PRIMARY LOAD SOURCE |
| AcOutToAcIn1 | 102.90 | Load back to grid | Feedback |
| **Total Out** | 2163.93 | All outputs | - |

### System Interpretation
- RS1: Grid charger (1037.81 kWh from grid, 267.93 kWh from solar)
- RS2: Load supplier (1363.11 kWh to load, 254.37 kWh from solar)
- Energy: Asymmetric by design/configuration

---

## Temperature Monitoring (Critical Gap)

### Current Status
```
Inverter RS1: NO TEMPERATURE SENSOR []
Inverter RS2: NO TEMPERATURE SENSOR []
MPPT RS: NO TEMPERATURE SENSOR []
MPPT VE.Can: NO TEMPERATURE SENSOR []
BMS: NO TEMPERATURE SENSOR []
```

### Recommended Additions
| Device | Sensor Type | Critical Threshold |
|--------|-------------|-------------------|
| RS1 | NTC Thermistor | >65C alarm, >75C shutdown |
| RS2 | NTC Thermistor | >65C alarm, >75C shutdown |
| BMS | Smart Thermistor | >55C alarm, >65C shutdown |
| MPPT RS | NTC | >75C alarm |
| MPPT VE.Can | NTC | >75C alarm |

---

## Synchronization Quality Metrics

### Phase Voltage Matching (Inverter AC Output)
```
RS1 AC Out: 225.2V
RS2 AC Out: 225.3V
Difference: 0.1V
Percentage: 0.044% (EXCELLENT)
Status: Synchronized
```

### DC Bus Voltage Matching
```
RS1 DC: 52.56V
RS2 DC: 52.56V
Difference: 0.0V
Status: PERFECT synchronization
```

### Frequency Matching
```
RS1: 50.0Hz
RS2: 50.0Hz
Grid: 50.04Hz
Difference: 0.0Hz (RS to RS), +0.04Hz (vs grid)
Status: PERFECT - grid-locked
```

### Phase Sequence
```
Grid Phase Rotation: Normal (0)
Phase Sequence: Stable
L1 → L2 → L3 → L1: Correct direction
Status: HEALTHY
```

---

## Error Codes & Diagnostic Paths

### Error Code Locations
```
RS1 ErrorCode: /Ac/Out/ErrorCode = 0 (HEALTHY)
RS2 ErrorCode: /Ac/Out/ErrorCode = 0 (HEALTHY)
BMS ErrorCode: /ErrorCode = 0 (HEALTHY)
Grid Meter: /ErrorCode = 0 (HEALTHY)
System: Check all alarms
```

### BMS Diagnostic Errors
```
Path: /value?service=com.victronenergy.battery.socketcan_can0_vi6_uc317637&path=/Diagnostics/LastErrors

LastError/1: 0 (no error)
LastError/2: 0 (no error)
LastError/3: 0 (no error)
LastError/4: 0 (no error)
Status: CLEAN HISTORY
```

### Alarm Status (All Should Be 0)
```
EnergyMeterMissing: 0 ✓
PhaseRotation: 0 ✓
GridLost: 0 ✓
ShortCircuit: 0 ✓
HighVoltageAcOut: 0 ✓
LowVoltageAcOut: 0 ✓
Ripple: 0 ✓
Overload: 0 ✓
HighTemperature: 0 ✓
HighVoltage: 0 ✓
LowVoltage: 0 ✓
LowSoc: 0 ✓

Status: ALL CLEAR
```

---

## Performance Baseline (for trending)

### Current Operating Point (Snapshot)
```
Time: Night/Evening operation (solar inactive)
SOC: 66.37%
Discharge: 22.9A total
Grid Power: -159.76W (exporting)
Load: 530.97W
System Frequency: 50.04Hz
```

### System Efficiency Metrics
```
Battery Round-Trip: 97.32% (chargedEnergy/dischargedEnergy)
Solar MPPT Efficiency: Unknown (no direct measurement)
Inverter Efficiency: ~95% typical (calculated)
BMS Loss: ~1-2% (from ripple and control)
```

---

## Alert Thresholds for AI Monitoring

### CRITICAL (Immediate Action)
```
SOC < 20%
Voltage < 41.6V
Current > 600A
Error Code != 0
Alarm triggered (non-zero)
Temperature > 70C (if added)
Frequency <49.5Hz or >50.5Hz
```

### WARNING (Investigation)
```
SOC < 40%
Load imbalance > 60% (currently 89%, so flagged)
Phase voltage >10V difference
Neutral current >2A
Power ripple >50mV
DC ripple >40mV
```

### INFORMATION (Trend)
```
Daily yield <50% of historical average
Load distribution asymmetry
Energy flow asymmetry between inverters
Grid power direction changes
SOC trending rate (charge/discharge speed)
```

---

## API Polling Intervals

### Real-Time Monitoring (Every 5 seconds)
- Battery SOC and voltage
- AC load currents
- Grid power direction
- Frequency lock

### Detailed Monitoring (Every 30 seconds)
- Phase voltages (all three)
- Energy meters (forward/reverse)
- Inverter output per phase
- Temperature (when added)

### Historical Tracking (Every 5 minutes)
- Energy totals
- Load distribution
- Grid interaction
- Battery efficiency

### Daily Analysis (Once daily)
- Solar yield
- Total consumption
- Grid net
- Battery cycling

---

## Device State Codes Reference

### Inverter State Values
- 0: Off
- 1: Idle (waiting for input)
- 2: Fault
- 3: Equalization
- 4: Absorption
- 5: Float
- 6: Storage
- 9: Shutdown
- 252: **CURRENT** (ESS operating)

### Battery/BMS State Values
- 2: **CURRENT** (charging/discharging)
- 9: **CURRENT** (online monitoring)

### Device Off Reasons
- 1: No AC input power
- 2: ESS disabled
- 1024: **CURRENT** (normal operation)
- 1028: **CURRENT** (no PV power)

---

## System Configuration Summary

### ESS Modes
- RS1: Mode 1 (Charger only) - limits inverter output
- RS2: Mode 3 (Inverter) - active load support
- Implication: Asymmetric operation by design

### Grid Code
- Setting: 16 (European standard)
- Compliance: Anti-islanding enabled
- Alarm Levels: All set to 1 (monitored)

### DVCC Status
- Enabled: true
- Control/BmsParameters: 1 (BMS controlling)
- Control/MaxChargeCurrent: true (BMS limits apply)
- Effective Voltage: 54.4V (with solar offset)

---

## File Locations

### Full Documentation
- `/tmp/victron_einstein_research.md` - 1,391 lines, 40KB
- `/tmp/victron_einstein_index.md` - Quick reference
- `/tmp/victron_einstein_metrics.md` - This file

### API Endpoint Base
- `http://192.168.88.189:8088/`

---

## Contact & Documentation
Generated: October 23, 2025
System: Victron Cerbo GX (c0619ab4e0e9)
Firmware: v3.70~22 Build 222721

