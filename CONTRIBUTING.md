# Contributing to Victron DBus API

Thank you for your interest in contributing! This project welcomes contributions from AI agent developers, Victron installers, and the community.

---

## 🤝 Ways to Contribute

### For AI Agent Developers
- **Share conversational patterns**: Document how your users interact with agents
- **Add monitoring use cases**: New anomaly detection patterns
- **Improve tutorials**: Enhance examples with real-world scenarios
- **Contribute thresholds**: Share your alert thresholds and decision rules

### For Victron Installers
- **Document troubleshooting**: Add field experience and edge cases
- **Share diagnostic workflows**: How you use AI agents for remote diagnosis
- **Improve validation checklists**: Installation validation improvements
- **Add alarm explanations**: Plain language alarm descriptions

### For Everyone
- **Fix documentation**: Typos, broken links, unclear sections
- **Add examples**: Real conversational flows from your usage
- **Improve code**: Python scripts and API server enhancements
- **Translate**: Help make documentation multilingual

---

## 📋 Contribution Guidelines

### Documentation

**Follow Diataxis Framework**:
- **Tutorials**: Learning-oriented, hands-on, working code (30-120 min)
- **How-To Guides**: Task-oriented, problem-solving (10-30 min)
- **Concepts**: Understanding-oriented, explain "why" (15-25 min)
- **Reference**: Information-oriented, quick lookup (2-5 min)

**Format Requirements**:
- User story first (As [persona], I want..., so that...)
- Conversational flow examples (User asks, Agent responds)
- Agent capabilities listed clearly
- Python code in collapsed `<details>` sections
- Cross-link related guides
- Add "Made in Ukraine 🇺🇦" footer

**File Length**:
- Keep focused: 100-500 lines per guide
- No monolithic 1,000+ line documents

### Code Contributions

**For Python Scripts**:
- Maintain read-only API principle
- Add docstrings and type hints
- Test on real Venus OS devices
- Include usage examples

**For API Server**:
- Security: Keep read-only, no write operations
- Compatibility: Venus OS v2.9+ (Python 3.9+)
- Error handling: Graceful failures
- Logging: Clear, actionable messages

### Testing

- **Documentation**: Test on target persona (AI Developer or Installer)
- **Code**: Run on actual Venus OS device (Cerbo GX, Venus GX)
- **Links**: Verify all cross-references work
- **Examples**: Ensure conversational flows are realistic

---

## 🔄 Contribution Workflow

### 1. Fork and Clone

```bash
# Fork repository on GitHub first, then:
git clone git@github.com:YOUR_USERNAME/ai_victron_dbus_api.git
cd ai_victron_dbus_api
git remote add upstream git@github.com:EnergyCitizen/ai_victron_dbus_api.git
```

### 2. Create Feature Branch

```bash
git checkout -b feature/add-solar-anomaly-detection
```

**Branch Naming**:
- `feature/[description]` - New features or guides
- `fix/[issue]` - Bug fixes
- `docs/[description]` - Documentation improvements

### 3. Make Changes

Follow the guidelines above. Test your changes.

### 4. Commit

```bash
git add .
git commit -m "Add how-to guide for solar production anomaly detection

- User story: Detect underperforming solar arrays
- Conversational flow examples
- Threshold: <70% of expected production
- Real case study from 50-site fleet"
```

**Commit Message Format**:
- First line: Brief summary (50 chars)
- Blank line
- Details: Bullet points explaining what and why
- No Claude/AI credits (per project policy)

### 5. Push and Create PR

```bash
git push origin feature/add-solar-anomaly-detection
gh pr create --title "Add solar production anomaly detection guide"
```

**PR Description Should Include**:
- Summary of changes
- Which persona benefits (AI Developer, Installer, or both)
- Testing performed (which Venus OS devices)
- Related issues or guides
- Screenshots/examples if applicable

---

## 📝 Documentation Standards

### User Story Format

```markdown
# [Guide Title]

## User Story
**As [AI Developer/Installer]**, I want my AI agent to [capability], so that [benefit].

## Business Value
| Benefit | Value |
|---------|-------|
| Cost Savings | $X saved per... |
| Time Saved | X hours per... |

## Conversational Flow

### User Says:
> "Question or request"

### Agent Thinks (internal):
1. Step 1
2. Step 2

### Agent Says:
> "Natural language response with context and next steps"

## Agent Capabilities
- Required DBus paths
- Analysis logic
- Response generation

## API Implementation
<details>
<summary>Click to expand</summary>

```python
# Code here
```

</details>

## Related Guides
- Tutorial: [Link](path)
- How-To: [Link](path)
- Concept: [Link](path)

---
Made in Ukraine 🇺🇦 with love by EnergyCitizen
```

### Code Style

