# Troubleshoot: Grid Frequency Issues

Quick diagnostic guide for resolving grid frequency problems that prevent inverter synchronization.

---

## Problem

**Customer Report**: "Inverter won't connect to grid" or "System keeps disconnecting"
**Your Goal**: Diagnose frequency issues remotely in <10 minutes, determine if grid or settings problem

---

## Conversational Diagnosis Flow

### Step 1: Ask Agent for Grid Status

**You Ask**:
> "Site 12 inverter won't sync to grid. What's the frequency?"

**Agent Checks** (internally):
1. Grid frequency reading
2. Grid code setting
3. Frequency limits
4. Connection status
5. Recent disconnection alarms

**Agent Responds**:
> "I've checked Site 12 grid connection:
>
> **Current Status**:
> - Grid Frequency: 51.2Hz (OUT OF RANGE)
> - Expected Range: 49.5-50.5Hz (for Grid Code 16)
> - Grid Voltage: 228V (OK)
> - Connection Status: DISCONNECTED
>
> **Root Cause**: Grid frequency is 1.2Hz above limit
>
> **Likely Reasons**:
> 1. Wrong grid code setting (currently 16 - Europe/50Hz)
> 2. Utility grid instability (overfrequency event)
> 3. Generator mode active (if backup present)
>
> **Diagnosis**:
> Let me check if this is sustained or temporary...
> [Checks last 10 readings over 5 minutes]
>
> Frequency has been 51.1-51.3Hz for 5 minutes straight. This is NOT a transient spike.
>
> **Most Likely**: Wrong grid code. If this is a 60Hz region, grid code should be 28 (US/60Hz), not 16 (EU/50Hz).
>
> **Actions**:
> 1. Verify customer location - is this 50Hz or 60Hz grid?
> 2. If 60Hz region: Change grid code to 28
> 3. If 50Hz region: Contact utility about overfrequency
>
> Would you like me to guide you through changing the grid code?"

---

## Common Causes & Diagnosis

### Cause 1: Wrong Grid Code Setting

**Symptoms**:
- Frequency reads consistently out of range
- 50Hz grid but frequency shows ~60Hz (or vice versa)
- GridLost alarm persistent
- System never connects to grid

**Ask Agent**:
> "What grid code is set at Site 12?"

**Agent Response**:
> "Grid code is set to 16 (Europe - 50Hz nominal).
>  Current frequency reading: 60.1Hz
>
>  **Problem**: This looks like a 60Hz grid (Americas/parts of Asia) but configured for 50Hz.
>
>  **60Hz Grid Codes**:
>  - Code 28: US/Canada
>  - Code 35: Philippines
>  - Code 27: Brazil
>
>  **50Hz Grid Codes**:
>  - Code 16: Europe (EN50549-1)
>  - Code 14: Australia
>  - Code 26: South Africa
>
>  To fix: Change grid code to match your location. In VictronConnect → Settings → Grid Code."

**Resolution**:
1. Verify actual grid frequency (ask utility or check other equipment)
2. Select correct grid code for region
3. System will reconnect automatically when code matches
4. Monitor for 5 minutes to confirm stable

**VRM Path**: Settings → System setup → Grid code
**API Path**: `/Settings/SystemSetup/AcInput1/GridCode` (vebus service)

---

### Cause 2: Utility Grid Overfrequency Event

**Symptoms**:
- Frequency above normal range (>50.5Hz for 50Hz grid, >60.5Hz for 60Hz grid)
- GridLost alarm triggers
- Other customers in area also affected
- Temporary condition (resolves after minutes/hours)

**Ask Agent**:
> "Is the frequency out of range or is grid code wrong?"

**Agent Response**:
> "Grid code is correct (16 - Europe 50Hz).
>  Current frequency: 50.8Hz (0.3Hz above 50.5Hz limit)
>
>  **Analysis**: This is a utility grid overfrequency event, not a configuration error.
>
>  **Why It Happens**:
>  - Grid has excess generation (sunny day with lots of solar)
>  - Load suddenly dropped (factory shutdown)
>  - Grid operator shedding generation (frequency rises)
>
>  **Regulation**: European standard EN50549-1 requires inverters to disconnect above 50.5Hz for 1 second.
>
>  **What Happens Next**:
>  - Inverter disconnects (protection)
>  - Retries connection every 60 seconds
>  - Reconnects automatically when frequency drops to 50.5Hz
>
>  **Estimated Duration**: Typically 5-30 minutes
>
>  **Current Status**: Monitoring... Last 3 readings: 50.8Hz, 50.7Hz, 50.7Hz (trending down)
>
>  No action needed from you. System will reconnect automatically."

