#!/bin/bash
# Victron DBus API Uninstallation Script
# Removes both API server and control server services

set -e

INSTALL_DIR="/data/dbus-api"
SERVICE_DIR="/service"
RC_LOCAL="/data/rc.local"

echo "=== Victron DBus API Uninstaller ==="
echo ""
echo "This will remove:"
echo "  - Main API server (port 8088)"
echo "  - Control server (port 8089)"
echo "  - All configuration and logs"
echo ""
echo "Continue? (y/N)"
read -r response
if [ "$response" != "y" ] && [ "$response" != "Y" ]; then
    echo "Aborted."
    exit 0
fi

echo ""

# Step 1: Stop services
echo "[1/4] Stopping services..."
if [ -d "$SERVICE_DIR/dbus-api-server" ]; then
    svc -d "$SERVICE_DIR/dbus-api-server" 2>/dev/null || true
    sleep 1
fi
if [ -d "$SERVICE_DIR/dbus-api-control" ]; then
    svc -d "$SERVICE_DIR/dbus-api-control" 2>/dev/null || true
    sleep 1
fi

# Kill any remaining processes
pkill -f dbus_api_server.py 2>/dev/null || true
pkill -f dbus_api_control.py 2>/dev/null || true

# Step 2: Remove service symlinks
echo "[2/4] Removing service symlinks..."
rm -f "$SERVICE_DIR/dbus-api-server"
rm -f "$SERVICE_DIR/dbus-api-control"

# Step 3: Remove installation directory
echo "[3/4] Removing installation directory..."
rm -rf "$INSTALL_DIR"

# Step 4: Remove from rc.local
echo "[4/4] Cleaning up rc.local..."
if [ -f "$RC_LOCAL" ]; then
    # Remove our section from rc.local
    sed -i '/# Victron DBus API Services/,/fi$/d' "$RC_LOCAL" 2>/dev/null || true
    echo "  Cleaned $RC_LOCAL"
fi

# Remove log directories
rm -rf /var/log/dbus-api-server
rm -rf /var/log/dbus-api-control

echo ""
echo "=== Uninstallation Complete ==="
echo ""
echo "The Victron DBus API has been removed."
echo "Configuration and logs have been deleted."
echo ""