**Python**:
- PEP 8 compliance
- Type hints for functions
- Docstrings (Google style)
- Error handling with try/except
- Comments for complex logic only

**Example**:
```python
def get_battery_soc(site_ip: str) -> Optional[float]:
    """
    Get battery state of charge from Victron device.

    Args:
        site_ip: IP address of Venus OS device

    Returns:
        SOC percentage (0-100) or None if unavailable
    """
    try:
        response = requests.get(...)
        return response.json()['value']
    except Exception as e:
        logger.error(f"Failed to get SOC: {e}")
        return None
```

---

## 🚫 What NOT to Contribute

### Don't Add:
- **Write operations**: API must remain read-only
- **Authentication**: Security should be network-level (VPN/firewall)
- **AI/Claude credits**: Per project NDA policy
- **Comprehensive docs without request**: Keep focused and purposeful
- **Large monolithic files**: Keep guides 100-500 lines
- **Python code without user story**: Show conversational flow first

---

## 🎯 Good First Contributions

### Easy (30 minutes)
- Fix typos or broken links
- Add conversational examples to existing guides
- Improve bash script comments
- Add real data examples from your system

### Medium (1-2 hours)
- Create new how-to guide from your use case
- Add concept doc explaining a topic
- Improve tutorial with better examples
- Add missing cross-links between guides

### Advanced (3+ hours)
- Create new tutorial from scratch
- Add comprehensive reference documentation
- Contribute new API server features (read-only)
- Add multi-language support

---

## 💡 Contribution Ideas

### AI Agent Patterns
- Multi-agent collaboration patterns
- Context window optimization strategies
- Prompt engineering for Victron diagnostics
- Error recovery and fallback patterns

### Installer Workflows
- More troubleshooting scenarios
- Country-specific grid code guides
- Installation validation checklists
- Before/after comparison methods

### Technical
- Additional Venus OS device support
- Performance optimization
- Batch query patterns
- WebSocket real-time updates (future)

---

## 🐛 Reporting Issues

### Bug Reports

Use GitHub Issues with:
- **Title**: Clear, specific (e.g., "API returns 500 on /settings endpoint")
- **Environment**: Venus OS version, firmware, device type
- **Steps to Reproduce**: Exact commands or API calls
- **Expected vs Actual**: What should happen vs what happens
- **Logs**: Error messages, API responses

### Feature Requests

Include:
- **Persona**: AI Developer or Installer
- **User Story**: As [persona], I want..., so that...
- **Use Case**: Real scenario where this helps
- **Acceptance Criteria**: How to know it's done

---

## 🔍 Code Review Process

### What We Look For

**Documentation**:
- ✅ Follows persona-based structure
- ✅ Conversational examples included
- ✅ Cross-links to related guides
- ✅ Tested on target persona
- ✅ Made in Ukraine footer

**Code**:
- ✅ Read-only principle maintained
- ✅ Works on Venus OS v2.9+
- ✅ Error handling included
- ✅ Type hints and docstrings
- ✅ Tested on real device

### Timeline

- **Initial Review**: Within 48 hours
- **Feedback**: We'll comment on PR
- **Merge**: After tests pass and review approved

---

## 🙏 Recognition

Contributors will be:
- Listed in GitHub contributors
- Mentioned in release notes
- Thanked in acknowledgments

**Top contributors may be invited to**:
- Collaborate with ecosystem partners
- Beta test VRM ProxyRelay integration
- Join Victron AI ecosystem partnership

---

## 📞 Questions?

- **GitHub Issues**: [Ask questions](https://github.com/EnergyCitizen/victron_dbus_api/issues)
- **GitHub Discussions**: Coming soon
- **Victron Community**: [community.victronenergy.com](https://community.victronenergy.com)

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License with authorized use for Victron AI ecosystem partners and Victron Energy. See [LICENSE](LICENSE) for details.

---

## 🎓 Resources for Contributors

### Learn About Project
- [README.md](README.md) - Project overview
- [PERSONAS.md](PERSONAS.md) - Target user profiles
- [00_START_HERE.md](00_START_HERE.md) - Documentation navigation

### Learn Diataxis
- [Diataxis Framework](https://diataxis.fr/) - Documentation system we follow
- [Our Structure](docs/) - See it in practice

### Learn Victron
- [Victron Professional](https://professional.victronenergy.com/) - Training and certification
- [Venus OS GitHub](https://github.com/victronenergy/venus) - Platform source code
- [DBus Documentation](https://github.com/victronenergy/dbus-mqtt) - DBus architecture

---

<div align="center">

**Made in Ukraine 🇺🇦 with love by [EnergyCitizen](https://github.com/EnergyCitizen)**

Thank you for contributing to the Victron AI ecosystem!

</div>
