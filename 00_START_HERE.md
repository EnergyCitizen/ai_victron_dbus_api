# Victron Einstein System - Research Documentation Index

**Generated**: October 23, 2025
**System**: Victron Cerbo GX (192.168.88.189:8088)
**Total Documentation**: 2,494 lines across 4 files
**Total Size**: 71KB

---

## Quick Navigation

Start with one of these based on your needs:

### For Quick Overview (5 minutes)
**Read**: `/tmp/README.md` (12KB)
- Executive summary of key findings
- Current operational state with metrics
- Immediate action items
- Critical issues and strengths summary

### For Comprehensive Understanding (30 minutes)
**Read**: `/tmp/victron_einstein_index.md` (10KB)
- Section-by-section navigation guide
- Quick stat sheet
- All 6 system strengths listed
- All 6 system weaknesses identified

### For Operational Monitoring (Reference)
**Read**: `/tmp/victron_einstein_metrics.md` (11KB)
- Device identification table (NAD addressing)
- Real-time monitoring parameters
- Daily monitoring checklist
- Alert thresholds for AI automation
- API polling intervals

### For Deep Technical Dive (2+ hours)
**Read**: `/tmp/victron_einstein_research.md` (38KB)
- Full 12-section analysis + 3 appendices
- Every device parameter documented
- State codes and error codes
- Complete API endpoint reference
- Energy flow analysis
- Synchronization metrics

---

## Research Coverage Summary

### Devices Analyzed (20 Services, 15+ Instances)

#### Inverter Systems
- [x] MultiRS1 (Serial: 0488085) - 5,100W, 48V/100A, Mode 1 ESS
- [x] MultiRS2 (Serial: 0382989) - 5,100W, 48V/100A, Mode 3 ESS
- [x] Multi RS PV (Serial: 0487020) - AC-output only, PV inverter mode

#### Battery Management
- [x] Lynx Smart BMS 500 (Serial: 0317637) - 1180Ah, 48V, 56.64kWh
- [x] Multi-battery synchronization (3 sources)
- [x] Battery diagnostics (error history, alarms)

#### Solar Charging (11 Trackers)
- [x] MultiRS1 integrated (2 trackers, ~5.7kW)
- [x] MultiRS2 integrated (2 trackers, ~8.3kW)
- [x] SmartSolar MPPT RS 450/200 (4 trackers, HIGH-V)
- [x] SmartSolar MPPT VE.Can 150/70 (1 tracker, ~4.4kW)

#### Energy Metering
- [x] VM-3P75CT Grid Meter (3-phase VE.Can)
- [x] Carlo Gavazzi EM24 (3-phase Modbus TCP)
- [x] Per-phase power analysis
- [x] Forward/reverse energy accounting

#### System Control
- [x] Cerbo GX system aggregation
- [x] DVCC (Distributed Voltage/Current Control)
- [x] AC System coordination (2 instances)
- [x] VE.Can network status

---

## Key Findings at a Glance

### System Strengths
1. **Synchronization**: Voltage 0.1V (0.044%), Frequency 0.0Hz - EXCELLENT
2. **Efficiency**: 97.32% battery round-trip - TOP TIER
3. **Redundancy**: 3 battery services with auto-failover
4. **Capacity**: 10.2kW inverter, 600A discharge, 56.64kWh storage
5. **Health**: All error codes 0, all alarms clear
6. **Integration**: 3-phase grid-parallel with active export

### Critical Issues (Must Address)
1. **Load Imbalance**: 89% MultiRS2 / 11% MultiRS1 (should be 50/50)
2. **No Temperature Sensors**: Risk of thermal runaway
3. **MPPT RS 450/200 Offline**: 0W output (was producing 6140kWh)
4. **Configuration Asymmetry**: ESS modes 1 & 3 create unequal operation
5. **Phase Imbalance**: 1.43% grid (improvable)

### Current State (Night/Evening)
- SOC: 66.37% (stable, synchronized across 3 sources)
- Battery Voltage: 52.55V (healthy)
- System Discharge: 22.9A (-614W)
- Grid Power: -159.76W (EXPORTING)
- System Load: 530.97W
- Time to Empty: 51+ hours
- Frequency: 50.04Hz (grid-locked)

