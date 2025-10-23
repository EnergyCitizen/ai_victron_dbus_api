# Natural Language Queries

Guide for implementing conversational interfaces that let users ask about Victron systems in plain English.

---

## User Story

**As Mauk**, I want users to ask my AI agent questions in natural language (not write code), so that the agent is accessible to non-technical users.

---

## 2025 UX Pattern

**Old Way** (Python code):
```python
response = requests.get(
    "http://192.168.88.77:8088/value",
    params={"service": "com.victronenergy.battery.socketcan_can0", "path": "/Soc"}
)
print(f"SOC: {response.json()['value']}%")
```

**New Way** (Conversational):
```
User: "What's the battery level at Site 3?"
Agent: "Site 3 battery is at 73%, charging at 15A. Should reach 90% in about 2 hours."
```

---

## Query Pattern Library

### Pattern 1: Simple Value Query

**User Query Variations**:
- "What's the battery level?"
- "Show me SOC"
- "How charged is the battery?"
- "Battery percentage?"

**Agent Understanding**:
```
Intent: GET_BATTERY_SOC
Entity: battery_level
Site: <from context or ask>
```

**Agent Actions**:
1. Query `/Soc` from battery service
2. Optionally query `/Dc/0/Current` for context (charging/discharging)
3. Format natural response

**Response Template**:
```
"Battery is at {soc}%, {status}"

Where status:
  - If current > 0: "charging at {current}A"
  - If current < 0: "discharging at {abs(current)}A"
  - If current == 0: "idle"
```

**Example Implementation**:
<details>
<summary>Click to expand</summary>

```python
def handle_battery_soc_query(site, context):
    """Handle variations of 'what's the battery level'"""

    # Get SOC
    soc = api_get_value(site, 'battery.socketcan_can0', '/Soc')

    # Get current for context
    current = api_get_value(site, 'battery.socketcan_can0', '/Dc/0/Current')

    # Format status
    if current > 1:
        status = f"charging at {current:.1f}A"
        # Estimate time to full
        capacity_remaining = (100 - soc) * capacity_ah / 100
        hours_to_full = capacity_remaining / current
        status += f". Should reach 100% in about {hours_to_full:.1f} hours"
    elif current < -1:
        status = f"discharging at {abs(current):.1f}A"
        # Estimate time to empty
        capacity_available = soc * capacity_ah / 100
        hours_to_empty = capacity_available / abs(current)
        status += f". About {hours_to_empty:.1f} hours remaining at current load"
    else:
        status = "idle"

    return f"{site.name} battery is at {soc:.0f}%, {status}."
```

</details>

---

### Pattern 2: Comparison Query

**User Query Variations**:
- "Which site has the lowest battery?"
- "Compare battery levels across all sites"
- "Show me batteries below 30%"
- "Rank sites by SOC"

**Agent Understanding**:
```
Intent: COMPARE_METRIC
Metric: battery_soc
Scope: all_sites
Filter: <optional threshold>
Sort: ascending
```

**Agent Actions**:
1. Query `/Soc` for all sites (parallel)
2. Sort by SOC (ascending for "lowest")
3. Apply filter if specified (e.g., <30%)
4. Format as ranked list

**Response Template**:
```
"Battery levels across {count} sites:

{rank}. {site}: {soc}% {status_emoji}
...

{summary}"
```

**Example Response**:
```
"Battery levels across 12 sites (lowest first):

1. Site Charlie: 18% 🔴 (Critical - load shedding advised)
2. Site Delta: 24% 🟡 (Low - monitor closely)
3. Site Bravo: 35% 🟡
4. Site Echo: 52% 🟢
5. Site Alpha: 67% 🟢
... [7 more sites 70-95%]

Summary: 1 site critical, 2 sites low, 9 sites healthy."
```

---

### Pattern 3: Status Query

**User Query Variations**:
- "Is everything OK at Site 5?"
- "System status for Site 5"
- "How's Site 5 doing?"
- "Check Site 5"

**Agent Understanding**:
```
Intent: GET_SYSTEM_STATUS
Site: Site 5
Detail_Level: summary
```

**Agent Actions**:
1. Check critical metrics: SOC, voltage, grid, alarms
2. Assess overall health score
3. Provide summary or detailed report

**Response Template** (Summary):
```
"{site} status: {overall_status}

{status_emoji} Battery: {soc}% SOC, {soh}% SOH
{status_emoji} Grid: {grid_status}
{status_emoji} Solar: {solar_power}W
{status_emoji} Alarms: {alarm_count}

{action_needed}"
```

