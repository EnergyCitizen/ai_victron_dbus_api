# Documentation Personas

This documentation is designed for two primary personas who interact with Victron systems in fundamentally different ways.

---

## 🤖 Persona 1: AI Agent Developer

### Background
- **Company**: Victron AI ecosystem partner
- **Role**: Senior AI Agent Developer
- **Experience**: 10+ years software development, 2 years AI/ML

### Responsibilities
- Build AI agents that monitor Victron installations
- Develop conversational interfaces for system diagnostics
- Create predictive maintenance algorithms
- Enable fleet-wide anomaly detection

### Goals & Motivations
- **Primary Goal**: Build AI agents that users can talk to naturally
- **User Interaction**: "Show me battery health across all my sites" (not: write Python code)
- **Scale**: Monitor 50-100+ VRM installations per customer
- **Value**: Predictive maintenance, early problem detection, cost savings

### Pain Points
- **Current**: Must deploy API server manually on each Venus device
- **Challenge**: Managing 50+ IP addresses, no centralized auth
- **Need**: VRM ProxyRelay integration for zero-friction deployment
- **Documentation**: Too much Python code, not enough user story examples

### Technical Proficiency
- **Strong**: Python, REST APIs, AI/ML frameworks, prompt engineering
- **Learning**: DBus architecture, Victron system specifics, battery chemistry
- **Tooling**: Uses Claude, ChatGPT, and custom AI agents for development

### Typical User Stories
1. **As an AI Developer**, I want my AI agent to alert me when any site's battery SOC drops below 20%
2. **As an AI Developer**, I want to ask "Which sites have battery degradation?" and get ranked results
3. **As an AI Developer**, I want the agent to proactively suggest maintenance based on trends
4. **As an AI Developer**, I want to predict battery failures 3-6 months in advance
5. **As an AI Developer**, I want to compare solar production across similar installations

### Information Needs

**Tutorials** (Learning):
- How to build first monitoring agent (30 min hands-on)
- Implementing battery health tracking
- Creating fleet dashboard with natural language queries
- Deploying predictive maintenance

**How-To Guides** (Task-oriented):
- Detect battery degradation early
- Identify grid quality issues
- Monitor cell imbalance
- Implement proactive alerts
- Create conversational query patterns

**Concepts** (Understanding):
- Why monitor batteries (ROI, failure patterns)
- Battery degradation science (chemistry, aging curves)
- Inverter load balancing principles
- Grid quality metrics interpretation
- ESS optimization strategies

**Reference** (Lookup):
- Critical API paths for monitoring
- Anomaly detection thresholds
- Python implementation examples (collapsed by default)
- Diagnostic path reference tables

### Success Criteria
After using documentation, an AI Developer can:
- Build working monitoring agent in <2 hours
- Implement conversational patterns (not just API calls)
- Find threshold values without reading 47KB technical docs
- Explain business value to stakeholders (ROI, cost savings)
- Deploy agents that users interact with in natural language

---

## 🔧 Persona 2: Victron Installer/Maintainer

### Background
- **Role**: Certified Victron Installer & System Maintainer
- **Location**: Various (installers worldwide)
- **Experience**: 5+ years solar/battery system installation
- **Certifications**: Victron Energy Professional

### Responsibilities
- Install Victron ESS systems (residential & commercial)
- Commission and configure new installations
- Troubleshoot customer issues remotely
- Perform preventive maintenance
- Validate system performance

### Goals & Motivations
- **Primary Goal**: Diagnose and fix issues quickly, ideally without site visits
- **User Interaction**: "What's wrong with Site 4?" → AI agent explains the issue
- **Efficiency**: Reduce truck rolls, resolve 60% of issues remotely
- **Quality**: Validate installations before leaving site

### Pain Points
- **Remote Diagnosis**: Need quick answers without complex tools
- **Documentation Overload**: Don't want to read 1,000-line technical docs
- **Time Pressure**: Customer waiting, need answers in minutes not hours
- **Knowledge Gaps**: May not know all DBus paths or diagnostic techniques

