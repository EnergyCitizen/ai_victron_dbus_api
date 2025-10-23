# Victron Einstein System - Research Index & Quick Reference

## Document Overview
- **Full Research Document**: `/tmp/victron_einstein_research.md`
- **Size**: 40KB (1,391 lines)
- **Coverage**: 12 comprehensive sections + 3 appendices
- **Generated**: October 23, 2025

---

## Research Content Summary

### SECTION 1: PARALLEL MULTI-INVERTER SYSTEM (DUAL CONFIGURATION)
**Pages**: 1-3
- MultiRS1 (0488085) & MultiRS2 (0382989) specifications
- Parallel operation coordination (voltage sync, frequency sync, phase alignment)
- ESS configuration (asymmetric modes 1 & 3)
- AC input configuration (grid integration)
- Health & alarm status (all clear)

**Key Findings**:
- Voltage sync: EXCELLENT (0.1V diff = 0.044%)
- Frequency sync: PERFECT (both 50.0Hz)
- Load sharing: IMBALANCED (89% MultiRS2, 11% MultiRS1)
- Error codes: ALL ZERO (healthy)

### SECTION 2: MULTI-PHASE AC SYSTEM & GRID SERVICES
**Pages**: 3-5
- AC System 0/1 (socketcan coordination)
- Grid Meter (VM-3P75CT) - 3-phase VE.Can
- AC Load Meter (Carlo Gavazzi EM24) - Modbus TCP
- Power factor analysis
- Phase voltage balance

**Key Findings**:
- Grid meter: -33.92W (NET EXPORTING)
- Load meter: 747.2W L3 (100% of consumption)
- Phase imbalance: 1.43% (acceptable)
- Neutral current: -1.2A (imbalance indicator)

### SECTION 3: BATTERY MANAGEMENT & BMS INTEGRATION
**Pages**: 5-7
- Lynx Smart BMS 500 specifications (Serial: 0317637)
- Battery state (SOC 66.39%, 52.55V, -13.3A discharge)
- Performance history (97.32% round-trip efficiency)
- BMS diagnostics (all alarms clear)
- Configuration limits (600A capability, 54.0V max)

**Key Findings**:
- Battery capacity: 1180Ah @ 48V = 56.64kWh
- Charge cycles: 152 (low usage)
- Time to empty: 51.3 hours @ -13.3A
- All safety indicators: HEALTHY

### SECTION 4: SOLAR CHARGING SYSTEM (TRIPLE MPPT CONFIGURATION)
**Pages**: 7-10
- MultiRS1 integrated solar (2 trackers, ~5.7kW)
- MultiRS2 integrated solar (2 trackers, ~8.3kW)
- SmartSolar MPPT RS 450/200 (4 trackers, offline)
- SmartSolar MPPT VE.Can 150/70 (1 tracker, producing)
- Multi RS PV Inverter (AC-only, standby)

**Key Findings**:
- Total PV capacity: ~27.4kW
- Daily yield (Day 1): 30.32kWh
- Active MPPT: VE.Can 150/70 (8.68kWh/day)
- MPPT RS 450/200: Offline (investigate)
- Charge capacity: 470A total

### SECTION 5: SYSTEM-LEVEL COORDINATION & POWER FLOW
**Pages**: 10-12
- Battery service selection (Lynx Smart BMS primary)
- DC/AC power measurements
- System operating state (State 252 = ESS grid-parallel)
- Multi-battery summary (3 sources synchronized)
- Load distribution (unequal 89/11 split)

**Key Findings**:
- All 3 battery sources: SOC 66.37% SYNCHRONIZED
- DC Bus voltage: 52.56V ±<1mV (perfect)
- System discharge: 22.9A total
- Grid power: -159.76W (exporting)

### SECTION 6: ENERGY FLOW PATHS & EFFICIENCY METRICS
**Pages**: 12-13
- MultiRS1 energy routing (7 paths documented)
- MultiRS2 energy routing (9 paths documented)
- Power flow comparison
- Efficiency analysis

**Key Findings**:
- MultiRS2 is primary power source (67.8x output difference)
- RS1 primarily charges from grid
- RS2 primarily discharges to load
- Energy routing: Asymmetric by design

