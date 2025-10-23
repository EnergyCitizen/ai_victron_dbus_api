# Victron Installer Documentation

Welcome! This documentation workspace is designed for Victron installers and system maintainers who troubleshoot and validate installations.

## 🔧 Your Profile

- **Role**: Certified Victron Installer & Maintainer
- **Goal**: Diagnose and fix issues quickly, ideally without site visits
- **Interaction**: Ask AI agent "What's wrong?" and get actionable diagnosis
- **Value**: Reduce truck rolls, resolve 60% of issues remotely

## 🚀 Quick Start

### Your Top Questions

| Question | Document | Time |
|----------|----------|------|
| "How do I validate a new installation?" | [Tutorial: Validate Installation](tutorials/01-validate-new-installation.md) | 20 min |
| "Customer says battery not charging - what do I check?" | [How-To: Battery Not Charging](how-to-guides/troubleshooting/battery-not-charging.md) | 10 min |
| "How do I ask the AI agent about system state?" | [How-To: Ask About System State](how-to-guides/conversational-queries/ask-about-system-state.md) | 5 min |
| "Why are parallel inverters unbalanced?" | [Concept: Parallel Inverter Operation](concepts/parallel-inverter-operation.md) | 15 min |
| "What do alarm codes mean?" | [Reference: Alarm Codes](reference/alarm-codes.md) | 2 min |

## 📚 Common Scenarios

### Remote Troubleshooting
- [Battery Not Charging](how-to-guides/troubleshooting/battery-not-charging.md) - BMS limits, temperature, alarms
- [Grid Frequency Issues](how-to-guides/troubleshooting/grid-frequency-issues.md) - Grid code, utility problems
- [Inverter Load Imbalance](how-to-guides/troubleshooting/inverter-load-imbalance.md) - Real case: 89/11 split
- [MPPT Offline](how-to-guides/troubleshooting/mppt-offline.md) - PV voltage, VE.Can connection

### Installation Validation
- [Verify Synchronization](how-to-guides/validation/verify-synchronization.md) - Voltage, frequency, phase match
- [Check Battery Health](how-to-guides/validation/check-battery-health.md) - SOC, SOH, cells
- [Validate Grid Connection](how-to-guides/validation/validate-grid-connection.md) - Power quality

### Using AI Agent
- [Ask About System State](how-to-guides/conversational-queries/ask-about-system-state.md) - "Is everything OK?"
- [Compare Two Sites](how-to-guides/conversational-queries/compare-two-sites.md) - Side-by-side
- [Explain Alarms](how-to-guides/conversational-queries/explain-alarms.md) - Plain language

## 📖 Documentation Types

### 🎓 Tutorials (Learning)
**Goal**: Learn troubleshooting workflows
**Format**: Step-by-step with real examples
**Time**: 15-30 minutes

→ [All Tutorials](tutorials/)

### 📋 How-To Guides (Tasks)
**Goal**: Fix specific issue
**Format**: Problem → Check → Solution
**Time**: 5-15 minutes

→ [All How-To Guides](how-to-guides/)

### 💡 Concepts (Understanding)
**Goal**: Understand "why"
**Format**: Explanations, diagrams
**Time**: 10-20 minutes

→ [All Concepts](concepts/)

### 📚 Reference (Lookup)
**Goal**: Quick facts
**Format**: Tables, checklists
**Time**: 2-5 minutes

→ [All Reference](reference/)

## 🔍 Troubleshooting Matrix

Quick lookup for common issues:

| Symptom | First Check | Common Cause | Guide |
|---------|-------------|--------------|-------|
| Battery not charging | Alarms, BMS limits, temperature | Temp >50°C, BMS block | [Battery Not Charging](how-to-guides/troubleshooting/battery-not-charging.md) |
| Low AC output voltage | Grid input, inverter state | Grid sag, overload | [Grid Issues](how-to-guides/troubleshooting/grid-frequency-issues.md) |
| MPPT no power | PV voltage, error codes | Panel disconnected, VE.Can | [MPPT Offline](how-to-guides/troubleshooting/mppt-offline.md) |
| Inverter imbalance | Load distribution, ESS mode | Mode mismatch, current limits | [Load Imbalance](how-to-guides/troubleshooting/inverter-load-imbalance.md) |
| High frequency | Grid connection, grid code | Utility issue, wrong code | [Grid Frequency](how-to-guides/troubleshooting/grid-frequency-issues.md) |

See full matrix: [Reference: Troubleshooting Matrix](reference/troubleshooting-matrix.md)

## 🔗 Cross-References

- **AI Agent Developer Docs**: [../ai-agent-developer/](../ai-agent-developer/) - Build custom monitoring agents
- **Shared Resources**: [../shared/](../shared/) - Architecture, API spec
- **PERSONAS.md**: [../../PERSONAS.md](../../PERSONAS.md) - Your detailed persona profile

## 💬 Feedback

Found an issue not covered? Have a troubleshooting tip to share?
- Add to GitHub Issues
- Contribute your field experience
- Help other installers

---

**Made in Ukraine 🇺🇦 with love by EnergyCitizen**