**Resolution**:
- Wait for grid frequency to stabilize
- System auto-reconnects when frequency returns to safe range
- If persists >1 hour, contact utility
- No settings changes needed

**Monitoring**:
- Agent can track frequency and alert when reconnection happens

---

### Cause 3: Underfrequency Event

**Symptoms**:
- Frequency below normal range (<49.5Hz for 50Hz grid, <59.5Hz for 60Hz grid)
- System may increase power export (grid support mode)
- GridLost alarm if very low

**Ask Agent**:
> "Grid frequency too low at Site 5, what's happening?"

**Agent Response**:
> "Site 5 grid frequency: 49.2Hz (0.3Hz below 49.5Hz limit)
>
>  **Analysis**: Grid underfrequency - grid needs more generation.
>
>  **Why It Happens**:
>  - High load, insufficient generation
>  - Power plant trip
>  - Grid instability
>
>  **System Response**:
>  - If grid code allows, inverter may INCREASE export to support grid
>  - If frequency drops below 47.5Hz, disconnects for safety
>
>  **Current Action**: Your inverter is exporting at maximum to help stabilize grid (grid support active).
>
>  **Risk**: If frequency continues falling, system will disconnect to protect itself.
>
>  **Monitoring**: I'll watch frequency. If drops below 48Hz, I'll alert you.
>
>  This is typically a temporary utility event (5-15 minutes)."

**Resolution**:
- System is already helping (grid support)
- If frequency <47.5Hz, automatic disconnection occurs
- Wait for utility to restore balance
- No action unless persists >1 hour

---

### Cause 4: Generator Mode with Wrong Frequency

**Symptoms**:
- Connected to generator (backup power)
- Generator frequency unstable or wrong
- Inverter disconnects repeatedly

**Ask Agent**:
> "System on generator, won't stay connected"

**Agent Response**:
> "Checking AC input frequency...
>
>  **Readings (last 30 seconds)**:
>  - 51.2Hz, 50.8Hz, 51.5Hz, 50.3Hz, 51.0Hz, 50.9Hz
>
>  **Problem**: Frequency is UNSTABLE (1.2Hz swing in 30 seconds)
>
>  **Cause**: Generator governor not holding stable frequency
>
>  **Why Inverter Disconnects**: Victron requires stable frequency within ±0.5Hz for safe operation. Your generator is swinging ±1Hz.
>
>  **Generator Issues**:
>  1. Governor needs adjustment (mechanical or electronic)
>  2. Generator overloaded or underloaded
>  3. Low-quality generator (poor speed regulation)
>
>  **Temporary Workaround**: Enable 'Weak AC' mode in VictronConnect:
>  - Settings → AC Input → Enable Weak AC
>  - Relaxes frequency tolerance
>  - **CAUTION**: Reduces protection
>
>  **Proper Fix**: Service generator - adjust governor to hold 50Hz ±0.2Hz"

**Resolution**:
1. Check generator speed governor
2. Ensure generator not overloaded (reduce load to 50-70%)
3. Verify fuel quality (old fuel = speed fluctuations)
4. Enable Weak AC mode temporarily (not permanent solution)
5. Consider better quality generator or UPS

---

## Diagnostic Checklist

Ask agent these questions in sequence:

```
1. "What's the grid frequency at Site X?"
   → If 50Hz ±0.5Hz (or 60Hz ±0.5Hz) = OK
   → If out of range = Problem identified

2. "What grid code is configured?"
   → If code doesn't match location = Configuration error
   → If code correct = Utility or generator issue

3. "Is frequency stable or fluctuating?"
   → If stable out-of-range = Wrong code or utility event
   → If fluctuating wildly = Generator or weak grid

4. "Show me frequency trend last 30 minutes"
   → If recent change = Utility event (temporary)
   → If always out of range = Configuration error

5. "Any other sites in same region having issues?"
   → If multiple sites = Utility problem (area-wide)
   → If only one site = Local generator or configuration
```

---

## Quick Diagnostic Script

For when AI agent isn't available (backup):

