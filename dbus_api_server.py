#!/usr/bin/env python3
"""
Victron DBus API Server v3.0.0
A lightweight HTTP server that exposes Victron dbus values via REST API
Runs as a daemon and provides read/write access to dbus system bus

Safety Features:
- AI Write Switch: Write operations require AI_write virtual switch to be ON
- Configuration Storage: Installation-specific configs stored in /data/ai_agent/
"""

import dbus
import json
import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import sys
import signal
import traceback
import threading
import time
from datetime import datetime

# Configuration
DEFAULT_PORT = 8088
DEFAULT_HOST = '0.0.0.0'
CONFIG_DIR = '/data/ai_agent'
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DBusAPIServer')


class DBusInterface:
    """Handle DBus system bus interactions"""

    def __init__(self):
        try:
            self.bus = dbus.SystemBus()
            logger.info("Connected to DBus system bus")
            # AI_write switch discovered on demand (not at startup)
            self.ai_write_service = None
        except Exception as e:
            logger.error(f"Failed to connect to system bus: {e}")
            raise

    def _find_ai_write_switch(self):
        """Find the AI_write virtual switch service by searching for CustomName='AI_write'"""
        try:
            services = self.list_services()
            for service in services:
                if 'switch.virtual' in service:
                    try:
                        name = self.get_value(service, '/CustomName')
                        if name and str(name).lower() == 'ai_write':
                            return service
                    except Exception:
                        continue
            return None
        except Exception as e:
            logger.error(f"Error finding AI_write switch: {e}")
            return None

    def get_venus_image_type(self):
        """Get Venus OS image type (0=Normal, 1=Large)

        Returns: (type_id: int, type_name: str)
        """
        try:
            image_type = self.get_value('com.victronenergy.settings', '/Settings/System/ImageType')
            if image_type == 1:
                return 1, "Large"
            else:
                return 0, "Normal"
        except Exception:
            return -1, "Unknown"

    def is_nodered_enabled(self):
        """Check if NodeRED service is enabled in settings

        Returns: bool
        """
        try:
            enabled = self.get_value('com.victronenergy.settings', '/Settings/Services/NodeRed')
            return enabled == 1
        except Exception:
            return False

    def is_nodered_running(self):
        """Check if NodeRED has started (virtual switches available)

        Returns: bool
        """
        try:
            services = self.list_services()
            # If any virtual switch exists, NodeRED is likely running
            return any('switch.virtual' in s for s in services)
        except Exception:
            return False

    def is_ai_write_enabled(self):
        """Check if AI_write switch is enabled (State != 0)

        Returns: (enabled: bool, message: str, details: dict)
        """
        details = {
            'venus_image_type': None,
            'nodered_enabled': None,
            'nodered_running': None,
            'switch_found': False,
            'switch_state': None
        }

        # Check Venus image type
        type_id, type_name = self.get_venus_image_type()
        details['venus_image_type'] = type_name

        if type_id == 0:
            return False, "Venus OS Normal image does not include NodeRED. Install Venus OS Large to use AI_write switch.", details

        # Check if NodeRED is enabled
        details['nodered_enabled'] = self.is_nodered_enabled()
        if not details['nodered_enabled']:
            return False, "NodeRED is disabled. Enable it in Remote Console > Settings > Services > NodeRED.", details

        # Check if NodeRED is running (has started)
        details['nodered_running'] = self.is_nodered_running()
        if not details['nodered_running']:
            return False, "NodeRED is not running yet. It may still be starting (takes ~60s after boot). Please wait.", details

        # Always discover switch on each call (NodeRED may have just started or switch recreated)
        self.ai_write_service = self._find_ai_write_switch()

        if not self.ai_write_service:
            details['switch_found'] = False
            return False, "AI_write virtual switch not found. Create it in NodeRED: Add a 'victron-virtual-switch' node with CustomName 'AI_write'.", details

        details['switch_found'] = True

        try:
            state = self.get_value(self.ai_write_service, '/State')
            details['switch_state'] = state
            # State 0 = OFF, any other value (e.g., 256) = ON
            if state and int(state) != 0:
                return True, "AI_write is enabled", details
            else:
                return False, "AI_write switch is OFF. Enable it in NodeRED or VRM to allow write operations.", details
        except Exception as e:
            logger.error(f"Error checking AI_write state: {e}")
            return False, f"Error checking AI_write switch: {e}", details

    def get_all_settings(self):
        """Get all settings from com.victronenergy.settings"""
        try:
            obj = self.bus.get_object('com.victronenergy.settings', '/')
            interface = dbus.Interface(obj, 'com.victronenergy.BusItem')
            items = interface.GetItems()

            # Convert dbus types to Python native types
            return self._convert_dbus_dict(items)
        except Exception as e:
            logger.error(f"Error getting all settings: {e}")
            raise

    def get_value(self, service, path):
        """Get value from specific dbus path"""
        try:
            obj = self.bus.get_object(service, path)
            interface = dbus.Interface(obj, 'com.victronenergy.BusItem')
            value = interface.GetValue()
            return self._convert_dbus_value(value)
        except Exception as e:
            logger.error(f"Error getting value from {service}{path}: {e}")
            raise


    def get_text(self, service, path):
        """Get text representation of value"""
        try:
            obj = self.bus.get_object(service, path)
            interface = dbus.Interface(obj, 'com.victronenergy.BusItem')
            text = interface.GetText()
            return str(text)
        except Exception as e:
            logger.error(f"Error getting text from {service}{path}: {e}")
            raise

    def set_value(self, service, path, value):
        """Set value at specific dbus path

        Uses the Victron BusItem SetValue method which validates
        the value against min/max constraints before writing.

        Returns: 0 on success, -1 on error (value out of range, invalid type, etc.)
        """
        try:
            obj = self.bus.get_object(service, path)
            interface = dbus.Interface(obj, 'com.victronenergy.BusItem')
            result = interface.SetValue(value)
            return int(result)
        except Exception as e:
            logger.error(f"Error setting value at {service}{path}: {e}")
            raise

    def list_services(self):
        """List all available dbus services"""
        try:
            obj = self.bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus')
            interface = dbus.Interface(obj, 'org.freedesktop.DBus')
            services = interface.ListNames()
            # Filter for victron services
            victron_services = [s for s in services if 'victron' in s.lower()]
            return sorted(victron_services)
        except Exception as e:
            logger.error(f"Error listing services: {e}")
            raise

    def _convert_dbus_value(self, value):
        """Convert dbus types to Python native types"""
        if isinstance(value, dbus.Dictionary):
            return {self._convert_dbus_value(k): self._convert_dbus_value(v)
                    for k, v in value.items()}
        elif isinstance(value, dbus.Array):
            return [self._convert_dbus_value(item) for item in value]
        elif isinstance(value, dbus.Boolean):
            return bool(value)
        elif isinstance(value, dbus.Byte):
            return int(value)
        elif isinstance(value, (dbus.Int16, dbus.Int32, dbus.Int64,
                               dbus.UInt16, dbus.UInt32, dbus.UInt64)):
            return int(value)
        elif isinstance(value, dbus.Double):
            return float(value)
        elif isinstance(value, dbus.String):
            return str(value)
        else:
            return value

    def _convert_dbus_dict(self, dbus_dict):
        """Convert dbus dictionary to regular Python dict"""
        result = {}
        for key, value in dbus_dict.items():
            result[str(key)] = self._convert_dbus_value(value)
        return result


class DBusAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for DBus API"""

    dbus_interface = None  # Shared DBus interface instance
    server_instance = None  # Reference to HTTP server for restart/stop
    restart_requested = False  # Flag for restart
    start_time = None  # Server start timestamp

    def _set_headers(self, status=200, content_type='application/json'):
        """Set response headers"""
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _send_json(self, data, status=200):
        """Send JSON response"""
        self._set_headers(status)
        self.wfile.write(json.dumps(data, indent=2).encode())

    def _send_error_json(self, message, status=500):
        """Send error response"""
        self._send_json({'error': message, 'success': False}, status)

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self._set_headers(204)

    def do_GET(self):
        """Handle GET requests"""
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            params = parse_qs(parsed.query)

            # Route: GET /
            if path == '/' or path == '':
                ai_enabled, ai_message, ai_details = self.dbus_interface.is_ai_write_enabled()
                self._send_json({
                    'name': 'Victron DBus API Server',
                    'version': '3.0.0',
                    'mode': 'read-write',
                    'ai_write_enabled': ai_enabled,
                    'ai_write_status': ai_message,
                    'endpoints': {
                        'GET /': 'API information',
                        'GET /settings': 'Get all settings from com.victronenergy.settings',
                        'GET /services': 'List all Victron dbus services',
                        'GET /value?service=X&path=Y': 'Get value from specific dbus path',
                        'GET /text?service=X&path=Y': 'Get text representation of value',
                        'GET /health': 'Health check',
                        'GET /ai-write-status': 'Check AI write switch status',
                        'GET /config': 'Get stored configuration',
                        'POST /value': 'Set value (requires AI_write switch ON)',
                        'POST /config': 'Save configuration (JSON body)',
                        'POST /restart': 'Restart API server (JSON body: {"confirm": true})',
                        'POST /stop': 'Stop API server (JSON body: {"confirm": true})'
                    }
                })

            # Route: GET /health
            elif path == '/health':
                uptime_seconds = int(time.time() - DBusAPIHandler.start_time) if DBusAPIHandler.start_time else 0
                started_at = datetime.fromtimestamp(DBusAPIHandler.start_time).isoformat() if DBusAPIHandler.start_time else None
                self._send_json({
                    'status': 'healthy',
                    'started_at': started_at,
                    'uptime_seconds': uptime_seconds,
                    'success': True
                })

            # Route: GET /ai-write-status
            elif path == '/ai-write-status':
                ai_enabled, ai_message, ai_details = self.dbus_interface.is_ai_write_enabled()
                self._send_json({
                    'enabled': ai_enabled,
                    'message': ai_message,
                    'switch_service': self.dbus_interface.ai_write_service,
                    'details': ai_details,
                    'faq': {
                        'venus_large': 'Venus OS Large includes NodeRED. Install from: https://www.victronenergy.com/live/venus-os:large',
                        'enable_nodered': 'Enable NodeRED in Remote Console > Settings > Services > NodeRED',
                        'create_switch': 'In NodeRED, add a victron-virtual-switch node with CustomName set to "AI_write"',
                        'toggle_switch': 'Control the switch via VRM dashboard, Remote Console, or NodeRED flows'
                    },
                    'success': True
                })

            # Route: GET /config
            elif path == '/config':
                try:
                    if os.path.exists(CONFIG_FILE):
                        with open(CONFIG_FILE, 'r') as f:
                            config = json.load(f)
                        self._send_json({
                            'config': config,
                            'path': CONFIG_FILE,
                            'success': True
                        })
                    else:
                        self._send_json({
                            'config': {},
                            'path': CONFIG_FILE,
                            'message': 'No configuration file found',
                            'success': True
                        })
                except Exception as e:
                    self._send_error_json(f'Failed to read config: {e}', 500)

            # Route: GET /settings
            elif path == '/settings':
                settings = self.dbus_interface.get_all_settings()
                self._send_json({'settings': settings, 'success': True})

            # Route: GET /services
            elif path == '/services':
                services = self.dbus_interface.list_services()
                self._send_json({'services': services, 'count': len(services), 'success': True})

            # Route: GET /value
            elif path == '/value':
                service = params.get('service', [''])[0]
                dbus_path = params.get('path', [''])[0]

                if not service or not dbus_path:
                    self._send_error_json('Missing service or path parameter', 400)
                    return

                value = self.dbus_interface.get_value(service, dbus_path)
                self._send_json({
                    'service': service,
                    'path': dbus_path,
                    'value': value,
                    'success': True
                })

            # Route: GET /text
            elif path == '/text':
                service = params.get('service', [''])[0]
                dbus_path = params.get('path', [''])[0]

                if not service or not dbus_path:
                    self._send_error_json('Missing service or path parameter', 400)
                    return

                text = self.dbus_interface.get_text(service, dbus_path)
                self._send_json({
                    'service': service,
                    'path': dbus_path,
                    'text': text,
                    'success': True
                })

            else:
                self._send_error_json('Not found', 404)

        except Exception as e:
            logger.error(f"Error handling GET request: {e}\n{traceback.format_exc()}")
            self._send_error_json(str(e))

    def do_POST(self):
        """Handle POST requests for writing values"""
        try:
            parsed = urlparse(self.path)
            path = parsed.path

            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self._send_error_json('Request body is required', 400)
                return

            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode('utf-8'))
            except json.JSONDecodeError as e:
                self._send_error_json(f'Invalid JSON: {e}', 400)
                return

            # Route: POST /value
            if path == '/value':
                # Safety check: Verify AI_write switch is enabled
                ai_enabled, ai_message, ai_details = self.dbus_interface.is_ai_write_enabled()
                if not ai_enabled:
                    logger.warning(f"Write blocked - AI_write disabled: {ai_message}")
                    self._send_json({
                        'error': 'AI write is disabled',
                        'message': ai_message,
                        'details': ai_details,
                        'hint': 'Enable the AI_write virtual switch in VRM or NodeRED to allow write operations',
                        'success': False
                    }, 403)
                    return

                service = data.get('service', '')
                dbus_path = data.get('path', '')
                value = data.get('value')

                if not service or not dbus_path:
                    self._send_error_json('Missing service or path in request body', 400)
                    return

                if value is None:
                    self._send_error_json('Missing value in request body', 400)
                    return

                # Get current value first for comparison
                try:
                    old_value = self.dbus_interface.get_value(service, dbus_path)
                except Exception:
                    old_value = None

                # Set the new value
                result = self.dbus_interface.set_value(service, dbus_path, value)

                if result == 0:
                    # Get new value to confirm
                    new_value = self.dbus_interface.get_value(service, dbus_path)
                    logger.info(f"Value set: {service}{dbus_path} = {value} (was: {old_value})")
                    self._send_json({
                        'service': service,
                        'path': dbus_path,
                        'value': new_value,
                        'previous_value': old_value,
                        'success': True
                    })
                else:
                    self._send_error_json(
                        'Failed to set value (value may be out of range or invalid type)',
                        400
                    )

            # Route: POST /config
            elif path == '/config':
                # Save configuration to file
                config_data = data.get('config', data)
                try:
                    os.makedirs(CONFIG_DIR, exist_ok=True)
                    with open(CONFIG_FILE, 'w') as f:
                        json.dump(config_data, f, indent=2)
                    logger.info(f"Configuration saved to {CONFIG_FILE}")
                    self._send_json({
                        'message': 'Configuration saved',
                        'path': CONFIG_FILE,
                        'success': True
                    })
                except Exception as e:
                    self._send_error_json(f'Failed to save config: {e}', 500)

            # Route: POST /restart
            elif path == '/restart':
                confirm = data.get('confirm', False)
                if not confirm:
                    self._send_error_json('Restart requires {"confirm": true} in request body', 400)
                    return

                logger.info("Restart requested via API")
                self._send_json({
                    'message': 'Server restarting...',
                    'success': True
                })

                # Set restart flag and shutdown in separate thread to allow response to complete
                DBusAPIHandler.restart_requested = True
                def shutdown_server():
                    if DBusAPIHandler.server_instance:
                        DBusAPIHandler.server_instance.shutdown()
                threading.Thread(target=shutdown_server, daemon=True).start()

            # Route: POST /stop
            elif path == '/stop':
                confirm = data.get('confirm', False)
                if not confirm:
                    self._send_error_json('Stop requires {"confirm": true} in request body', 400)
                    return

                logger.info("Stop requested via API")
                self._send_json({
                    'message': 'Server stopping...',
                    'success': True
                })

                # Shutdown in separate thread to allow response to complete
                DBusAPIHandler.restart_requested = False
                def shutdown_server():
                    if DBusAPIHandler.server_instance:
                        DBusAPIHandler.server_instance.shutdown()
                threading.Thread(target=shutdown_server, daemon=True).start()

            else:
                self._send_error_json('Not found', 404)

        except Exception as e:
            logger.error(f"Error handling POST request: {e}\n{traceback.format_exc()}")
            self._send_error_json(str(e))

    def log_message(self, format, *args):
        """Override to use custom logger"""
        logger.info(f"{self.client_address[0]} - {format % args}")


def run_server(host=DEFAULT_HOST, port=DEFAULT_PORT):
    """Run the HTTP server with restart support"""
    while True:
        try:
            # Reset restart flag and set start time
            DBusAPIHandler.restart_requested = False
            DBusAPIHandler.start_time = time.time()

            # Initialize DBus interface
            dbus_interface = DBusInterface()
            DBusAPIHandler.dbus_interface = dbus_interface

            # Create server
            server = HTTPServer((host, port), DBusAPIHandler)
            DBusAPIHandler.server_instance = server
            logger.info(f"Starting Victron DBus API Server v3.0.0 on {host}:{port}")
            logger.info(f"Access API at http://{host}:{port}/")

            # Handle shutdown gracefully
            def signal_handler(sig, frame):
                logger.info("Shutting down server (signal)...")
                DBusAPIHandler.restart_requested = False
                server.shutdown()

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            # Start server
            server.serve_forever()

            # Check if restart was requested
            if DBusAPIHandler.restart_requested:
                logger.info("Restarting server...")
                server.server_close()
                continue
            else:
                logger.info("Server stopped")
                sys.exit(0)

        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            sys.exit(1)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Victron DBus API Server')
    parser.add_argument('--host', default=DEFAULT_HOST, help=f'Host to bind to (default: {DEFAULT_HOST})')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help=f'Port to listen on (default: {DEFAULT_PORT})')

    args = parser.parse_args()

    run_server(args.host, args.port)
