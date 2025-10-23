# Documentation Restructure Proposal

**Status**: 🎯 Ready for Review
**Date**: 2025-10-23
**Author**: EnergyCitizen team

---

## Executive Summary

**Problem**: Current documentation (3,548 lines across 7 files) is organized around system components (battery, inverter, grid) rather than user goals. Excellent technical reference, but not optimized for 2025 AI agent interaction patterns.

**Solution**: Transform into Diataxis-based, persona-driven documentation where users talk to AI agents in natural language instead of writing Python code.

**Key Insight**: In 2025, users don't write `requests.get(...)` - they ask "Show me battery health across all sites" and AI agents handle the implementation.

---

## Current State Analysis

### Existing Documentation (119KB Total)

| Document | Lines | Type | Issues |
|----------|-------|------|--------|
| VICTRON_DBUS_DIAGNOSTIC_API_RESEARCH.md | 1,092 | Technical Reference | Too long, component-focused |
| victron_einstein_research.md | 1,391 | System Analysis | Complex case study buried |
| IMPLEMENTATION_GUIDE_AI_AGENTS.md | 689 | Backend Code | Python-first, not user-story-first |
| QUICK_REFERENCE_DIAGNOSTIC_PATHS.json | 463 | Data | Hard to digest, needs context |
| victron_einstein_metrics.md | 436 | Monitoring Ref | Operational, not conversational |
| victron_einstein_index.md | 310 | Navigation | System-centric index |
| 00_START_HERE.md | 334 | Index | Needs persona routing |

**Total**: 4,715 lines that need reorganization

### What Works Well ✅

- Comprehensive DBus path documentation
- Real-world examples (einstein system)
- Anomaly detection thresholds
- Implementation code examples
- Multi-device analysis

### What Needs Improvement ⚠️

- **Organization**: By component (battery, inverter) not by user goal (detect degradation, troubleshoot)
- **Format**: Large monolithic files (1,000+ lines) instead of focused 100-300 line guides
- **Interaction Model**: Shows Python code first, user stories second (should be reversed)
- **Discoverability**: Hard to find "how do I detect battery degradation?" without reading 1,000 lines
- **2025 UX**: Doesn't reflect conversational AI patterns (natural language, proactive agents)

---

## Proposed Structure

### Diataxis Framework Application

