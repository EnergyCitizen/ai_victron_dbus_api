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

**Safe way to manage the API server:**

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

1. **Always use specific process targeting** when stopping services
2. **Test on non-production devices first**
3. **AI_write switch must be ON** for any write operations
4. **Never modify ESS modes or charge settings** without explicit user confirmation

## Repository Structure

- `dbus_api_server.py` - Main API server
- `/data/ai_agent/config.json` - Installation-specific configuration (on device)
- `docs/` - Diataxis-structured documentation
