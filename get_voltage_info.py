#!/usr/bin/env python3
"""
Victron Voltage Information Script
Queries all devices for voltage readings (DC and AC)
"""

import requests
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

API_BASE_URL = "http://192.168.88.77:8088"


def get_services() -> List[str]:
    """Get all available Victron services"""
    response = requests.get(f"{API_BASE_URL}/services")
    data = response.json()
    return data.get('services', [])


def get_value(service: str, path: str) -> Optional[Any]:
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
    except Exception:
        return None


def get_dc_voltages(service: str) -> Dict[str, Any]:
    """Get DC voltage readings from a service"""
    voltages = {}

    # Common DC voltage paths
    dc_paths = [
        '/Dc/0/Voltage',
        '/Dc/1/Voltage',
        '/Dc/Battery/Voltage',
        '/Dc/System/Voltage',
        '/Dc/Pv/Voltage',
    ]

    for path in dc_paths:
        value = get_value(service, path)
        if value is not None:
            voltages[path] = value

    return voltages


def get_ac_voltages(service: str) -> Dict[str, Any]:
    """Get AC voltage readings from a service"""
    voltages = {}

    # Common AC voltage paths for all three phases
    ac_paths = [
        # Output voltages
        '/Ac/Out/L1/V',
        '/Ac/Out/L2/V',
        '/Ac/Out/L3/V',
        # Input voltages
        '/Ac/In/1/L1/V',
        '/Ac/In/1/L2/V',
        '/Ac/In/1/L3/V',
        '/Ac/In/2/L1/V',
        '/Ac/In/2/L2/V',
        '/Ac/In/2/L3/V',
        # Generic AC voltages (for meters, etc)
        '/Ac/L1/Voltage',
        '/Ac/L2/Voltage',
        '/Ac/L3/Voltage',
        # ActiveIn voltages
        '/Ac/ActiveIn/L1/V',
        '/Ac/ActiveIn/L2/V',
        '/Ac/ActiveIn/L3/V',
    ]

    for path in ac_paths:
        value = get_value(service, path)
        if value is not None:
            voltages[path] = value

    return voltages


def get_voltage_settings() -> Dict[str, Any]:
    """Get voltage-related settings"""
    settings = {}

    voltage_settings_paths = [
        '/Settings/SystemSetup/MaxChargeVoltage',
        '/Settings/SystemSetup/SharedVoltageSense',
        '/Settings/Generator0/BatteryVoltage/StartValue',
        '/Settings/Generator0/BatteryVoltage/StopValue',
        '/Settings/Alarm/Vebus/HighDcVoltage',
    ]

    for path in voltage_settings_paths:
        value = get_value('com.victronenergy.settings', path)
        if value is not None:
            settings[path] = value

    return settings


def get_device_name(service: str) -> str:
    """Get human-readable device name"""
    product_name = get_value(service, '/ProductName')
    custom_name = get_value(service, '/CustomName')

    if custom_name:
        return f"{product_name} ({custom_name})" if product_name else custom_name
    return product_name or service.split('.')[-1]


def main():
    print("=" * 80)
    print("Victron Voltage Information")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    all_voltage_data = {
        'timestamp': datetime.now().isoformat(),
        'devices': [],
        'settings': {}
    }

    # Get all services
    services = get_services()

    # Filter for device services
    device_services = [s for s in services if s.startswith('com.victronenergy.')
                      and s != 'com.victronenergy.settings']

    print("DC Voltages:")
    print("-" * 80)

    dc_found = False
    for service in sorted(device_services):
        dc_voltages = get_dc_voltages(service)
        if dc_voltages:
            dc_found = True
            device_name = get_device_name(service)
            print(f"\n{device_name}")
            print(f"  Service: {service}")
            for path, value in dc_voltages.items():
                if isinstance(value, (int, float)):
                    print(f"  {path}: {value:.2f} V")
                else:
                    print(f"  {path}: {value}")

            all_voltage_data['devices'].append({
                'service': service,
                'device_name': device_name,
                'dc_voltages': dc_voltages
            })

    if not dc_found:
        print("  No DC voltages found")

    print()
    print("AC Voltages:")
    print("-" * 80)

    ac_found = False
    for service in sorted(device_services):
        ac_voltages = get_ac_voltages(service)
        if ac_voltages:
            ac_found = True
            device_name = get_device_name(service)
            print(f"\n{device_name}")
            print(f"  Service: {service}")
            for path, value in ac_voltages.items():
                if isinstance(value, (int, float)):
                    print(f"  {path}: {value:.2f} V")
                else:
                    print(f"  {path}: {value}")

            # Update or add device info with AC voltages
            existing = next((d for d in all_voltage_data['devices']
                           if d['service'] == service), None)
            if existing:
                existing['ac_voltages'] = ac_voltages
            else:
                all_voltage_data['devices'].append({
                    'service': service,
                    'device_name': device_name,
                    'ac_voltages': ac_voltages
                })

    if not ac_found:
        print("  No AC voltages found")

    print()
    print("Voltage Settings:")
    print("-" * 80)

    voltage_settings = get_voltage_settings()
    if voltage_settings:
        for path, value in voltage_settings.items():
            print(f"  {path}: {value}")
            all_voltage_data['settings'][path] = value
    else:
        print("  No voltage settings found")

    print()
    print("=" * 80)
    print("Summary:")
    print("-" * 80)

    dc_count = sum(1 for d in all_voltage_data['devices'] if 'dc_voltages' in d)
    ac_count = sum(1 for d in all_voltage_data['devices'] if 'ac_voltages' in d)

    print(f"Devices with DC voltage: {dc_count}")
    print(f"Devices with AC voltage: {ac_count}")
    print(f"Voltage settings: {len(voltage_settings)}")
    print()

    # Export to JSON
    with open('voltage_info.json', 'w') as f:
        json.dump(all_voltage_data, f, indent=2)

    print("Voltage information exported to: voltage_info.json")
    print()


if __name__ == '__main__':
    main()
