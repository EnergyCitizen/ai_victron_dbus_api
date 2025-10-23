# Archived Documentation

This directory contains the original monolithic research documents that have been reorganized into the persona-based Diataxis structure.

---

## Archived Files

| File | Size | Status | Replacement |
|------|------|--------|-------------|
| VICTRON_DBUS_DIAGNOSTIC_API_RESEARCH.md | 47KB | Archived | Split into docs/ai-agent-developer/ and docs/installer/ guides |
| victron_einstein_research.md | 38KB | Archived | Extracted into how-tos and concepts |
| victron_einstein_index.md | 10KB | Archived | Replaced by persona workspace READMEs |
| victron_einstein_metrics.md | 11KB | Archived | Integrated into reference docs |
| IMPLEMENTATION_GUIDE_AI_AGENTS.md | 20KB | Archived | Converted to tutorials |

---

## Why Archived?

These documents were excellent technical references but:
- **Too long**: 300-1,400 lines per file (hard to navigate)
- **Component-focused**: Organized by system component, not user goal
- **Python-first**: Code examples before user stories
- **Not conversational**: Didn't reflect 2025 AI agent interaction patterns

---

## New Structure

Content has been reorganized into **40+ focused guides** (100-400 lines each) following the **Diataxis framework**:

- **Tutorials**: Hands-on learning (30-120 min)
- **How-To Guides**: Task-oriented problem solving (10-30 min)
- **Concepts**: Understanding theory (15-25 min)
- **Reference**: Quick lookup (2-5 min)

**See**: [00_START_HERE.md](../../00_START_HERE.md) for navigation

---

## Content Mapping

### From VICTRON_DBUS_DIAGNOSTIC_API_RESEARCH.md

| Original Section | New Location |
|------------------|--------------|
| Section 2: Battery | → detect-battery-degradation.md, battery-thresholds.md, battery-degradation-patterns.md |
| Section 3: Inverter | → inverter monitoring guides, state-codes.md |
| Section 5: Grid | → detect-grid-issues.md, grid-thresholds.md |
| Section 13: Anomaly Detection | → All anomaly detection how-tos |
| Section 17: Alarms | → alarm-codes.md |

### From victron_einstein_research.md

| Original Section | New Location |
|------------------|--------------|
| Section 1: Parallel Multi-Inverter | → parallel-inverter-operation.md (concept) |
| Section 7: Load Imbalance | → inverter-load-imbalance.md (real case study) |
| Section 8: ESS Features | → ess-modes-explained.md (concept) |
| Section 10: Optimization | → ess-optimization-strategies.md (concept) |

### From IMPLEMENTATION_GUIDE_AI_AGENTS.md

| Original Phase | New Location |
|----------------|--------------|
| Phase 1: Basic Monitoring | → 01-first-monitoring-agent.md (tutorial) |
| Phase 2: Battery Diagnostics | → 02-battery-health-agent.md (tutorial) |
| Phase 3: ESS Optimization | → 03-fleet-dashboard-agent.md (tutorial) |
| Phase 4: Predictive Maintenance | → 04-predictive-maintenance-agent.md (tutorial) |

---

## When to Use Archived Docs

**Use archived docs if**:
- You need comprehensive technical reference (all paths in one place)
- You're researching a specific DBus path not yet documented in new structure
- You want to see original research context

**Use new docs for**:
- Learning (tutorials)
- Solving specific problems (how-tos)
- Understanding concepts
- Quick reference lookups

---

## Migration Complete

**Date**: 2025-10-23
**Old Structure**: 7 files, 119KB, 3,548 lines
**New Structure**: 40+ files, organized by persona and Diataxis type

All content preserved, reorganized for better discoverability and 2025 AI agent interaction patterns.

---

**Made in Ukraine 🇺🇦 with love by EnergyCitizen**
