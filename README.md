# Victron DBus API Research & Implementation Documentation

Complete research and implementation guides for AI agents monitoring Victron VRM stations via the DBus HTTP API.

## Overview

This repository contains comprehensive documentation for integrating Victron DBus API diagnostics into AI agent monitoring systems. Research was conducted on a live Cerbo GX device running firmware v3.70~33.

**API Endpoint:** `http://192.168.88.77:8088`

## Documents Included

### 1. VICTRON_DBUS_DIAGNOSTIC_API_RESEARCH.md
**Comprehensive 20-section reference guide**

- Complete DBus API specification with 300+ diagnostic paths
- Real API responses and actual values from live system
- Organized by diagnostic category (battery, grid, inverter, etc.)
- Anomaly detection thresholds and guidelines
- Performance metrics and efficiency calculations
- CAN-bus and infrastructure diagnostics

**Key Sections:**
- System Health & Status Values
- Battery & Energy Storage (including cell-level monitoring)
- Inverter/Charger Status (VEBus Multi-Plus)
- Grid & Consumption Metrics (3-phase metering)
- ESS & Dynamic Charging Control
- Temperature & Sensor Monitoring
- Platform Diagnostics & Firmware Tracking
- Alarm History & Notifications
- Multi-station Monitoring Strategy

**Use When:** You need detailed technical reference for any diagnostic value or API path

---

### 2. QUICK_REFERENCE_DIAGNOSTIC_PATHS.json
**Machine-readable diagnostic path configuration**

- 50+ critical monitoring paths with metadata
- Organized by priority and function
- Polling intervals and thresholds pre-configured
- Anomaly detection rules in JSON format
- Batch query patterns for efficiency
- Ready for programmatic use

**Data Structure:**
```
Critical paths (battery SOC, grid lost, alarms)
Health monitoring (temperature, SOH, cell balancing)
Grid quality metrics
Consumption monitoring
System health checks
ESS control state
Batch query patterns
Anomaly detection rules
```

**Use When:** Building monitoring software, want structured data format, need polling intervals

---

### 3. IMPLEMENTATION_GUIDE_AI_AGENTS.md
**Phased implementation roadmap (8 weeks)**

- Phase 1: Basic Real-Time Monitoring (Week 1-2)
- Phase 2: Battery Health & Diagnostics (Week 3-4)
- Phase 3: Grid & ESS Optimization (Week 5-6)
- Phase 4: Predictive Maintenance (Week 7-8)

**Includes:**
- Python code examples for each phase
- Database selection guidance (InfluxDB, Prometheus, SQLite)
- Alerting engine implementation
- Performance optimization tips
- Deployment checklist
- Testing & validation examples
- Troubleshooting guide

**Use When:** Planning implementation, need code samples, want best practices

---

## Quick Start

### For Monitoring Implementation
1. Read: IMPLEMENTATION_GUIDE_AI_AGENTS.md (Phase 1)
2. Reference: QUICK_REFERENCE_DIAGNOSTIC_PATHS.json
3. Look up details: VICTRON_DBUS_DIAGNOSTIC_API_RESEARCH.md

### For Technical Understanding
1. Read: VICTRON_DBUS_DIAGNOSTIC_API_RESEARCH.md sections 1-6
2. Review: Anomaly detection guide (Section 13)
3. Understand: Multi-station architecture (Section 15)

### For Software Architecture
1. Review: Data pipeline in IMPLEMENTATION_GUIDE_AI_AGENTS.md
2. Parse: QUICK_REFERENCE_DIAGNOSTIC_PATHS.json
3. Implement: Phase 1 code examples

---

## Key Findings Summary

### API Capabilities
- **20 DBus Services** providing specialized functions
- **300+ Diagnostic Paths** covering all system aspects
- **Real-time Capable** - poll critical metrics every 5-10 seconds
- **Batch Efficient** - 150+ values returned in single request
- **Complete Alarms** - all device errors logged with timestamps

### Diagnostic Coverage

#### Battery Management (Most Critical)
- Real-time: SOC, voltage, current, power, temperature
- Health: SOH degradation tracking, cell voltage monitoring
- Alarms: 15+ specific battery failure modes
- Limits: BMS-imposed operational constraints

#### Grid & Inverter
- 3-phase voltage/current/power monitoring
- Frequency tracking for grid stability
- Grid lost detection
- Energy flow accounting (import/export/storage)

#### System Health
- Firmware version tracking across fleet
- Network connectivity (WiFi signal, VRM portal)
- CAN-bus error statistics
- Disk storage and filesystem health

#### Energy Control
- ESS state machine status
- Dynamic charging scheduler
- Power setpoints and limits
- Hub4 grid-tied mode

### Anomaly Detection Ready
- 15+ critical alert conditions identified
- 20+ warning thresholds documented
- Performance degradation indicators provided
- Failure risk scoring methodology included

---

## System Under Test

**Device:** Victron Cerbo GX (HQ2308C9WMH)
**Firmware:** v3.70~33 (Build: 20250909064940)

**Components:**
- Inverter/Charger: MultiPlus-II 48/3000/35-32 (VEBus)
- Battery: Pylontech 8kWh (CAN-bus BMS)
- Grid Meter: Carlo Gavazzi EM24 Ethernet (3-phase)
- Temperature Sensors: 2x ADC analog inputs
- Configuration: ESS mode with Hub4 grid-tied

