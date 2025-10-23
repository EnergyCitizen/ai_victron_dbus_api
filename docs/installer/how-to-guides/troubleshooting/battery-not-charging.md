# Troubleshoot: Battery Not Charging

Quick diagnostic guide for resolving "battery not charging" issues remotely using AI agent queries.

---

## Problem

**Customer Report**: "My battery isn't charging"
**Your Goal**: Diagnose remotely in <15 minutes, resolve without site visit if possible

---

## Conversational Diagnosis Flow

### Step 1: Ask Agent for System State

**You Ask**:
> "What's wrong with Site 7? Customer says battery not charging."

**Agent Checks** (internally):
1. Battery current (is it actually charging?)
2. Inverter state (bulk/absorption/float/off?)
3. BMS alarms (charge blocked?)
4. Temperature (too hot/cold?)
5. Voltage (at safe levels?)
6. AC input (grid available?)

**Agent Responds**:
> "I've checked Site 7. Here's what I found:
>
> **Current Status**:
> - Battery: 48.2V, 45% SOC
> - Charge current: 0A (NOT charging)  ← Problem confirmed
> - Inverter: Mode=On, State=Float
> - AC Input: 228V, 50Hz (Grid OK)
>
> **Root Cause**: ChargeBlocked alarm is ACTIVE
>
> **Reason**: Battery temperature is 52°C, above the 50°C charge limit.
> The BMS is blocking charging to protect the cells from thermal damage.
>
> **Resolution**:
> - Wait for battery to cool below 45°C (check in 30 min)
> - OR check cooling system (fan working? Ventilation blocked?)
> - System will resume charging automatically when temp drops
>
> Shall I monitor temperature and notify when charging resumes?"
```

**Outcome**: Issue diagnosed in 30 seconds, no truck roll needed. Customer informed to wait for cooling.

---

## Common Causes & Diagnosis

### Cause 1: Temperature Out of Range

**Symptoms**:
- Charge current = 0A
- ChargeBlocked alarm = Active
- Temperature >50°C or <0°C

**Ask Agent**:
> "Check battery temperature at Site 7"

**Agent Response**:
> "Battery temperature is 52°C (too hot). BMS has blocked charging to protect cells.
>  Normal operating range: 0-50°C. Should cool down in 30-60 minutes."

**Resolution**:
- Wait for cooling
- Check cooling fan operation
- Improve ventilation
- Reduce charge current (less heat)

**API Paths**:
- `/Dc/0/Temperature` (battery service)
- `/Alarms/ChargeBlocked` (vebus service)

---

### Cause 2: BMS Limits Reached

**Symptoms**:
- Charge current = 0A or very low
- ChargeLimitedBms = Active
- SOC approaching 100%

**Ask Agent**:
> "Why is charge current only 2A?"

**Agent Response**:
> "Battery is at 98% SOC, nearly full. BMS has reduced charge acceptance to 2A for final balancing.
>  This is normal behavior. Will reach 100% in ~20 minutes, then switch to Float mode."

**Resolution**:
- No action needed (normal)
- BMS managing final charging phase

**API Paths**:
- `/Soc` (battery service)
- `/Dc/0/Current` (battery service)
- `/Alarms/ChargeLimitedBms` (vebus service)

---

### Cause 3: AC Input Missing

**Symptoms**:
- Charge current = 0A
- Inverter State = Inverting (9)
- AC input voltage = 0V

**Ask Agent**:
> "Is there grid power at Site 7?"

**Agent Response**:
> "No grid power detected. AC input voltage is 0V. System is running on battery (inverting).
>  Either:
>  1. Grid outage (check with utility)
>  2. Circuit breaker tripped
>  3. AC input wiring issue
>
>  Battery will discharge. Estimated runtime: 4 hours at current load (550W)."

**Resolution**:
- Check grid connection
- Reset circuit breakers
- Verify AC input wiring
- Contact utility if area outage

**API Paths**:
- `/Ac/ActiveIn/L1/V` (vebus service)
- `/Alarms/GridLost` (vebus service)
- `/State` (vebus service: 9 = inverting)

---

### Cause 4: Inverter Disabled/Off

**Symptoms**:
- Charge current = 0A
- Inverter State = Off (0)
- No alarms

**Ask Agent**:
> "Is the inverter on at Site 7?"

**Agent Response**:
> "Inverter is OFF (State = 0). Battery cannot charge with inverter disabled.
>
>  Possible reasons:
>  1. Manually switched off in VictronConnect
>  2. Remote disable via VRM
>  3. Soft-start delay after power cycle
>
>  Solution: Enable inverter in VictronConnect or VRM portal."

**Resolution**:
- Check inverter enable switch
- Enable via VRM portal
- Check for soft-start timer

**API Paths**:
- `/State` (vebus service: 0 = off)
- `/Mode` (vebus service)

---

### Cause 5: Battery Voltage Too High

**Symptoms**:
- Charge current = 0A
- Battery voltage >53V
- HighDcVoltage alarm

**Ask Agent**:
> "Check voltage at Site 7"

**Agent Response**:
> "Battery voltage is 53.8V (too high). This exceeds the safe charging limit (53.5V).
>  System has stopped charging to prevent overcharging damage.
>
>  Possible causes:
>  1. Float voltage set too high (check settings)
>  2. BMS not limiting charge properly
>  3. Voltage sense error
>
>  CAUTION: High voltage can damage battery. Don't reconnect load until voltage drops below 53V."

**Resolution**:
- Check float voltage setting (should be 52-53V)
- Verify BMS charge voltage limit
- Check voltage sense wiring
- May need to manually discharge slightly

**API Paths**:
- `/Dc/0/Voltage` (battery service)
- `/Settings/SystemSetup/MaxChargeVoltage` (settings service)
- `/Alarms/HighDcVoltage` (vebus service)

---

## Diagnostic Checklist

Ask agent these questions in sequence:

```
1. "What's the battery current at Site X?"
   → If 0A, not charging. If >0A, it IS charging.

