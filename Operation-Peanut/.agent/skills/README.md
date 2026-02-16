# ToolUniverse Skills for Data Retrieval

This directory contains specialized skills for retrieving scientific data using ToolUniverse tools.

## Available Skills

### 0. ToolUniverse General Strategies (Start Here!)
**Path**: `tooluniverse/`  
**Focus**: Master strategies for using ToolUniverse's 1000++ tools effectively  
**Triggers**: research, scientific data, how to use tooluniverse, best practices, tool discovery

**Use when**:
- Learning how to use ToolUniverse effectively
- Need general guidance on scientific research workflows
- Task doesn't fit a specialized skill
- Want to understand multi-hop tool chains
- Need to combine multiple research approaches

**Key Features**:
- **8 Core Strategies**: Tool discovery, multi-hop chains, multi-database queries, disambiguation, fallback handling, comprehensive reports, specialized skills, parallel execution
- Exhaustive tool discovery patterns
- Multi-hop tool chain examples (5-10 tools per question)
- Database fallback chains for resilience
- Evidence grading and citation requirements
- Quick reference checklists

---

### 1. Sequence Retrieval
**Path**: `tooluniverse-sequence-retrieval/`  
**Focus**: DNA, RNA, and protein sequences  
**Databases**: NCBI (GenBank, RefSeq), ENA  
**Triggers**: genome, sequence, gene, nucleotide, protein, accession

**Use when**:
- Finding organism genomes
- Getting gene sequences
- Retrieving protein sequences
- Working with GenBank/RefSeq accessions

---

### 2. Expression Data Retrieval
**Path**: `tooluniverse-expression-data-retrieval/`  
**Focus**: Gene expression and multi-omics datasets  
**Databases**: ArrayExpress, BioStudies  
**Triggers**: expression, microarray, RNA-seq, omics, E-MTAB, E-GEOD

**Use when**:
- Finding gene expression experiments
- Getting RNA-seq datasets
- Retrieving microarray data
- Accessing multi-omics studies

---

### 3. Chemical Compound Retrieval
**Path**: `tooluniverse-chemical-compound-retrieval/`  
**Focus**: Chemical compounds and drug information  
**Databases**: PubChem, ChEMBL  
**Triggers**: compound, chemical, drug, CID, SMILES, ChEMBL

**Use when**:
- Finding chemical structures
- Getting compound properties
- Retrieving bioactivity data
- Drug discovery research

---

### 4. Protein Structure Retrieval
**Path**: `tooluniverse-protein-structure-retrieval/`  
**Focus**: 3D protein structures  
**Databases**: RCSB PDB, PDBe, AlphaFold  
**Triggers**: structure, PDB, crystallography, protein 3D, AlphaFold

**Use when**:
- Finding protein structures
- Getting structural metadata
- Downloading PDB files
- Structural biology research

---

### 5. Literature Deep Research (Enhanced v5.0)
**Path**: `tooluniverse-literature-deep-research/`  
**Focus**: Comprehensive literature research with target disambiguation and evidence grading  
**Databases**: PubMed, OpenAlex, Europe PMC, Semantic Scholar, Crossref, arXiv, bioRxiv + annotation DBs (UniProt, GTEx, HPA, InterPro, Open Targets)  
**Triggers**: literature, papers, research, publications, systematic review, what does literature say, target profile

**Use when**:
- Conducting comprehensive literature reviews
- Profiling biological targets with sparse literature
- Systematic literature searches with evidence grading
- Citation network analysis
- Identifying research gaps and trends
- Grant proposal background research
- Generating testable hypotheses from literature

**Key Features**:
- Target disambiguation phase (resolve IDs, detect naming collisions)
- Evidence grading (T1-T4 tiers for all claims)
- Mandatory completeness checklist (15 sections)
- Report-only output (methodology in separate appendix)
- Collision-aware query strategy
- Citation-network-first for sparse targets
- Biological model synthesis with testable hypotheses
- Scalable bibliography (JSON/CSV separate from narrative)

---

### 6. ToolUniverse Target Research
**Path**: `tooluniverse-target-research/`  
**Focus**: Comprehensive drug target profiling and validation  
**Databases**: UniProt, PDB, AlphaFold, STRING, GTEx, HPA, Open Targets, ChEMBL, DGIdb, gnomAD, ClinVar, PubMed  
**Triggers**: drug target, protein target, gene target, druggability, target validation, target profile

