# Conversational AI UX Patterns (2025)

Modern UX patterns for building conversational AI agents that users love.

---

## Core Principles

### 1. Natural Language First

**Bad** (2020 approach):
> "Battery SOC: 75%, SOH: 92%, Cell spread: 0.08V"

**Good** (2025 approach):
> "Your battery is healthy (92% health), currently at 75% charge. Cells are well balanced. Everything looks good—no action needed."

**Why**: Users don't speak in acronyms. Translate technical data into human language.

---

### 2. Proactive, Not Reactive

**Bad**: Wait for user to notice problem and ask

**Good**: Agent alerts user before problem becomes critical
> "🔔 Heads up: Site Alpha's battery temperature has been averaging 42°C this week (8° above optimal). This could reduce lifespan by 30%. Should I investigate the cooling system?"

**Why**: Users don't monitor constantly. Agent should be the vigilant watcher.

---

### 3. Conversational Flow

**Bad** (command-response):
```
User: check battery site 5
Agent: SOC: 82%, SOH: 95%, Voltage: 51.2V, Temperature: 28C
User: is that good
Agent: Yes
```

**Good** (natural conversation):
```
User: How's Site 5 battery?
Agent: Site 5 is in great shape! Battery health is 95% (excellent for a 2-year-old system), currently at 82% charge, and temperature is a comfortable 28°C. Aging normally at 0.2% per month. I'd say you've got another 8-10 years before replacement. Want to see the trend chart?
```

**Why**: Anticipate follow-up questions, provide context

---

### 4. Show, Don't Just Tell

**Bad**:
> "Cell spread is 0.12V, which is above the 0.10V threshold"

**Good**:
> "Your battery cells are becoming imbalanced. Here's what I see:
>
> Highest cell: 3.335V (Cell 0101)
> Lowest cell: 3.215V (Cell 0204)
> Difference: 0.120V (⚠️ Warning level)
>
> **What this means**: Cell 0204 is consistently weaker. If this continues, it'll limit your battery capacity.
>
> **What to do**: Enable BMS balancing first. If spread doesn't improve in 2 weeks, that cell may need replacement."

**Why**: Visual representations and explanations beat raw numbers

---

## Pattern 1: Proactive Assistance

### When to Use
- Monitoring dashboards
- Fleet management
- Predictive maintenance

### Pattern

**Agent detects issue → Initiates conversation → Explains context → Offers solutions**

**Example**:
> "🔔 Alert: I've noticed something at Site Bravo.
>
> **What happened**: Battery SOH dropped from 88% to 82% in just one month—that's 10× faster than normal.
>
> **Why it matters**: At this rate, you'll need replacement in 6 months instead of the 18 months I originally predicted.
>
> **Likely cause**: Temperature has been running hot (42°C average, 8° above optimal).
>
> **What I recommend**:
> 1. Check the cooling fan—might be failing
> 2. Improve ventilation in battery enclosure
> 3. Reduce charge rate 20% to generate less heat
>
> Should I create a maintenance ticket?"

---

## Pattern 2: Guided Conversations

### When to Use
- Complex troubleshooting
- Multi-step processes
- Installation validation

### Pattern

**Agent asks clarifying questions → Narrows diagnosis → Provides specific solution**

**Example**:
```
User: Battery not charging

Agent: Let me help figure this out. First, is the inverter showing any alarms?

User: Yes, ChargeBlocked

Agent: Got it. That usually means temperature or BMS protection. What's the battery temperature right now?

User: 52°C

Agent: Ah, there's the problem! Battery is too hot (>50°C), so the BMS is blocking charging to protect the cells.

Here's what to do:
1. Check if the cooling fan is running (should hear it)
2. Make sure air vents aren't blocked
3. Wait for temperature to drop below 40°C (usually 30-60 min)
4. Charging will resume automatically

Want me to monitor temperature and notify you when it's safe to charge?
```

---

## Pattern 3: Context-Aware Responses

### When to Use
- Multi-site management
- Historical queries
- Trend analysis

### Pattern

**Agent remembers context → References past conversations → Provides continuity**

**Example**:
```
User: How's Site Alpha?

Agent: Site Alpha is looking better! Remember last week when I flagged the cell imbalance (0.12V spread)? After enabling BMS balancing, it's improved to 0.08V. Still slightly elevated, but trending in the right direction.

Battery health: 82% (unchanged - good)
Temperature: 38°C (down from 42°C - much better!)

The cooling fix you did last Thursday is definitely helping. Keep monitoring, but I'm optimistic we've caught this early.

User: When should I check again?

Agent: I'll keep watching daily. If spread drops below 0.05V (normal), I'll let you know the issue is resolved. If it climbs back above 0.10V, I'll alert immediately. Either way, I'd say check in with me in a week?
```

---

## Pattern 4: Intelligent Disambiguation

### When to Use
- Ambiguous queries
- Multiple possible meanings
- Fleet management

### Pattern

**Agent clarifies intent → Offers options → Executes correct action**

**Example**:
```
User: Check battery health

Agent: I can help with that! Just to clarify:
1. Check all sites (12 total) - quick fleet overview?
2. Detailed analysis of a specific site?
3. Sites with warnings/issues only?

User: Just Site Alpha

Agent: Got it, pulling detailed health report for Site Alpha...

[Report follows]
```

---

## Pattern 5: Actionable Insights

### When to Use
- Reporting
- Dashboards
- Executive summaries

### Pattern

**Data → Insight → Recommendation → Action**

