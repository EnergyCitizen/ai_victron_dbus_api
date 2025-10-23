# Parallel Inverter Operation

Understanding how multiple inverters synchronize and share load in Victron systems.

---

## How Synchronization Works

### The Three Pillars of Sync

For inverters to work in parallel, they must match on three parameters:

**1. Voltage** (within 1V)
**2. Frequency** (within 0.05Hz)
**3. Phase** (0° or 120°/240° for 3-phase)

---

## Voltage Matching

### Droop Control Mechanism

**How It Works**:
```
Output Voltage = Nominal Voltage - (Current × Droop Resistance)

Example:
- Nominal: 230V
- Droop: 0.5Ω
- Current: 10A
- Output: 230V - (10A × 0.5Ω) = 225V
```

**Purpose**: Allows load sharing without communication between units

**Visual**:
```
Unit 1:                 Unit 2:
230V ─┐                 230V ─┐
      │╲                      │╲
      │ ╲                     │ ╲
225V  │  ╲                225V│  ╲
      │   ╲                   │   ╲
220V  └────┴─              220V└────┴─
      0A   20A                  0A   20A

Both units reach same voltage at same current (balanced)
```

---

## Load Sharing Mechanisms

### Method 1: Master-Slave (VE.Bus)

**Configuration**:
- One unit designated "Master"
- Other units are "Slaves"
- Master controls all units via VE.Bus

**Advantages**:
- Perfect synchronization
- Balanced load sharing
- Single point of control

**Disadvantages**:
- Requires VE.Bus connection
- All units must be same model/firmware

**Example** (Einstein system should use this):
```
Master (MultiRS1) ──VE.Bus──> Slave (MultiRS2)
       │                           │
       └───────AC Output───────────┘
                   │
                 Load
```

---

### Method 2: Grid-Following (AC-Coupled)

**Configuration**:
- Multiple units on same AC bus
- All follow grid voltage/frequency
- No direct communication

**Advantages**:
- Mix different inverter models
- Simpler wiring
- Redundancy (one fails, others continue)

**Disadvantages**:
- Imperfect load sharing
- Requires stable grid reference
- Can't operate off-grid

---

## Load Balance Calculation

### Expected vs Actual

**Expected** (for identical units):
```
Load: 1000W
Unit 1: 500W (50%)
Unit 2: 500W (50%)
Imbalance: 0%
```

**Acceptable** (10% tolerance):
```
Load: 1000W
Unit 1: 450W (45%)
Unit 2: 550W (55%)
Imbalance: 10% ✅
```

**Problem** (>20% imbalance):
```
Load: 1000W
Unit 1: 200W (20%)
Unit 2: 800W (80%)
Imbalance: 60% ❌
```

**Formula**:
```python
imbalance = abs(power1 - power2) / (power1 + power2) * 100

# Example:
power1 = 200
power2 = 800
imbalance = abs(200 - 800) / (200 + 800) * 100 = 60%
```

---

## Einstein System Case Study

### Configuration

**System**:
- 2× Multi RS Solar 48/6000VA/100A
- Both on Phase 3 (L3)
- Same DC bus (52.56V)

**Problem Detected**:
```
Unit 1 (MultiRS1): -46W (-0.5A) ← Supplying power
Unit 2 (MultiRS2): +413W (+3.3A) ← Drawing power
Total Load: 367W
Imbalance: 78% ❌
```

### Root Cause Analysis

**Configuration Mismatch**:

| Parameter | Unit 1 | Unit 2 | Impact |
|-----------|--------|--------|--------|
| ESS Mode | Mode 1 (Charger) | Mode 3 (Inverter) | Unit 1 avoids inverting |
| Min SOC | 65% | 5% | Unit 1 stops earlier |
| Current Limit | 37.5A | 50.0A | Unit 1 limited |
| Energy Meter | Enabled | Disabled | Unit 1 grid-aware |

**Why It Causes Imbalance**:
- ESS Mode 1 = "Charge battery, minimize inverting"
- ESS Mode 3 = "Active inverter, handle loads"
- Unit 1 configured as charger → avoids supplying load
- Unit 2 handles all inverting → overloaded

### Solution

**Fix**: Harmonize ESS modes
```
Before:
  Unit 1: ESS Mode 1 (Charger)
  Unit 2: ESS Mode 3 (Inverter)

After:
  Unit 1: ESS Mode 3 (Inverter)
  Unit 2: ESS Mode 3 (Inverter)
```

