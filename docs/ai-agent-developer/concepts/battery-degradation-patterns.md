# Battery Degradation Patterns

Understanding how and why lithium batteries age, enabling better predictions and interventions.

---

## Chemistry Fundamentals

### LiFePO4 (Lithium Iron Phosphate) - Most Common

**Characteristics**:
- Nominal voltage: 3.2V per cell
- Very stable chemistry
- Excellent cycle life: 6,000-10,000 cycles
- Safe (no thermal runaway risk)
- Slow capacity fade

**Aging Curve**:
```
100% ─┐
      │╲
 90%  │ ╲___
      │     ╲___
 80%  │         ╲___
      │             ╲___
 70%  │                 ╲___
      └─────────────────────────
      0   2   4   6   8   10 years

Typical: 95% after 3 years, 85% after 7 years, 70% after 10 years
```

**Degradation Rate**: 2-5% per year (normal), accelerates after 70% SOH

---

## Primary Degradation Factors

### 1. Temperature (Most Critical)

**Arrhenius Law**: Reaction rate doubles every 10°C

| Temperature | Aging Rate | 10-Year Lifespan Becomes |
|-------------|------------|---------------------------|
| 15°C | 0.7× | 14 years |
| 25°C | 1× | 10 years |
| 35°C | 1.5× | 6.7 years |
| 45°C | 2.5× | 4 years |
| 55°C | 4× | 2.5 years |

**Why**: Heat accelerates:
- SEI (Solid Electrolyte Interface) growth
- Electrolyte decomposition
- Lithium plating
- Structural changes in cathode

**Agent Detection**:
```python
if avg_temp > 40:
    lifespan_reduction = (avg_temp - 25) * 0.06  # 6% per degree above 25°C
    alert = f"High temperature reducing lifespan by {lifespan_reduction*100:.0f}%"
```

---

### 2. Depth of Discharge (DoD)

**Cycle Life vs DoD**:
```
Cycles to 80% SOH:
- 100% DoD (0% → 100%): 3,000 cycles
-  80% DoD (10% → 90%): 5,000 cycles
-  60% DoD (20% → 80%): 8,000 cycles
-  40% DoD (30% → 70%): 15,000 cycles
```

**Why**: Deep discharge causes:
- Lithium plating on anode
- Copper dissolution
- Structural stress on cathode
- Electrolyte reduction

**Optimal Strategy**: Keep SOC between 20-80% for daily cycling

**Agent Recommendation**:
```python
if typical_soc_range > 80:  # Cycling from 10% to 90%
    recommendation = "Narrow SOC range to 30-80% to extend lifespan 40%"
```

---

### 3. C-Rate (Charge/Discharge Speed)

**C-Rate Definition**: 1C = full capacity in 1 hour

| C-Rate | Example (10kWh battery) | Lifespan Impact |
|--------|-------------------------|-----------------|
| 0.2C | 2kW (5 hours to full) | 1× (baseline) |
| 0.5C | 5kW (2 hours to full) | 0.9× |
| 1C | 10kW (1 hour to full) | 0.7× (-30%) |
| 2C | 20kW (30 min to full) | 0.5× (-50%) |

**Why**: High currents cause:
- Resistive heating (I²R losses)
- Lithium plating (charge)
- Dendrite formation
- Mechanical stress

**Agent Detection**:
```python
current = 50  # Amps
capacity = 174  # Ah
c_rate = current / capacity

if c_rate > 0.5:
    warning = f"C-rate {c_rate:.2f}C exceeds recommended 0.5C. Reduce power limits."
```

---

### 4. State of Charge (Storage)

**Calendar Aging** (battery at rest):

| Storage SOC | Aging Rate @ 25°C | Aging Rate @ 40°C |
|-------------|-------------------|-------------------|
| 100% SOC | 20%/year | 35%/year |
| 80% SOC | 10%/year | 20%/year |
| 50% SOC | 5%/year | 10%/year |
| 30% SOC | 4%/year | 8%/year |

**Why**: High SOC storage causes:
- Electrolyte oxidation at cathode
- SEI layer growth
- Gassing (pressure buildup)

**Recommendation**: Store at 50% SOC if not using for >1 month

---

## Degradation Mechanisms

### 1. SEI Layer Growth (Dominant)

**What**: Passivation layer on anode surface
**Impact**: Increases internal resistance, reduces capacity
**Rate**: Grows continuously, accelerated by heat and high SOC
**Detection**: Rising internal resistance, voltage drop under load

**Agent Pattern**:
```
IF (voltage_drop > 1V under 500W load) AND (battery_age > 3 years):
    likely_cause = "SEI layer growth (internal resistance increase)"
    recommendation = "Normal aging, monitor for further degradation"
```

---

### 2. Lithium Plating (High Current)

**What**: Metallic lithium deposits on anode during fast charging
**Impact**: Capacity loss, safety risk (dendrites)
**Cause**: Charging too fast, especially when cold (<10°C)
**Detection**: Capacity fade, low-temperature charging

**Agent Pattern**:
```
IF (charge_current > 0.5C) AND (temperature < 15°C):
    risk = "Lithium plating risk"
    action = "Reduce charge current or wait for battery to warm up"
```

---

### 3. Cell Imbalance (Manufacturing Variance)

**What**: Cells age at slightly different rates
**Impact**: Weakest cell limits pack capacity
**Cause**: Manufacturing variance, temperature gradients
**Detection**: Growing voltage spread between cells

