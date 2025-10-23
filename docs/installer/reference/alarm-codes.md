# Alarm Codes Reference

Complete list of Victron alarm codes with plain language explanations and recommended actions.

---

## Battery/BMS Alarms

### Critical Alarms (Immediate Action)

| Alarm Code | Path | Meaning | Cause | Action |
|------------|------|---------|-------|--------|
| `BmsConnectionLost` | `/Alarms/BmsConnectionLost` | BMS communication lost | CAN cable disconnected/damaged | Check CAN cable, reboot BMS |
| `InternalFailure` | `/Alarms/InternalFailure` | Battery internal fault | Cell failure, BMS malfunction | Contact manufacturer, replace battery |
| `LowCellVoltage` | `/Alarms/LowCellVoltage` | Cell voltage critically low | Over-discharge, weak cell | Stop discharge, charge immediately |
| `HighCellVoltage` | `/Alarms/HighCellVoltage` | Cell voltage too high | Overcharge, BMS failure | Stop charging immediately |
| `DischargeBlocked` | `/Alarms/DischargeBlocked` | BMS blocking discharge | Safety threshold reached | Check BMS logs, investigate cause |

### Warning Alarms (Monitor/Plan)

| Alarm Code | Path | Meaning | Cause | Action |
|------------|------|---------|-------|--------|
| `ChargeBlocked` | `/Alarms/ChargeBlocked` | BMS blocking charging | Temperature, voltage limits | Check temperature, wait for normal range |
| `CellImbalance` | `/Alarms/CellImbalance` | Cells unbalanced | Aging, weak cell | Enable balancing, monitor weekly |
| `HighTemperature` | `/Alarms/HighTemperature` | Battery too hot | Poor cooling, high load | Check fan, improve ventilation |
| `LowTemperature` | `/Alarms/LowTemperature` | Battery too cold | Cold environment | Wait to warm, reduce charge rate |
| `HighChargeCurrent` | `/Alarms/HighChargeCurrent` | Charging too fast | Charger misconfigured | Reduce charge current limit |
| `HighDischargeCurrent` | `/Alarms/HighDischargeCurrent` | Discharging too fast | Load too high | Reduce load or discharge limit |
| `LowSoc` | `/Alarms/LowSoc` | State of charge low | Battery depleting | Charge battery or reduce load |
| `LowVoltage` | `/Alarms/LowVoltage` | Battery voltage low | Low SOC or weak battery | Charge immediately |

---

## Inverter/Charger Alarms

### Critical Alarms

| Alarm Code | Path | Meaning | Cause | Action |
|------------|------|---------|-------|--------|
| `GridLost` | `/Alarms/GridLost` | Grid disconnected | Power outage, breaker trip | Check grid, reset breaker |
| `Overload` | `/Alarms/Overload` | Load exceeds capacity | Too many devices | Reduce load immediately |
| `HighDcVoltage` | `/Alarms/HighDcVoltage` | Battery overvoltage | Charger issue, BMS failure | Stop charging, check voltage |
| `HighDcCurrent` | `/Alarms/HighDcCurrent` | DC current too high | Overload, short circuit | Reduce load, check wiring |
| `ShortCircuit` | `/Alarms/ShortCircuit` | AC output shorted | Wiring fault | Disconnect load, check wiring |
| `PhaseRotation` | `/Alarms/PhaseRotation` | Wrong phase order | Incorrect wiring | Fix L1/L2/L3 connections |

### Warning Alarms

| Alarm Code | Path | Meaning | Cause | Action |
|------------|------|---------|-------|--------|
| `HighTemperature` | `/Alarms/HighTemperature` | Inverter overheating | Poor ventilation, overload | Improve airflow, reduce load |
| `LowBattery` | `/Alarms/LowBattery` | Battery voltage low | Low SOC | Charge battery |
| `Ripple` | `/Alarms/Ripple` | Excessive AC ripple | Loose connection, capacitor | Check connections, service unit |
| `HighVoltageAcOut` | `/Alarms/HighVoltageAcOut` | AC output too high | Configuration error | Check settings |
| `LowVoltageAcOut` | `/Alarms/LowVoltageAcOut` | AC output too low | Overload, weak battery | Reduce load, check battery |
| `TemperatureSensor` | `/Alarms/TemperatureSensor` | Temp sensor failed | Sensor disconnected | Check sensor wiring |
| `VoltageSensor` | `/Alarms/VoltageSensor` | Voltage sense error | Sense wire disconnected | Check voltage sense wiring |

