# Troubleshoot: Inverter Load Imbalance (Parallel Systems)

Diagnostic guide for resolving uneven load distribution in parallel multi-inverter systems.

---

## Problem

**Customer Report**: "One inverter working harder than the other" or "Uneven heating between units"
**Your Goal**: Diagnose load sharing issues remotely, balance load within 30 minutes

---

## Real Case Study: Einstein System

**System Configuration**:
- 2× Multi RS Solar 48/6000VA/100A
- Total capacity: 10.2kW
- Both units on Phase 3 (L3)
- Same DC bus (52.56V battery)

**Problem Detected**:
- MultiRS1: -46W output (-0.5A, supplying power back)
- MultiRS2: +413W output (+3.3A, drawing power)
- **Load Distribution**: 89% on RS2, only 11% on RS1
- **Expected**: 50/50 split (±5% tolerance)
- **Actual**: 78% imbalance

---

## Conversational Diagnosis Flow

### Step 1: Ask Agent to Check Load Sharing

**You Ask**:
> "Einstein system - customer says one inverter is hot, the other cool. Check load balance."

**Agent Checks** (internally):
1. AC output power from each inverter
2. AC output current from each inverter
3. DC current from each inverter
4. ESS mode configuration
5. Current limit settings
6. Voltage/frequency sync

**Agent Responds**:
> "I've checked the Einstein system (dual Multi RS). Here's what I found:
>
> **Current Load Distribution**:
> - MultiRS1 (Unit 1): -46W output, -0.5A
> - MultiRS2 (Unit 2): +413W output, +3.3A
> - **Total Load**: 367W
> - **Imbalance**: 89% on Unit 2, 11% on Unit 1 ❌
>
> **Synchronization** (verified):
> - Voltage: RS1=225.2V, RS2=225.3V (0.1V difference) ✅
> - Frequency: Both 50.0Hz ✅
> - DC Bus: Both 52.56V ✅
>
> **Root Cause Found**: ESS Mode Mismatch
> - MultiRS1: ESS Mode 1 (Charger only)
> - MultiRS2: ESS Mode 3 (Inverter mode)
>
> **Why This Causes Imbalance**:
> - Mode 1 (RS1) = Prioritizes charging, minimal inverting
> - Mode 3 (RS2) = Active inverter, handles loads
> - RS1 is configured to avoid inverting, so RS2 does all the work
>
> **Additional Factors**:
> - RS1 has energy meter enabled (grid-aware control)
> - RS1 SOC limit: 65% (high, conservative)
> - RS2 SOC limit: 5% (low, aggressive)
> - RS1 current limit: 37.5A (energy meter based)
> - RS2 current limit: 50.0A (33% higher)
>
> **Fix**: Harmonize ESS modes to Mode 3 on both units.
>
> Would you like me to guide you through the configuration change?"

---

## Common Causes & Diagnosis

### Cause 1: ESS Mode Mismatch (MOST COMMON)

**Symptoms**:
- One inverter handles >70% of load
- Load imbalance consistent across all load levels
- Both units online and synchronized
- No alarms

**Configuration Check**:

| Parameter | MultiRS1 | MultiRS2 | Impact |
|-----------|----------|----------|--------|
| ESS Mode | Mode 1 (Charger) | Mode 3 (Inverter) | RS1 avoids inverting |
| Min SOC | 65% | 5% | RS1 stops earlier |
| Current Limit | 37.5A | 50.0A | RS1 limited to 75% |
| Energy Meter | Enabled | Disabled | RS1 grid-aware |

**Ask Agent**:
> "What ESS mode is each inverter in?"

**Agent Response**:
> "ESS Mode Configuration:
>  - Unit 1: Mode 1 (Charger only) ❌
>  - Unit 2: Mode 3 (Inverter mode) ✅
>
>  **Problem**: Mode 1 means Unit 1 will charge battery but avoid inverting. It's designed to import from grid and charge, not supply loads.
>
>  **Solution**: Set both units to Mode 3 (Inverter mode) for balanced load sharing.
>
>  **How to Fix**:
>  1. VictronConnect → Unit 1 → Settings → ESS
>  2. Change Mode from 1 to 3
>  3. Save and reboot
>  4. Wait 5 minutes
>  5. I'll verify load balances"

