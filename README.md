# Victron DBus API Server (Read-Only)

A lightweight HTTP REST API server that provides read-only access to Victron dbus system bus over HTTP.

## Features

- **Read-Only Mode**: No write operations allowed - safe for remote monitoring
- **REST API**: Simple HTTP GET requests to query dbus values
- **JSON Responses**: All data returned in JSON format
- **CORS Enabled**: Can be accessed from web browsers
- **Lightweight**: Minimal dependencies, runs efficiently on embedded systems
- **Daemon Mode**: Runs in background persistently

## Deployment

The server is deployed and running on:
- **Host**: 192.168.88.77
- **Port**: 8088
- **URL**: http://192.168.88.77:8088/

## API Endpoints

### 1. API Information
```bash
GET http://192.168.88.77:8088/
```
Returns server info and available endpoints.

### 2. Health Check
```bash
GET http://192.168.88.77:8088/health
```
Simple health check endpoint.

### 3. List All Victron Services
```bash
GET http://192.168.88.77:8088/services
```
Returns all available Victron dbus services.

Example response:
```json
{
  "services": [
    "com.victronenergy.battery.socketcan_can0",
    "com.victronenergy.settings",
    "com.victronenergy.system",
    ...
  ],
  "count": 20,
  "success": true
}
```

### 4. Get All Settings
```bash
GET http://192.168.88.77:8088/settings
```
Returns all settings from com.victronenergy.settings with their values, defaults, min/max, etc.

### 5. Get Specific Value
```bash
GET http://192.168.88.77:8088/value?service=<SERVICE>&path=<PATH>
```

Parameters:
- `service`: The dbus service name (e.g., `com.victronenergy.settings`)
- `path`: The dbus path (e.g., `/Settings/CGwacs/Hub4Mode`)

Example:
```bash
curl "http://192.168.88.77:8088/value?service=com.victronenergy.settings&path=/Settings/CGwacs/Hub4Mode"
```

Response:
```json
{
  "service": "com.victronenergy.settings",
  "path": "/Settings/CGwacs/Hub4Mode",
  "value": 2,
  "success": true
}
```

### 6. Get Text Representation
```bash
GET http://192.168.88.77:8088/text?service=<SERVICE>&path=<PATH>
```

Same parameters as `/value` but returns the text representation of the value.

## Security

### Read-Only Protection

All write operations are disabled. POST requests will return:
```json
{
  "error": "Write operations are disabled. This server is read-only.",
  "success": false
}
```

## Server Management

### Check if Running
```bash
ssh root@192.168.88.77 "ps | grep dbus_api_server"
```

### View Logs
```bash
ssh root@192.168.88.77 "cat ~/dbus_api.log"
```

### Stop Server
```bash
ssh root@192.168.88.77 "pkill -f dbus_api_server"
```

### Start Server
```bash
ssh root@192.168.88.77 "cd ~ && python3 dbus_api_server.py --port 8088 > dbus_api.log 2>&1 &"
```

### Restart Server
```bash
ssh root@192.168.88.77 "pkill -f dbus_api_server && sleep 1 && cd ~ && python3 dbus_api_server.py --port 8088 > dbus_api.log 2>&1 &"
```

## Usage Examples

### Get Battery Voltage
```bash
curl "http://192.168.88.77:8088/value?service=com.victronenergy.battery.socketcan_can0&path=/Dc/0/Voltage"
```

### Get System State
```bash
curl "http://192.168.88.77:8088/value?service=com.victronenergy.system&path=/SystemState/State"
```

### Get All Settings (Full Dump)
```bash
curl http://192.168.88.77:8088/settings > settings.json
```

### Monitor Specific Value (Polling)
```bash
watch -n 2 'curl -s "http://192.168.88.77:8088/value?service=com.victronenergy.settings&path=/Settings/CGwacs/Hub4Mode"'
```

## Error Handling

All errors return JSON with `success: false`:
```json
{
  "error": "Error message here",
  "success": false
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad request (missing parameters)
- `403`: Forbidden (write operations)
- `404`: Endpoint not found
- `500`: Internal server error

## Technical Details

- **Language**: Python 3
- **Dependencies**:
  - `dbus-python` (for system bus access)
  - Standard library only (http.server, json, logging)
- **Bus**: Connects to DBus SystemBus
- **Binding**: 0.0.0.0:8088 (accessible from network)
- **Log File**: ~/dbus_api.log on server

## Files

- `dbus_api_server.py`: Main server script
- `dbus_api.log`: Server log file (on remote host)
- `DBUS_API_README.md`: This documentation

## Related Resources

- Victron localsettings repository: https://github.com/victronenergy/localsettings
- DBus documentation: https://dbus.freedesktop.org/doc/dbus-python/