Following [Diataxis documentation system](https://diataxis.fr/) and template_for_agents.git patterns:

```
docs/
├── PERSONAS.md                         # ✅ Created - Define Mauk & Installer
│
├── ai-agent-developer/                 # Mauk Müller's workspace
│   ├── README.md                       # Persona intro, quick start
│   │
│   ├── tutorials/                      # 📚 Learning-oriented (30-120 min)
│   │   ├── 01-first-monitoring-agent.md        # 30 min: Poll SOC, alert on low battery
│   │   ├── 02-battery-health-agent.md          # 60 min: Track SOH, predict EOL
│   │   ├── 03-fleet-dashboard-agent.md         # 90 min: Multi-site comparison
│   │   └── 04-predictive-maintenance-agent.md  # 120 min: Risk scoring, failure prediction
│   │
│   ├── how-to-guides/                  # 📋 Task-oriented (10-30 min each)
│   │   ├── anomaly-detection/
│   │   │   ├── detect-battery-degradation.md   # "Alert me when SOH < 85%"
│   │   │   ├── detect-grid-issues.md           # "Notify me of frequency problems"
│   │   │   ├── detect-cell-imbalance.md        # "Warn about cell voltage spread"
│   │   │   └── detect-inverter-faults.md       # "Check inverter health"
│   │   ├── conversational-patterns/
│   │   │   ├── natural-language-queries.md     # "Show me all low SOC sites"
│   │   │   ├── proactive-alerts.md             # Agent suggests actions
│   │   │   └── explain-system-state.md         # "What's happening at Site 5?"
│   │   ├── fleet-monitoring/
│   │   │   ├── compare-site-performance.md     # Rank by metrics
│   │   │   ├── aggregate-alerts.md             # Multi-site rollups
│   │   │   └── identify-underperformers.md     # Find outliers
│   │   └── optimization/
│   │       ├── recommend-ess-settings.md       # Suggest config changes
│   │       └── balance-inverter-loads.md       # Fix 89/11 imbalance
│   │
│   ├── concepts/                        # 💡 Understanding-oriented (15-25 min reads)
│   │   ├── why-monitor-batteries.md             # ROI, failure patterns
│   │   ├── battery-degradation-patterns.md      # Chemistry, aging curves
│   │   ├── inverter-load-balancing.md           # Sync mechanisms
│   │   ├── grid-quality-metrics.md              # Frequency/voltage
│   │   ├── ess-optimization-strategies.md       # Peak shaving, solar max
│   │   └── predictive-maintenance-theory.md     # Risk scoring
│   │
│   └── reference/                       # 📚 Information-oriented (lookup)
│       ├── api/
│       │   ├── critical-paths.md                # From QUICK_REFERENCE json
│       │   ├── health-monitoring-paths.md       # Battery, inverter health
│       │   ├── grid-quality-paths.md            # Grid metrics
│       │   └── optimization-paths.md            # ESS control
│       ├── conversational-patterns/
│       │   ├── query-templates.md               # Prompt patterns
│       │   ├── response-formats.md              # How to format answers
│       │   └── context-management.md            # Memory strategies
│       ├── thresholds/
│       │   ├── battery-thresholds.md            # SOC, SOH, temp limits
│       │   ├── grid-thresholds.md               # Voltage, frequency
│       │   └── temperature-thresholds.md        # Thermal limits
│       └── implementation/
│           ├── python-examples.md               # Code snippets
│           ├── polling-strategies.md            # Batch queries
│           └── data-structures.md               # JSON schemas
│
├── installer/                           # Victron Installer workspace
│   ├── README.md                        # Persona intro
│   │
│   ├── tutorials/                       # 📚 Learning-oriented (15-30 min)
│   │   ├── 01-validate-new-installation.md     # Pre-departure checklist
│   │   ├── 02-troubleshoot-remotely.md         # Diagnose without site visit
│   │   └── 03-compare-before-after.md          # Measure impact
│   │
│   ├── how-to-guides/                   # 📋 Task-oriented (5-15 min each)
│   │   ├── troubleshooting/
│   │   │   ├── battery-not-charging.md         # Check BMS, limits, temp
│   │   │   ├── grid-frequency-issues.md        # Grid code, utility contact
│   │   │   ├── inverter-load-imbalance.md      # Real case: 89/11 split
│   │   │   └── mppt-offline.md                 # Check PV, VE.Can
│   │   ├── validation/
│   │   │   ├── verify-synchronization.md       # Voltage, frequency match
│   │   │   ├── check-battery-health.md         # SOC, SOH, cells
│   │   │   └── validate-grid-connection.md     # Power quality
│   │   └── conversational-queries/
│   │       ├── ask-about-system-state.md       # "Is everything OK?"
│   │       ├── compare-two-sites.md            # Side-by-side metrics
│   │       └── explain-alarms.md               # Plain language
│   │
│   ├── concepts/                         # 💡 Understanding-oriented
│   │   ├── parallel-inverter-operation.md      # How sync works
│   │   ├── ess-modes-explained.md              # Mode 1 vs Mode 3
│   │   ├── grid-codes-compliance.md            # Anti-islanding
│   │   └── dvcc-control-system.md              # Who's in control
│   │
│   └── reference/                        # 📚 Information-oriented
│       ├── troubleshooting-matrix.md           # Quick lookup table
│       ├── alarm-codes.md                      # Decode alarms
│       ├── state-codes.md                      # Inverter states
│       └── device-specifications.md            # Product specs
│
└── shared/                               # Common to both personas
    ├── architecture/
    │   ├── system-overview.md                  # Component diagram
    │   ├── dbus-architecture.md                # Service structure
    │   └── device-topology.md                  # VE.Can, Modbus
    ├── api-specification/
    │   ├── http-api-reference.md               # Clean API spec
    │   ├── authentication.md                   # Network access
    │   └── rate-limits.md                      # Polling guidelines
    └── conversational-ai/
        ├── 2025-ux-patterns.md                 # Multi-agent, proactive
        ├── prompt-engineering.md               # System prompts
        └── context-window-management.md        # Memory strategies
```

---

## User Story Framework

### Every How-To Guide Structure

```markdown
# [Capability Name]

## User Story
**As [persona]**, I want my AI agent to [capability], so that [benefit].

## Conversational Flow

### User Says:
> "Show me battery health across all my sites"

### Agent Thinks (Internal):
1. Identify metrics: SOC, SOH, cell voltage spread, temperature
2. Query all sites
3. Apply thresholds
4. Rank by health score

### Agent Says:
> "I've checked 12 sites. Here's the summary:
>
> HEALTHY (10 sites): SOC 60-80%, SOH >90%
> WARNING (2 sites):
> - Site Alpha: SOH 82% (plan replacement in 12 months)
> - Site Beta: Cell spread 0.12V (imbalance developing)
>
> Would you like details on the warning sites?"

## Agent Capabilities Required
- Query `/Soc`, `/Soh`, `/System/MaxCellVoltage`, `/System/MinCellVoltage`
- Apply thresholds (SOH <85%, cell spread >0.1V)
- Rank sites by composite health score

## API Calls
<details>
<summary>Technical Implementation (Click to expand)</summary>

```python
# Python code here (collapsed by default)
```

</details>

## Related Guides
- Concept: [Why Monitor Battery Health](../concepts/why-monitor-batteries.md)
- Reference: [Battery Thresholds](../../reference/thresholds/battery-thresholds.md)
```

---

## Content Migration Plan

### Phase 1: Foundation (Week 1)

**Create:**
- ✅ PERSONAS.md (Mauk & Installer)
- Directory structure (mkdir -p docs/{ai-agent-developer,installer,shared}/...)
- README files for each persona workspace

**Extract:**
- QUICK_REFERENCE_DIAGNOSTIC_PATHS.json → Convert to markdown tables in reference/api/

### Phase 2: Core How-Tos (Week 2)

**Priority 1 - Must Have:**
1. `ai-agent-developer/how-to-guides/anomaly-detection/detect-battery-degradation.md`
   - From: DIAGNOSTIC_API_RESEARCH.md Section 2 (Battery)
   - Transform: Add conversational flow, collapse Python code

2. `installer/how-to-guides/troubleshooting/battery-not-charging.md`
   - From: Common troubleshooting pattern
   - Add: Agent-guided diagnosis steps

3. `ai-agent-developer/how-to-guides/conversational-patterns/natural-language-queries.md`
   - New: Prompt engineering for system queries

4. `installer/how-to-guides/troubleshooting/inverter-load-imbalance.md`
   - From: victron_einstein_research.md Section 7 (real case study)

### Phase 3: Tutorials (Week 3)

1. `ai-agent-developer/tutorials/01-first-monitoring-agent.md`
   - From: IMPLEMENTATION_GUIDE Phase 1
   - Add: Conversational examples

2. `installer/tutorials/01-validate-new-installation.md`
   - New: Checklist with agent queries

### Phase 4: Concepts (Week 4)

1. `ai-agent-developer/concepts/battery-degradation-patterns.md`
   - From: DIAGNOSTIC_API_RESEARCH.md Section 2 + external research
   - Explain: Chemistry, aging curves, prediction

2. `installer/concepts/parallel-inverter-operation.md`
   - From: victron_einstein_research.md Section 1
   - Explain: Sync mechanisms, load balancing

### Phase 5: Reference (Week 5-6)

1. Consolidate all API paths from DIAGNOSTIC_API_RESEARCH.md
2. Extract thresholds from Section 13 (Anomaly Detection)
3. Create troubleshooting matrix from common issues
4. Document conversation patterns

### Phase 6: Cleanup (Week 7)

- Archive or deprecate large monolithic files
- Update 00_START_HERE.md → Persona routing
- Add "Related Guides" links to all docs
- Verify all examples work

---

## Example: Detect Battery Degradation

### Before (Current State)

**File**: VICTRON_DBUS_DIAGNOSTIC_API_RESEARCH.md
**Location**: Section 2.2, Line 94-100 (buried in 1,092 line file)
**Format**: Technical reference

```markdown
### 2.2 Battery State of Health & Degradation

| Path | Value | Type | Unit | Purpose | Anomaly Thresholds |
|------|-------|------|------|---------|-------------------|
| `/Soh` | 99.0 | float | % | State of Health | <80%=Investigate, <70%=Replace |
```

**Issues:**
- Buried in large file
- No user story context
- No conversational example
- Threshold without explanation
- No implementation guidance

### After (Proposed)

**File**: `docs/ai-agent-developer/how-to-guides/anomaly-detection/detect-battery-degradation.md`
**Length**: ~300 lines (focused)
**Format**: User story + conversational flow

```markdown
# Detect Battery Degradation

## User Story
**As Mauk**, I want my AI agent to detect battery degradation early, so that I can schedule replacements before failures.

## Business Value
- Cost savings: $5k-20k per battery (avoid emergency replacements)
- Uptime: Prevent unexpected outages
- Planning: 3-6 month lead time

## Conversational Flow

### Agent (proactive):
> "Site Alpha's battery SOH dropped from 88% to 82% in the last month—3x faster than normal. Based on this trend, it'll hit 70% (replacement threshold) in about 8 months. Should I create a maintenance ticket?"

### User:
> "Yes, and show me the degradation chart."

### Agent:
> "[Shows graph]
> Likely cause: Average temperature 42°C (8° above optimal).
> Recommend: 1) Check cooling, 2) Reduce peak discharge, 3) Plan replacement Q2 2026"

## Agent Capabilities
- Query `/Soh`, `/History/ChargedEnergy`, `/Dc/0/Temperature`
- Track SOH over 30-90 days
- Calculate degradation rate (% per month)
- Predict replacement date
- Generate natural language explanation

## API Calls
<details>
<summary>Python Implementation (Click to expand)</summary>

```python
def check_battery_health(site):
    # Code here...
```

</details>

## Thresholds

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| SOH | ≥90% | 85-90% | <85% |
| Degradation Rate | <0.2%/month | 0.2-0.5% | >0.5% |

## Related Guides
- Tutorial: [Build Battery Health Agent](../../tutorials/02-battery-health-agent.md)
- Concept: [Battery Degradation Patterns](../../concepts/battery-degradation-patterns.md)
- Reference: [Battery Thresholds](../../reference/thresholds/battery-thresholds.md)
```

**Improvements:**
- Focused 300-line guide (not 1,000+ line file)
- User story first
- Conversational flow shows 2025 interaction pattern
- Business value explicit
- Python code collapsed by default
- Related guides for deeper learning

---

## 2025 AI Agent UX Patterns

Based on 2025 research, documentation should reflect these interaction patterns:

### 1. Natural Language First

**Old Way** (Python-first):
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

Agent: "Site 3 battery is at 73% SOC, charging at 15A.
        Should reach 90% in about 2 hours."
```

### 2. Proactive Assistance

**Old Way**: User must ask
```python
if soc < 20:
    send_alert("Low SOC")
```

**New Way**: Agent takes initiative
```
Agent: "I notice Site 5's battery is at 15%.
        Grid is available. Should I enable grid charging?"
```

### 3. Guided Conversations

**Old Way**: Show all data
```json
{
  "soc": 45,
  "soh": 82,
  "voltage": 48.2,
  "current": -15.3,
  ...
}
```

**New Way**: Agent guides diagnosis
```
User: "Something's wrong with Site 7"

Agent: "Let me check... I see low SOC (18%) and
        ChargeBlocked alarm. Checking BMS limits...

        Root cause: Battery temperature is 52°C, above
        the 50°C charge limit. The BMS is blocking
        charging to protect the cells.

        Resolution: Wait for cooling (<45°C) or check
        cooling system. Should I monitor temp and notify
        when charging resumes?"
```

### 4. Context-Aware

**Old Way**: Stateless queries
```python
# Each query independent
get_soc(site)
get_soh(site)
get_voltage(site)
```

**New Way**: Agent remembers context
```
User: "Show me Site 3 battery"
Agent: [Shows SOC, SOH, voltage]

User: "How about Site 4?"
Agent: [Knows you want battery metrics]

User: "Which is healthier?"
Agent: [Compares Site 3 vs 4 without re-asking]
```

---

## Success Criteria

### For Mauk (AI Agent Developer)

After restructure, Mauk can:
- [ ] Build working monitoring agent in <2 hours (Tutorial 01)
- [ ] Find "detect battery degradation" without reading 1,000 lines
- [ ] Understand conversational patterns (not just API calls)
- [ ] Implement proactive alerts with natural language
- [ ] Explain ROI to stakeholders (business value in concepts)

### For Installer

After restructure, an installer can:
- [ ] Validate installation using AI queries in <30 min (Tutorial 01)
- [ ] Troubleshoot "battery not charging" remotely (How-to guide)
- [ ] Understand *why* load imbalance happens (Concept doc)
- [ ] Ask agent "What's wrong?" and get actionable diagnosis
- [ ] Copy-paste bash scripts without reading technical docs

### Documentation Quality

- [ ] Every how-to has conversational flow example
- [ ] Every concept explains "why", not just "what"
- [ ] Every tutorial builds working agent
- [ ] Every reference has context links
- [ ] Python code collapsed by default
- [ ] Related guides cross-linked
- [ ] No file >500 lines

---

## Migration Checklist

### Week 1: Foundation
- [ ] Create directory structure
- [ ] Write PERSONAS.md ✅
- [ ] Create README for each persona workspace
- [ ] Convert QUICK_REFERENCE json → markdown tables

### Week 2: Core How-Tos (4 guides)
- [ ] detect-battery-degradation.md
- [ ] battery-not-charging.md
- [ ] natural-language-queries.md
- [ ] inverter-load-imbalance.md (from einstein case study)

### Week 3: Tutorials (2 guides)
- [ ] 01-first-monitoring-agent.md
- [ ] 01-validate-new-installation.md

### Week 4: Concepts (2 guides)
- [ ] battery-degradation-patterns.md
- [ ] parallel-inverter-operation.md

### Week 5-6: Reference
- [ ] Consolidate API paths
- [ ] Extract thresholds
- [ ] Create troubleshooting matrix

### Week 7: Polish
- [ ] Add "Related Guides" links
- [ ] Verify examples work
- [ ] Update 00_START_HERE
- [ ] Archive old files

---

## File Size Targets

| Document Type | Target Lines | Rationale |
|---------------|--------------|-----------|
| Tutorial | 200-400 | Complete learning path |
| How-To Guide | 100-300 | Focused task |
| Concept | 150-300 | Explain one idea well |
| Reference | 100-200 per page | Quick lookup |

**Current Problem**: Files are 300-1,391 lines
**Proposed Solution**: Break into focused 100-400 line guides

---

## Risks & Mitigation

### Risk 1: Lose Technical Depth

**Concern**: Splitting files might lose comprehensive reference

**Mitigation**:
- Keep complete API reference in `reference/` section
- Link related guides extensively
- Archive (don't delete) original files

### Risk 2: Duplicate Content

**Concern**: Same threshold appears in multiple places

**Mitigation**:
- Single source of truth in `reference/thresholds/`
- Other docs link to reference
- DRY principle: Don't Repeat Yourself

### Risk 3: User Can't Find Content

**Concern**: 50+ files harder to navigate than 7 files

**Mitigation**:
- Clear persona routing from README
- Each persona workspace has navigation
- Search-friendly file names (detect-battery-degradation.md)
- Extensive cross-linking

---

## Rollout Strategy

### Phase 1: Pilot (Week 1-2)

**Create 4 new guides** (1 per category):
1. Tutorial: 01-first-monitoring-agent.md
2. How-to: detect-battery-degradation.md
3. Concept: battery-degradation-patterns.md
4. Reference: critical-paths.md

**Feedback**: Share with Mauk and 2 installers
**Measure**: Time to complete tutorial, questions asked

### Phase 2: Expand (Week 3-4)

**If pilot succeeds**, create remaining priority guides

### Phase 3: Full Migration (Week 5-7)

**Migrate all content**, archive old files

### Phase 4: Maintain

**Ongoing**: Add community contributions, update with new Victron features

---

## Next Steps

1. **Review this proposal** with @podarok and stakeholders
2. **Get feedback** from Mauk and 1-2 installers
3. **Approve directory structure** and file naming
4. **Create pilot guides** (Week 1-2)
5. **Iterate** based on feedback
6. **Full migration** (Week 3-7)

---

## Questions for Review

1. **Personas**: Are Mauk and Installer descriptions accurate?
2. **Structure**: Does Diataxis categorization make sense?
3. **Priorities**: Are the Phase 2 "must have" guides correct?
4. **User Stories**: Does the "detect battery degradation" example work?
5. **File Sizes**: Are 100-400 line targets reasonable?
6. **Migration**: Is 7-week timeline achievable?

---

## Resources

- **Diataxis**: https://diataxis.fr/
- **template_for_agents.git**: Directory structure inspiration
- **2025 AI UX Research**: Conversational patterns, proactive agents
- **Current Docs**: 119KB in git@github.com:EnergyCitizen/victron_dbus_api.git

---

**Prepared by**: EnergyCitizen team
**Review by**: @podarok
**Stakeholders**: Mauk Muller (El Niño), Victron Energy, Installer community

---

**Made in Ukraine 🇺🇦 with love by EnergyCitizen**
