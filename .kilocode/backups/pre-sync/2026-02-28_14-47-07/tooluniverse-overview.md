# ToolUniverse Skills Overview

## What is ToolUniverse?

ToolUniverse is a comprehensive collection of 10,000+ scientific and development tools accessible through the Model Context Protocol (MCP). It provides AI agents with capabilities for drug discovery, clinical research, bioinformatics, and more.

## Architecture

```mermaid
graph LR
    subgraph ToolUniverse MCP Server
        TF[Tool Finder]
        DR[Drug Research Tools]
        CR[Clinical Tools]
        BR[Bioinformatics Tools]
        PR[Protein Tools]
        LR[Literature Tools]
    end
    
    subgraph AI Agent
        KC[KiloCode]
        CU[Cursor]
        CL[Claude]
    end
    
    AI Agent --> |MCP Protocol| ToolUniverse MCP Server
    TF --> DR
    TF --> CR
    TF --> BR
    TF --> PR
    TF --> LR
```

## Core Philosophy

### 1. Search Widely
Before starting any research task, use tool finders like `Tool_Finder_Keyword` to discover relevant tools. This ensures you leverage the full capabilities available.

### 2. Multi-Hop Research
Scientific queries typically require chains of 3-5 tool calls:
1. **Discovery** - Find relevant tools and data sources
2. **Retrieval** - Gather initial data from multiple sources
3. **Analysis** - Process and analyze retrieved data
4. **Validation** - Cross-reference findings
5. **Synthesis** - Compile comprehensive results

### 3. Clarify First
When requests are ambiguous, ask clarifying questions before initiating tool use:
- "Research cancer" → What type? What aspect? Treatment or mechanisms?
- "Find drug interactions" → For which drugs? What type of interactions?

## Skill Categories

### Research & Discovery
| Skill | Purpose | Key Tools |
|-------|---------|-----------|
| `tooluniverse-drug-research` | Comprehensive drug information | PubChem, ChEMBL, DrugBank |
| `tooluniverse-target-research` | Drug target identification | ChEMBL, OpenTargets |
| `tooluniverse-disease-research` | Disease mechanism research | DisGeNET, OMIM |
| `tooluniverse-literature-deep-research` | Literature synthesis | PubMed, Europe PMC |

### Clinical Development
| Skill | Purpose | Key Tools |
|-------|---------|-----------|
| `tooluniverse-clinical-trial-design` | Trial protocol design | ClinicalTrials.gov, FDA |
| `tooluniverse-pharmacovigilance` | Safety monitoring | FAERS, EudraVigilance |
| `tooluniverse-drug-drug-interaction` | DDI analysis | DrugBank, DDI databases |

### Bioinformatics
| Skill | Purpose | Key Tools |
|-------|---------|-----------|
| `tooluniverse-crispr-screen-analysis` | Genetic screen analysis | MAGeCK, CRISPR tools |
| `tooluniverse-structural-variant-analysis` | Genomic rearrangements | Manta, DELLY |
| `tooluniverse-rare-disease-diagnosis` | Rare disease diagnosis | ClinVar, OMIM |
| `tooluniverse-precision-oncology` | Cancer genomics | cBioPortal, COSMIC |

### Protein Engineering
| Skill | Purpose | Key Tools |
|-------|---------|-----------|
| `tooluniverse-antibody-engineering` | Antibody design | OAS, AbDb |
| `tooluniverse-binder-discovery` | Protein binder design | PDB, AlphaFold |
| `tooluniverse-protein-therapeutic-design` | Therapeutic proteins | UniProt, PDB |
| `tooluniverse-protein-structure-retrieval` | Structure data | PDB, AlphaFold DB |

### Data Retrieval
| Skill | Purpose | Key Tools |
|-------|---------|-----------|
| `tooluniverse-sequence-retrieval` | Sequence data | UniProt, NCBI |
| `tooluniverse-expression-data-retrieval` | Expression data | GEO, Expression Atlas |
| `tooluniverse-chemical-compound-retrieval` | Compound data | PubChem, ChEMBL |

### Development Tools
| Skill | Purpose |
|-------|---------|
| `devtu-create-tool` | Create new tools |
| `devtu-fix-tool` | Debug and fix tools |
| `devtu-optimize-skills` | Optimize skill descriptions |
| `devtu-auto-discover-apis` | Discover new APIs |

## Configuration

### API Keys Required
Most tools require API keys configured in `.env`:
```
NCBI_API_KEY=your_key
CHEMBL_API_KEY=your_key
CLINICALTRIALS_API_KEY=your_key
ALPHAFOLD_API_KEY=your_key
```

### MCP Server Setup
ToolUniverse runs as an MCP server. Configure in your AI platform's MCP settings:
```json
{
  "mcpServers": {
    "tooluniverse": {
      "command": "npx",
      "args": ["-y", "tooluniverse"],
      "env": {
        "NCBI_API_KEY": "${NCBI_API_KEY}"
      }
    }
  }
}
```

## Best Practices

1. **Start with Tool Finder** - Always discover available tools first
2. **Read SKILL.md** - Each skill has detailed documentation
3. **Check EXAMPLES.md** - Review example workflows before starting
4. **Use CHECKLIST.md** - Validate your approach against checklists
5. **Handle Rate Limits** - Implement appropriate delays between API calls

---

*Last Updated: 2026-02-16*