---

## Critical Metrics to Monitor

### Real-Time (Every 5 seconds)
```
/battery.../Soc                    → Currently 66.37%
/battery.../Dc/0/Voltage           → Currently 52.55V
/multi.../Ac/Out/L3/P              → RS1: -46W, RS2: +413W
/grid.../Ac/Power                  → Currently -33.92W (export)
/system.../Ac/ActiveIn/L3/Power    → Monitor frequency lock
```

### Warning Thresholds
- SOC < 40% (currently 66.37% - safe)
- Voltage < 41.6V or > 54.5V
- Load imbalance > 60% (currently 89% - FLAGGED)
- Phase voltage > 10V spread (currently 3.0V - acceptable)
- Neutral current > 2A (currently -1.2A - acceptable)
- Any error code ≠ 0 or alarm = 1

### Daily Metrics
- Solar yield (Day 1: 30.32kWh)
- Battery cycles (currently 152)
- Grid import/export (net: 1999.13kWh imported)
- Load distribution (currently 89/11 asymmetric)

---

## Immediate Action Items (Priority Order)

### CRITICAL - Do First
1. **Investigate MPPT RS 450/200**
   - Status: Offline (0W)
   - Historical: 6140.53kWh (was working)
   - Action: Check connections, panel strings, communication

### HIGH - Within Week
2. **Rebalance Inverter Load Sharing**
   - Issue: 89% on RS2, 11% on RS1
   - Root: Mode 1 vs Mode 3, current limit difference
   - Solution: Both Mode 3, equalize current limits to 45A

3. **Add Temperature Monitoring**
   - Current: NO sensors on any device
   - Risk: No thermal protection
   - Solution: NTC thermistors on inverters + BMS

### MEDIUM - Within Month
4. **Harmonize Battery Thresholds**
   - RS1: 65% min SOC
   - RS2: 5% min SOC
   - Target: Both at 55-60%

5. **Improve Phase Balance**
   - Neutral current: -1.2A
   - Phase voltage spread: 3.0V
   - Action: Redistribute L1/L2 loads (all currently on L3)

---

## File Guide

| File | Size | Lines | Purpose | Read Time |
|------|------|-------|---------|-----------|
| **README.md** | 12KB | 391 | Executive summary, current state, actions | 5 min |
| **victron_einstein_index.md** | 10KB | 328 | Quick reference, section summary, stats | 10 min |
| **victron_einstein_metrics.md** | 11KB | 432 | Operational monitoring, thresholds, alerts | 15 min |
| **victron_einstein_research.md** | 38KB | 1,391 | Complete technical documentation | 60+ min |

### Total Research Package
- **4 Files** with complementary information
- **2,494 Lines** of detailed analysis
- **71KB** of documentation
- **100+ API Endpoints** documented
- **20 Services** analyzed
- **15+ Device Instances** detailed

---

## API Endpoint Reference

### Base URL
```
http://192.168.88.189:8088/
```

### Critical Monitoring Endpoints

**Battery/BMS**:
```
GET /value?service=com.victronenergy.battery.socketcan_can0_vi6_uc317637&path=/Soc
GET /value?service=com.victronenergy.battery.socketcan_can0_vi6_uc317637&path=/Dc/0/Voltage
GET /value?service=com.victronenergy.battery.socketcan_can0_vi6_uc317637&path=/Dc/0/Current
```

**Inverters**:
```
GET /value?service=com.victronenergy.multi.socketcan_can0_vi1_uc488085&path=/Ac/Out/L3/P
GET /value?service=com.victronenergy.multi.socketcan_can0_vi2_uc382989&path=/Ac/Out/L3/P
GET /value?service=com.victronenergy.multi.socketcan_can0_vi1_uc488085&path=/Ess/Mode
GET /value?service=com.victronenergy.multi.socketcan_can0_vi2_uc382989&path=/Ess/Mode
```

**Grid**:
```
GET /value?service=com.victronenergy.grid.socketcan_can0_vi0_uc449643&path=/Ac/Power
GET /value?service=com.victronenergy.grid.socketcan_can0_vi0_uc449643&path=/Ac/Frequency
```