```bash
#!/bin/bash
# diagnose-frequency.sh <SITE_IP>

SITE_IP="$1"
API="http://${SITE_IP}:8088"

echo "=== Grid Frequency Diagnosis ==="
echo ""

echo "1. Current Grid Status:"
curl -s "${API}/value?service=com.victronenergy.vebus.ttyS4&path=/Ac/ActiveIn/L1/F" \
  | jq -r '"  Frequency: \(.value)Hz (" + (if .value > 50.5 or .value < 49.5 then "OUT OF RANGE ❌" else "OK ✅" end) + ")"'

curl -s "${API}/value?service=com.victronenergy.vebus.ttyS4&path=/Ac/ActiveIn/L1/V" \
  | jq -r '"  Voltage: \(.value)V"'

curl -s "${API}/value?service=com.victronenergy.vebus.ttyS4&path=/Ac/ActiveIn/Connected" \
  | jq -r '"  Connected: " + (if .value == 1 then "YES ✅" else "NO ❌" end)'

echo ""
echo "2. Grid Code Setting:"
curl -s "${API}/settings" | jq -r '
  .settings | to_entries[]
  | select(.key | contains("GridCode"))
  | "  Grid Code: \(.value.Value) (\(.value.Description // "Unknown"))"
'

echo ""
echo "3. Recent Alarms:"
curl -s "${API}/value?service=com.victronenergy.vebus.ttyS4&path=/Alarms/GridLost" \
  | jq -r '"  GridLost: " + (if .value == 1 then "ACTIVE ❌" else "Clear ✅" end)'

echo ""
echo "4. Frequency Tolerance:"
echo "  50Hz Grid: 49.5-50.5Hz (±0.5Hz)"
echo "  60Hz Grid: 59.5-60.5Hz (±0.5Hz)"

echo ""
echo "=== Diagnosis Complete ==="
```

---

## Frequency Tolerance by Grid Code

### Common Grid Codes

| Code | Region | Nominal | Min | Max | Notes |
|------|--------|---------|-----|-----|-------|
| **16** | Europe (EN50549-1) | 50Hz | 49.5Hz | 50.5Hz | Strict limits |
| **28** | US/Canada | 60Hz | 59.5Hz | 60.5Hz | IEEE 1547 |
| **14** | Australia (AS4777) | 50Hz | 49.0Hz | 51.0Hz | Wider tolerance |
| **26** | South Africa | 50Hz | 49.5Hz | 50.5Hz | Similar to Europe |
| **35** | Philippines | 60Hz | 59.5Hz | 60.5Hz | Similar to US |

### Disconnection Times

| Frequency Range | Disconnect Time | Reason |
|-----------------|-----------------|--------|
| >51.5Hz (50Hz grid) | Immediate | Severe overfrequency |
| 50.5-51.5Hz | 1-10 seconds | Overfrequency protection |
| 49.0-49.5Hz | 10-300 seconds | Underfrequency warning |
| <49.0Hz | 2 seconds | Severe underfrequency |

---

## Decision Tree

```
Is frequency out of range?
│
├─ YES → Is it consistent or fluctuating?
│   │
│   ├─ CONSISTENT → Check grid code
│   │   │
│   │   ├─ Wrong code → FIX: Set correct code for region
│   │   │
│   │   └─ Correct code → Check if other sites affected
│   │       │
│   │       ├─ Multiple sites → UTILITY EVENT: Wait it out
│   │       │
│   │       └─ Only this site → Check generator or local wiring
│   │
│   └─ FLUCTUATING → Generator issue or weak grid
│       │
│       └─ FIX: Adjust generator governor or enable Weak AC mode
│
└─ NO → Frequency OK, check voltage or connection issues
```

---

## Success Criteria

After using this guide, you should be able to:
- ✅ Diagnose frequency issues in <10 minutes
- ✅ Identify if problem is configuration, utility, or generator
- ✅ Set correct grid code for customer location
- ✅ Explain to customer when service will resume
- ✅ Escalate to utility when appropriate

---

## Related Guides

**Troubleshooting**:
- [Battery Not Charging](./battery-not-charging.md) - Charging issues
- [Inverter Load Imbalance](./inverter-load-imbalance.md) - Parallel inverter issues

**Validation**:
- [Verify Synchronization](../validation/verify-synchronization.md) - Grid connection checks
- [Check System Health](../validation/check-system-health.md) - Overall system status

**Concepts**:
- [ESS Modes Explained](../../concepts/ess-modes-explained.md) - Grid-tie behavior
- [Grid Code Standards](../../concepts/grid-code-standards.md) - Regional requirements

**Reference**:
- [Grid Code Table](../../reference/grid-codes.md) - All grid codes
- [Alarm Codes](../../reference/alarm-codes.md) - All alarm meanings

---

**Made in Ukraine 🇺🇦 with love by EnergyCitizen**