**Example Response**:
```
"Site 5 status: ALL OK ✅

✅ Battery: 73% SOC, 96% SOH (healthy)
✅ Grid: Connected, 229V, 50.0Hz
✅ Solar: 1,850W production
✅ Alarms: None active

No action needed. System operating normally."
```

**Example Response** (Issue Detected):
```
"Site 5 status: ATTENTION NEEDED ⚠️

✅ Battery: 45% SOC (low but OK), 82% SOH (degrading)
🟡 Grid: Frequency 50.3Hz (slightly high, monitor)
❌ Solar: MPPT tracker 2 offline (0W, should be ~400W)
⚠️  Alarms: 1 active (PvIsolation)

Action: Check MPPT tracker 2 - possible PV wiring issue or panel fault.

Shall I create a service ticket?"
```

---

### Pattern 4: Time-Based Query

**User Query Variations**:
- "Show me solar production today"
- "Battery SOC over the last 24 hours"
- "Grid outages this week"
- "Compare this month vs last month"

**Agent Understanding**:
```
Intent: GET_HISTORICAL_DATA
Metric: solar_production / battery_soc / grid_outages
Time_Range: today / 24h / this_week / this_month
Comparison: <optional: vs last month>
```

**Agent Actions**:
1. Query historical database (not real-time API)
2. Aggregate data for time range
3. Compare if requested
4. Visualize trend

**Response Template**:
```
"{metric} {time_range}:

{visualization}

{summary}
{comparison if requested}"
```

**Example Response**:
```
"Solar production today:

Hour-by-hour:
06:00  ▁▁▁▁  120W
09:00  ▃▃▃▃▃  850W
12:00  ██████  2,100W (peak)
15:00  ▅▅▅▅▅  1,450W
18:00  ▂▂▂▂  340W

Total: 18.4 kWh

Compared to yesterday (19.8 kWh): -7% (slightly cloudy)
Compared to 30-day average (17.2 kWh): +7% (above average)"
```

---

### Pattern 5: Diagnostic Query

**User Query Variations**:
- "Why is Site 7's battery not charging?"
- "What's wrong with Site 3?"
- "Diagnose low solar output at Site 9"
- "Explain the high voltage alarm"

**Agent Understanding**:
```
Intent: DIAGNOSE_ISSUE
Problem: battery_not_charging / low_solar / high_voltage_alarm
Site: Site 7/3/9
```

**Agent Actions** (Guided Diagnosis):
1. Collect relevant metrics for the issue type
2. Check related alarms
3. Analyze patterns
4. Determine root cause
5. Provide step-by-step resolution

**Response Template**:
```
"I've diagnosed {site}. Here's what I found:

**Problem Confirmed**: {issue_description}

**Root Cause**: {cause}

**Why This Happens**: {explanation}

**Resolution Steps**:
1. {step_1}
2. {step_2}
3. {step_3}

{expected_outcome}

Would you like me to {follow_up_action}?"
```

**Example** (see [battery-not-charging.md](../../../installer/how-to-guides/troubleshooting/battery-not-charging.md) for full example)

---

### Pattern 6: Predictive Query

**User Query Variations**:
- "When will I need to replace the battery?"
- "Predict solar production tomorrow"
- "How long until battery is full?"
- "When will the grid outage end?" (if pattern detected)

**Agent Understanding**:
```
Intent: PREDICT_FUTURE
Event: battery_replacement / solar_production / battery_full
Time_Horizon: tomorrow / next_week / months
```

**Agent Actions**:
1. Collect historical trends
2. Apply prediction model
3. Calculate time estimate
4. Provide confidence level

**Response Template**:
```
"Prediction: {event} in {time_estimate}

**Based On**:
- {trend_1}
- {trend_2}

**Confidence**: {confidence_level}

{caveats}"
```

**Example**:
```
"Based on current degradation rate (2.0%/month), Site Alpha's battery will reach
 the 70% replacement threshold in approximately 6 months (April 2026).

**Based On**:
- 30 days of SOH tracking
- Current SOH: 82%
- Degradation rate: 2.0%/month (10× normal)

**Confidence**: Medium (need 60+ days data for high confidence)

**Caveat**: If temperature is reduced (currently 42°C), degradation may slow.
 I'll update this prediction as more data becomes available."
```

