# Tutorial: Validate a New Installation with AI Agent

**Duration**: 20 minutes
**Level**: Beginner
**Prerequisites**: Access to site DBus API, basic understanding of Victron systems

Learn to use an AI agent to validate a freshly installed Victron system and catch configuration issues before you leave the site.

---

## What You'll Validate

By the end of this tutorial, you'll have verified:

1. **Synchronization** - All devices communicating properly
2. **Battery Health** - SOC, SOH, voltage, temperature in safe ranges
3. **Grid Connection** - Voltage, frequency, and phase alignment correct
4. **Alarms** - No critical alarms present
5. **Configuration** - ESS mode, grid code, limits properly set

**Time Savings**: 20-minute checklist vs 2-hour troubleshooting after you've left!

---

## Pre-Installation Checklist

Before starting validation:

- [ ] All equipment physically installed
- [ ] DC wiring complete and torqued
- [ ] AC wiring complete and tested
- [ ] CAN/VE.Bus cables connected
- [ ] System powered on for 5+ minutes
- [ ] Network configured (WiFi or Ethernet)
- [ ] DBus API accessible at `http://<SITE_IP>:8088`

---

## Validation Workflow

```
┌─────────────────────────────────────────┐
│   1. Device Discovery                   │
│   Are all devices online?               │
└─────────────────┬───────────────────────┘
                  │
                  v
┌─────────────────────────────────────────┐
│   2. Synchronization Check              │
│   Voltage, frequency, DC bus aligned?   │
└─────────────────┬───────────────────────┘
                  │
                  v
┌─────────────────────────────────────────┐
│   3. Battery Validation                 │
│   SOC, voltage, temperature OK?         │
└─────────────────┬───────────────────────┘
                  │
                  v
┌─────────────────────────────────────────┐
│   4. Grid Connection Check              │
│   Frequency, voltage, grid code OK?     │
└─────────────────┬───────────────────────┘
                  │
                  v
┌─────────────────────────────────────────┐
│   5. Alarm Review                       │
│   Any critical alarms?                  │
└─────────────────┬───────────────────────┘
                  │
                  v
┌─────────────────────────────────────────┐
│   6. Load Test                          │
│   System handles load correctly?        │
└─────────────────┬───────────────────────┘
                  │
                  v
            ✅ VALIDATED
```

---

## Step 1: Device Discovery (3 minutes)

### Ask Agent: "What devices are online?"

**Agent Checks**:
- System service available
- Battery/BMS detected
- Inverter/charger responding
- Grid meter present (if configured)
- Solar chargers detected (if present)

**Expected Response (Good)**:
> "✅ All devices online:
>
> **System**: Cerbo GX (Firmware v3.70~33)
> - Uptime: 15 minutes
> - System Type: ESS
>
> **Battery/BMS**: Pylontech US3000C (2 modules)
> - Device: com.victronenergy.battery.socketcan_can0
> - Status: Online, communicating
> - Modules Online: 2/2 ✅
>
> **Inverter**: Multi Plus-II 48/3000/35-32
> - Device: com.victronenergy.vebus.ttyS4
> - Status: Online
> - Mode: 3 (On)
>
> **Grid Meter**: Carlo Gavazzi EM24
> - Device: com.victronenergy.acload.cg_*
> - Status: Connected
>
> **Solar**: SmartSolar MPPT 150/70
> - Device: com.victronenergy.solarcharger.*
> - Status: Online
>
> All critical devices detected and communicating."

**Response (Problem)**:
> "⚠️ Device Issue Detected:
>
> ✅ System: Online
> ✅ Inverter: Online
> ❌ **Battery/BMS**: NOT DETECTED
> ✅ Grid Meter: Online
>
> **Problem**: Battery BMS is not communicating. System cannot operate safely without battery monitor.
>
> **Check**:
> 1. CAN cable connection from BMS to Cerbo
> 2. BMS DIP switch settings (termination)
> 3. Power to BMS (some require 12V external power)
> 4. Cerbo CAN port enabled in settings"

---

## Step 2: Synchronization Check (2 minutes)

### Ask Agent: "Check system synchronization"

**Agent Checks**:
- DC voltage across all battery services
- AC voltage across phases
- Frequency alignment
- Grid connection status

