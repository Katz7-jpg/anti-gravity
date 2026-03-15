# ToolUniverse Skills Index

## Complete Skills Catalog

This index provides a comprehensive listing of all ToolUniverse skills available in the AI_FACTORY workspace.

---

## Research Skills

### Drug Research
| Skill | Location | Description |
|-------|----------|-------------|
| `tooluniverse-drug-research` | `Operation-Peanut/skills/tooluniverse-drug-research/` | Comprehensive drug information retrieval and analysis |
| `tooluniverse-drug-repurposing` | `Operation-Peanut/skills/tooluniverse-drug-repurposing/` | Identify new indications for existing drugs |
| `tooluniverse-drug-drug-interaction` | `Operation-Peanut/skills/tooluniverse-drug-drug-interaction/` | Analyze potential drug-drug interactions |

### Target & Disease Research
| Skill | Location | Description |
|-------|----------|-------------|
| `tooluniverse-target-research` | `Operation-Peanut/skills/tooluniverse-target-research/` | Drug target identification and validation |
| `tooluniverse-disease-research` | `Operation-Peanut/skills/tooluniverse-disease-research/` | Disease mechanism and pathway research |
| `tooluniverse-infectious-disease` | `Operation-Peanut/skills/tooluniverse-infectious-disease/` | Infectious disease research tools |

### Literature Research
| Skill | Location | Description |
|-------|----------|-------------|
| `tooluniverse-literature-deep-research` | `Operation-Peanut/skills/tooluniverse-literature-deep-research/` | Comprehensive literature search and synthesis |

---

## Clinical Development Skills

| Skill | Location | Description |
|-------|----------|-------------|
| `tooluniverse-clinical-trial-design` | `Operation-Peanut/skills/tooluniverse-clinical-trial-design/` | Clinical trial protocol design and optimization |
| `tooluniverse-pharmacovigilance` | `Operation-Peanut/skills/tooluniverse-pharmacovigilance/` | Drug safety monitoring and signal detection |
| `tooluniverse-precision-oncology` | `Operation-Peanut/skills/tooluniverse-precision-oncology/` | Precision oncology treatment matching |

---

## Bioinformatics Skills

| Skill | Location | Description |
|-------|----------|-------------|
| `tooluniverse-crispr-screen-analysis` | `Operation-Peanut/skills/tooluniverse-crispr-screen-analysis/` | CRISPR screen data analysis |
| `tooluniverse-structural-variant-analysis` | `Operation-Peanut/skills/tooluniverse-structural-variant-analysis/` | Genomic structural variant detection |
| `tooluniverse-rare-disease-diagnosis` | `Operation-Peanut/skills/tooluniverse-rare-disease-diagnosis/` | Rare disease diagnostic support |

---

## Protein Engineering Skills

| Skill | Location | Description |
|-------|----------|-------------|
| `tooluniverse-antibody-engineering` | `Operation-Peanut/skills/tooluniverse-antibody-engineering/` | Therapeutic antibody design |
| `tooluniverse-binder-discovery` | `Operation-Peanut/skills/tooluniverse-binder-discovery/` | Protein binder identification |
| `tooluniverse-protein-therapeutic-design` | `Operation-Peanut/skills/tooluniverse-protein-therapeutic-design/` | Protein therapeutic engineering |

---

## Data Retrieval Skills

| Skill | Location | Description |
|-------|----------|-------------|
| `tooluniverse-sequence-retrieval` | `Operation-Peanut/skills/tooluniverse-sequence-retrieval/` | Biological sequence data retrieval |
| `tooluniverse-expression-data-retrieval` | `Operation-Peanut/skills/tooluniverse-expression-data-retrieval/` | Gene expression data access |
| `tooluniverse-chemical-compound-retrieval` | `Operation-Peanut/skills/tooluniverse-chemical-compound-retrieval/` | Chemical compound information |
| `tooluniverse-protein-structure-retrieval` | `Operation-Peanut/skills/tooluniverse-protein-structure-retrieval/` | Protein structure data |

---

## Development Tools

| Skill | Location | Description |
|-------|----------|-------------|
| `devtu-create-tool` | `Operation-Peanut/skills/devtu-create-tool/` | Create new ToolUniverse tools |
| `devtu-fix-tool` | `Operation-Peanut/skills/devtu-fix-tool/` | Debug and fix existing tools |
| `devtu-optimize-skills` | `Operation-Peanut/skills/devtu-optimize-skills/` | Optimize skill descriptions |
| `devtu-optimize-descriptions` | `Operation-Peanut/skills/devtu-optimize-descriptions/` | Optimize tool descriptions |
| `devtu-docs-quality` | `Operation-Peanut/skills/devtu-docs-quality/` | Documentation quality tools |
| `devtu-auto-discover-apis` | `Operation-Peanut/skills/devtu-auto-discover-apis/` | Automatic API discovery |

---

## Setup & SDK

| Skill | Location | Description |
|-------|----------|-------------|
| `setup-tooluniverse` | `Operation-Peanut/skills/setup-tooluniverse/` | ToolUniverse installation and setup |
| `tooluniverse-sdk` | `Operation-Peanut/skills/tooluniverse-sdk/` | SDK for ToolUniverse development |
| `tooluniverse` | `Operation-Peanut/skills/tooluniverse/` | Core ToolUniverse integration |
| `create-tooluniverse-skill` | `Operation-Peanut/skills/create-tooluniverse-skill/` | Create new ToolUniverse skills |

---

## Skill File Structure

Each skill typically contains:

```
skill-name/
├── SKILL.md              # Main skill definition (required)
├── README.md             # Overview and usage guide
├── EXAMPLES.md           # Example workflows
├── CHECKLIST.md          # Validation checklist
├── QUICK_START.md        # Quick start guide
├── TOOLS_REFERENCE.md    # Tool reference documentation
├── python_implementation.py  # Python implementation (optional)
└── references/           # Additional reference materials
```

---

## Quick Reference by Task

### I need to research a drug
→ Use `tooluniverse-drug-research`

### I need to find drug targets
→ Use `tooluniverse-target-research`

### I need to design a clinical trial
→ Use `tooluniverse-clinical-trial-design`

### I need to analyze CRISPR screen data
→ Use `tooluniverse-crispr-screen-analysis`

### I need to design an antibody
→ Use `tooluniverse-antibody-engineering`

### I need to research a disease
→ Use `tooluniverse-disease-research`

### I need to find literature
→ Use `tooluniverse-literature-deep-research`

### I need to check drug interactions
→ Use `tooluniverse-drug-drug-interaction`

### I need to retrieve protein structures
→ Use `tooluniverse-protein-structure-retrieval`

### I need to create a new tool
→ Use `devtu-create-tool`

---

*Last Updated: 2026-02-16*