**Use when**:
- Assessing drug target druggability
- Getting comprehensive target profiles
- Validating potential drug targets
- Understanding target biology across multiple dimensions
- Finding drugs targeting a specific protein/gene
- Evaluating target safety profiles

**Key Features**:
- 8 parallel research paths (identity, structure, function, interactions, expression, variants, drugs, literature)
- ID resolution (gene symbol ↔ UniProt ↔ Ensembl)
- 225+ relevant tools organized by category
- Multi-step workflows for deep analysis
- Druggability and tractability assessment
- Safety profile evaluation

---

### 7. Disease Intelligence Gatherer
**Path**: `tooluniverse-disease-research/`  
**Focus**: Comprehensive disease analysis and treatment landscape  
**Databases**: Open Targets, ClinicalTrials.gov, PubMed, GWAS Catalog, ClinVar  
**Triggers**: disease, condition, treatment options, disease mechanisms, epidemiology

**Use when**:
- Understanding disease mechanisms
- Finding disease-associated targets
- Mapping treatment landscape
- Analyzing epidemiology and risk factors
- Identifying clinical trials

---

### 8. Documentation Quality Assurance
**Path**: `devtu-docs-quality/`  
**Focus**: Comprehensive documentation quality combining automated validation with ToolUniverse-specific auditing  
**Triggers**: audit docs, optimize docs, review documentation, fix docs, check documentation quality

**Use when**:
- Pre-release documentation review
- After major refactoring (commands, APIs, tool counts changed)
- Users report confusing or outdated documentation
- Want to establish automated validation pipeline
- Need to check for circular navigation or structural problems

**Key Features**:
- Automated validation scripts (commands, links, terminology)
- ToolUniverse-specific checks (circular navigation, MCP config duplication, tool counts)
- Auto-generated file header verification
- CLI and environment variable documentation checks
- Priority-based issue categorization (Critical → High → Medium → Low)
- CI/CD integration templates

---

### 9. DevTU Optimize Skills
**Path**: `devtu-optimize-skills/`  
**Focus**: Best practices for creating and improving ToolUniverse research skills  
**Triggers**: optimize skill, improve skill, review skill, skill best practices

**Use when**:
- Creating new ToolUniverse research skills
- Reviewing/improving existing skills
- User complains about missing details, noisy results, or unclear reports
- Need to apply evidence grading, disambiguation, or completeness patterns

**Key Features**:
- Disambiguation-first pattern
- Evidence grading system (T1-T4)
- Report-only output structure
- Mandatory completeness checklist
- Query strategy optimization (collision handling, citation expansion)
- Tool failure handling patterns
- Common anti-patterns and fixes

---

## Skill Organization

Each skill follows this structure:

```
skill-name/
├── SKILL.md          # Main instructions (concise, <500 lines)
├── examples.md       # Usage examples (optional)
└── reference.md      # Detailed reference (optional)
```

## Quick Start

Skills are automatically available to the AI agent. Just ask naturally:

```
"Find the E. coli K-12 genome"           → Uses tooluniverse-sequence-retrieval
"Get gene expression data for diabetes"  → Uses tooluniverse-expression-data-retrieval  
"Find properties of aspirin"             → Uses tooluniverse-chemical-compound-retrieval
"Get the structure of insulin"           → Uses tooluniverse-protein-structure-retrieval
"Tell me about EGFR as a drug target"    → Uses tooluniverse-target-research
"What do we know about Alzheimer's?"     → Uses tooluniverse-disease-research
```

## Workflow Pattern

All skills follow the same workflow:

1. **Search** - Find data by name/keyword
2. **Get Identifier** - Retrieve accession/ID
3. **Retrieve Details** - Fetch complete data

## Common to All Skills

### ToolUniverse Initialization
```python
from tooluniverse import ToolUniverse
tu = ToolUniverse()
tu.load_tools()
```

### Error Handling
All tools return standardized responses:
```python
{
    "status": "success" | "error",
    "data": { ... },
    "error": "message if error"
}
```