**Resolution**:
1. Access VictronConnect or VRM
2. Navigate to ESS settings for Unit 1
3. Change ESS Mode to 3 (same as Unit 2)
4. Apply and restart
5. Monitor for 10 minutes
6. Load should balance to 50/50 ±10%

**VRM Path**: Settings → ESS → ESS Mode
**API Paths**:
- `/Ess/Mode` (multi service) - 1=Charger, 3=Inverter

---

### Cause 2: Current Limit Mismatch

**Symptoms**:
- One inverter reaches current limit, other doesn't
- Imbalance worse under heavy load
- One unit shows ChargeLimited alarm

**Configuration Check**:

**Ask Agent**:
> "Check current limits on both inverters"

**Agent Response**:
> "Current Limit Configuration:
>  - Unit 1: 37.5A (energy meter controlled)
>  - Unit 2: 50.0A (fixed setting)
>  - **Difference**: 33% (12.5A)
>
>  **Impact**: When load exceeds 37.5A capability of Unit 1, it maxes out and Unit 2 takes remainder.
>
>  **At Current Load** (367W):
>  - Expected per unit: ~183W (1.5A each)
>  - Actual: Unit 1 supplies -46W, Unit 2 supplies 413W
>
>  **Why**: Unit 1's energy meter is restricting current to manage grid import.
>
>  **Solution**: Adjust Unit 1 current limit to match Unit 2 (50A) or reduce both to same value (45A)."

**Resolution**:
1. Check if energy meter is controlling current limit
2. Set both units to same AC input current limit (e.g., 45A)
3. Verify current limits via API or VictronConnect
4. Test under load

**API Paths**:
- `/Ess/CurrentLimitEnergyMeter` (multi service)
- `/Ac/In/1/CurrentLimit` (vebus service)

---

### Cause 3: SOC Limit Mismatch

**Symptoms**:
- One inverter stops inverting before the other
- Imbalance appears below certain SOC
- One unit goes to Float while other still inverting

**Configuration Check**:

**Ask Agent**:
> "What are the minimum SOC limits?"

**Agent Response**:
> "Minimum SOC Configuration:
>  - Unit 1: 65% (stops inverting at 65% SOC)
>  - Unit 2: 5% (continues inverting down to 5% SOC)
>
>  **Current Battery SOC**: 66.37%
>
>  **Impact**: Unit 1 is at or near its cutoff point (65%), so it's avoiding discharge. Unit 2 will continue inverting.
>
>  **Result**: As SOC approaches 65%, Unit 1 backs off and Unit 2 handles all load.
>
>  **Solution**: Harmonize SOC limits to same value (recommend 50-60% for both)."

**Resolution**:
1. Set both units to same minimum SOC (55-60% typical)
2. Consider system-level needs (backup runtime)
3. Apply settings to both units
4. Monitor behavior as battery discharges

**API Path**: `/Ess/MinimumSocLimit` (multi service)

---

### Cause 4: Voltage/Frequency Desynchronization

**Symptoms**:
- Load sharing changes randomly
- One unit fighting the other
- AC ripple or voltage instability
- Units producing reactive power

**Synchronization Check**:

**Ask Agent**:
> "Are the inverters synchronized?"

**Agent Response (GOOD)**:
> "Synchronization Status: ✅ EXCELLENT
>
>  **Voltage Sync**:
>  - Unit 1 AC Out: 225.2V
>  - Unit 2 AC Out: 225.3V
>  - Difference: 0.1V (0.044% mismatch)
>  - Status: PERFECT (threshold: <1V)
>
>  **Frequency Sync**:
>  - Unit 1: 50.0Hz
>  - Unit 2: 50.0Hz
>  - Difference: 0.0Hz
>  - Status: PERFECT
>
>  **DC Bus Sync**:
>  - Unit 1 DC: 52.56V
>  - Unit 2 DC: 52.56V
>  - Difference: 0.0V
>  - Status: PERFECT
>
>  Voltage and frequency are synchronized. Load imbalance is NOT due to sync issues."