**Network:** WiFi connected to VRM portal

---

## Implementation Examples

### Minimal Viable Collector (5 minutes to implement)
```python
import requests

def collect_victron_data(base_url):
    services = [
        "com.victronenergy.system",
        "com.victronenergy.vebus.ttyS4",
        "com.victronenergy.battery.socketcan_can0"
    ]
    
    data = {}
    for service in services:
        url = f"{base_url}/value?service={service}&path=/"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data[service] = resp.json().get("value", {})
    
    return data
```

### Critical Alerts (Extract essential metrics)
```python
def check_alerts(data):
    sys = data.get("com.victronenergy.system", {})
    vebus = data.get("com.victronenergy.vebus.ttyS4", {})
    
    if sys.get("Dc/Battery/Soc", 100) < 10:
        print("CRITICAL: Battery SOC below 10%")
    
    if vebus.get("Alarms/GridLost") == 1:
        print("CRITICAL: Grid lost - UPS mode active")
    
    if vebus.get("Alarms/BmsConnectionLost") == 1:
        print("CRITICAL: Battery management system offline")
```

See IMPLEMENTATION_GUIDE_AI_AGENTS.md for complete examples.

---

## Performance Characteristics

### Response Times
- Single service query (all paths): ~50-100ms
- All 5 core services: ~300-400ms
- Network transfer: <50KB per full collection
- CPU overhead: Minimal (simple HTTP requests)

### Storage Requirements (per station per year)
- InfluxDB: ~35-40MB
- Prometheus: ~50-60MB
- SQLite: ~100-150MB

### Polling Intervals Recommended
- Critical metrics (SOC, alarms): 10 seconds
- Extended metrics (temp, health): 60 seconds
- System health (firmware, network): 5 minutes
- Logs & statistics: 5-10 minutes

---

## Real Data Examples

### Current System State (Live Reading)
```
Battery:        SOC=81%, V=49.8V, I=-0.9A (discharging), T=30.7C
Grid:           Power=167W import, Freq=50.1Hz, Connected=Yes
Inverter:       Mode=Passthrough, Load=148W, Output=225V
System:         Firmware=v3.70~33, Uptime=77d, Connected=Yes
Status:         All systems nominal, ESS active, Grid stable
```

### Anomaly Examples in History
```
Grid Lost (2x):      Detected at inverter (event logged)
CAN Errors:          649 errors on VE.CAN (intermittent issues)
Cell Imbalance:      Max-Min voltage 0.005V (healthy)
Temperature:         Inlet 35.8C, Boiler top 64.8C (thermal system OK)
```

---

## Implementation Path

**Recommended Progression:**

1. **Day 1-2:** Set up data collection (Phase 1)
   - Extract critical metrics
   - Store in time-series DB
   - Verify data accuracy vs VRM

2. **Day 3-5:** Configure alerting
   - Implement critical alert rules
   - Test notification delivery
   - Document thresholds per site

3. **Day 6-10:** Add diagnostics (Phase 2)
   - Battery health trending
   - Cell monitoring
   - Degradation detection

4. **Day 11-20:** Deploy optimization (Phase 3)
   - ESS control integration
   - Grid stress detection
   - Scheduled charging

5. **Week 4+:** Predictive maintenance (Phase 4)
   - Risk scoring
   - Failure prediction
   - Maintenance scheduling

---

## Integration Points

### Data Source
- Victron DBus API (read-only)
- All queried values are diagnostic/informational
- No configuration changes needed

### Output Options
- Time-series database (recommended)
- MQTT publishing
- RESTful API
- Grafana dashboards
- Email/SMS alerting

### External Systems
- VRM Portal (for comparison/validation)
- Weather forecasts (for ESS optimization)
- Maintenance tracking systems
- Energy cost data (for optimization)

---

## Support & References

### Victron Resources
- Venus OS Documentation
- VRM Portal
- Community Forum
- DBus specification (on-device)

### Files
- `VICTRON_DBUS_DIAGNOSTIC_API_RESEARCH.md` - Complete reference
- `QUICK_REFERENCE_DIAGNOSTIC_PATHS.json` - Configuration data
- `IMPLEMENTATION_GUIDE_AI_AGENTS.md` - How-to guide
- `README.md` - This file

---

## Document Versions

| Document | Version | Date | Status |
|----------|---------|------|--------|
| Research Guide | 1.0 | 2025-10-23 | Final |
| Quick Reference | 1.0 | 2025-10-23 | Final |
| Implementation Guide | 1.0 | 2025-10-23 | Final |
| README | 1.0 | 2025-10-23 | Final |

---

## Next Steps

1. Review IMPLEMENTATION_GUIDE_AI_AGENTS.md Phase 1 (20 min read)
2. Deploy minimal collector code (1-2 hours)
3. Configure database and alerting (2-4 hours)
4. Test with your system(s) and validate data
5. Plan phases 2-4 based on your requirements

---

## Notes

- All data is from live Cerbo GX system
- No simulation or theoretical values
- Real response times and payload sizes measured
- Thresholds based on Victron specifications
- Implementation code is production-ready pattern (not production code)

**Created:** 2025-10-23  
**Target Audience:** Software engineers implementing Victron monitoring  
**Scope:** Single device monitoring and multi-station fleet management  
**Status:** Ready for implementation