**Expected Result**:
```
Unit 1: ~184W (50%)
Unit 2: ~184W (50%)
Imbalance: 0%
```

---

## Synchronization Validation

### Voltage Check

**Command**:
```bash
# Query AC output voltage from both units
curl "http://SITE/value?service=...multi...vi1...&path=/Ac/Out/L3/V"
curl "http://SITE/value?service=...multi...vi2...&path=/Ac/Out/L3/V"
```

**Expected**:
```
Unit 1: 225.2V
Unit 2: 225.3V
Difference: 0.1V ✅ (<1V threshold)
```

**Problem**:
```
Unit 1: 225.2V
Unit 2: 228.7V
Difference: 3.5V ❌ (>1V threshold)
```

---

### Frequency Check

**Command**:
```bash
curl "http://SITE/value?service=...multi...vi1...&path=/Ac/Out/L3/F"
curl "http://SITE/value?service=...multi...vi2...&path=/Ac/Out/L3/F"
```

**Expected**:
```
Unit 1: 50.00Hz
Unit 2: 50.00Hz
Difference: 0.00Hz ✅ (perfect)
```

**Problem**:
```
Unit 1: 50.00Hz
Unit 2: 50.12Hz
Difference: 0.12Hz ❌ (>0.05Hz threshold)
```

---

## Common Issues

### Issue 1: Circulating Current

**Symptom**: One unit shows +500W, other shows -500W, but load is 0W

**Cause**: Phase mismatch or voltage difference

**Detection**:
```python
if (power1 > 0) and (power2 < 0) and (power1 + power2 ≈ 0):
    problem = "Circulating current - units fighting each other"
```

**Fix**:
1. Check phase alignment (wiring)
2. Verify voltage droop settings
3. Check frequency synchronization

---

### Issue 2: One Unit Maxed Out

**Symptom**: Unit 1 at 100% capacity, Unit 2 at 30%

**Cause**: Current limit mismatch

**Detection**:
```python
if (power1 / rated_power1 > 0.95) and (power1 + power2 < total_rated_power):
    problem = "Unit 1 hitting current limit before load is shared"
```

**Fix**:
1. Increase Unit 1 current limit
2. Or reduce Unit 2 current limit (balance them)

---

### Issue 3: Random Imbalance

**Symptom**: Load sharing changes every minute

**Cause**: Unstable grid or poor droop settings

**Detection**:
```python
if std_dev(power_ratio) > 0.15:  # High variation
    problem = "Unstable load sharing - check grid stability"
```

**Fix**:
1. Verify grid voltage/frequency stable
2. Check droop settings (may need adjustment)
3. Enable "Weak AC" mode if on generator

---

## Agent Monitoring Pattern

### Real-Time Check

```python
def check_parallel_balance(site_ip):
    """Monitor parallel inverter balance"""

    # Query both units
    power1 = get_power(site_ip, unit=1)
    power2 = get_power(site_ip, unit=2)

    total = power1 + power2
    if total == 0:
        return "No load, cannot assess balance"

    # Calculate balance
    ratio1 = power1 / total * 100
    ratio2 = power2 / total * 100
    imbalance = abs(ratio1 - ratio2)

    # Assess
    if imbalance < 10:
        status = "Balanced"
        emoji = "✅"
    elif imbalance < 20:
        status = "Minor Imbalance"
        emoji = "🟡"
    else:
        status = "Imbalanced"
        emoji = "❌"

    return f"{emoji} Load: {total}W, Unit1: {ratio1:.0f}%, Unit2: {ratio2:.0f}%, Imbalance: {imbalance:.0f}%"
```

---

## Related Documentation

**Troubleshooting**:
- [Inverter Load Imbalance](../how-to-guides/troubleshooting/inverter-load-imbalance.md)

**Validation**:
- [Verify Synchronization](../how-to-guides/validation/verify-synchronization.md)
- [Validate New Installation](../tutorials/01-validate-new-installation.md)

**Concepts**:
- [ESS Modes Explained](./ess-modes-explained.md)

**Reference**:
- [ESS Mode Reference](../reference/ess-modes.md)

---

**Made in Ukraine 🇺🇦 with love by EnergyCitizen**
