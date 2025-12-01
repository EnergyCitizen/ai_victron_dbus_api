# AI Agent Developer Documentation

Welcome! This documentation workspace is designed for AI agent developers building conversational interfaces for Victron system monitoring.

## 🤖 Your Profile

- **Goal**: Build AI agents that monitor 50-100+ VRM installations
- **Interaction**: Users talk to agents naturally, agents handle API calls
- **Value**: Predictive maintenance, anomaly detection, cost savings

## 🚀 Quick Start

### Your Top Questions

| Question | Document | Time |
|----------|----------|------|
| "How do I build my first monitoring agent?" | [Tutorial 01: First Monitoring Agent](tutorials/01-first-monitoring-agent.md) | 30 min |
| "How do I detect battery degradation?" | [How-To: Detect Battery Degradation](how-to-guides/anomaly-detection/detect-battery-degradation.md) | 15 min |
| "What conversational patterns should I use?" | [How-To: Natural Language Queries](how-to-guides/conversational-patterns/natural-language-queries.md) | 20 min |
| "Why should I monitor batteries?" | [Concept: Why Monitor Batteries](concepts/why-monitor-batteries.md) | 10 min |
| "What API paths are critical?" | [Reference: Critical Paths](reference/api/critical-paths.md) | 5 min |

## 📚 Learning Path

### Beginner (Week 1)
1. [Tutorial 01: First Monitoring Agent](tutorials/01-first-monitoring-agent.md) - Build agent that polls SOC
2. [Concept: Why Monitor Batteries](concepts/why-monitor-batteries.md) - Understand business value
3. [How-To: Natural Language Queries](how-to-guides/conversational-patterns/natural-language-queries.md) - Implement conversational interface

### Intermediate (Week 2-3)
4. [Tutorial 02: Battery Health Agent](tutorials/02-battery-health-agent.md) - Track SOH trends
5. [How-To: Detect Battery Degradation](how-to-guides/anomaly-detection/detect-battery-degradation.md) - Early warning system
6. [Concept: Battery Degradation Patterns](concepts/battery-degradation-patterns.md) - Understand aging science

### Advanced (Week 4+)
7. [Tutorial 03: Fleet Dashboard Agent](tutorials/03-fleet-dashboard-agent.md) - Multi-site comparison
8. [Tutorial 04: Predictive Maintenance](tutorials/04-predictive-maintenance-agent.md) - Failure prediction
9. [How-To: Proactive Alerts](how-to-guides/conversational-patterns/proactive-alerts.md) - Agent-initiated actions

## 📖 Documentation Types

### 🎓 Tutorials (Learning)
**Goal**: Learn by doing
**Format**: Step-by-step, hands-on
**Time**: 30-120 minutes
**Outcome**: Working agent

→ [All Tutorials](tutorials/)

### 📋 How-To Guides (Tasks)
**Goal**: Solve specific problem
**Format**: User story → conversational flow → implementation
**Time**: 10-30 minutes
**Outcome**: Feature added to your agent

→ [All How-To Guides](how-to-guides/)

### 💡 Concepts (Understanding)
**Goal**: Understand "why"
**Format**: Explanations, diagrams, theory
**Time**: 15-25 minutes
**Outcome**: Deeper knowledge

→ [All Concepts](concepts/)

### 📚 Reference (Lookup)
**Goal**: Find specific information
**Format**: Tables, lists, code snippets
**Time**: 2-5 minutes
**Outcome**: Answer to specific question

→ [All Reference](reference/)

## 🎯 Common Use Cases

### Fleet Monitoring
- [Compare Site Performance](how-to-guides/fleet-monitoring/compare-site-performance.md)
- [Aggregate Alerts](how-to-guides/fleet-monitoring/aggregate-alerts.md)
- [Identify Underperformers](how-to-guides/fleet-monitoring/identify-underperformers.md)

### Anomaly Detection
- [Detect Battery Degradation](how-to-guides/anomaly-detection/detect-battery-degradation.md)
- [Detect Grid Issues](how-to-guides/anomaly-detection/detect-grid-issues.md)
- [Detect Cell Imbalance](how-to-guides/anomaly-detection/detect-cell-imbalance.md)
- [Detect Inverter Faults](how-to-guides/anomaly-detection/detect-inverter-faults.md)

### Conversational Patterns
- [Natural Language Queries](how-to-guides/conversational-patterns/natural-language-queries.md)
- [Proactive Alerts](how-to-guides/conversational-patterns/proactive-alerts.md)
- [Explain System State](how-to-guides/conversational-patterns/explain-system-state.md)

### Optimization
- [Recommend ESS Settings](how-to-guides/optimization/recommend-ess-settings.md)
- [Balance Inverter Loads](how-to-guides/optimization/balance-inverter-loads.md)

## 🔗 Cross-References

- **Installer Docs**: [../installer/](../installer/) - Troubleshooting and validation guides
- **Shared Resources**: [../shared/](../shared/) - Architecture, API spec, AI patterns
- **PERSONAS.md**: [../../PERSONAS.md](../../PERSONAS.md) - Your detailed persona profile

## 💬 Feedback

Building an AI agent on Victron platform? We want to hear from you!
- Share your use cases
- Report gaps in documentation
- Contribute conversational patterns

---

**Made in Ukraine 🇺🇦 with love by EnergyCitizen**