---

## Prompt Engineering for Conversational Queries

### System Prompt Template

```
You are a Victron energy system monitoring assistant. You help users understand
their solar, battery, and inverter systems by analyzing real-time data from the
Victron DBus API.

**Your Capabilities**:
- Query battery metrics (SOC, SOH, voltage, current, temperature)
- Monitor grid connection (voltage, frequency, power)
- Track solar production (power, daily yield)
- Detect alarms and explain them in plain language
- Predict battery replacement needs
- Compare performance across multiple sites

**Your Personality**:
- Helpful and proactive
- Explain technical concepts simply
- Always provide context (not just numbers)
- Suggest actions when issues detected
- Use emojis sparingly for status indicators

**Response Format**:
- Start with direct answer
- Add context if helpful
- Offer follow-up actions
- Keep responses concise (<200 words unless detail requested)

**Safety**:
- Flag critical alarms immediately (🚨)
- Explain risks clearly
- Never suggest actions that could damage equipment
- Recommend professional help for serious issues
```

---

### Intent Classification

**Common Intents** (train your model on these):

| User Query | Intent | Required Data |
|------------|--------|---------------|
| "What's the battery level?" | GET_VALUE | SOC |
| "Is everything OK?" | SYSTEM_STATUS | SOC, voltage, grid, alarms |
| "Why isn't it charging?" | DIAGNOSE_ISSUE | Current, state, alarms, temp |
| "When to replace battery?" | PREDICT_EVENT | SOH history, degradation rate |
| "Compare sites" | COMPARE_METRICS | Same metric across sites |
| "Show me alarms" | LIST_ALARMS | All active alarms |
| "Explain [alarm]" | EXPLAIN_CONCEPT | Alarm context, meaning |

---

### Entity Extraction

**Sites**:
- "Site 3", "Site Alpha", "installation #7"
- "all sites", "my sites", "everything"

**Metrics**:
- "battery level" → SOC
- "battery health" → SOH
- "voltage" → Dc/0/Voltage
- "grid power" → Ac/Grid/L1/Power
- "solar production" → Yield/Power

**Time Ranges**:
- "today", "yesterday", "last week"
- "last 24 hours", "this month"

---

### Few-Shot Examples for Training

**Example 1**:
```
User: "Battery level at Site 3?"
Agent: "Site 3 battery is at 67%, discharging at 8A. About 5 hours remaining at current load."

[Reasoning: Queried SOC (67%), Current (-8A = discharging), calculated time remaining]
```

**Example 2**:
```
User: "Everything OK at Site 5?"
Agent: "Site 5 is operating normally ✅
        - Battery: 81% SOC, healthy
        - Grid: Connected, 228V
        - Solar: 1.2kW production
        - No alarms"

[Reasoning: System status intent → check SOC, grid voltage, solar power, alarms → all OK]
```

**Example 3**:
```
User: "Why low solar at Site 9?"
Agent: "Site 9 solar is only 450W (expected ~2kW for this time).

        Issue: MPPT tracker 2 is offline (0W output).

        Possible causes:
        1. PV array disconnected (check combiner box)
        2. VE.Can communication lost (check cable)
        3. MPPT fault (check error codes)

        Recommendation: Check MPPT tracker 2 connections. Shall I create a service ticket?"

[Reasoning: Diagnostic intent → compare current (450W) vs expected (2kW) → found MPPT offline → explain causes]
```

---

## Implementation Pattern

### Step 1: Parse User Intent

<details>
<summary>Click to expand code</summary>

