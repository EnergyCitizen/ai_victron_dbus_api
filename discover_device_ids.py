#!/usr/bin/env python3
"""
Victron Device ID Discovery Script
Queries the DBus API server to discover all device IDs, instances, and serial numbers
"""

import requests
import json
from typing import Dict, List, Any

API_BASE_URL = "http://192.168.88.77:8088"


def get_services() -> List[str]:
    """Get all available Victron services"""
    response = requests.get(f"{API_BASE_URL}/services")
    data = response.json()
    return data.get('services', [])


def get_value(service: str, path: str) -> Any:
    """Get value from specific dbus path"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/value",
            params={'service': service, 'path': path},
            timeout=2
        )
        data = response.json()
        if data.get('success'):
            return data.get('value')
        return None
    except Exception as e:
        return None


def get_all_settings() -> Dict:
    """Get all settings"""
    response = requests.get(f"{API_BASE_URL}/settings")
    data = response.json()
    return data.get('settings', {})


def discover_device_info(service: str) -> Dict[str, Any]:
    """Discover device information for a service"""
    info = {
        'service': service,
        'device_instance': None,
        'product_id': None,
        'product_name': None,
        'serial': None,
        'firmware_version': None,
        'custom_name': None,
        'connection': None,
        'vrm_instance': None
    }

    # Common paths to check
    paths_to_check = [
        ('/DeviceInstance', 'device_instance'),
        ('/ProductId', 'product_id'),
        ('/ProductName', 'product_name'),
        ('/Serial', 'serial'),
        ('/FirmwareVersion', 'firmware_version'),
        ('/CustomName', 'custom_name'),
        ('/Mgmt/Connection', 'connection'),
        ('/DeviceType', 'device_type'),
        ('/Ac/ActiveIn/Source', 'active_input'),
    ]

    for path, key in paths_to_check:
        value = get_value(service, path)
        if value is not None:
            info[key] = value

    return info


def extract_device_ids_from_settings() -> Dict[str, Dict]:
    """Extract device IDs from settings paths"""
    settings = get_all_settings()
    devices = {}

    for path in settings.keys():
        if path.startswith('/Settings/Devices/'):
            parts = path.split('/')
            if len(parts) >= 4:
                device_id = parts[3]
                if device_id not in devices:
                    devices[device_id] = {
                        'device_id': device_id,
                        'settings_paths': []
                    }
                devices[device_id]['settings_paths'].append(path)

                # Try to get ClassAndVrmInstance
                if 'ClassAndVrmInstance' in path:
                    value = settings.get(path, {}).get('Value')
                    if value:
                        devices[device_id]['class_vrm_instance'] = value

    return devices


def main():
    print("=" * 80)
    print("Victron Device ID Discovery")
    print("=" * 80)
    print()

    # 1. System Serial Number
    print("System Information:")
    print("-" * 80)
    system_serial = get_value('com.victronenergy.system', '/Serial')
    if system_serial:
        print(f"System Serial: {system_serial}")

    vrm_portal_id = get_value('com.victronenergy.settings', '/Settings/System/VrmPortalId')
    if vrm_portal_id:
        print(f"VRM Portal ID: {vrm_portal_id}")
    print()

    # 2. Discover all services and their device info
    print("Device Services:")
    print("-" * 80)
    services = get_services()

    device_services = []
    for service in services:
        if service.startswith('com.victronenergy.') and service != 'com.victronenergy.settings':
            device_services.append(service)

    devices_info = []
    for service in sorted(device_services):
        info = discover_device_info(service)
        if any(v is not None for k, v in info.items() if k != 'service'):
            devices_info.append(info)

    # Print device information
    for info in devices_info:
        print(f"\nService: {info['service']}")
        for key, value in info.items():
            if key != 'service' and value is not None:
                print(f"  {key}: {value}")

    print()

    # 3. Extract device IDs from settings
    print("Device IDs from Settings:")
    print("-" * 80)
    settings_devices = extract_device_ids_from_settings()

    for device_id, device_info in sorted(settings_devices.items()):
        print(f"\nDevice ID: {device_id}")
        if 'class_vrm_instance' in device_info:
            print(f"  Class/VRM Instance: {device_info['class_vrm_instance']}")
        print(f"  Settings paths: {len(device_info['settings_paths'])}")

    print()
    print("=" * 80)
    print("Summary:")
    print("-" * 80)
    print(f"Total Services: {len(device_services)}")
    print(f"Services with Device Info: {len(devices_info)}")
    print(f"Device IDs in Settings: {len(settings_devices)}")
    print()

    # Export to JSON
    output = {
        'system': {
            'serial': system_serial,
            'vrm_portal_id': vrm_portal_id
        },
        'device_services': devices_info,
        'settings_devices': settings_devices
    }

    with open('device_ids.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("Device information exported to: device_ids.json")
    print()


if __name__ == '__main__':
    main()
