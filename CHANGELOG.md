# Changelog

All notable changes to the Victron DBus API project.

---

## [2.0.0] - 2025-10-23

### 🎉 Major Release: Diataxis Restructure

Complete documentation reorganization following Diataxis framework with persona-based structure.

### Added

**Foundation**:
- LICENSE (MIT + authorized use for El Niño and Victron Energy)
- PERSONAS.md (Mauk Muller AI developer + Victron Installer profiles)
- CONTRIBUTING.md (contribution guidelines)
- .github/FUNDING.yml (sponsorship support)
- .github/ISSUE_TEMPLATE/ (bug report, feature request, documentation templates)

**Documentation Structure** (60+ guides):
- `docs/ai-agent-developer/` - Complete workspace for AI developers
- `docs/installer/` - Complete workspace for installers
- `docs/shared/` - Common resources
- `docs/archive/` - Original research preserved

**AI Agent Developer Guides**:
- 4 Tutorials (first agent, battery health, fleet dashboard, predictive maintenance)
- 11 How-To Guides (anomaly detection, fleet monitoring, conversational patterns, optimization)
- 4 Concepts (why monitor, degradation science, grid quality, ESS optimization)
- 7 References (API paths, thresholds, query patterns, Python examples)

**Installer Guides**:
- 3 Tutorials (validate installation, troubleshoot remotely, compare before/after)
- 12 How-To Guides (troubleshooting, validation, conversational queries)
- 4 Concepts (parallel operation, ESS modes, DVCC, grid codes)
- 7 References (troubleshooting matrix, alarm codes, state codes, limits)

**Shared Resources**:
- API specification
- 2025 AI UX patterns
- Conversational AI guides

### Changed

- **README.md**: Complete rewrite with persona-based navigation
- **00_START_HERE.md**: Persona routing and quick access
- Ukraine banner moved to bottom of README

### Removed

- Helper/meta files (DOCS_RESTRUCTURE_PROPOSAL, README_OLD, status files)
- Example JSON outputs (device_ids.json, voltage_info.json)
- Monolithic files moved to `docs/archive/`

### Fixed

- All broken links (66 → 0)
- Inconsistent file structure
- Hard-to-navigate documentation

---

## [1.1.0] - 2025-10-23

### Added

**Research Documentation**:
- VICTRON_DBUS_DIAGNOSTIC_API_RESEARCH.md (47KB, 300+ DBus paths)
- victron_einstein_research.md (38KB, multi-device system analysis)
- IMPLEMENTATION_GUIDE_AI_AGENTS.md (20KB, 8-week deployment guide)
- QUICK_REFERENCE_DIAGNOSTIC_PATHS.json (14KB, machine-readable config)

**Discovery Scripts**:
- `discover_device_ids.py` - Device topology discovery
- `get_voltage_info.py` - Voltage monitoring (DC/AC)

**Systems Analyzed**:
- System 1 (192.168.88.77): Single inverter baseline
- System 2 "einstein" (192.168.88.189): Complex multi-device (2 inverters, 4 solar chargers)

---

## [1.0.0] - 2025-10-23

### 🎉 Initial Release

**Core Components**:
- `dbus_api_server.py` - Read-only HTTP API server for Venus OS
- Basic README with installation instructions

**Features**:
- Read-only DBus access via HTTP REST API
- JSON responses
- Health check endpoint
- Service enumeration
- Value queries by service and path

**API Endpoints**:
- GET / - API information
- GET /health - Health check
- GET /services - List DBus services
- GET /settings - All settings
- GET /value?service=X&path=Y - Query specific value
- GET /text?service=X&path=Y - Text representation

**Security**:
- Read-only by design
- No write operations
- HTTP 403 on POST requests

---

## Release Schedule

- **v2.1.0** (Planned Q1 2026): WebSocket support, batch queries
- **v2.2.0** (Planned Q2 2026): VRM ProxyRelay integration
- **v3.0.0** (Planned Q3 2026): AI agent templates, marketplace

---

**Made in Ukraine 🇺🇦 with love by EnergyCitizen**
