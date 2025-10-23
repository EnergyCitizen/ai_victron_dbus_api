# Tutorial: Build Your First Monitoring Agent

Learn to build a conversational AI agent that monitors Victron battery levels and alerts on low SOC.

**Time**: 30 minutes
**Skill Level**: Beginner
**Prerequisites**: Python 3.9+, access to Victron system with API server running

---

## What You'll Build

A simple AI agent that:
- Lets users ask "What's the battery level?"
- Responds in natural language: "Battery is at 73%, charging"
- Alerts when SOC drops below 20%
- Remembers conversation context

**By the end**, you'll have a working agent monitoring one site.

---

## Learning Objectives

After this tutorial, you will:
- [ ] Understand how to query the Victron DBus API
- [ ] Parse natural language user queries
- [ ] Generate conversational responses
- [ ] Implement basic alerting
- [ ] Handle conversation context

---

## Step 1: Setup (5 minutes)

### Install Dependencies

```bash
# Create project directory
mkdir victron-monitoring-agent
cd victron-monitoring-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install requests openai anthropic  # Choose your AI provider
```

### Test API Access

```python
# test_api.py
import requests

API_BASE = "http://192.168.88.77:8088"  # Replace with your device IP

# Test connection
response = requests.get(f"{API_BASE}/health")
print(f"API Health: {response.json()}")

# Expected output:
# API Health: {'status': 'healthy', 'success': True}
```

**✅ Checkpoint**: API connection works

---

## Step 2: Create API Client (10 minutes)

Create `victron_api.py`:

```python
import requests
from typing import Optional

class VictronAPI:
    """Simple client for Victron DBus API"""

    def __init__(self, device_ip: str, port: int = 8088):
        self.base_url = f"http://{device_ip}:{port}"
        self.battery_service = "com.victronenergy.battery.socketcan_can0"
        self.system_service = "com.victronenergy.system"

    def get_value(self, service: str, path: str) -> Optional[float]:
        """Get value from DBus path"""
        try:
            response = requests.get(
                f"{self.base_url}/value",
                params={'service': service, 'path': path},
                timeout=2
            )
            data = response.json()
            if data.get('success'):
                return data['value']
        except Exception as e:
            print(f"API Error: {e}")
        return None

    def get_battery_soc(self) -> Optional[float]:
        """Get battery state of charge (%)"""
        return self.get_value(self.battery_service, '/Soc')

    def get_battery_current(self) -> Optional[float]:
        """Get battery current (A, negative = discharging)"""
        return self.get_value(self.battery_service, '/Dc/0/Current')

    def get_battery_voltage(self) -> Optional[float]:
        """Get battery voltage (V)"""
        return self.get_value(self.battery_service, '/Dc/0/Voltage')

# Test it
if __name__ == '__main__':
    api = VictronAPI("192.168.88.77")

    soc = api.get_battery_soc()
    current = api.get_battery_current()
    voltage = api.get_battery_voltage()

    print(f"Battery: {soc}% SOC, {voltage}V, {current}A")
    # Expected: Battery: 73.0% SOC, 49.8V, -8.3A
```

**Run**: `python victron_api.py`

**✅ Checkpoint**: Can query battery metrics

---

## Step 3: Add Conversational Interface (10 minutes)

Create `agent.py`:

```python
from victron_api import VictronAPI
import anthropic  # or openai
import os

class VictronAgent:
    """Conversational AI agent for Victron monitoring"""

    def __init__(self, device_ip: str, anthropic_api_key: str):
        self.api = VictronAPI(device_ip)
        self.client = anthropic.Anthropic(api_key=anthropic_api_key)
        self.conversation_history = []

    def ask(self, user_query: str) -> str:
        """
        Process user query and return conversational response

        Args:
            user_query: Natural language question

        Returns:
            str: Agent's response
        """
        # Get current system data
        soc = self.api.get_battery_soc()
        current = self.api.get_battery_current()
        voltage = self.api.get_battery_voltage()

        # Build system prompt with current data
        system_prompt = f"""You are a Victron energy system assistant.

Current System Data:
- Battery SOC: {soc}%
- Battery Voltage: {voltage}V
- Battery Current: {current}A (negative = discharging, positive = charging)

Answer user questions about the system naturally and concisely.
Add helpful context. Use emojis sparingly for status (✅🟡🔴).
"""

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_query
        })

        # Call Claude
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=system_prompt,
            messages=self.conversation_history
        )

        response_text = message.content[0].text

        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response_text
        })

        return response_text

# Test it
if __name__ == '__main__':
    agent = VictronAgent(
        device_ip="192.168.88.77",
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    # Simulate conversation
    print("User: What's the battery level?")
    response = agent.ask("What's the battery level?")
    print(f"Agent: {response}")
    print()

    print("User: Is that good?")
    response = agent.ask("Is that good?")
    print(f"Agent: {response}")
```

**Expected Output**:
```
User: What's the battery level?
Agent: Battery is at 73%, discharging at 8A. That's healthy - plenty of capacity remaining.

User: Is that good?
Agent: Yes, 73% is good for a battery. Anything above 20% is safe. You have about 5 hours
       of runtime at the current discharge rate before needing to recharge.
```

