# Saudi Intelligence Engine (SIE)

> **GOD-LEVEL B2B Lead Discovery + Strategic Bottleneck Intelligence**
> *Autonomous intelligence extraction for Saudi Arabia's industrial ecosystem*

---

## 🚀 Quick Start

### 1. Configure Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

| Secret Name | Value | Where to Get |
|-------------|-------|--------------|
| `TELEGRAM_BOT_TOKEN` | Your bot token | [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | Your chat ID | [@userinfobot](https://t.me/userinfobot) |
| `EXA_API_KEY` | Exa search API key | [exa.ai](https://exa.ai) |

### 2. Run Locally (Test Mode)

```bash
cd Operation-Peanut/skills/saudi-intelligence-engine
python run_cycle.py
```

### 3. Deploy to GitHub Actions

The workflow automatically runs every 3 days. To trigger manually:

1. Go to Actions tab in GitHub
2. Select "Saudi Intelligence Engine - 3-Day Cycle"
3. Click "Run workflow"

---

## 📁 File Structure

```
saudi-intelligence-engine/
├── SKILL.md              # Core skill definition & methodology
├── QUERIES.md            # Search query templates library
├── ECOSYSTEMS.md         # Target ecosystem mappings (Aramco, NEOM, PIF)
├── BOTTLENECKS.md        # Known inefficiency patterns database
├── telegram_delivery.py  # Telegram delivery module
├── extraction_engine.py  # Main extraction pipeline
├── run_cycle.py          # Quick run script (test mode)
└── README.md             # This file
```

---

## 🎯 What Gets Delivered

### People (10-20 per cycle)
- Name, Role, Company
- Sector/Niche
- Bottleneck Insight (specific inefficiency)
- AI Solvability (High/Medium/Low)
- Score (0-100, threshold ≥70)
- Profile Link

### Companies (5-10 per cycle)
- Company Name
- Sector
- Bottleneck/Gap Insight
- AI Solvability
- Why Follow
- Page Link

---

## 📊 Scoring System

| Factor | Weight | Description |
|--------|--------|-------------|
| Role Authority | 20% | Decision-making power, seniority |
| Multi-Project Influence | 20% | Works across multiple mega-projects |
| Sector Impact | 20% | Tier S > Tier A > Tier B |
| Economic Impact | 30% | Size of inefficiency/gap |
| AI Solvability | 10% | Can our stack realistically solve it |

**Threshold:** Only leads with score ≥70 are delivered.

---

## 🏭 Sector Priorities

### Tier S — Maximum Leverage
- Predictive Maintenance AI
- Industrial Automation
- Asset Lifecycle Management
- Supply Chain Optimization
- Compliance/Reporting Automation

### Tier A — Strategic Platforms
- Digital Twins
- BIM Platforms
- Sovereign Ledger AI

### Tier B — Supporting Infrastructure
- Enterprise Fintech
- Risk Analytics
- Cross-Border Payments

---

## 🎯 Target Ecosystems

| Ecosystem | Why It Matters |
|-----------|----------------|
| **Saudi Aramco** | World's largest oil company, massive AI adoption |
| **NEOM** | $500B mega-project, technology-first |
| **PIF Portfolio** | 500+ companies, all sectors |
| **LEAP Conference** | Annual tech event, speaker directory |

---

## 🔧 Configuration

### Environment Variables

```bash
# Required
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"

# Optional (for live extraction)
export EXA_API_KEY="your_exa_key"
```

### Customization

Edit `QUERIES.md` to add custom search patterns:
```markdown
"[Role]" + "[Sector]" + "Saudi Arabia" + "[Bottleneck Keyword]"
```

Edit `BOTTLENECKS.md` to add known inefficiencies:
```markdown
BOTTLENECK: [Description]
Impact: $X annually
AI Solvability: HIGH/MEDIUM/LOW
```

---

## 🚨 Troubleshooting

### Telegram Delivery Fails

1. **Check network access** - Telegram may be blocked in some regions
2. **Verify bot token** - Ensure it's correct and not revoked
3. **Verify chat ID** - Must be numeric, use @userinfobot

### No Qualified Leads

1. **Lower threshold** in `run_cycle.py` (line ~100)
2. **Add more queries** in `QUERIES.md`
3. **Check Exa API** if using live extraction

### GitHub Actions Not Running

1. **Check workflow is enabled** in Actions tab
2. **Verify secrets are set** correctly
3. **Check workflow syntax** is valid YAML

---

## 📈 Future Enhancements

- [ ] Add Exa API integration for live extraction
- [ ] Implement cycle history tracking
- [ ] Add duplicate detection across cycles
- [ ] Support multiple Telegram channels
- [ ] Add Arabic language support

---

## 📝 Changelog

### v1.0.0 (2026-03-20)
- Initial release
- Core skill framework
- Telegram delivery
- 5-factor scoring system
- GitHub Actions workflow

---

*Built with GOD-LEVEL techniques. Not your average lead generation.*