**Expected Response (Good)**:
> "✅ System Synchronized:
>
> **DC Bus**:
> - Battery voltage: 51.2V
> - Inverter sees: 51.1V
> - Difference: 0.1V (excellent, <0.5V threshold)
>
> **AC Voltage** (Phase 1):
> - Grid input: 228V
> - Inverter output: 228V
> - Difference: 0V (synchronized)
>
> **Frequency**:
> - Grid: 50.02Hz
> - Inverter: 50.02Hz
> - Difference: 0.00Hz (perfect sync)
>
> **Grid Connection**: Connected ✅
>
> System is properly synchronized. AC and DC buses aligned."

**Response (Problem)**:
> "⚠️ Synchronization Issue:
>
> **DC Bus**:
> - Battery voltage: 51.2V
> - Inverter sees: 49.8V
> - Difference: 1.4V ❌ (>0.5V threshold)
>
> **Problem**: Large voltage difference indicates voltage sense issue or wiring problem.
>
> **Check**:
> 1. DC voltage sense wires connected to inverter
> 2. Loose DC bus bar connections (high resistance)
> 3. Battery BMS allowing current (check alarms)
> 4. DC fuse/breaker intact
>
> ⚠️ Do NOT commission until voltage difference <0.5V"

---

## Step 3: Battery Validation (3 minutes)

### Ask Agent: "Validate battery health"

**Agent Checks**:
- SOC in safe range
- SOH (if available)
- Voltage matches SOC
- Temperature acceptable
- No battery alarms
- Modules all online

**Expected Response (Good)**:
> "✅ Battery Health: GOOD
>
> **State of Charge**: 75% (safe starting point)
> **State of Health**: 99% (new battery)
> **Voltage**: 51.2V (matches 75% SOC for LiFePO4)
> **Temperature**: 22°C (optimal range)
>
> **Modules**:
> - Online: 2/2 ✅
> - Blocking Charge: 0
> - Blocking Discharge: 0
>
> **Cell Voltages**:
> - Max: 3.320V
> - Min: 3.315V
> - Spread: 0.005V (excellent balance)
>
> **Alarms**: None ✅
>
> Battery is healthy and ready for operation."

**Response (Problem)**:
> "⚠️ Battery Issue:
>
> **State of Charge**: 15% ❌ (too low for commissioning)
> **Voltage**: 47.8V (matches low SOC)
> **Temperature**: 52°C ❌ (too hot)
>
> **Alarms**:
> - HighTemperature: ACTIVE ❌
> - ChargeBlocked: ACTIVE ❌
>
> **Problems**:
> 1. Battery too hot (>50°C) - BMS blocking charging
> 2. SOC too low for reliable testing
>
> **Actions**:
> 1. Wait for battery to cool below 40°C (30-60 min)
> 2. Check ventilation around battery enclosure
> 3. Once cool, charge to 60-80% before further testing
>
> ⚠️ Do NOT commission until temperature <40°C and SOC >50%"

---

## Step 4: Grid Connection Check (3 minutes)

### Ask Agent: "Check grid connection"

**Agent Checks**:
- Grid voltage in range
- Grid frequency correct
- Grid code matches region
- Phase rotation correct (3-phase)
- Connection stable

**Expected Response (Good)**:
> "✅ Grid Connection: VALID
>
> **Voltage**: 228V (within 220-240V range) ✅
> **Frequency**: 50.02Hz (within 49.5-50.5Hz) ✅
> **Grid Code**: 16 (Europe - EN50549-1) ✅
> **Connected**: Yes ✅
> **GridLost Alarm**: Clear ✅
>
> **Phase Rotation**: Normal (L1-L2-L3) ✅
>
> **Frequency Stability** (last 60 seconds):
> - Min: 49.98Hz
> - Max: 50.05Hz
> - Average: 50.01Hz
> - Deviation: ±0.03Hz (stable) ✅
>
> Grid connection is stable and properly configured."

**Response (Problem)**:
> "❌ Grid Connection Issue:
>
> **Voltage**: 228V ✅
> **Frequency**: 60.1Hz ❌ (expected 50Hz for Europe)
> **Grid Code**: 16 (Europe - 50Hz) ❌
> **Connected**: No ❌
>
> **Problem**: Frequency reads 60Hz but grid code set for 50Hz region.
>
> **Likely Cause**: Wrong grid code setting
>
> **Is this a 60Hz region** (US, Canada, Philippines, etc.)?
> - If YES: Change grid code to 28 (US/Canada 60Hz)
> - If NO: Verify utility grid frequency with meter
>
> **How to Fix**:
> 1. VictronConnect → Inverter → Settings → Grid Code
> 2. Select code matching your region
> 3. Save and reboot
> 4. Revalidate connection
>
> ⚠️ System will NOT connect to grid until code matches frequency"