```python
from typing import Dict, Optional
import re

class IntentParser:
    """Parse natural language queries into structured intents"""

    INTENT_PATTERNS = {
        'GET_VALUE': [
            r'what.*battery level',
            r'show.*soc',
            r'battery.*percentage',
            r'how.*charged'
        ],
        'SYSTEM_STATUS': [
            r'everything.*ok',
            r'system status',
            r'how.*doing',
            r'check.*site'
        ],
        'DIAGNOSE_ISSUE': [
            r'why.*not charging',
            r'what.*wrong',
            r'diagnose.*',
            r'troubleshoot.*'
        ],
        'COMPARE': [
            r'compare.*sites',
            r'which.*lowest',
            r'rank.*by',
            r'show.*all'
        ]
    }

    def parse(self, query: str) -> Dict:
        """
        Parse query into intent and entities

        Returns:
            {
                'intent': str,
                'entities': {
                    'metric': str,
                    'site': str,
                    'time_range': str
                }
            }
        """
        query_lower = query.lower()

        # Match intent
        intent = 'UNKNOWN'
        for intent_type, patterns in self.INTENT_PATTERNS.items():
            if any(re.search(pattern, query_lower) for pattern in patterns):
                intent = intent_type
                break

        # Extract entities
        entities = {
            'metric': self.extract_metric(query_lower),
            'site': self.extract_site(query),
            'time_range': self.extract_time_range(query_lower)
        }

        return {
            'intent': intent,
            'entities': entities,
            'original_query': query
        }

    def extract_metric(self, query: str) -> Optional[str]:
        """Extract metric from query"""
        metric_keywords = {
            'battery level': 'soc',
            'battery health': 'soh',
            'voltage': 'voltage',
            'solar': 'solar_power',
            'grid': 'grid_power',
            'temperature': 'temperature',
            'alarms': 'alarms'
        }

        for keyword, metric in metric_keywords.items():
            if keyword in query:
                return metric

        return None

    def extract_site(self, query: str) -> Optional[str]:
        """Extract site name/number from query"""
        # Match "Site 3", "Site Alpha", "installation 7"
        patterns = [
            r'site\s+(\w+)',
            r'installation\s+(\w+)',
            r'#(\d+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1)

        # "all sites" or "everything"
        if re.search(r'all sites|everything|all my', query, re.IGNORECASE):
            return 'all'

        return None

    def extract_time_range(self, query: str) -> Optional[str]:
        """Extract time range from query"""
        time_keywords = {
            'today': 'today',
            'yesterday': 'yesterday',
            'last 24 hours': '24h',
            'last week': 'week',
            'this month': 'month'
        }

        for keyword, time_range in time_keywords.items():
            if keyword in query:
                return time_range

        return None
```

</details>

---

### Step 2: Execute Query

<details>
<summary>Click to expand code</summary>

```python
class QueryExecutor:
    """Execute parsed intents by calling DBus API"""

    def execute(self, intent: str, entities: Dict, context: Dict) -> str:
        """
        Execute intent and return natural language response

        Args:
            intent: Intent type (GET_VALUE, SYSTEM_STATUS, etc.)
            entities: Extracted entities (metric, site, etc.)
            context: User context (previous queries, preferences)

        Returns:
            str: Natural language response
        """
        if intent == 'GET_VALUE':
            return self.handle_get_value(entities, context)
        elif intent == 'SYSTEM_STATUS':
            return self.handle_system_status(entities, context)
        elif intent == 'DIAGNOSE_ISSUE':
            return self.handle_diagnose(entities, context)
        elif intent == 'COMPARE':
            return self.handle_compare(entities, context)
        else:
            return "I'm not sure what you're asking. Could you rephrase?"

    def handle_get_value(self, entities: Dict, context: Dict) -> str:
        """Handle simple value queries"""
        metric = entities['metric']
        site = entities['site'] or context.get('current_site')

        if not site:
            return "Which site would you like me to check?"

        # Map metric to API call
        if metric == 'soc':
            value = self.api.get_battery_soc(site)
            current = self.api.get_battery_current(site)

            if current > 1:
                status = f"charging at {current:.1f}A"
            elif current < -1:
                status = f"discharging at {abs(current):.1f}A"
            else:
                status = "idle"

            return f"{site.name} battery is at {value:.0f}%, {status}."

        # ... handle other metrics

    def handle_system_status(self, entities: Dict, context: Dict) -> str:
        """Comprehensive system health check"""
        site = entities['site'] or context.get('current_site')

        # Collect metrics
        soc = self.api.get_battery_soc(site)
        soh = self.api.get_battery_soh(site)
        grid_v = self.api.get_grid_voltage(site)
        grid_f = self.api.get_grid_frequency(site)
        solar_p = self.api.get_solar_power(site)
        alarms = self.api.get_active_alarms(site)

        # Assess health
        issues = []
        if soc < 20:
            issues.append(f"🔴 Battery low ({soc:.0f}%)")
        if soh < 85:
            issues.append(f"🟡 Battery aging (SOH {soh:.0f}%)")
        if not (220 <= grid_v <= 240):
            issues.append(f"🟡 Grid voltage {grid_v:.0f}V (out of range)")
        if alarms:
            issues.append(f"⚠️  {len(alarms)} alarm(s) active")

        if not issues:
            return f"{site.name} status: ALL OK ✅\n\n" \
                   f"✅ Battery: {soc:.0f}% SOC, {soh:.0f}% SOH\n" \
                   f"✅ Grid: {grid_v:.0f}V, {grid_f:.1f}Hz\n" \
                   f"✅ Solar: {solar_p:.0f}W\n\n" \
                   f"System operating normally."
        else:
            issue_list = '\n'.join(issues)
            return f"{site.name} status: ATTENTION NEEDED ⚠️\n\n{issue_list}\n\n" \
                   f"Shall I provide detailed diagnosis?"
```