**Progression**:
```
Year 1: 0.010V spread (all cells 3.320-3.330V)
Year 2: 0.030V spread (3.315-3.345V)
Year 3: 0.060V spread (3.300-3.360V)
Year 4: 0.100V spread (3.280-3.380V) ← Action needed
Year 5: 0.150V spread (3.250-3.400V) ← Critical
```

**Agent Alert**:
```python
if cell_spread > 0.10:
    months_to_failure = (0.15 - cell_spread) / (spread_growth_per_month)
    alert = f"Cell imbalance critical. Likely failure in {months_to_failure:.0f} months"
```

---

## Predictive Models

### Model 1: Linear SOH Degradation

**Assumption**: Constant degradation rate

```python
def predict_replacement_linear(current_soh, history, threshold=70):
    """
    Simple linear extrapolation
    Best for: Stable, well-maintained systems
    """
    rate = calculate_rate(history)  # %/month
    months = (current_soh - threshold) / rate
    return months
```

**Accuracy**: ±3 months for slow degradation (<0.3%/month)

---

### Model 2: Accelerating Degradation

**Assumption**: Degradation accelerates as SOH decreases

```python
def predict_replacement_exponential(current_soh, history, threshold=70):
    """
    Accounts for acceleration in late life
    Best for: Aging batteries (SOH <85%)
    """
    base_rate = calculate_rate(history)

    # Acceleration factor (increases as SOH drops)
    accel = 1 + ((100 - current_soh) / 100) * 0.5

    effective_rate = base_rate * accel
    months = (current_soh - threshold) / effective_rate
    return months * 0.85  # Conservative estimate
```

**Accuracy**: ±2 months for moderate degradation (0.3-0.8%/month)

---

### Model 3: Temperature-Corrected

**Assumption**: Temperature dominates aging rate

```python
def predict_with_temperature(current_soh, avg_temp, threshold=70):
    """
    Adjusts for operating temperature
    Best for: Hot climates, poor cooling
    """
    base_rate = 0.3  # %/month at 25°C

    # Temperature acceleration
    temp_factor = 2 ** ((avg_temp - 25) / 10)  # Doubles per 10°C

    adjusted_rate = base_rate * temp_factor
    months = (current_soh - threshold) / adjusted_rate
    return months
```

**Example**:
```
25°C environment: 10% degradation → 33 months remaining
35°C environment: 10% degradation → 22 months remaining (33% faster)
45°C environment: 10% degradation → 13 months remaining (60% faster)
```

---

## Intervention Strategies

### 1. Temperature Management

**Problem**: Battery at 45°C (2.5× aging rate)

**Interventions** (priority order):
1. Add/fix cooling fan ($200) → Save $10,000 lifespan
2. Improve ventilation (enclosure design)
3. Reduce charge current 20% (less heat generation)
4. Add thermal insulation (hot climates)
5. Relocate battery to cooler area

**ROI**: $200 investment → 40% lifespan extension → $8,000 savings

---

### 2. SOC Management

**Problem**: Battery cycling 10-95% daily (85% DoD)

**Interventions**:
1. Increase minimum SOC to 25% (reduce DoD to 70%)
2. Reduce maximum SOC to 85% (less stress)
3. Result: 40% lifespan extension

**Trade-off**: 30% less usable capacity, but battery lasts 40% longer

**Net**: Positive (ROI depends on electricity costs)

---

### 3. C-Rate Reduction

**Problem**: Charging at 1.2C (too fast)

**Interventions**:
1. Reduce inverter charge current limit
2. Increase battery bank size (same power, lower C-rate)
3. Stagger charging (if multiple batteries)

**Example**:
```
Before: 174Ah battery, 200A charging = 1.15C → 7-year lifespan
After: 200A limit → 150A = 0.86C → 9-year lifespan (+28%)
```

---

## Failure Prediction Accuracy

### Confidence Levels

**High Confidence** (±1 month):
- 90+ days of history
- Stable degradation rate
- Known operating conditions
- SOH 75-90%

**Medium Confidence** (±2 months):
- 30-90 days of history
- Moderate rate variation
- SOH 70-75% or 90-95%

**Low Confidence** (±4 months):
- <30 days of history
- High rate variation
- SOH <70% or >95%
- Recent changes (temperature, usage)

**Agent Response**:
```python
if data_points < 10:
    confidence = "low"
    message = "Need more data (only {data_points} samples). Check again in 2 weeks."
elif rate_variation > 0.2:
    confidence = "medium"
    message = "Degradation rate unstable. Prediction ±2 months."
else:
    confidence = "high"
    message = "Stable pattern. Prediction ±1 month."
```

---

## Related Documentation

**How-To Guides**:
- [Detect Battery Degradation](../how-to-guides/anomaly-detection/detect-battery-degradation.md)
- [Detect Cell Imbalance](../how-to-guides/anomaly-detection/detect-cell-imbalance.md)

**Tutorials**:
- [Build Battery Health Agent](../tutorials/02-battery-health-agent.md)

**Concepts**:
- [Why Monitor Batteries](./why-monitor-batteries.md)

**Reference**:
- [Battery Thresholds](../reference/thresholds/battery-thresholds.md)

---

**Made in Ukraine 🇺🇦 with love by EnergyCitizen**
