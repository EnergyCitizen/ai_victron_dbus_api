#!/usr/bin/env python3
"""
Victron DBus API Server (Read-Only)
A lightweight HTTP server that exposes Victron dbus values via REST API
Runs as a daemon and provides READ-ONLY access to dbus system bus
"""

import dbus
import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import sys
import signal
import traceback

# Configuration
DEFAULT_PORT = 8088
DEFAULT_HOST = '0.0.0.0'

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
        except Exception as e:
            logger.error(f"Failed to connect to system bus: {e}")
            raise

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

    def _set_headers(self, status=200, content_type='application/json'):
        """Set response headers"""
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
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
                self._send_json({
                    'name': 'Victron DBus API Server (Read-Only)',
                    'version': '1.0.0',
                    'mode': 'read-only',
                    'endpoints': {
                        'GET /': 'API information',
                        'GET /settings': 'Get all settings from com.victronenergy.settings',
                        'GET /services': 'List all Victron dbus services',
                        'GET /value?service=X&path=Y': 'Get value from specific dbus path',
                        'GET /text?service=X&path=Y': 'Get text representation of value',
                        'GET /health': 'Health check'
                    }
                })

            # Route: GET /health
            elif path == '/health':
                self._send_json({'status': 'healthy', 'success': True})

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
        """Handle POST requests - disabled for read-only mode"""
        self._send_error_json('Write operations are disabled. This server is read-only.', 403)

    def log_message(self, format, *args):
        """Override to use custom logger"""
        logger.info(f"{self.client_address[0]} - {format % args}")


def run_server(host=DEFAULT_HOST, port=DEFAULT_PORT):
    """Run the HTTP server"""
    try:
        # Initialize DBus interface
        dbus_interface = DBusInterface()
        DBusAPIHandler.dbus_interface = dbus_interface

        # Create server
        server = HTTPServer((host, port), DBusAPIHandler)
        logger.info(f"Starting Victron DBus API Server on {host}:{port}")
        logger.info(f"Access API at http://{host}:{port}/")

        # Handle shutdown gracefully
        def signal_handler(sig, frame):
            logger.info("Shutting down server...")
            server.shutdown()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start server
        server.serve_forever()

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