</details>

---

### Step 3: Generate Natural Response

**Key Principles**:

1. **Start with the answer**
   - Bad: "The SOC value from the battery service is 73 percentage points"
   - Good: "Battery is at 73%"

2. **Add context automatically**
   - Bad: "67%"
   - Good: "67%, discharging at 8A. About 5 hours remaining."

3. **Use status indicators**
   - ✅ Healthy/OK
   - 🟢 Good
   - 🟡 Warning
   - 🔴 Critical
   - ⚠️ Attention needed

4. **Offer next steps**
   - Bad: "SOC is 18%" (leaves user wondering what to do)
   - Good: "SOC is 18% (Critical). Load shedding advised. Shall I enable grid charging?"

5. **Explain technical terms**
   - Bad: "State = 4"
   - Good: "Inverter is in Absorption mode (State 4), will switch to Float in ~30 min"

---

## Testing Your Implementation

### Test Queries

**Basic**:
```
✅ "What's the battery level?" → Should return SOC with context
✅ "Show me Site 3" → Should ask "What would you like to know about Site 3?"
✅ "Solar production" → Should return current power or ask for time range
```

**Intermediate**:
```
✅ "Which sites are below 30%?" → Should list filtered sites
✅ "Is everything OK at Site 5?" → Should provide comprehensive status
✅ "Compare solar yield across all sites" → Should rank by kWh
```

**Advanced**:
```
✅ "Why is Site 7's battery not charging?" → Should diagnose root cause
✅ "When should I replace the battery at Site Alpha?" → Should predict based on SOH trend
✅ "Explain the high voltage alarm" → Should educate user on overvoltage protection
```

### Expected Response Quality

**Good Response Checklist**:
- [ ] Answers the question directly
- [ ] Provides relevant context
- [ ] Uses natural language (not technical jargon)
- [ ] Includes status emoji if applicable
- [ ] Offers follow-up action
- [ ] Explains "why", not just "what"
- [ ] <200 words unless detail requested

---

## Common Pitfalls

### ❌ Pitfall 1: Too Technical
```
Bad: "The DBus path /Dc/Battery/Soc returned value 67.3 of type float"
Good: "Battery is at 67%"
```

### ❌ Pitfall 2: No Context
```
Bad: "73%"
Good: "Battery is at 73%, charging. Will be full in 2 hours."
```

### ❌ Pitfall 3: Overwhelming Detail
```
Bad: "SOC: 67%, SOH: 96%, Voltage: 49.2V, Current: -8.3A, Power: -408W,
      Max Cell: 3.28V, Min Cell: 3.22V, Spread: 0.06V, Temp: 32°C..."

Good: "Battery is at 67%, discharging at 8A. Healthy (SOH 96%)."
      [If user asks for details, then show full metrics]
```

### ❌ Pitfall 4: No Follow-Up
```
Bad: "Battery is at 18%"  ← Leaves user wondering what to do

Good: "Battery is at 18% (Critical). Estimated 2 hours remaining.
       Should I enable grid charging?"
```

---

## Related Documentation

**Tutorials**:
- [Tutorial 01: First Monitoring Agent](../../tutorials/01-first-monitoring-agent.md) - Build basic query agent

**How-To Guides**:
- [Proactive Alerts](./proactive-alerts.md) - Agent-initiated notifications
- [Explain System State](./explain-system-state.md) - Comprehensive status responses

**Concepts**:
- [2025 AI UX Patterns](../../../shared/conversational-ai/2025-ux-patterns.md) - Conversational interface theory

**Reference**:
- [Query Templates](../../reference/conversational-patterns/query-templates.md) - Prompt patterns
- [Response Formats](../../reference/conversational-patterns/response-formats.md) - Formatting guidelines

---

**Made in Ukraine 🇺🇦 with love by EnergyCitizen**