**Example**:
> "📊 Monthly Fleet Report - November 2025
>
> **The Numbers**:
> - 12 sites monitored
> - 2 batteries need attention
> - 10 healthy systems
>
> **Key Insight**: Site Alpha and Site Charlie are both degrading faster than normal (0.8%/month vs 0.3% typical). Both are also running hot (42°C average).
>
> **Pattern I See**: Seems like hot climate installations need better cooling. This is costing you ~$5,000/year in premature replacements.
>
> **My Recommendation**: Budget $1,200 to upgrade cooling fans on all hot-climate sites. Should extend battery life 2-3 years, saving $15,000+ over time.
>
> **Next Step**: Want me to prioritize which sites need cooling upgrades first?"

---

## Pattern 6: Progressive Disclosure

### When to Use
- Complex data
- Technical users who want detail
- Debugging

### Pattern

**Simple summary first → Details on demand → Technical data if requested**

**Example**:
```
User: Check Site 5

Agent: Site 5 is healthy. Battery at 85%, system running normally, no issues.

User: Show more details

Agent: **Site 5 - Detailed Status**

Battery Health: 95% (excellent)
Current Charge: 85%
Temperature: 28°C (optimal)
Cell Balance: 0.04V spread (good)
Degradation Rate: 0.2%/month (normal)
Predicted Replacement: 8-10 years

Last Issue: None (clean record)
Uptime: 99.8% (30 days)

User: Show me the cell voltages

Agent: **Cell Voltage Details**:

Module 1:
  Cell 0101: 3.330V ✅
  Cell 0102: 3.328V ✅
  Cell 0103: 3.325V ✅
  ...

[Technical details]
```

---

## Anti-Patterns (Avoid These)

### ❌ Jargon Without Explanation
```
Bad: "SOH degradation rate exceeds 0.5%/month threshold"
Good: "Battery aging faster than normal (0.8% per month vs typical 0.3%). At this rate, you'll need replacement in 10 months instead of 3 years."
```

### ❌ Alarm Fatigue
```
Bad: Alert for every minor event
Good: Alert only for actionable issues, batch minor notifications
```

### ❌ No Context
```
Bad: "Battery temperature: 45°C"
Good: "Battery temperature is 45°C—that's hot enough to reduce lifespan by 40%. Normal range is 20-30°C."
```

### ❌ Can't Answer Follow-ups
```
Bad:
  User: Why is it hot?
  Agent: I don't understand that question

Good:
  User: Why is it hot?
  Agent: Looking at the data... Your cooling fan hasn't been running (0 RPM). That's likely why temperature climbed from 28°C to 45°C over 3 days. Fan needs repair or replacement.
```

### ❌ Too Much Data at Once
```
Bad: Dump 100 metrics in response
Good: Summarize key points, offer drill-down
```

---

## Implementation Tips

### 1. Use Templates with Variables

```python
templates = {
    'battery_healthy': "Battery at {site} is healthy ({soh}% health). Aging normally at {rate}%/month. No action needed.",

    'battery_warning': "Battery at {site} needs attention ({soh}% health). Degrading at {rate}%/month (faster than normal). Predicted replacement: {months} months. Likely cause: {cause}.",

    'battery_critical': "🚨 URGENT: Battery at {site} requires replacement ({soh}% health, below 70% threshold). System may fail unexpectedly. Schedule replacement THIS WEEK."
}
```

### 2. Add Personality (But Stay Professional)

**Good**:
> "Great news! Your battery is aging like fine wine—slow and steady at 0.2% per month."

**Too Much**:
> "OMG your battery is literally perfect!!! 💯💯💯"

### 3. Explain Technical Terms on First Use

```
First mention: "SOH (State of Health) is at 95%—that's like saying your battery has 95% of its original capacity."

Subsequent: "SOH is now 94%..."
```

### 4. Provide Next Steps

Always end with clear action or next step:
- "Should I...?"
- "Want me to...?"
- "I'll monitor and alert if..."

---

## Measuring Success

### User Satisfaction Metrics

**Response Quality**:
- User asks clarifying question < 20% of time (clear responses)
- User satisfied with response (survey)
- No "I don't understand" loops

**Proactive Value**:
- Issues caught before customer notices > 80%
- False alarms < 10%
- User trusts agent recommendations

**Efficiency**:
- Time to diagnose issue < 5 minutes
- Reduced truck rolls > 30%
- User doesn't need to check VRM portal

---

## Examples from Real Users

### Before (2020 Style)
```
User: check battery
Bot: battery_soc=82, battery_soh=95, battery_voltage=51.2, battery_temp=28, battery_status=ok
User: is that good?
Bot: yes
```
**User satisfaction: 3/10** (" I just want to know if my battery is okay!")

### After (2025 Style)
```
User: check battery
Agent: Your battery is in excellent shape! Health is at 95% (like having 95% of original capacity), currently 82% charged, and running at a comfortable 28°C. It's aging at a normal 0.2% per month—on track for 8-10 years of service. No issues to worry about.

Want to see the trend over time, or check another site?
```
**User satisfaction: 9/10** ("This is so much clearer!")

---

## Related Documentation

**Tutorials**:
- [Build Battery Health Agent](../../ai-agent-developer/tutorials/02-battery-health-agent.md)

**How-To Guides**:
- [Detect Battery Degradation](../../ai-agent-developer/how-to-guides/anomaly-detection/detect-battery-degradation.md)

---

**Made in Ukraine 🇺🇦 with love by EnergyCitizen**