### SECTION 7: PARALLEL INVERTER DIAGNOSTICS FOR AI
**Pages**: 13-15
- Synchronization metrics (voltage, frequency, phase, DC)
- Load sharing asymmetry analysis (3.8A imbalance)
- Health indicators (ripple, temperature, errors)
- Stress indicators (grid quality, discharge asymmetry)

**Key Findings**:
- Voltage ripple: 17.99mV (RS1) vs 32.99mV (RS2)
- No temperature sensors (risk area)
- Potential causes of load imbalance: 5 documented
- Battery discharge asymmetry: 11.6A difference

### SECTION 8: ADVANCED ESS (ENERGY STORAGE SYSTEM) FEATURES
**Pages**: 15-16
- DVCC Configuration (all parameters enabled)
- ESS Mode asymmetry (Mode 1 vs Mode 3)
- Grid code compliance (Code 16 = European standard)
- Sustain mode & offset parameters

**Key Findings**:
- DVCC fully enabled with BMS control
- Effective charge voltage: 54.4V
- ESS modes: By design for asymmetric operation
- All alarm levels: Set to 1 (monitored)

### SECTION 9: GRID-PARALLEL OPERATION DIAGNOSTICS
**Pages**: 16-18
- Grid connection status (grid-parallel mode active)
- Three-phase power flow (L1/L2/L3 detail)
- Grid meter energy accounting (forward/reverse)
- Load meter vs Grid meter reconciliation (11.4x difference explained)

**Key Findings**:
- Grid power factor: 0.093 (leading/capacitive)
- Net grid import: 1999.13kWh (historical)
- Load supplied: Battery + Solar + Grid (not just grid)
- Grid frequency: 50.04Hz (synchronized)

### SECTION 10: PERFORMANCE OPTIMIZATION OPPORTUNITIES
**Pages**: 18-20
- Load balancing recommendations (5 steps)
- Solar charging optimization (3 steps)
- BMS integration enhancement (3 steps)
- Multi-inverter synchronization (4 steps)
- Three-phase grid balance (4 steps)

**Key Findings**:
- Critical issue: Load imbalance 89/11
- Root causes identified and documented
- MPPT RS 450/200 offline - needs investigation
- VE.Can MPPT has highest productivity per watt

### SECTION 11: REAL-TIME OPERATIONAL STATE SUMMARY
**Pages**: 20-21
- Current system snapshot (night operation)
- Parallel system status
- Multi-inverter configuration
- BMS & battery management
- Grid interaction

**Key Findings**:
- Operating in inverter mode (battery to AC)
- Slight net export to grid (-159.76W)
- All devices healthy with Error Code 0
- System design: Asymmetric by configuration

### SECTION 12: API ENDPOINT REFERENCE FOR AI MONITORING
**Pages**: 21-22
- Critical paths for real-time monitoring
- Historical data paths for trending
- Complete endpoint listing with examples

**Endpoints Documented**: 30+ critical monitoring paths

---

## APPENDICES

### APPENDIX A: DEVICE ADDRESSING REFERENCE (Page 22)
| NAD | Device | Instance | Serial | Product |
|-----|--------|----------|--------|---------|
| 64 | Grid Meter | 0 | 0449643 | VM-3P75CT |
| 65 | MPPT RS 450/200 | 5 | 0431531 | SmartSolar |
| 66 | MultiRS2 | 2 | 0382989 | Multi RS |
| 67 | MultiRS1 | 1 | 0488085 | Multi RS |
| 68 | MultiRS PV | 0 | 0487020 | Multi RS PV |
| 36 | MPPT VE.Can 150/70 | 7 | 0283819 | SmartSolar |
| 41 | Lynx Smart BMS | 6 | 0317637 | BMS 500 |

### APPENDIX B: STATE CODE REFERENCE (Page 23)
- Inverter States: 252 (online operating)
- Battery States: 9 (online monitoring)
- Mode Values: 1-4 (charger/inverter/off)
- ESS Modes: 1 & 3 (asymmetric control)

### APPENDIX C: CRITICAL SYSTEM PARAMETERS (Pages 23-24)
- Must-monitor parameters (6 identified)
- Daily alert thresholds (5 triggers)
- Weekly health checks (4 items)

---

## CRITICAL FINDINGS FOR AI INTEGRATION

