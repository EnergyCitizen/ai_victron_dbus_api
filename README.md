# Victron DBus API for AI Agents

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![Victron](https://img.shields.io/badge/Victron-Venus%20OS-orange)](https://github.com/victronenergy/venus)
[![Version](https://img.shields.io/badge/Version-3.1.0-green)](https://github.com/EnergyCitizen/ai_victron_dbus_api/releases)
[![Contributors](https://img.shields.io/github/contributors/EnergyCitizen/ai_victron_dbus_api)](https://github.com/EnergyCitizen/ai_victron_dbus_api/graphs/contributors)
[![Stars](https://img.shields.io/github/stars/EnergyCitizen/ai_victron_dbus_api?style=social)](https://github.com/EnergyCitizen/ai_victron_dbus_api/stargazers)

> **Read-Write HTTP REST API** for Victron Venus OS devices with **AI safety controls**. Enables AI agents to monitor AND control solar/battery systems with user-controlled write permissions.

---

## What's New in v3.1.0

| Feature | Description |
|---------|-------------|
| **Two-Server Architecture** | Separate servers for DBus operations (8088) and management (8089) |
| **Daemontools Integration** | Proper Venus OS service management with auto-restart |
| **Control Server** | Remote start/stop/restart/upgrade via dedicated API |
| **Install Script** | One-command deployment with `install.sh` |
| **Firmware Persistence** | Services survive Venus OS firmware updates |

### v3.0.0 Features (included)

| Feature | Description |
|---------|-------------|
| **Read-Write Mode** | AI agents can write values to DBus (not just read) |
| **AI Safety Switch** | Write operations require `AI_write` virtual switch to be ON |
| **Health Monitoring** | Uptime tracking with `started_at` timestamp |
| **NodeRED Flow** | Pre-built safety switch flow included |

---

## Architecture

```
┌─────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│  AI Agent   │────▶│  Main API Server     │────▶│  Venus OS DBus  │
│             │     │  Port 8088           │     └─────────────────┘
└─────────────┘     │  - Read/Write DBus   │
                    │  - AI_write safety   │
                    └──────────┬───────────┘
                               │
┌─────────────┐     ┌──────────▼───────────┐     ┌─────────────────┐
│  Admin/Dev  │────▶│  Control Server      │────▶│  daemontools    │
│             │     │  Port 8089           │     │  svc commands   │
└─────────────┘     │  - Start/Stop/Restart│     └─────────────────┘
                    │  - Upgrade (git pull)│
                    │  - View logs         │
                    └──────────────────────┘

                    ┌──────────────────────┐
                    │  AI_write Switch     │
                    │  (NodeRED Virtual)   │
                    │  ┌───┐               │
                    │  │OFF│ = Writes blocked
                    │  │ ON│ = Writes allowed
                    │  └───┘               │
                    └──────────────────────┘
```

---

## Quick Start

### 1. Prerequisites

- **Venus OS Large** image (includes NodeRED)
- **NodeRED enabled** in Settings > Services
- SSH access to Venus device

### 2. Install (One Command)

```bash
# Clone repository to Venus device
ssh root@<DEVICE_IP>
cd /data
git clone https://github.com/EnergyCitizen/ai_victron_dbus_api.git dbus-api-repo
cd dbus-api-repo

# Run installer
./install.sh
```

Or manually copy files:

```bash
# From your workstation
scp -r . root@<DEVICE_IP>:/data/dbus-api-repo/
ssh root@<DEVICE_IP> "cd /data/dbus-api-repo && ./install.sh"
```

### 3. Import Safety Switch (NodeRED)

1. Open NodeRED: `http://<DEVICE_IP>:1880`
2. Menu → Import → Clipboard
3. Paste contents of [`nodered/safety_switch.json`](nodered/safety_switch.json)
4. Deploy

### 4. Test API

```bash
# Main server health
curl http://<DEVICE_IP>:8088/health

# Control server health
curl http://<DEVICE_IP>:8089/health

# Check AI write status
curl http://<DEVICE_IP>:8088/ai-write-status

# Read battery SOC
curl "http://<DEVICE_IP>:8088/value?service=com.victronenergy.system&path=/Dc/Battery/Soc"
```

---

## API Reference

### Main Server (Port 8088)

#### Read Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | API info, version, AI write status |
| `GET /health` | Health check with uptime |
| `GET /services` | List all Victron DBus services |
| `GET /settings` | All system settings (300+ values) |
| `GET /value?service=X&path=Y` | Get specific DBus value |
| `GET /text?service=X&path=Y` | Get text representation |
| `GET /ai-write-status` | Detailed AI write switch diagnostics |
| `GET /config` | Get stored agent configuration |

#### Write Endpoints

| Endpoint | Description | Requires |
|----------|-------------|----------|
| `POST /value` | Set DBus value | AI_write switch ON |
| `POST /config` | Save agent configuration | - |

### Control Server (Port 8089)

| Endpoint | Method | Description | Requires |
|----------|--------|-------------|----------|
| `/` | GET | Control server info | - |
| `/health` | GET | Control server health | - |
| `/status` | GET | Main server status (pid, uptime) | - |
| `/logs` | GET | Recent log entries (?lines=N) | - |
| `/start` | POST | Start main server | `{"confirm": true}` |
| `/stop` | POST | Stop main server | `{"confirm": true}` |
| `/restart` | POST | Restart main server | `{"confirm": true}` |
| `/upgrade` | POST | Git pull + restart | `{"confirm": true}` |

---

## Server Management

### Via Control Server API

```bash
# Check main server status
curl http://<DEVICE_IP>:8089/status

# Restart main server
curl -X POST http://<DEVICE_IP>:8089/restart \
  -H "Content-Type: application/json" \
  -d '{"confirm": true}'

# Stop main server
curl -X POST http://<DEVICE_IP>:8089/stop \
  -H "Content-Type: application/json" \
  -d '{"confirm": true}'

# Upgrade (git pull + restart)
curl -X POST http://<DEVICE_IP>:8089/upgrade \
  -H "Content-Type: application/json" \
  -d '{"confirm": true}'

# View logs
curl "http://<DEVICE_IP>:8089/logs?lines=100"
```

### Via SSH (daemontools)

```bash
# Check service status
svstat /service/dbus-api-server
svstat /service/dbus-api-control

# Restart main server
svc -t /service/dbus-api-server

# Stop main server
svc -d /service/dbus-api-server

# Start main server
svc -u /service/dbus-api-server

# View logs
tail -f /var/log/dbus-api-server/current
```

### Uninstall

```bash
cd /data/dbus-api-repo
./uninstall.sh
```

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

### Write with Safety Check

```python
import requests

BASE_URL = "http://192.168.88.77:8088"

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
├── dbus_api_server.py          # Main API server (port 8088)
├── dbus_api_control.py         # Control server (port 8089)
├── install.sh                  # Installation script
├── uninstall.sh                # Uninstallation script
├── service/
│   ├── dbus-api-server/        # Main server daemontools service
│   │   ├── run
│   │   └── log/run
│   └── dbus-api-control/       # Control server daemontools service
│       ├── run
│       └── log/run
├── nodered/
│   └── safety_switch.json      # AI_write switch flow
├── docs/
│   ├── ai-agent-developer/     # Build AI monitoring agents
│   └── installer/              # Troubleshoot & validate systems
├── AGENTS.md                   # AI agent safety guidelines
├── CLAUDE.md                   # Claude Code safety instructions
└── README.md                   # This file
```

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
| Main server not responding | `curl http://<IP>:8089/status` to check via control server |
| Control server not responding | `svstat /service/dbus-api-control` via SSH |
| Service not starting | Check logs: `tail /var/log/dbus-api-server/current` |

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

---

## Resources

- **Repository**: [github.com/EnergyCitizen/ai_victron_dbus_api](https://github.com/EnergyCitizen/ai_victron_dbus_api)
- **Issues**: [GitHub Issues](https://github.com/EnergyCitizen/ai_victron_dbus_api/issues)
- **Victron Community**: [community.victronenergy.com](https://community.victronenergy.com)

---

<div align="center">

[![](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner2-direct.svg)](https://github.com/vshymanskyy/StandWithUkraine/blob/main/docs/README.md)

**Made in Ukraine with love by [EnergyCitizen](https://github.com/EnergyCitizen)**

**Version**: 3.1.0 | **Last Updated**: 2025-12-01

</div>