### Best Practices
- Start with broad searches, then narrow
- Always provide identifiers in outputs
- Check data quality metrics
- Cross-reference multiple databases
- Cite accessions/IDs in reports

## Coverage Summary

| Domain | Tools | Databases | Identifiers |
|--------|-------|-----------|-------------|
| **Sequences** | 9 | NCBI, ENA | NC_*, U*, M* |
| **Expression** | 8 | ArrayExpress, BioStudies | E-MTAB-*, S-BSST* |
| **Compounds** | 18 | PubChem, ChEMBL | CID, CHEMBL* |
| **Structures** | 15+ | PDB, PDBe, AlphaFold | 4-char PDB IDs |
| **Literature** | 10+ | PubMed, OpenAlex, Europe PMC, arXiv, bioRxiv, etc. | PMID, DOI |
| **Targets** | 225+ | UniProt, Open Targets, ChEMBL, STRING, etc. | UniProt, Ensembl, Gene Symbol |
| **Diseases** | 20+ | Open Targets, ClinicalTrials, GWAS | EFO IDs |

## When to Use Which Skill

### Start with tooluniverse (general strategies) if:
- New to ToolUniverse and need guidance
- Task spans multiple domains
- Need to understand best practices
- Want to maximize research coverage
- Not sure which specialized skill to use

### Start with tooluniverse-sequence-retrieval if:
- Need genomic sequences
- Working with genes or organisms
- Want nucleotide or protein sequences

### Start with tooluniverse-expression-data-retrieval if:
- Need gene expression data
- Working with RNA-seq or microarray
- Want omics datasets

### Start with tooluniverse-chemical-compound-retrieval if:
- Need chemical structures
- Working with drugs or compounds
- Want bioactivity data

### Start with tooluniverse-protein-structure-retrieval if:
- Need 3D structures
- Working with structural biology
- Want crystallography data

### Start with tooluniverse-literature-deep-research if:
- Need comprehensive literature coverage
- Conducting systematic reviews
- Finding all papers on a topic
- Analyzing research trends
- Identifying research gaps

### Start with tooluniverse-target-research if:
- Assessing a drug target
- Need comprehensive target profile
- Evaluating druggability
- Understanding target biology
- Finding drugs for a target
- Target validation research

### Start with tooluniverse-disease-research if:
- Understanding a disease
- Finding disease-associated targets
- Mapping treatment landscape
- Analyzing disease mechanisms

### Start with devtu-docs-quality if:
- Reviewing documentation before release
- After refactoring (commands, APIs changed)
- Need to validate documentation accuracy
- Want automated validation pipeline
- Users report confusing or circular documentation

### Start with devtu-optimize-skills if:
- Creating a new ToolUniverse skill
- Improving an existing skill
- Reports are too short or noisy
- Need to add evidence grading or disambiguation
- Users complain about skill output quality

## Combining Skills

Skills can be used together for comprehensive research:

**Example**: Drug-Target Analysis
1. `tooluniverse-chemical-compound-retrieval` → Find compound, get CID
2. `tooluniverse-chemical-compound-retrieval` → Get target proteins
3. `tooluniverse-protein-structure-retrieval` → Get target structures
4. `tooluniverse-sequence-retrieval` → Get target gene sequences

**Example**: Comparative Genomics
1. `tooluniverse-sequence-retrieval` → Get genome sequences
2. `tooluniverse-expression-data-retrieval` → Get expression data
3. Cross-reference by accessions

## Skill Development

These skills were created following the ToolUniverse SDK patterns and the Cursor skill creation guidelines. Each skill:

- ✅ Focuses on a specific domain
- ✅ Provides clear workflows
- ✅ Includes concrete examples
- ✅ Under 500 lines for main SKILL.md
- ✅ Uses consistent terminology
- ✅ Follows best practices

## Contributing

To add more skills:
1. Identify a distinct data domain in ToolUniverse
2. Create `skill-name/SKILL.md` with proper frontmatter
3. Follow the established pattern (Search → ID → Retrieve)
4. Keep SKILL.md concise (<500 lines)
5. Add examples for common use cases
6. Update this README

## Related Documentation

- [ToolUniverse Main Documentation](../../docs/)
- [Tool Creation Guide](../devtu-create-tool/)
- [API Reference](../../src/tooluniverse/)