### System Strengths
1. **Synchronization**: Voltage/frequency perfect, voltage sync excellent
2. **Redundancy**: Triple battery service with auto-failover
3. **Capacity**: 10.2kW inverter, 600A discharge, 56.64kWh storage
4. **Grid Integration**: 3-phase grid-parallel with export capability
5. **Health**: All error codes zero, all alarms clear
6. **Efficiency**: 97.32% round-trip battery efficiency

### System Weaknesses
1. **Load Imbalance**: 89% on one inverter (should be 50/50)
2. **Temperature Monitoring**: No sensors on critical devices
3. **MPPT Offline**: MPPT RS 450/200 not producing (investigate)
4. **Phase Imbalance**: 1.43% (acceptable but improvable)
5. **Configuration Asymmetry**: ESS modes 1 & 3 create unequal load sharing
6. **Current Ripple**: MultiRS2 at 32.99mV (1.83x higher than RS1)

### Immediate Actions Recommended
1. **Investigate MPPT RS 450/200** - Check connections/configuration
2. **Equalize current limits** - Both inverters should have same limit
3. **Rebalance SOC thresholds** - Harmonize minimum SOC limits
4. **Monitor neutral current** - Trending for phase balance
5. **Add temperature sensors** - Critical for safe operation
6. **Adjust ESS modes** - Consider both as inverters if load support needed

---

## QUICK STAT SHEET

### System Hardware
- **Inverter Capacity**: 10,200W (5100W × 2)
- **Battery Capacity**: 56.64kWh (1180Ah @ 48V)
- **Solar Capacity**: ~27.4kW (11 trackers)
- **Max Discharge**: 600A (33C rate)
- **Max Charge**: 600A available (but limited to 470A by chargers)

### Current Operation (Night/Evening)
- **System Load**: 530.97W
- **Battery Discharge**: 22.9A (-614W)
- **Grid Power**: -159.76W (exporting)
- **SOC**: 66.37% (synchronized across 3 sources)
- **Time to Empty**: 51+ hours

### Performance Metrics
- **Voltage Synchronization**: 0.1V difference (EXCELLENT)
- **Frequency Synchronization**: 0.0Hz difference (PERFECT)
- **Load Sharing**: 89%/11% (IMBALANCED)
- **Phase Voltage Range**: 3.0V (1.34% - ACCEPTABLE)
- **Battery Efficiency**: 97.32% round-trip
- **Error Code Status**: ALL ZERO (HEALTHY)

### Grid Interaction
- **Mode**: Grid-parallel (can import or export)
- **Frequency Lock**: 50.04Hz (synchronized)
- **Net Direction**: Exporting (-159.76W)
- **Phase Factor**: 0.093 (leading/capacitive)
- **Grid Code**: European Standard 16

---

## MONITORING RECOMMENDATIONS FOR AI

### Real-Time (Every 5 seconds)
- SOC and voltage (detect rapid changes)
- Phase currents (load imbalance detection)
- Grid power (direction changes)
- Temperature (if sensors added)

### Hourly
- Energy totals (solar, battery, grid)
- Average efficiency metrics
- Phase balance trending
- Load distribution consistency

### Daily
- SOC curve profile
- Solar yield measurement
- Grid import/export totals
- Battery cycle count changes

### Weekly
- Historical trend analysis
- Error/alarm event review
- Device firmware status
- Predictive maintenance indicators

---

## API BASE ENDPOINT
```
http://192.168.88.189:8088
```

### Key Services
- `com.victronenergy.multi.socketcan_can0_vi1_uc488085` - MultiRS1
- `com.victronenergy.multi.socketcan_can0_vi2_uc382989` - MultiRS2
- `com.victronenergy.battery.socketcan_can0_vi6_uc317637` - Lynx BMS
- `com.victronenergy.grid.socketcan_can0_vi0_uc449643` - Grid Meter
- `com.victronenergy.acload.cg_BX18600620015` - Load Meter (Modbus TCP)
- `com.victronenergy.system` - System aggregation

---

## DOCUMENT LOCATION
```
/tmp/victron_einstein_research.md
```

**Access**: Full detailed documentation with every parameter, state code, voltage reading, and diagnostic metric captured during comprehensive API exploration of the Victron Einstein multi-device system.

