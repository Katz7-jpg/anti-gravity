# Technical Context

## Technology Stack

### Core Technologies

| Technology | Purpose | Version/Notes |
|------------|---------|---------------|
| Python | Primary scripting language | 3.10+ recommended |
| MCP | Model Context Protocol for tool integration | Via ToolUniverse |
| OpenCode | AI agent configuration framework | v1.0+ |
| Markdown | Documentation and skill definitions | CommonMark spec |

### AI Model Configuration

**Primary Model**: `zai/glm-5`
- Configured in `opencode.json`
- Supports thinking mode for complex reasoning
- Temperature: 0.1 for consistent outputs

### Supported AI Platforms

| Platform | Config Directory | Status |
|----------|------------------|--------|
| KiloCode | `.kilocode/` | Active |
| Cursor | `.cursor/` | Available |
| Claude | `.claude/` | Available |
| Cline | `.cline/` | Available |
| Continue | `.continue/` | Available |
| Goose | `.goose/` | Available |
| Junie | `.junie/` | Available |
| Kiro | `.kiro/` | Available |
| OpenHands | `.openhands/` | Available |
| Windsurf | `.windsurf/` | Available |

## Dependencies

### External APIs & Services

#### Chemical & Drug Databases
- **PubChem** - Chemical compounds and bioassays
- **ChEMBL** - Bioactive molecules with drug-like properties
- **DrugBank** - Drug target information
- **ChemSpider** - Chemical structure database

#### Clinical & Medical
- **ClinicalTrials.gov** - Clinical trial registry
- **FDA API** - Drug approvals and safety data
- **EMA** - European medicines data

#### Genomics & Proteomics
- **Ensembl** - Genome browser and annotation
- **UCSC Genome Browser** - Genomic data
- **UniProt** - Protein sequences and functions
- **PDB** - Protein 3D structures
- **AlphaFold DB** - Predicted protein structures
- **cBioPortal** - Cancer genomics

#### Literature & Knowledge
- **PubMed/NCBI** - Biomedical literature
- **Europe PMC** - Life sciences literature
- **CrossRef** - DOI and citation data

### Python Libraries

Commonly used in skill implementations:
- `requests` - HTTP client for API calls
- `pandas` - Data manipulation
- `biopython` - Bioinformatics utilities
- `rdkit` - Cheminformatics
- `pydantic` - Data validation

## Development Setup

### Environment Configuration

1. **API Keys** - Configure in `.env`:
   ```
   PUBCHEM_API_KEY=your_key
   CHEMBL_API_KEY=your_key
   CLINICALTRIALS_API_KEY=your_key
   # ... additional keys as needed
   ```

2. **Skill Installation** - Skills are symlinked from user configuration

3. **MCP Server Setup** - ToolUniverse MCP server configuration in respective platform config

### Build & Test Commands

```bash
# Test API connectivity
python test_api.py

# Verify skill installation
npx skills list

# Test specific skill
npx skills test tooluniverse-drug-research
```

## File Structure

```
AI_FACTORY/
├── .env                    # API keys and secrets
├── AGENTS.md               # Agent instructions (empty - to be populated)
├── opencode.json           # OpenCode configuration
├── test_api.py             # API connectivity tests
├── .agent/                 # Agent-specific files
│   └── skills/             # Shared skills directory
├── .kilocode/              # KiloCode configuration
│   ├── memory-bank/        # Memory bank files
│   └── skills/             # KiloCode-specific skills
└── Operation-Peanut/       # Main skill implementations
    ├── AGENTS.md           # Detailed agent instructions
    ├── opencode.json       # Project-specific config
    └── skills/             # ToolUniverse skills
```

## Configuration Files

### opencode.json Schema
```json
{
  "model": "model_identifier",
  "small_model": "smaller_model_for_simple_tasks",
  "provider": {
    "openai": {
      "apiKey": "api_key_or_placeholder",
      "baseUrl": "api_endpoint",
      "options": {
        "enable_thinking": true,
        "temperature": 0.1
      }
    }
  },
  "permission": "allow"
}
```

### AGENTS.md Structure
1. Build, Lint, and Test Commands
2. Code Style & Conventions
3. Project Architecture
4. Agent Operational Rules
5. ToolUniverse Skills Integration
6. Platform-Specific Rules

---

*Last Updated: 2026-02-16*
