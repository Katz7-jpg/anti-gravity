# Saudi Intelligence Engine (SIE)

> **GOD-LEVEL INTELLIGENCE EXTRACTION SYSTEM**
> *Autonomous B2B Lead Discovery + Strategic Bottleneck Intelligence for Saudi Arabia*

---

## 🎯 Core Mission

Extract high-leverage decision-makers, companies, and unsolved inefficiencies from Saudi Arabia's industrial ecosystem. Deliver curated intelligence every 3 days via Telegram.

---

## ⚡ Execution Protocol

### Phase 1: Query Generation Matrix

Generate structured search queries using the **ROLE × SECTOR × GEOGRAPHY × BOTTLENECK** matrix:

```
Query Template: "[Role] + [Sector] + [Geography] + [Bottleneck Keyword]"

Examples:
- "Predictive Maintenance Manager Oil Gas Saudi Arabia operational inefficiency"
- "Supply Chain Director Riyadh logistics bottleneck"
- "Industrial AI Engineer NEOM automation gap"
- "Asset Lifecycle Manager Aramco equipment tracking"
- "Digital Twin Engineer Saudi construction delay"
```

### Phase 2: Multi-Source Extraction

| Source Type | Extraction Method | Data Points |
|-------------|-------------------|-------------|
| Public LinkedIn | Google site:linkedin.com/in | Name, Role, Company |
| Corporate Websites | Company /team pages | Executive bios |
| Conference Speakers | LEAP, FII, PIF events | Decision-makers |
| News Mentions | Press releases, interviews | Strategic moves |
| Tender Documents | Government procurement | Project opportunities |

### Phase 3: Scoring Algorithm

```python
def calculate_lead_score(lead):
    """
    5-Factor Weighted Scoring System
    Threshold: ≥70 points required
    """
    score = 0
    
    # Factor 1: Role Authority (20 points max)
    role_scores = {
        "CEO/President": 20,
        "VP/SVP": 18,
        "Director": 16,
        "Senior Manager": 14,
        "Manager": 12,
        "Senior Engineer": 10,
        "Lead/Principal": 8
    }
    score += role_scores.get(lead.role_type, 5)
    
    # Factor 2: Multi-Project Influence (20 points max)
    if lead.connected_projects >= 3:
        score += 20
    elif lead.connected_projects == 2:
        score += 15
    elif lead.connected_projects == 1:
        score += 10
    
    # Factor 3: Sector Impact (20 points max)
    tier_scores = {"S": 20, "A": 15, "B": 10}
    score += tier_scores.get(lead.tier, 5)
    
    # Factor 4: Economic Impact of Gap (30 points max)
    impact_scores = {
        "multi_million_loss": 30,
        "major_delay": 25,
        "operational_inefficiency": 20,
        "compliance_gap": 15,
        "process_improvement": 10
    }
    score += impact_scores.get(lead.bottleneck_type, 5)
    
    # Factor 5: AI Solvability (10 points max)
    solvability_scores = {"High": 10, "Medium": 6, "Low": 2}
    score += solvability_scores.get(lead.ai_solvability, 2)
    
    return score
```

---

## 🏗️ Sector Priority Framework

### Tier S — Maximum Leverage (Score Multiplier: 1.5x)

| Niche | Why It Matters | Bottleneck Patterns |
|-------|----------------|---------------------|
| Predictive Maintenance AI | Aramco, Sabic, mining ops | Equipment downtime, spare parts waste |
| Industrial Automation | Manufacturing, logistics | Manual processes, quality issues |
| Asset Lifecycle Management | Mega-projects, facilities | Tracking gaps, depreciation losses |
| Workforce Systems | Construction, operations | Scheduling inefficiencies, compliance |
| Regulatory Reporting | All sectors | Manual reporting, deadline pressure |

### Tier A — Strategic Platforms (Score Multiplier: 1.2x)

| Niche | Why It Matters | Bottleneck Patterns |
|-------|----------------|---------------------|
| Digital Twins | NEOM, smart cities | Data silos, simulation gaps |
| BIM Platforms | Construction, real estate | Design-construction disconnect |
| Sovereign Ledger AI | Government, finance | Audit trails, transparency |

### Tier B — Supporting Infrastructure (Score Multiplier: 1.0x)

| Niche | Why It Matters | Bottleneck Patterns |
|-------|----------------|---------------------|
| Enterprise Fintech | Banking, payments | Cross-border friction |
| Risk Analytics | Insurance, finance | Data quality, model gaps |
| Compliance Systems | Regulated industries | Manual checks, reporting |

