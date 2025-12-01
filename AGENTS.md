# AI Agent Guidelines for Victron DBus API

## Safety-First Architecture

This API includes built-in safety mechanisms to prevent AI agents from making unauthorized or dangerous changes to Victron systems.

## AI_write Virtual Switch

**All write operations require the AI_write switch to be enabled.**

### How It Works

1. User creates a virtual switch named "AI_write" in VRM or NodeRED
2. API server discovers this switch on startup
3. Before any POST /value operation, the server checks if the switch is ON
4. If OFF: Returns 403 error with explanation
5. If ON: Proceeds with write operation

### User Control

Users maintain full control:
- Toggle AI_write OFF to instantly block all AI write operations
- Toggle ON only when ready to accept AI-suggested changes
- Can be automated via NodeRED based on time, presence, etc.

## Critical Safety Rules for AI Agents

### NEVER Do These on Venus OS

```bash
# DANGEROUS - kills critical system services
killall python3
pkill python
kill -9 $(pgrep python)
```

### Safe Process Management

```bash
# Only kill the specific API server
pkill -f dbus_api_server.py

# Or target specific PID
ps | grep dbus_api_server
kill <specific_pid>
```

## Protected Settings

AI agents should NEVER modify these without explicit user confirmation:
- ESS modes (`/Settings/CGwacs/Hub4Mode`)
- Charge current limits
- Grid setpoints
- Battery protection settings
- Any setting that affects system safety

## Configuration Storage

Agents can store installation-specific data at:
- Endpoint: `GET/POST /config`
- File location: `/data/ai_agent/config.json`

Use this for:
- Learned thresholds
- Installation metadata
- Agent preferences
- Anomaly baselines

## Best Practices

1. **Always check AI_write status** before suggesting writes
2. **Log all operations** for audit trail
3. **Prefer reads over writes** - analyze, don't modify
4. **Request user confirmation** for any system changes
5. **Use /config for agent data** - not system settings
