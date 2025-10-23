---
name: Bug Report
about: Report a problem with the API server or documentation
title: '[BUG] '
labels: bug
assignees: ''
---

## Describe the Bug
A clear description of what the bug is.

## Environment
- **Device**: Cerbo GX / Venus GX / Other
- **Venus OS Version**: (e.g., v3.70)
- **API Server Version**: (check dbus_api_server.py)
- **Python Version**: (run `python3 --version` on device)

## Steps to Reproduce
1. Start API server with `python3 dbus_api_server.py --port 8088`
2. Call endpoint `curl http://...`
3. See error

## Expected Behavior
What should happen.

## Actual Behavior
What actually happens.

## Error Messages
```
Paste error messages or logs here
```

## API Response (if applicable)
```json
{
  "error": "...",
  "success": false
}
```

## Additional Context
- Network setup (local/VPN/remote)
- Other running services
- Recent changes to system