**Load**:
```
GET /value?service=com.victronenergy.acload.cg_BX18600620015&path=/Ac/Power
```

**System**:
```
GET /value?service=com.victronenergy.system&path=/Batteries
GET /value?service=com.victronenergy.system&path=/Ac/ActiveIn
GET /value?service=com.victronenergy.system&path=/Dc/Battery
```

---

## Research Methodology

### Data Collection Method
- Direct HTTP API queries to Cerbo GX
- GET requests to `/value` endpoint
- Service-specific path navigation
- Real-time operational snapshot

### Coverage
- All 20 discovered services queried
- 100+ individual data paths explored
- Device hierarchy fully mapped
- State and mode values documented
- Error and alarm conditions tracked
- Historical data captured
- Energy flow paths analyzed

### Analysis Depth
- Parallel inverter synchronization: DETAILED
- BMS integration: COMPREHENSIVE
- Solar system architecture: FULL
- Grid coordination: THREE-PHASE ANALYSIS
- Battery redundancy: FAILOVER DOCUMENTED
- Energy routing: ALL PATHS MAPPED
- Configuration: EVERY SETTING CAPTURED

---

## System Architecture at a Glance

```
GRID (50.04Hz, 3-phase)
  ↓ ↑
  ├─ VM-3P75CT Grid Meter (VE.Can)
  └─ Carlo Gavazzi Load Meter (Modbus TCP)
      ↓ ↑
      ├─ MultiRS1 (5.1kW inverter, Mode 1 ESS)
      │   ├─ 2x Solar trackers (~5.7kW)
      │   └─ Energy meter feedback
      │
      └─ MultiRS2 (5.1kW inverter, Mode 3 ESS)
          └─ 2x Solar trackers (~8.3kW)

SOLAR INPUTS (11 Trackers, ~27.4kW)
  ├─ MultiRS1 integrated (2 tracks)
  ├─ MultiRS2 integrated (2 tracks)
  ├─ MPPT VE.Can 150/70 (1 track) - PRODUCING
  ├─ MPPT RS 450/200 (4 tracks) - OFFLINE
  └─ Multi RS PV (2 tracks) - AC OUTPUT ONLY

BATTERY BUS (48V, ~57kWh)
  ├─ Lynx Smart BMS 500 (PRIMARY) - 1180Ah
  ├─ MultiRS1 (FALLBACK)
  └─ MultiRS2 (FALLBACK)

CERBO GX CONTROLLER (System Aggregation)
  Serial: c0619ab4e0e9
  Firmware: v3.70~22 Build 222721
  System Type: AC System (grid-parallel ESS)
```

---

## Next Steps for Implementation

### For AI Diagnostics Setup
1. Implement 5-second polling to 6 critical endpoints
2. Set up alert triggers for WARNING and CRITICAL thresholds
3. Collect 24-hour baseline data for trending
4. Implement daily energy accounting
5. Enable predictive maintenance based on battery cycle count

### For System Optimization
1. Fix inverter load balancing (week 1)
2. Investigate MPPT RS offline status (week 1)
3. Add temperature sensors (week 2)
4. Rebalance battery thresholds (week 2)
5. Improve grid phase distribution (week 3)

### For Production Monitoring
1. Dashboard with real-time metrics
2. Trending graphs for efficiency
3. Alert notifications for anomalies
4. Daily report generation
5. Historical analysis for optimization

---

## Contact Information

- **System**: Victron Cerbo GX (c0619ab4e0e9)
- **Firmware**: v3.70~22 Build 222721
- **API Endpoint**: 192.168.88.189:8088
- **Research Date**: October 23, 2025
- **Status**: COMPLETE & READY FOR IMPLEMENTATION

---

## Conclusion

This comprehensive research package provides complete documentation for AI-driven diagnostics and optimization of the Victron Einstein multi-device system. The system is mature, well-coordinated, and ready for advanced monitoring and predictive maintenance integration.

**Start with `/tmp/README.md` for a 5-minute overview, or jump to the full research document for deep technical details.**

