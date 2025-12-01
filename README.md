# Victron DBus API for AI Agents

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![Victron](https://img.shields.io/badge/Victron-Venus%20OS-orange)](https://github.com/victronenergy/venus)
[![Version](https://img.shields.io/badge/Version-3.0.0-green)](https://github.com/EnergyCitizen/ai_victron_dbus_api/releases)
[![Contributors](https://img.shields.io/github/contributors/EnergyCitizen/ai_victron_dbus_api)](https://github.com/EnergyCitizen/ai_victron_dbus_api/graphs/contributors)
[![Stars](https://img.shields.io/github/stars/EnergyCitizen/ai_victron_dbus_api?style=social)](https://github.com/EnergyCitizen/ai_victron_dbus_api/stargazers)

> **Read-Write HTTP REST API** for Victron Venus OS devices with **AI safety controls**. Enables AI agents to monitor AND control solar/battery systems with user-controlled write permissions.

---

## What's New in v3.0.0

| Feature | Description |
|---------|-------------|
| **Read-Write Mode** | AI agents can now write values to DBus (not just read) |
| **AI Safety Switch** | Write operations require `AI_write` virtual switch to be ON |
| **Server Management** | Remote restart/stop via API endpoints |
| **Health Monitoring** | Uptime tracking with `started_at` timestamp |
| **Config Storage** | Persistent agent configuration at `/data/ai_agent/config.json` |
| **NodeRED Flow** | Pre-built safety switch flow included |

---

## Safety-First Architecture

**All write operations require explicit user permission via the AI_write switch.**

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  AI Agent   │────▶│  DBus API Server │────▶│  Venus OS DBus  │
└─────────────┘     └────────┬─────────┘     └─────────────────┘
                             │
                    ┌────────▼─────────┐
                    │  AI_write Switch │
                    │  (NodeRED)       │
                    │  ┌───┐           │
                    │  │OFF│ = Blocked │
                    │  │ ON│ = Allowed │
                    │  └───┘           │
                    └──────────────────┘
```

**User maintains full control:**
- Toggle OFF → instantly blocks all AI write operations
- Toggle ON → allows AI to make approved changes
- Automate via NodeRED (time-based, presence-based, etc.)

See [AGENTS.md](AGENTS.md) for AI agent safety guidelines.

---

## Quick Start

### 1. Prerequisites

- **Venus OS Large** image (includes NodeRED)
- **NodeRED enabled** in Settings > Services
- SSH access to Venus device

### 2. Deploy API Server

```bash
# Copy server to Venus OS device
scp dbus_api_server.py root@<DEVICE_IP>:/data/

# SSH into device
ssh root@<DEVICE_IP>

# Start server
python3 /data/dbus_api_server.py &

# Verify
curl http://<DEVICE_IP>:8088/health
```

### 3. Import Safety Switch (NodeRED)

1. Open NodeRED: `http://<DEVICE_IP>:1880`
2. Menu → Import → Clipboard
3. Paste contents of [`nodered/safety_switch.json`](nodered/safety_switch.json)
4. Deploy

### 4. Test API

```bash
# Check server info
curl http://<DEVICE_IP>:8088/

# Check AI write status
curl http://<DEVICE_IP>:8088/ai-write-status

# Read battery SOC
curl "http://<DEVICE_IP>:8088/value?service=com.victronenergy.system&path=/Dc/Battery/Soc"

# Write value (requires AI_write switch ON)
curl -X POST http://<DEVICE_IP>:8088/value \
  -H "Content-Type: application/json" \
  -d '{"service": "com.victronenergy.settings", "path": "/Settings/Alarm/Audible", "value": 1}'
```

---

## API Reference

### Read Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | API info, version, AI write status |
| `GET /health` | Health check with uptime (`started_at`, `uptime_seconds`) |
| `GET /services` | List all Victron DBus services |
| `GET /settings` | All system settings (300+ values) |
| `GET /value?service=X&path=Y` | Get specific DBus value |
| `GET /text?service=X&path=Y` | Get text representation |
| `GET /ai-write-status` | Detailed AI write switch diagnostics |
| `GET /config` | Get stored agent configuration |

### Write Endpoints

| Endpoint | Description | Requires |
|----------|-------------|----------|
| `POST /value` | Set DBus value | AI_write switch ON |
| `POST /config` | Save agent configuration | - |
| `POST /restart` | Restart API server | `{"confirm": true}` |
| `POST /stop` | Stop API server | `{"confirm": true}` |

### Example Responses

<details>
<summary><code>GET /</code> - API Info</summary>

```json
{
  "name": "Victron DBus API Server",
  "version": "3.0.0",
  "mode": "read-write",
  "ai_write_enabled": true,
  "ai_write_status": "AI_write is enabled",
  "endpoints": {
    "GET /": "API information",
    "GET /health": "Health check",
    "GET /services": "List all Victron dbus services",
    "GET /value?service=X&path=Y": "Get value from specific dbus path",
    "POST /value": "Set value (requires AI_write switch ON)",
    "POST /restart": "Restart API server",
    "POST /stop": "Stop API server"
  }
}
```
</details>

<details>
<summary><code>GET /health</code> - Health with Uptime</summary>

```json
{
  "status": "healthy",
  "started_at": "2025-12-01T11:01:22.186090",
  "uptime_seconds": 3600,
  "success": true
}
```
</details>

<details>
<summary><code>GET /ai-write-status</code> - Detailed Diagnostics</summary>

```json
{
  "enabled": true,
  "message": "AI_write is enabled",
  "switch_service": "com.victronenergy.switch.virtual_6a7aeab51e5dd6e9",
  "details": {
    "venus_image_type": "Large",
    "nodered_enabled": true,
    "nodered_running": true,
    "switch_found": true,
    "switch_state": 256
  },
  "faq": {
    "venus_large": "Venus OS Large includes NodeRED...",
    "enable_nodered": "Enable NodeRED in Remote Console > Settings > Services",
    "create_switch": "In NodeRED, add victron-virtual-switch with CustomName 'AI_write'",
    "toggle_switch": "Control via VRM dashboard, Remote Console, or NodeRED"
  },
  "success": true
}
```
</details>

<details>
<summary><code>POST /value</code> - Write Value</summary>

**Request:**
```json
{
  "service": "com.victronenergy.settings",
  "path": "/Settings/Alarm/Audible",
  "value": 1
}
```

**Response (success):**
```json
{
  "service": "com.victronenergy.settings",
  "path": "/Settings/Alarm/Audible",
  "value": 1,
  "previous_value": 0,
  "success": true
}
```

**Response (blocked):**
```json
{
  "error": "AI write is disabled",
  "message": "AI_write switch is OFF. Enable it in NodeRED or VRM.",
  "success": false
}
```
</details>

---

## Common Services

| Service | Description |
|---------|-------------|
| `com.victronenergy.system` | System aggregates (SOC, power flows) |
| `com.victronenergy.battery.*` | Battery monitor (BMS data) |
| `com.victronenergy.vebus.*` | Multi/Quattro inverter/charger |
| `com.victronenergy.solarcharger.*` | MPPT solar controllers |
| `com.victronenergy.settings` | System configuration |
| `com.victronenergy.switch.virtual_*` | Virtual switches (NodeRED) |

---

## AI Agent Integration

### Conversational Example

```
User: "What's the battery level?"

Agent: [Calls GET /value?service=com.victronenergy.system&path=/Dc/Battery/Soc]

Agent: "Battery is at 73%, discharging at 8A. About 5 hours remaining."
```

### Write with Safety Check

```python
import requests

BASE_URL = "http://192.168.88.189:8088"

# 1. Check if writes are allowed
status = requests.get(f"{BASE_URL}/ai-write-status").json()
if not status["enabled"]:
    print(f"Cannot write: {status['message']}")
    exit(1)

# 2. Perform write operation
response = requests.post(f"{BASE_URL}/value", json={
    "service": "com.victronenergy.settings",
    "path": "/Settings/Alarm/Audible",
    "value": 1
})

if response.json()["success"]:
    print("Value updated successfully")
```

---

## Repository Structure

```
ai_victron_dbus_api/
├── dbus_api_server.py          # Main API server (v3.0.0)
├── nodered/
│   └── safety_switch.json      # AI_write switch flow (import to NodeRED)
├── docs/
│   ├── ai-agent-developer/     # Build AI monitoring agents
│   └── installer/              # Troubleshoot & validate systems
├── AGENTS.md                   # AI agent safety guidelines
├── CLAUDE.md                   # Claude Code safety instructions
├── CONTRIBUTING.md             # Contribution guidelines
└── README.md                   # This file
```

---

## Documentation

### By Persona

| Persona | Start Here | Focus |
|---------|------------|-------|
| **AI Agent Developer** | [docs/ai-agent-developer/](docs/ai-agent-developer/) | Build conversational monitoring agents |
| **Victron Installer** | [docs/installer/](docs/installer/) | Troubleshoot & validate systems |

### Quick Links

**Tutorials:**
- [First Monitoring Agent](docs/ai-agent-developer/tutorials/01-first-monitoring-agent.md) (30 min)
- [Validate New Installation](docs/installer/tutorials/01-validate-new-installation.md) (20 min)

**How-To Guides:**
- [Detect Battery Degradation](docs/ai-agent-developer/how-to-guides/anomaly-detection/detect-battery-degradation.md)
- [Battery Not Charging](docs/installer/how-to-guides/troubleshooting/battery-not-charging.md)

**Reference:**
- [Critical API Paths](docs/ai-agent-developer/reference/api/critical-paths.md)
- [Troubleshooting Matrix](docs/installer/reference/troubleshooting-matrix.md)

---

## Server Management

### Remote Restart

```bash
curl -X POST http://<DEVICE_IP>:8088/restart \
  -H "Content-Type: application/json" \
  -d '{"confirm": true}'
```

### Remote Stop

```bash
curl -X POST http://<DEVICE_IP>:8088/stop \
  -H "Content-Type: application/json" \
  -d '{"confirm": true}'
```

### Check Uptime

```bash
curl http://<DEVICE_IP>:8088/health
# Returns started_at timestamp and uptime_seconds
```

### Safe Process Management

```bash
# Stop ONLY the API server (safe)
pkill -f dbus_api_server.py

# NEVER run this on Venus OS:
# killall python3  # DANGEROUS - kills critical system services!
```

See [CLAUDE.md](CLAUDE.md) for critical safety rules.

---

## Troubleshooting

### AI Write Not Working

| Issue | Solution |
|-------|----------|
| "Venus OS Normal image" | Install Venus OS Large (includes NodeRED) |
| "NodeRED is disabled" | Enable in Remote Console > Settings > Services |
| "NodeRED is not running" | Wait ~60s after boot for NodeRED to start |
| "AI_write switch not found" | Import `nodered/safety_switch.json` to NodeRED |
| "AI_write switch is OFF" | Toggle switch ON in VRM or NodeRED |

### Server Issues

| Issue | Solution |
|-------|----------|
| Port 8088 in use | `pkill -f dbus_api_server.py` then restart |
| Server not responding | Check with `curl http://<IP>:8088/health` |
| Connection refused | Verify server is running: `ps \| grep dbus_api_server` |

---

## Contributing

We welcome contributions from:
- AI agent developers building on Victron platform
- Victron installers with field experience
- Venus OS developers

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

**MIT License** - See [LICENSE](LICENSE)

**Authorized Use**: Explicitly permitted for:
- Victron AI ecosystem partners
- Victron Energy (Venus OS platform provider)

---

## Resources

- **Repository**: [github.com/EnergyCitizen/ai_victron_dbus_api](https://github.com/EnergyCitizen/ai_victron_dbus_api)
- **Issues**: [GitHub Issues](https://github.com/EnergyCitizen/ai_victron_dbus_api/issues)
- **Victron Community**: [community.victronenergy.com](https://community.victronenergy.com)

---

<div align="center">

[![](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner2-direct.svg)](https://github.com/vshymanskyy/StandWithUkraine/blob/main/docs/README.md)

**Made in Ukraine with love by [EnergyCitizen](https://github.com/EnergyCitizen)**

**Version**: 3.0.0 | **Last Updated**: 2025-12-01

</div>