**Agent Response (BAD)**:
> "⚠️ Synchronization Issue Detected:
>
>  **Voltage Sync**:
>  - Unit 1 AC Out: 225.2V
>  - Unit 2 AC Out: 228.7V
>  - Difference: 3.5V (1.5% mismatch) ❌
>
>  **Problem**: Voltage droop settings or calibration differ between units.
>
>  **Impact**: Higher voltage unit will push power to lower voltage unit, causing circulating current and load imbalance.
>
>  **Solution**:
>  1. Check voltage sense wiring (ensure both measure same point)
>  2. Verify droop settings are identical
>  3. Calibrate voltage sensing if supported
>  4. Check firmware versions match"

**Resolution**:
- If voltage difference >1V: Check sense wiring, droop settings
- If frequency difference >0.05Hz: Check grid synchronization
- Update firmware to same version on both units
- Verify AC output wiring is identical

**API Paths**:
- `/Ac/Out/L1/V` (multi service) - AC output voltage
- `/Ac/Out/L1/F` (multi service) - AC output frequency
- `/Dc/0/Voltage` (multi service) - DC bus voltage

---

### Cause 5: Phase Assignment Error

**Symptoms**:
- Load imbalance in 3-phase system
- Some phases have no inverter
- Overload on one phase

**Ask Agent**:
> "Which phase is each inverter assigned to?"

**Agent Response**:
> "Phase Assignment:
>  - Unit 1: Phase 3 (L3)
>  - Unit 2: Phase 3 (L3)
>
>  **Configuration**: Both inverters on same phase (L3 only)
>
>  **Total L3 Output**: 367W
>  - Unit 1 contribution: -46W
>  - Unit 2 contribution: +413W
>
>  **Other Phases**:
>  - L1: No inverter (grid only)
>  - L2: No inverter (grid only)
>
>  This is a single-phase system using 2 units in parallel on L3. Load sharing between units is expected to be 50/50."

**Resolution** (if phase assignment is wrong):
1. Verify intended system design (3-phase vs 1-phase)
2. If 3-phase intended: Assign Unit 1 to L1, Unit 2 to L2 (example)
3. If 1-phase intended: Both on same phase (correct, but need load balancing fix)

---

## Diagnostic Checklist

Ask agent these questions in sequence:

```
1. "What's the load on each inverter?"
   → Calculate imbalance percentage
   → If >20% imbalance = Problem

2. "What ESS mode is each unit in?"
   → If different modes = Configuration mismatch
   → If same modes = Check other factors

3. "Are voltage and frequency synchronized?"
   → If >1V or >0.05Hz difference = Sync problem
   → If synchronized = Configuration issue

4. "What are the current limits?"
   → If different limits = Adjust to match
   → If same limits = Check SOC limits

5. "What are the minimum SOC limits?"
   → If different SOC limits = Harmonize
   → If same = Check energy meter settings

6. "Is energy meter enabled on both units?"
   → If only one has meter = That unit will be grid-aware
   → If both or neither = Check power setpoints
```

---

## Quick Diagnostic Script

For when AI agent isn't available (backup):