2. "What's the inverter state?"
   → If Off (0) or Fault (2), inverter issue
   → If Bulk/Absorption/Float (3/4/5), should be charging

3. "Are there any charge-related alarms?"
   → ChargeBlocked, ChargeLimitedBms, HighDcVoltage

4. "What's the battery temperature?"
   → If >50°C or <0°C, BMS blocks charging

5. "Is AC input available?"
   → If 0V, no grid = no charging (unless solar)

6. "What's the battery voltage?"
   → If >53V, overvoltage protection
   → If <45V, may be in error state
```

---

## Quick Diagnostic Script

For when AI agent isn't available (backup):

```bash
#!/bin/bash
# diagnose-charging.sh <SITE_IP>

SITE_IP="$1"
API="http://${SITE_IP}:8088"

echo "=== Battery Charging Diagnosis ==="
echo ""

echo "1. Battery State:"
curl -s "${API}/value?service=com.victronenergy.battery.socketcan_can0&path=/Dc/0/Current" \
  | jq -r '"  Current: \(.value)A (" + (if .value > 0 then "CHARGING ✅" elif .value < 0 then "DISCHARGING ❌" else "IDLE ❌" end) + ")"'

curl -s "${API}/value?service=com.victronenergy.battery.socketcan_can0&path=/Dc/0/Voltage" \
  | jq -r '"  Voltage: \(.value)V"'

curl -s "${API}/value?service=com.victronenergy.battery.socketcan_can0&path=/Soc" \
  | jq -r '"  SOC: \(.value)%"'

echo ""
echo "2. Inverter State:"
curl -s "${API}/value?service=com.victronenergy.vebus.ttyS4&path=/State" \
  | jq -r '"  State: \(.value) (" + (if .value == 0 then "OFF ❌" elif .value == 2 then "FAULT ❌" elif .value == 3 then "Bulk ✅" elif .value == 4 then "Absorption ✅" elif .value == 5 then "Float ✅" elif .value == 9 then "Inverting" else "Unknown" end) + ")"'

echo ""
echo "3. Temperature:"
curl -s "${API}/value?service=com.victronenergy.battery.socketcan_can0&path=/Dc/0/Temperature" \
  | jq -r '"  Battery Temp: \(.value)°C (" + (if .value > 50 then "TOO HOT ❌" elif .value < 0 then "TOO COLD ❌" else "OK ✅" end) + ")"'

echo ""
echo "4. AC Input:"
curl -s "${API}/value?service=com.victronenergy.vebus.ttyS4&path=/Ac/ActiveIn/L1/V" \
  | jq -r '"  AC Voltage: \(.value)V (" + (if .value > 0 then "Grid OK ✅" else "No Grid ❌" end) + ")"'

echo ""
echo "5. Alarms:"
curl -s "${API}/settings" | jq -r '
  .settings | to_entries[]
  | select(.key | contains("Alarm"))
  | select(.value.Value == 2)
  | "  ⚠️  \(.key): ACTIVE"
'

echo ""
echo "=== Diagnosis Complete ==="
```

---

## Success Criteria

After using this guide, you should be able to:
- ✅ Diagnose "battery not charging" in <15 minutes
- ✅ Identify root cause using AI agent queries
- ✅ Resolve 60%+ issues without site visit
- ✅ Explain to customer what's happening and when it will resolve

---

## Related Guides

**Troubleshooting**:
- [Grid Frequency Issues](./grid-frequency-issues.md) - Grid connection problems
- [MPPT Offline](./mppt-offline.md) - Solar charger not producing

**Validation**:
- [Check Battery Health](../validation/check-battery-health.md) - SOC, SOH, cells
- [Verify Synchronization](../validation/verify-synchronization.md) - Voltage/frequency match

**Concepts**:
- [DVCC Control System](../../concepts/dvcc-control-system.md) - Who controls charging
- [ESS Modes Explained](../../concepts/ess-modes-explained.md) - Mode 1 vs 3

**Reference**:
- [Alarm Codes](../../reference/alarm-codes.md) - All alarm meanings
- [State Codes](../../reference/state-codes.md) - Inverter state machine

---

**Made in Ukraine 🇺🇦 with love by EnergyCitizen**