---

## 🎯 Target Ecosystems

### Primary Targets

| Ecosystem | Key Entities | Connection Points |
|-----------|--------------|-------------------|
| **Saudi Aramco** | Aramco, Sabic, subsidiaries | Contractors, suppliers, JV partners |
| **NEOM** | NEOM Company, subsidiaries | Technology partners, construction |
| **PIF Portfolio** | 500+ companies | Board members, executives |
| **LEAP Conference** | Tech leaders, investors | Speakers, sponsors, attendees |

### Shadow Ecosystem Discovery

```
Technique: Identify Tier-2/Tier-3 suppliers to mega-projects

Query Patterns:
- "[Company] supplier Saudi Arabia"
- "[Project] contractor list"
- "Aramco approved vendors [category]"
- "NEOM technology partners"
- "PIF portfolio company suppliers"
```

---

## 🔍 Advanced Intelligence Techniques

### Technique 1: Network Node Mapping

```
Step 1: Identify Tier-1 contractors (EPC firms, system integrators)
Step 2: Extract key personnel from Tier-1
Step 3: Find Tier-2 suppliers (SMEs, specialists)
Step 4: Cross-reference with LinkedIn connections
Step 5: Map influence clusters
```

### Technique 2: Bottleneck Signal Detection

```
Search Patterns for Inefficiency Discovery:
- "[Company] operational challenges"
- "[Sector] Saudi Arabia delay"
- "[Industry] bottleneck Riyadh"
- "[Company] system implementation issues"
- "[Sector] manual process Saudi"
```

### Technique 3: Boring Lucre Capture

```
High-Value, Low-Competition Niches:
- Equipment inspection systems
- Compliance dashboards
- Asset tracking for leasing
- Workforce scheduling optimization
- Regulatory reporting automation
- Document management for tenders
```

### Technique 4: Multi-Project Relevance Scoring

```
Identify professionals who appear across:
- Multiple PIF projects
- Aramco + NEOM simultaneously
- Government + private sector
- Multiple construction mega-projects

These individuals have outsized influence.
```

---

## 📊 Output Format

### People Output Template

```
🔥 [TIER] — High-Impact Lead

**Name:** [Full Name]
**Role:** [Job Title]
**Company:** [Company Name]
**Sector:** [Sector / Niche]
**Bottleneck Insight:** [Specific inefficiency or gap]
**AI Solvability:** [High/Medium/Low]
**Why This Person Matters:** [1-line strategic value]
**Score:** [0-100]
**Profile:** [LinkedIn URL or search reference]
```

### Company Output Template

```
🏢 [TIER] — High-Impact Company

**Company:** [Company Name]
**Sector:** [Sector / Niche]
**Bottleneck Insight:** [Optional gap]
**AI Solvability:** [High/Medium/Low]
**Why Follow:** [1-line relevance]
**Link:** [Website or LinkedIn]
```

### Cycle Summary Template

```
📊 **Intelligence Cycle Summary**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**Leads Extracted:** [X] people, [Y] companies
**Tier S Opportunities:** [Z]
**High AI-Solvable Gaps:** [N]
**Sectors Covered:** [Energy, Logistics, Industrial AI, etc.]
**Next Cycle:** [Date]
```

---

## 🔐 Operational Constraints

- ✅ Read-only operations (no LinkedIn login)
- ✅ Public sources only
- ✅ No automated messaging
- ✅ No data storage beyond cycle
- ✅ Respect robots.txt
- ✅ Rate-limited requests

---

## 📁 File Structure

```
saudi-intelligence-engine/
├── SKILL.md              # This file
├── QUERIES.md            # Query templates library
├── SCORING.md            # Detailed scoring rubrics
├── ECOSYSTEMS.md         # Target ecosystem mappings
├── BOTTLENECKS.md        # Known inefficiency patterns
├── TELEGRAM_FORMAT.md    # Delivery formatting rules
└── CYCLE_LOG.md          # Previous cycle history
```

---

## 🚀 Quick Start

1. **Generate Queries** → Use QUERIES.md templates
2. **Execute Search** → Exa MCP + Playwright MCP
3. **Score Results** → Apply scoring algorithm
4. **Filter** → Keep only ≥70 scores
5. **Format** → Apply Telegram templates
6. **Deliver** → Send to configured Chat ID

---

*Last Updated: 2026-03-20*
*Version: 1.0.0 - GOD LEVEL*