---

## Grid/Frequency Alarms

| Alarm Code | Meaning | Cause | Action |
|------------|---------|-------|--------|
| GridLost (frequency) | Grid frequency out of range | Utility issue or wrong grid code | Check grid code setting |
| GridLost (voltage) | Grid voltage out of range | Utility issue or wiring problem | Check grid voltage, contact utility |
| Anti-islanding | Anti-islanding protection | Grid instability detected | Wait for grid to stabilize |

---

## System Alarms

| Alarm Code | Path | Meaning | Cause | Action |
|------------|------|---------|-------|--------|
| `VebusCommunicationError` | `/Alarms/VebusCommunicationError` | VE.Bus comm loss | Cable issue, firmware | Check VE.Bus cable, update firmware |
| `DataPartitionFull` | `/Device/DataPartitionFullError` | Storage full | Logs filling disk | Clear logs, check VRM |
| `FirmwareUpdateFailed` | `/Alarms/FirmwareUpdateFailure` | Update failed | Corruption, power loss | Retry update, restore backup |

---

## Alarm Value Meanings

Most alarms use these values:

| Value | Meaning |
|-------|---------|
| `0` | No alarm (clear) |
| `1` | Warning (monitor) |
| `2` | Alarm (action needed) |

Some alarms are boolean:

| Value | Meaning |
|-------|---------|
| `0` | False (no alarm) |
| `1` | True (alarm active) |

---

## How to Query Alarms

### Check All Battery Alarms

```bash
curl "http://SITE_IP:8088/value?service=com.victronenergy.battery.socketcan_can0&path=/Alarms"
```

### Check Specific Alarm

```bash
curl "http://SITE_IP:8088/value?service=com.victronenergy.battery.socketcan_can0&path=/Alarms/HighTemperature"
```

### Check Inverter Alarms

```bash
curl "http://SITE_IP:8088/value?service=com.victronenergy.vebus.ttyS4&path=/Alarms"
```

---

## Alarm History

### Recent Alarms

Platform service stores alarm history:

```bash
curl "http://SITE_IP:8088/value?service=com.victronenergy.platform&path=/Notifications"
```

**Response includes**:
- Timestamp
- Alarm type
- Device name
- Active/cleared status
- Acknowledged status

---

## Alarm Priority Levels

### Priority 1: Safety Critical (Act Immediately)
- InternalFailure
- ShortCircuit
- HighDcVoltage (>55V)
- Thermal runaway risk

**Action**: Disconnect system if unsafe

### Priority 2: Operational Critical (Act Within Hours)
- GridLost (extended)
- BmsConnectionLost
- Overload
- DischargeBlocked

**Action**: Diagnose and resolve same day

### Priority 3: Warning (Act Within Days)
- CellImbalance
- HighTemperature (sustained)
- LowSoc

**Action**: Schedule maintenance, monitor trend

### Priority 4: Information (Monitor)
- Temporary GridLost (seconds)
- LowBattery (recovering)
- Brief overload

**Action**: Log for trend analysis

---

## Common Alarm Combinations

### Battery Overheating + ChargeBlocked

**Meaning**: Battery too hot, BMS stopped charging to protect cells

**Action**:
1. Check cooling system
2. Wait for battery to cool (<40°C)
3. Charging will resume automatically

---

### GridLost + Overload

**Meaning**: Grid disconnected, inverter overloaded on battery

**Action**:
1. Reduce load immediately
2. System will shut down if overload continues
3. Wait for grid to return

---

### CellImbalance + LowVoltage

**Meaning**: Weak cell causing premature low voltage

**Action**:
1. Enable BMS balancing
2. Charge to 100% and hold for 2 hours
3. If persists, plan battery replacement

---

### BmsConnectionLost + All Battery Alarms

**Meaning**: Communication lost, alarms are stale

**Action**:
1. Check CAN cable (primary issue)
2. Reboot BMS
3. Other alarms will clear when comms restore

---

## Related Documentation

**Troubleshooting**:
- [Battery Not Charging](../how-to-guides/troubleshooting/battery-not-charging.md)
- [Grid Frequency Issues](../how-to-guides/troubleshooting/grid-frequency-issues.md)

**Reference**:
- [Troubleshooting Matrix](./troubleshooting-matrix.md)
- [State Codes](./state-codes.md)

---

**Made in Ukraine 🇺🇦 with love by EnergyCitizen**