---

## Step 5: Alarm Review (2 minutes)

### Ask Agent: "Are there any active alarms?"

**Agent Checks**:
- All alarm paths across devices
- Recent alarm history
- Severity levels

**Expected Response (Good)**:
> "✅ No Active Alarms
>
> Checked all alarm categories:
> - Battery/BMS: No alarms ✅
> - Inverter: No alarms ✅
> - Grid: No alarms ✅
> - Temperature: No alarms ✅
> - System: No alarms ✅
>
> **Recent History**: 2 cleared alarms
> - GridLost (30 min ago): Cleared when grid connected ✅
> - LowSoc (45 min ago): Cleared after charging ✅
>
> System is alarm-free and ready for operation."

**Response (Problem)**:
> "⚠️ Active Alarms Detected:
>
> **CRITICAL** (1):
> - BmsConnectionLost ❌
>   Device: Inverter
>   Since: 2 minutes ago
>   Impact: System cannot safely charge/discharge
>
> **WARNING** (2):
> - CellImbalance
>   Device: Battery
>   Since: 15 minutes ago
>   Impact: Battery balancing needed
>
> - HighDcVoltage
>   Device: Inverter
>   Since: 1 minute ago
>   Impact: Charging stopped for safety
>
> **Problem**: BMS communication lost
>
> **Check**:
> 1. CAN cable connection (BMS to Cerbo)
> 2. BMS power (some need 12V)
> 3. CAN termination (120Ω resistor on last device)
> 4. Reboot BMS and wait 60 seconds
>
> ⚠️ Do NOT commission until BmsConnectionLost clears"

---

## Step 6: Load Test (5 minutes)

### Ask Agent: "Run a load test"

**Manual Steps**:
1. Turn on a known load (e.g., 500W heater)
2. Wait 30 seconds for system to stabilize
3. Ask agent to verify

**Agent Checks**:
- Inverter output power matches load
- AC voltage stable under load
- Battery current reasonable for load
- No overload alarms
- Efficiency within expected range

**Expected Response (Good)**:
> "✅ Load Test: PASSED
>
> **Load Applied**: ~500W
>
> **System Response**:
> - Inverter Output: 485W ✅
> - AC Voltage: 227V (stable, no sag) ✅
> - Battery Current: 10.2A (matches load) ✅
> - Battery Voltage: 51.0V (no significant drop) ✅
>
> **Efficiency**: 95% (485W AC / 520W DC)
> - Within normal range (90-95%) ✅
>
> **Alarms**: None ✅
>
> **Power Flow**:
> - Battery → Inverter → Load
> - Grid: 0W (off-grid mode working)
>
> System handles load correctly. Ready for commissioning."

**Response (Problem)**:
> "⚠️ Load Test: ISSUES DETECTED
>
> **Load Applied**: ~500W
>
> **System Response**:
> - Inverter Output: 485W
> - AC Voltage: 215V ❌ (sagging from 228V)
> - Battery Current: 18.5A ❌ (too high for 500W load)
> - Battery Voltage: 48.2V ❌ (dropped from 51.0V)
>
> **Problem**: Excessive voltage drop under load
>
> **Likely Causes**:
> 1. Undersized DC cables (high resistance)
> 2. Loose DC connections
> 3. Weak battery (unlikely if new)
> 4. High internal resistance
>
> **Check**:
> 1. Verify DC cable gauge (should be 35mm² minimum for 3kVA)
> 2. Check all DC crimps and connections
> 3. Measure DC resistance (should be <10mΩ)
> 4. Re-torque all DC terminals
>
> ⚠️ Fix voltage drop before commissioning (target: <1V drop under 500W)"

---

## Validation Checklist Summary

### Quick Checklist (Use This at Site)