### Technical Proficiency
- **Strong**: Electrical systems, Victron hardware, VictronConnect app
- **Moderate**: VRM portal, basic scripting (copy-paste bash)
- **Learning**: DBus queries, API concepts, AI agent interaction
- **Tooling**: VictronConnect, VRM portal, basic terminal commands

### Typical User Stories
1. **As an Installer**, I want to ask an AI agent "Is everything OK at Site 7?" and get a health check
2. **As an Installer**, I want to validate a new installation before leaving the site
3. **As an Installer**, I want to troubleshoot "battery not charging" remotely
4. **As an Installer**, I want to compare two identical systems to find why one underperforms
5. **As an Installer**, I want the agent to explain alarm codes in plain language

### Information Needs

**Tutorials** (Learning):
- Validate new installation (20 min checklist)
- Troubleshoot remotely with AI agent (30 min)
- Compare before/after system performance (15 min)

**How-To Guides** (Task-oriented):
- Troubleshoot battery not charging
- Fix grid frequency issues
- Resolve inverter load imbalance
- Diagnose MPPT offline
- Ask agent about system state
- Compare two sites side-by-side
- Explain alarm codes

**Concepts** (Understanding):
- How parallel inverters synchronize
- ESS modes explained (Mode 1 vs Mode 3)
- Grid code compliance
- DVCC control system
- When to use shared vs individual voltage sense

**Reference** (Lookup):
- Troubleshooting matrix (symptom → check → fix)
- Alarm code reference
- State code meanings
- Device specifications
- Quick diagnostic bash scripts (copy-paste ready)

### Success Criteria
After using documentation, an Installer can:
- Validate installation using AI queries in <30 min
- Troubleshoot common issues remotely without reading manuals
- Understand *why* issues happen (not just how to fix)
- Ask agent "What's wrong?" and get actionable diagnosis
- Compare system performance before/after changes

---

## Key Differences

| Aspect | AI Developer | Installer |
|--------|---------------------|-----------|
| **Scale** | 50-100+ installations | 1-10 installations |
| **Interaction** | Builds AI agents for users | Uses AI agents directly |
| **Time Horizon** | Weeks/months (predictive) | Minutes/hours (reactive) |
| **Technical Depth** | Needs API details, thresholds | Needs quick answers, explanations |
| **Documentation** | Wants user stories + code | Wants troubleshooting steps |
| **Primary Tool** | Python, AI frameworks | VictronConnect, VRM portal |
| **Success Metric** | Fleet-wide anomaly detection | Fixed customer issue |

---

## Shared Needs

Both personas need:
- **Natural Language**: Interact with AI agents conversationally
- **Fast Answers**: Don't want to read 1,000-line docs
- **Context**: Understand "why", not just "what"
- **Examples**: Real-world scenarios they can relate to
- **Progressive Disclosure**: High-level first, details on demand

---

## Documentation Strategy

### For AI Agent Developer
**docs/ai-agent-developer/**
- Focus: User stories → conversational patterns → API calls
- Style: "Users ask agent X, agent does Y, here's the implementation"
- Code: Collapsed by default, Python examples in reference section
- Value: Enable AI agent ecosystem on Victron platform

### For Installer
**docs/installer/**
- Focus: Problem → diagnosis → solution
- Style: "Customer says X, agent checks Y, fix is Z"
- Code: Bash scripts (copy-paste ready)
- Value: Resolve issues faster with less truck rolls

### Shared
**docs/shared/**
- Architecture: System overview, DBus structure
- API: Clean HTTP API specification
- Conversational AI: 2025 UX patterns, prompt engineering

---

## Version History

- **v1.0** (2025-10-23): Initial persona definitions
- Based on: Real feedback from AI ecosystem partners and Victron installers
- Next: User story validation with actual users

---

**Made in Ukraine 🇺🇦 with love by EnergyCitizen**
