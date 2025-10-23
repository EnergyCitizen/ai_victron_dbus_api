# Troubleshooting Matrix

Quick lookup table for common Victron system issues and their solutions.

---

## Battery Issues

| Symptom | First Check | Common Cause | Guide Link |
|---------|-------------|--------------|------------|
| Battery not charging | Current = 0A? | Temperature out of range | [Battery Not Charging](../how-to-guides/troubleshooting/battery-not-charging.md) |
| Battery not charging | ChargeBlocked alarm? | BMS protecting cells | [Battery Not Charging](../how-to-guides/troubleshooting/battery-not-charging.md) |
| Battery not charging | Grid voltage = 0V? | No AC input | [Battery Not Charging](../how-to-guides/troubleshooting/battery-not-charging.md) |
| Short backup time | SOH < 85%? | Battery degraded | [Detect Battery Degradation](../../ai-agent-developer/how-to-guides/anomaly-detection/detect-battery-degradation.md) |
| BMS offline | CAN connection? | Cable loose/wrong | [Validate Installation](../tutorials/01-validate-new-installation.md) |
| Cell imbalance | Spread > 0.10V? | Weak cell or aging | [Detect Cell Imbalance](../../ai-agent-developer/how-to-guides/anomaly-detection/detect-cell-imbalance.md) |
| Battery temperature high | Cooling fan working? | Fan failed | [Battery Not Charging](../how-to-guides/troubleshooting/battery-not-charging.md) |

---

## Grid Connection Issues

| Symptom | First Check | Common Cause | Guide Link |
|---------|-------------|--------------|------------|
| Grid lost alarm | Frequency in range? | Wrong grid code | [Grid Frequency Issues](../how-to-guides/troubleshooting/grid-frequency-issues.md) |
| Won't sync to grid | Grid code setting? | Code doesn't match | [Grid Frequency Issues](../how-to-guides/troubleshooting/grid-frequency-issues.md) |
| Frequent disconnects | Frequency stable? | Weak grid or generator | [Grid Frequency Issues](../how-to-guides/troubleshooting/grid-frequency-issues.md) |
| Voltage sag under load | DC cable size? | Undersized wiring | [Validate Installation](../tutorials/01-validate-new-installation.md) |
| Phase rotation error | Wiring L1/L2/L3? | Swapped phases | [Validate Installation](../tutorials/01-validate-new-installation.md) |

---

## Inverter Issues

| Symptom | First Check | Common Cause | Guide Link |
|---------|-------------|--------------|------------|
| Inverter overload | Load > capacity? | Too many devices | [Alarm Codes](./alarm-codes.md) |
| High temperature | Ventilation OK? | Poor airflow | [Alarm Codes](./alarm-codes.md) |
| Low voltage | Battery SOC < 20%? | Battery depleted | [Battery Not Charging](../how-to-guides/troubleshooting/battery-not-charging.md) |
| One inverter hot (parallel) | Load balance? | ESS mode mismatch | [Inverter Load Imbalance](../how-to-guides/troubleshooting/inverter-load-imbalance.md) |
| Circulating current | Voltage difference? | Sync issue | [Parallel Inverter Operation](../concepts/parallel-inverter-operation.md) |

---

## System Configuration Issues

| Symptom | First Check | Common Cause | Guide Link |
|---------|-------------|--------------|------------|
| System not visible in VRM | Network connected? | WiFi/Ethernet issue | [Validate Installation](../tutorials/01-validate-new-installation.md) |
| No solar charging | MPPT state? | Night or disconnected | [Validate Installation](../tutorials/01-validate-new-installation.md) |
| ESS not working | Grid meter detected? | Meter offline | [Validate Installation](../tutorials/01-validate-new-installation.md) |
| DVCC not limiting charge | DVCC enabled? | Setting not active | [Validate Installation](../tutorials/01-validate-new-installation.md) |

---

## Communication Issues

| Symptom | First Check | Common Cause | Guide Link |
|---------|-------------|--------------|------------|
| BMS connection lost | CAN cable? | Loose/damaged cable | [Alarm Codes](./alarm-codes.md) |
| VE.Bus error | Cable length? | Too long (>10m) | [Alarm Codes](./alarm-codes.md) |
| Modbus timeout | IP reachable? | Network issue | [Validate Installation](../tutorials/01-validate-new-installation.md) |
| API not responding | Cerbo powered? | Device offline | [Validate Installation](../tutorials/01-validate-new-installation.md) |

---

## Related Documentation

**How-To Guides**:
- [Battery Not Charging](../how-to-guides/troubleshooting/battery-not-charging.md)
- [Grid Frequency Issues](../how-to-guides/troubleshooting/grid-frequency-issues.md)
- [Inverter Load Imbalance](../how-to-guides/troubleshooting/inverter-load-imbalance.md)

**Reference**:
- [Alarm Codes](./alarm-codes.md)
- [State Codes](./state-codes.md)

---

**Made in Ukraine 🇺🇦 with love by EnergyCitizen**