```
Installation Validation Checklist
Site: ________________  Date: __________  Installer: __________

☐ 1. Device Discovery
    ☐ Cerbo GX online
    ☐ Battery/BMS online (modules: __/__)
    ☐ Inverter online
    ☐ Grid meter online (if configured)
    ☐ Solar chargers online (if configured)

☐ 2. Synchronization
    ☐ DC voltage difference <0.5V
    ☐ AC voltage aligned
    ☐ Frequency synchronized
    ☐ Grid connected

☐ 3. Battery Health
    ☐ SOC 50-90% (starting range)
    ☐ SOH >95% (new battery)
    ☐ Voltage matches SOC
    ☐ Temperature 15-40°C
    ☐ No battery alarms
    ☐ Cell spread <0.10V

☐ 4. Grid Connection
    ☐ Voltage 220-240V (Europe) or per region
    ☐ Frequency 50Hz ±0.5Hz or 60Hz ±0.5Hz
    ☐ Grid code matches region
    ☐ Connection stable (no GridLost)
    ☐ Phase rotation correct (3-phase)

☐ 5. Alarms
    ☐ No critical alarms
    ☐ No BMS alarms
    ☐ No inverter alarms
    ☐ No grid alarms

☐ 6. Load Test
    ☐ 500W load test passed
    ☐ Voltage sag <5V
    ☐ No overload alarms
    ☐ Efficiency 85-95%

☐ 7. Configuration
    ☐ ESS mode correct (Mode 3 for grid-tie)
    ☐ SOC limits configured (Min: 50-60%)
    ☐ Current limits set (AC input, charge/discharge)
    ☐ Grid code verified
    ☐ DVCC enabled (multi-device systems)

☐ FINAL: System Validated ✅
    Customer signature: ____________________
    Installer signature: ____________________
```

---

## Common Issues & Quick Fixes

### Issue: BMS Not Detected

**Symptoms**: No battery service in device list
**Fix**:
1. Check CAN cable (RJ45, straight-through)
2. Verify BMS powered (some need 12V)
3. Check DIP switches on BMS (termination)
4. Reboot Cerbo and wait 60 seconds
5. Check CAN port enabled: Settings → Services

### Issue: Grid Won't Connect

**Symptoms**: GridLost alarm, frequency out of range
**Fix**:
1. Verify grid code matches region
2. Check AC input wiring (L, N, PE)
3. Verify circuit breaker closed
4. Check AC input current limit (increase if too low)
5. Test grid with multimeter (verify 50/60Hz)

### Issue: High DC Voltage Drop

**Symptoms**: Voltage sags >1V under load
**Fix**:
1. Check DC cable gauge (35mm² for 3kVA, 70mm² for 5kVA)
2. Re-torque all DC connections (M8: 10Nm, M10: 13Nm)
3. Verify crimp quality (redo if questionable)
4. Check for corroded terminals
5. Measure resistance (should be <10mΩ total)

### Issue: Cell Imbalance on New Battery

**Symptoms**: Cell spread >0.10V on fresh install
**Fix**:
1. Verify battery just unpacked (cells may be unbalanced from storage)
2. Enable BMS balancing
3. Charge to 100% (balancing occurs at top)
4. Hold at 100% for 2 hours
5. Re-check spread (should drop to <0.05V)
6. If still high: Return battery (defect)

---

## Post-Validation Steps

After successful validation:

1. **Document Configuration**:
   - Take screenshots of key settings
   - Record battery/inverter serial numbers
   - Save configuration to file

2. **Customer Walkthrough**:
   - Show VRM portal
   - Explain basic monitoring
   - Demonstrate VictronConnect app

3. **Set Up Monitoring**:
   - Register on VRM portal
   - Enable remote support (if agreed)
   - Configure alert emails/SMS

4. **Final Check**:
   - Verify VRM is receiving data
   - Test remote access
   - Confirm customer satisfied

---

## Success Criteria

After completing this tutorial, you should be able to:
- ✅ Validate all devices are online and communicating
- ✅ Verify system synchronization across DC and AC
- ✅ Confirm battery health and safe operating state
- ✅ Validate grid connection and configuration
- ✅ Review and clear any alarms
- ✅ Perform load test to verify system operation
- ✅ Complete validation in <20 minutes
- ✅ Leave site confident system will work reliably

---

## Related Guides

**Troubleshooting**:
- [Battery Not Charging](../how-to-guides/troubleshooting/battery-not-charging.md)
- [Grid Frequency Issues](../how-to-guides/troubleshooting/grid-frequency-issues.md)
- [Inverter Load Imbalance](../how-to-guides/troubleshooting/inverter-load-imbalance.md)

**Validation**:
- [Check Battery Health](../how-to-guides/validation/check-battery-health.md)
- [Verify Synchronization](../how-to-guides/validation/verify-synchronization.md)

**Concepts**:
- [ESS Modes Explained](../concepts/ess-modes-explained.md)
- [DVCC Control System](../concepts/dvcc-control-system.md)

**Reference**:
- [Alarm Codes](../reference/alarm-codes.md)
- [Grid Code Table](../reference/grid-codes.md)

---

**Made in Ukraine 🇺🇦 with love by EnergyCitizen**