```bash
#!/bin/bash
# diagnose-load-balance.sh <SITE_IP>

SITE_IP="$1"
API="http://${SITE_IP}:8088"

echo "=== Parallel Inverter Load Balance Diagnosis ==="
echo ""

echo "1. Load Distribution:"
POWER1=$(curl -s "${API}/value?service=com.victronenergy.multi.socketcan_can0_vi1_uc488085&path=/Ac/Out/L3/P" | jq -r '.value')
POWER2=$(curl -s "${API}/value?service=com.victronenergy.multi.socketcan_can0_vi2_uc382989&path=/Ac/Out/L3/P" | jq -r '.value')

echo "  Unit 1: ${POWER1}W"
echo "  Unit 2: ${POWER2}W"

TOTAL=$(echo "$POWER1 + $POWER2" | bc)
PCT1=$(echo "scale=1; ($POWER1 / $TOTAL) * 100" | bc)
PCT2=$(echo "scale=1; ($POWER2 / $TOTAL) * 100" | bc)

echo "  Distribution: Unit1=${PCT1}%, Unit2=${PCT2}%"

echo ""
echo "2. Synchronization:"
VOLT1=$(curl -s "${API}/value?service=com.victronenergy.multi.socketcan_can0_vi1_uc488085&path=/Ac/Out/L3/V" | jq -r '.value')
VOLT2=$(curl -s "${API}/value?service=com.victronenergy.multi.socketcan_can0_vi2_uc382989&path=/Ac/Out/L3/V" | jq -r '.value')

echo "  Unit 1 Voltage: ${VOLT1}V"
echo "  Unit 2 Voltage: ${VOLT2}V"

FREQ1=$(curl -s "${API}/value?service=com.victronenergy.multi.socketcan_can0_vi1_uc488085&path=/Ac/Out/L3/F" | jq -r '.value')
FREQ2=$(curl -s "${API}/value?service=com.victronenergy.multi.socketcan_can0_vi2_uc382989&path=/Ac/Out/L3/F" | jq -r '.value')

echo "  Unit 1 Frequency: ${FREQ1}Hz"
echo "  Unit 2 Frequency: ${FREQ2}Hz"

echo ""
echo "3. ESS Configuration:"
MODE1=$(curl -s "${API}/value?service=com.victronenergy.multi.socketcan_can0_vi1_uc488085&path=/Ess/Mode" | jq -r '.value')
MODE2=$(curl -s "${API}/value?service=com.victronenergy.multi.socketcan_can0_vi2_uc382989&path=/Ess/Mode" | jq -r '.value')

echo "  Unit 1 ESS Mode: $MODE1 (1=Charger, 3=Inverter)"
echo "  Unit 2 ESS Mode: $MODE2"

SOC1=$(curl -s "${API}/value?service=com.victronenergy.multi.socketcan_can0_vi1_uc488085&path=/Ess/MinimumSocLimit" | jq -r '.value')
SOC2=$(curl -s "${API}/value?service=com.victronenergy.multi.socketcan_can0_vi2_uc382989&path=/Ess/MinimumSocLimit" | jq -r '.value')

echo "  Unit 1 Min SOC: ${SOC1}%"
echo "  Unit 2 Min SOC: ${SOC2}%"

echo ""
echo "=== Diagnosis Complete ==="
echo ""
echo "Expected Load Balance: 50/50 ±10%"
echo "Voltage Sync Tolerance: <1V"
echo "Frequency Sync Tolerance: <0.05Hz"
```

---

## Load Balance Tolerance

### Acceptable Ranges

| Load Imbalance | Status | Action |
|----------------|--------|--------|
| **0-10%** | Excellent | No action needed |
| **10-20%** | Good | Monitor, minor adjustment if easy |
| **20-40%** | Poor | Investigate configuration, adjust settings |
| **>40%** | Critical | Fix immediately, risk of overheating/failure |

### Einstein System Example

- Actual: 89/11 split = 78% imbalance
- Status: **Critical** ❌
- Required Action: Harmonize ESS modes immediately

---

## Success Criteria

After using this guide, you should be able to:
- ✅ Diagnose load imbalance in <20 minutes
- ✅ Identify root cause (ESS mode, limits, sync)
- ✅ Configure settings for balanced operation
- ✅ Verify 50/50 load sharing ±10%
- ✅ Prevent inverter overheating and failure

---

## Related Guides

**Troubleshooting**:
- [Grid Frequency Issues](./grid-frequency-issues.md) - Grid sync problems
- [Battery Not Charging](./battery-not-charging.md) - Charging issues

**Validation**:
- [Verify Synchronization](../validation/verify-synchronization.md) - Voltage/frequency check
- [Validate New Installation](../../tutorials/01-validate-new-installation.md) - Full system check

**Concepts**:
- [Parallel Inverter Operation](../../concepts/parallel-inverter-operation.md) - How sync works
- [ESS Modes Explained](../../concepts/ess-modes-explained.md) - Mode 1 vs 3

**Reference**:
- [ESS Mode Reference](../../reference/ess-modes.md) - All mode meanings
- [Current Limit Settings](../../reference/current-limits.md) - Configuration guide

---

**Made in Ukraine 🇺🇦 with love by EnergyCitizen**
