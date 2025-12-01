#!/bin/bash
# Victron DBus API v3.1.0 Installation Script
# Installs/updates main API server and control server as daemontools services
# Safe to run multiple times (idempotent)

set -e

INSTALL_DIR="/data/dbus-api"
SERVICE_DIR="/service"
RC_LOCAL="/data/rc.local"

# Detect if this is an update or fresh install
if [ -d "$INSTALL_DIR" ] && [ -f "$INSTALL_DIR/dbus_api_server.py" ]; then
    echo "=== Victron DBus API v3.1.0 Update ==="
    IS_UPDATE=true
else
    echo "=== Victron DBus API v3.1.0 Fresh Install ==="
    IS_UPDATE=false
fi
echo ""

# Check if running on Venus OS
if [ ! -d "/opt/victronenergy" ]; then
    echo "Warning: This doesn't appear to be a Venus OS device."
    echo "Continue anyway? (y/N)"
    read -r response
    if [ "$response" != "y" ] && [ "$response" != "Y" ]; then
        echo "Aborted."
        exit 1
    fi
fi

# Determine script directory (where install.sh is located)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Source directory: $SCRIPT_DIR"
echo "Install directory: $INSTALL_DIR"
echo ""

# Step 1: Stop existing services if running (use SIGKILL for reliability)
echo "[1/7] Stopping existing services..."
if [ -d "$SERVICE_DIR/dbus-api-server" ]; then
    svc -k "$SERVICE_DIR/dbus-api-server" 2>/dev/null || true
    sleep 1
fi
if [ -d "$SERVICE_DIR/dbus-api-control" ]; then
    svc -k "$SERVICE_DIR/dbus-api-control" 2>/dev/null || true
    sleep 1
fi

# Also kill any manually started instances
pkill -9 -f dbus_api_server.py 2>/dev/null || true
pkill -9 -f dbus_api_control.py 2>/dev/null || true
sleep 1

# Step 2: Create installation directory
echo "[2/7] Creating installation directory..."
mkdir -p "$INSTALL_DIR"

# Step 3: Copy Python files
echo "[3/7] Copying server files..."
cp "$SCRIPT_DIR/dbus_api_server.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/dbus_api_control.py" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/dbus_api_server.py"
chmod +x "$INSTALL_DIR/dbus_api_control.py"

# Step 4: Copy service directories
echo "[4/7] Setting up daemontools services..."

# Main API server service
rm -rf "$INSTALL_DIR/service-dbus-api-server"
cp -r "$SCRIPT_DIR/service/dbus-api-server" "$INSTALL_DIR/service-dbus-api-server"
chmod +x "$INSTALL_DIR/service-dbus-api-server/run"
chmod +x "$INSTALL_DIR/service-dbus-api-server/log/run"

# Control server service
rm -rf "$INSTALL_DIR/service-dbus-api-control"
cp -r "$SCRIPT_DIR/service/dbus-api-control" "$INSTALL_DIR/service-dbus-api-control"
chmod +x "$INSTALL_DIR/service-dbus-api-control/run"
chmod +x "$INSTALL_DIR/service-dbus-api-control/log/run"

# Step 5: Create symlinks in /service
echo "[5/7] Creating service symlinks..."

# Remove old symlinks if they exist
rm -f "$SERVICE_DIR/dbus-api-server"
rm -f "$SERVICE_DIR/dbus-api-control"

# Create new symlinks
ln -s "$INSTALL_DIR/service-dbus-api-server" "$SERVICE_DIR/dbus-api-server"
ln -s "$INSTALL_DIR/service-dbus-api-control" "$SERVICE_DIR/dbus-api-control"

# Step 6: Add to rc.local for persistence across firmware updates
echo "[6/7] Configuring persistence (rc.local)..."

# Create rc.local if it doesn't exist
if [ ! -f "$RC_LOCAL" ]; then
    cat > "$RC_LOCAL" << 'RCEOF'
#!/bin/bash
# Venus OS rc.local - executed on boot
# Add custom startup commands here

RCEOF
    chmod +x "$RC_LOCAL"
fi

# Add our service setup to rc.local if not already present
if ! grep -q "dbus-api-server" "$RC_LOCAL"; then
    cat >> "$RC_LOCAL" << 'RCEOF'

# Victron DBus API Services
# Recreate service symlinks (survives firmware updates)
if [ -d "/data/dbus-api" ]; then
    ln -sf /data/dbus-api/service-dbus-api-server /service/dbus-api-server
    ln -sf /data/dbus-api/service-dbus-api-control /service/dbus-api-control
fi
RCEOF
    echo "  Added to $RC_LOCAL"
else
    echo "  Already configured in $RC_LOCAL"
fi

# Step 7: Start services
echo "[7/7] Starting services..."
svc -u "$SERVICE_DIR/dbus-api-server"
sleep 3
svc -u "$SERVICE_DIR/dbus-api-control"
sleep 2

# Verify installation
echo ""
if [ "$IS_UPDATE" = true ]; then
    echo "=== Update Complete ==="
else
    echo "=== Installation Complete ==="
fi
echo ""
echo "Service Status:"
svstat "$SERVICE_DIR/dbus-api-server" 2>/dev/null || echo "  Main server: not running"
svstat "$SERVICE_DIR/dbus-api-control" 2>/dev/null || echo "  Control server: not running"

# Get IP address (BusyBox compatible)
DEVICE_IP=$(ip route get 1 2>/dev/null | awk '{for(i=1;i<=NF;i++)if($i=="src")print $(i+1)}' || hostname 2>/dev/null || echo "localhost")

echo ""
echo "Endpoints:"
echo "  Main API:    http://${DEVICE_IP}:8088/"
echo "  Control API: http://${DEVICE_IP}:8089/"
echo ""
echo "Test with:"
echo "  curl http://localhost:8088/health"
echo "  curl http://localhost:8089/health"
echo ""