**✅ Checkpoint**: Conversational agent works!

---

## Step 4: Add Alerting (5 minutes)

Extend `agent.py` with alert checking:

```python
def check_for_alerts(self) -> Optional[str]:
    """
    Check if any metrics need immediate attention
    Returns alert message or None
    """
    soc = self.api.get_battery_soc()

    if soc is None:
        return "⚠️ Cannot reach battery monitor - check API connection"

    if soc < 10:
        return f"🚨 CRITICAL: Battery at {soc:.0f}% - system may shut down soon!"

    if soc < 20:
        return f"🔴 WARNING: Battery low at {soc:.0f}% - consider enabling grid charging"

    return None

# Add to your monitoring loop
if __name__ == '__main__':
    agent = VictronAgent("192.168.88.77", os.getenv("ANTHROPIC_API_KEY"))

    # Check for alerts
    alert = agent.check_for_alerts()
    if alert:
        print(alert)
        # In production: send email, SMS, push notification
```

**✅ Checkpoint**: Alerts trigger correctly

---

## Step 5: Deploy and Test (Hands-On)

### Continuous Monitoring

```python
# monitor.py
import time
from agent import VictronAgent
import os

def main():
    agent = VictronAgent("192.168.88.77", os.getenv("ANTHROPIC_API_KEY"))

    print("Victron Monitoring Agent Started")
    print("Checking battery every 60 seconds...")
    print("Press Ctrl+C to stop")
    print()

    while True:
        # Check for alerts
        alert = agent.check_for_alerts()
        if alert:
            print(f"[{time.strftime('%H:%M:%S')}] {alert}")

        # Wait 60 seconds
        time.sleep(60)

if __name__ == '__main__':
    main()
```

**Run**: `python monitor.py`

**Expected Output**:
```
Victron Monitoring Agent Started
Checking battery every 60 seconds...
Press Ctrl+C to stop

[22:45:30] Battery healthy (73%)
[22:46:30] Battery healthy (72%)
...
[23:15:30] 🔴 WARNING: Battery low at 19% - consider enabling grid charging
[23:16:30] 🔴 WARNING: Battery low at 18%
```

---

## What You've Built

Congratulations! You now have:
- ✅ **API Client**: Queries Victron DBus API
- ✅ **Conversational Interface**: Users ask in natural language
- ✅ **Context Memory**: Agent remembers previous questions
- ✅ **Alerting**: Proactive notifications on low SOC
- ✅ **Monitoring Loop**: Continuous checking

**Your agent can**:
- Answer "What's the battery level?"
- Explain status in plain language
- Alert when SOC < 20%
- Provide helpful context automatically

---

## Next Steps

### Expand Capabilities

1. **Add More Metrics**:
   - Solar production: [Tutorial 03](./03-fleet-dashboard-agent.md)
   - Grid status: Add grid voltage/frequency queries
   - Inverter state: Track charging modes

2. **Improve Alerting**:
   - [How-To: Proactive Alerts](../how-to-guides/conversational-patterns/proactive-alerts.md)
   - Send emails/SMS on critical alerts
   - Escalation rules (if SOC <10% for >1hr)

3. **Multi-Site Monitoring**:
   - [Tutorial 03: Fleet Dashboard](./03-fleet-dashboard-agent.md)
   - Query 10+ sites in parallel
   - Aggregate alerts across fleet

4. **Advanced Diagnostics**:
   - [How-To: Detect Battery Degradation](../how-to-guides/anomaly-detection/detect-battery-degradation.md)
   - Track SOH trends
   - Predict battery replacement

### Learn More

**Concepts**:
- [Why Monitor Batteries](../concepts/why-monitor-batteries.md) - Business value
- [2025 AI UX Patterns](../../shared/conversational-ai/2025-ux-patterns.md) - Modern interaction patterns

**How-To Guides**:
- [Natural Language Queries](../how-to-guides/conversational-patterns/natural-language-queries.md) - Advanced query patterns
- [Explain System State](../how-to-guides/conversational-patterns/explain-system-state.md) - Comprehensive responses

---

## Troubleshooting

### "API connection failed"
- Check device IP is correct
- Verify API server is running: `ssh root@<IP> "ps | grep dbus_api_server"`
- Check network connectivity: `ping 192.168.88.77`

### "Anthropic API error"
- Verify ANTHROPIC_API_KEY environment variable is set
- Check API key is valid at console.anthropic.com
- Review rate limits if error persists

### "Agent responses are too technical"
- Improve system prompt: emphasize "explain simply"
- Add few-shot examples of good responses
- Review [Response Formats](../reference/conversational-patterns/response-formats.md)

---

## Success Criteria

You've successfully completed this tutorial if you can:
- [ ] Run `python monitor.py` and see battery level
- [ ] Ask agent "What's the battery level?" and get natural response
- [ ] See alert when manually setting test SOC < 20%
- [ ] Agent remembers context between questions

**Estimated Time**: If completed in ~30 minutes, you're ready for Tutorial 02!

---

## Community

Share your agent implementation:
- Show your conversational examples
- Contribute prompt improvements
- Help other builders

---

**Made in Ukraine 🇺🇦 with love by EnergyCitizen**
