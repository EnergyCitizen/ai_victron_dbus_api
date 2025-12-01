#!/usr/bin/env python3
"""
Victron DBus API Control Server v3.1.0
A lightweight HTTP server for managing the main DBus API server
Runs as a daemontools service on port 8089

Provides:
- Server status monitoring
- Start/stop/restart operations via daemontools svc command
- Log access
- Upgrade functionality (git pull + restart)
"""

import json
import logging
import os
import subprocess
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import sys
import signal
import traceback

# Configuration
VERSION = '3.1.0'
DEFAULT_PORT = 8089
DEFAULT_HOST = '0.0.0.0'
SERVICE_NAME = 'dbus-api-server'
SERVICE_PATH = f'/service/{SERVICE_NAME}'
LOG_PATH = f'/var/log/{SERVICE_NAME}/current'
INSTALL_DIR = '/data/dbus-api'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DBusAPIControl')


def run_command(cmd, timeout=10):
    """Run shell command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout.strip(),
            'stderr': result.stderr.strip(),
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Command timed out',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }


def get_service_status():
    """Get status of main API server via svstat"""
    result = run_command(f'svstat {SERVICE_PATH}')
    if result['success']:
        # Parse svstat output: "/service/dbus-api-server: up (pid 1234) 567 seconds"
        output = result['stdout']
        status = {
            'raw': output,
            'running': 'up' in output,
            'pid': None,
            'uptime_seconds': None
        }

        # Extract PID
        if '(pid ' in output:
            try:
                pid_str = output.split('(pid ')[1].split(')')[0]
                status['pid'] = int(pid_str)
            except (IndexError, ValueError):
                pass

        # Extract uptime
        if ' seconds' in output:
            try:
                seconds_str = output.split(') ')[1].split(' seconds')[0]
                status['uptime_seconds'] = int(seconds_str)
            except (IndexError, ValueError):
                pass

        return status
    else:
        return {
            'raw': result['stderr'],
            'running': False,
            'pid': None,
            'uptime_seconds': None,
            'error': result['stderr']
        }


def get_recent_logs(lines=50):
    """Get recent log entries"""
    if os.path.exists(LOG_PATH):
        result = run_command(f'tail -n {lines} {LOG_PATH}')
        if result['success']:
            return result['stdout'].split('\n')
    return []


class ControlAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Control API"""

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
                self._send_json({
                    'name': 'Victron DBus API Control Server',
                    'version': VERSION,
                    'managed_service': SERVICE_NAME,
                    'endpoints': {
                        'GET /': 'Control server information',
                        'GET /health': 'Control server health check',
                        'GET /status': 'Main API server status',
                        'GET /logs': 'Recent log entries (optional: ?lines=N)',
                        'POST /start': 'Start main API server',
                        'POST /stop': 'Stop main API server',
                        'POST /restart': 'Restart main API server',
                        'POST /upgrade': 'Git pull and restart'
                    }
                })

            # Route: GET /health
            elif path == '/health':
                uptime_seconds = int(time.time() - ControlAPIHandler.start_time) if ControlAPIHandler.start_time else 0
                started_at = datetime.fromtimestamp(ControlAPIHandler.start_time).isoformat() if ControlAPIHandler.start_time else None
                self._send_json({
                    'service': 'dbus-api-control',
                    'version': VERSION,
                    'status': 'healthy',
                    'started_at': started_at,
                    'uptime_seconds': uptime_seconds,
                    'success': True
                })

            # Route: GET /status
            elif path == '/status':
                status = get_service_status()
                self._send_json({
                    'service': SERVICE_NAME,
                    'service_path': SERVICE_PATH,
                    'running': status['running'],
                    'pid': status['pid'],
                    'uptime_seconds': status['uptime_seconds'],
                    'raw_status': status['raw'],
                    'success': True
                })

            # Route: GET /logs
            elif path == '/logs':
                lines = int(params.get('lines', ['50'])[0])
                lines = min(lines, 500)  # Limit to 500 lines
                logs = get_recent_logs(lines)
                self._send_json({
                    'log_path': LOG_PATH,
                    'lines_requested': lines,
                    'lines_returned': len(logs),
                    'logs': logs,
                    'success': True
                })

            else:
                self._send_error_json('Not found', 404)

        except Exception as e:
            logger.error(f"Error handling GET request: {e}\n{traceback.format_exc()}")
            self._send_error_json(str(e))

    def do_POST(self):
        """Handle POST requests for server control"""
        try:
            parsed = urlparse(self.path)
            path = parsed.path

            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            data = {}
            if content_length > 0:
                body = self.rfile.read(content_length)
                try:
                    data = json.loads(body.decode('utf-8'))
                except json.JSONDecodeError:
                    pass

            # Require confirmation for control operations
            confirm = data.get('confirm', False)

            # Route: POST /start
            if path == '/start':
                if not confirm:
                    self._send_error_json('Start requires {"confirm": true}', 400)
                    return

                logger.info("Starting main API server")
                result = run_command(f'svc -u {SERVICE_PATH}')

                if result['success']:
                    time.sleep(1)  # Wait for service to start
                    status = get_service_status()
                    self._send_json({
                        'message': 'Start command sent',
                        'running': status['running'],
                        'pid': status['pid'],
                        'success': True
                    })
                else:
                    self._send_error_json(f"Failed to start: {result['stderr']}", 500)

            # Route: POST /stop
            elif path == '/stop':
                if not confirm:
                    self._send_error_json('Stop requires {"confirm": true}', 400)
                    return

                logger.info("Stopping main API server")
                result = run_command(f'svc -d {SERVICE_PATH}')

                if result['success']:
                    time.sleep(1)  # Wait for service to stop
                    status = get_service_status()
                    self._send_json({
                        'message': 'Stop command sent',
                        'running': status['running'],
                        'success': True
                    })
                else:
                    self._send_error_json(f"Failed to stop: {result['stderr']}", 500)

            # Route: POST /restart
            elif path == '/restart':
                if not confirm:
                    self._send_error_json('Restart requires {"confirm": true}', 400)
                    return

                logger.info("Restarting main API server")
                # Use svc -k (SIGKILL) + svc -u to force restart (SIGTERM may not work reliably)
                run_command(f'svc -k {SERVICE_PATH}')
                time.sleep(1)
                result = run_command(f'svc -u {SERVICE_PATH}')

                if result['success']:
                    time.sleep(2)  # Wait for service to restart
                    status = get_service_status()
                    self._send_json({
                        'message': 'Restart completed',
                        'running': status['running'],
                        'pid': status['pid'],
                        'uptime_seconds': status['uptime_seconds'],
                        'success': True
                    })
                else:
                    self._send_error_json(f"Failed to restart: {result['stderr']}", 500)

            # Route: POST /upgrade
            elif path == '/upgrade':
                if not confirm:
                    self._send_error_json('Upgrade requires {"confirm": true}', 400)
                    return

                logger.info("Upgrading main API server")

                # Check if git repo exists
                if not os.path.exists(os.path.join(INSTALL_DIR, '.git')):
                    self._send_error_json('Not a git repository - manual upgrade required', 400)
                    return

                # Git pull
                pull_result = run_command(f'cd {INSTALL_DIR} && git pull', timeout=60)

                if not pull_result['success']:
                    self._send_error_json(f"Git pull failed: {pull_result['stderr']}", 500)
                    return

                # Restart service (use SIGKILL + svc -u for reliability)
                run_command(f'svc -k {SERVICE_PATH}')
                time.sleep(1)
                run_command(f'svc -u {SERVICE_PATH}')
                time.sleep(2)

                status = get_service_status()
                self._send_json({
                    'message': 'Upgrade completed',
                    'git_output': pull_result['stdout'],
                    'running': status['running'],
                    'pid': status['pid'],
                    'success': True
                })

            else:
                self._send_error_json('Not found', 404)

        except Exception as e:
            logger.error(f"Error handling POST request: {e}\n{traceback.format_exc()}")
            self._send_error_json(str(e))

    def log_message(self, format, *args):
        """Override to use custom logger"""
        logger.info(f"{self.client_address[0]} - {format % args}")


def run_server(host=DEFAULT_HOST, port=DEFAULT_PORT):
    """Run the HTTP server"""
    try:
        # Set start time
        ControlAPIHandler.start_time = time.time()

        # Create server
        server = HTTPServer((host, port), ControlAPIHandler)
        logger.info(f"Starting Victron DBus API Control Server v{VERSION} on {host}:{port}")
        logger.info(f"Managing service: {SERVICE_PATH}")

        # Handle shutdown gracefully
        def signal_handler(sig, frame):
            logger.info("Shutting down control server (signal)...")
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

    parser = argparse.ArgumentParser(description='Victron DBus API Control Server')
    parser.add_argument('--host', default=DEFAULT_HOST, help=f'Host to bind to (default: {DEFAULT_HOST})')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help=f'Port to listen on (default: {DEFAULT_PORT})')

    args = parser.parse_args()

    run_server(args.host, args.port)
