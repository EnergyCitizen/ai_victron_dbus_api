# Claude Code Instructions for ai_victron_dbus_api

## Critical Safety Rules

### Venus OS Device Operations

**NEVER run these commands on Venus OS devices:**

```bash
# DANGEROUS - kills critical Victron system services
killall python3  # NEVER DO THIS

# DANGEROUS - kills system processes
pkill python     # NEVER DO THIS
```

**Safe way to manage the API servers (v3.1.0+):**

```bash
# Use daemontools svc commands (recommended)
svc -t /service/dbus-api-server    # Restart main server
svc -d /service/dbus-api-server    # Stop main server
svc -u /service/dbus-api-server    # Start main server

# Or use the Control Server API (port 8089)
curl -X POST http://<IP>:8089/restart -H "Content-Type: application/json" -d '{"confirm":true}'

# Check status
svstat /service/dbus-api-server
svstat /service/dbus-api-control
```

**Legacy (manual start only):**

```bash
# Stop ONLY the API server (safe)
pkill -f dbus_api_server.py

# Or find and kill specific PID
ps | grep dbus_api_server
kill <specific_pid>
```

### Why This Matters

Venus OS runs many critical Python services:
- `localsettings.py` - System settings
- `dbus_systemcalc` - System calculations
- `vrmlogger.py` - VRM logging
- `dbus-modbus-cli` - Modbus communication
- Many more...

Killing all Python processes will crash the system and require a reboot.

## Development Guidelines

1. **Always use daemontools commands** (`svc`, `svstat`) for service management
2. **Test on non-production devices first**
3. **AI_write switch must be ON** for any write operations
4. **Never modify ESS modes or charge settings** without explicit user confirmation
5. **AI_write bitmask**: State value bit 0 determines ON/OFF (257=ON, 256=OFF)

## Repository Structure

```
ai_victron_dbus_api/
├── dbus_api_server.py          # Main API server (port 8088)
├── dbus_api_control.py         # Control server (port 8089)
├── install.sh                  # Installation script
├── uninstall.sh                # Uninstallation script
├── service/                    # daemontools service definitions
│   ├── dbus-api-server/
│   └── dbus-api-control/
├── nodered/
│   └── safety_switch.json      # AI_write switch flow
└── docs/                       # Diataxis-structured documentation
```

## Installation Paths (on Venus OS)

- `/data/dbus-api/` - Installation directory (survives firmware updates)
- `/service/dbus-api-server` - Main server service symlink
- `/service/dbus-api-control` - Control server service symlink
- `/var/log/dbus-api-server/current` - Main server logs
- `/var/log/dbus-api-control/current` - Control server logs
