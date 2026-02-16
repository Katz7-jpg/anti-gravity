# ToolUniverse Skill Optimization Checklist

Quick reference for reviewing and optimizing ToolUniverse skills.

---

## Pre-Search Phase

### Disambiguation (Required for Biological Targets)
- [ ] Resolve official IDs (UniProt, Ensembl, NCBI, ChEMBL)
- [ ] Document all synonyms/aliases
- [ ] Check for naming collisions (`"[SYMBOL]"[Title]` test)
- [ ] Build negative filters if collisions detected
- [ ] Get baseline from annotation DBs (not literature):
  - [ ] Protein domains (InterPro)
  - [ ] Subcellular location (HPA/UniProt)
  - [ ] Expression (GTEx/HPA)
  - [ ] GO terms + pathways

---

## Query Strategy

### High-Precision First
- [ ] Use `"[GENE]"[Title]` for core seed set
- [ ] Include protein name variants
- [ ] Target 15-30 high-confidence papers

### Citation Expansion
- [ ] Forward citations (PubMed_get_cited_by → EuropePMC fallback)
- [ ] Related papers (PubMed_get_related)
- [ ] Backward citations (EuropePMC_get_references)
- [ ] Especially important for sparse targets (<30 seed papers)

### Collision Filtering
- [ ] Apply NOT filters for known collisions
- [ ] Example: `NOT plasmid NOT conjugation` for immune TRAG

---

## Evidence Grading

### Apply to ALL Claims
| Tier | Symbol | When to Use |
|------|--------|-------------|
| T1 | ★★★ | Mechanistic study, direct experimental evidence |
| T2 | ★★☆ | Functional study (knockdown/OE phenotype) |
| T3 | ★☆☆ | Association (screen, GWAS, correlation) |
| T4 | ☆☆☆ | Mention (review, text-mined, peripheral) |

### Per-Section Summary
- [ ] Count papers by tier
- [ ] State "Evidence Quality: Strong/Moderate/Limited"

---

## Report Structure

### Output Files
| File | Content | Generated |
|------|---------|-----------|
| `[topic]_report.md` | Narrative findings | Always |
| `[topic]_bibliography.json` | Full paper data | Always |
| `methods_appendix.md` | Search methodology | Only if requested |

### Report Content Rules
- [ ] Focus on FINDINGS, not PROCESS
- [ ] No "searched X databases, found Y papers"
- [ ] Every claim has source + evidence grade
- [ ] Top 20-50 papers highlighted; rest in JSON

---

## Mandatory Sections

**All must exist, even if "Limited evidence" or "N/A"**

### Identity
- [ ] Official identifiers
- [ ] Synonyms/aliases
- [ ] Naming collisions (or "none detected")

### Biology
- [ ] Protein architecture (or "N/A")
- [ ] Subcellular localization
- [ ] Expression profile
- [ ] GO terms + pathways

### Mechanism
- [ ] Core function (evidence-graded)
- [ ] Model organism data (or "none found")
- [ ] Key assays/readouts

### Disease
- [ ] Genetic variants
- [ ] Disease links (evidence-graded)
- [ ] Pathogens (or "none identified")

### Synthesis (CRITICAL)
- [ ] Research themes (≥3 papers each)
- [ ] Open questions/gaps
- [ ] Biological model (3-5 paragraphs)
- [ ] Testable hypotheses (≥3 with experiments)
- [ ] Conclusions + confidence assessment

---

## Tool Failure Handling

### Retry Protocol
```
Attempt 1 → fail → 2s wait → Attempt 2 → fail → 5s wait → Fallback
```

### Fallback Chains
| Primary | Fallback |
|---------|----------|
| PubMed_get_cited_by | EuropePMC_get_citations |
| PubMed_get_related | SemanticScholar_search_papers |
| GTEx_* | HPA_* |
| Unpaywall | EuropePMC/OpenAlex OA flags |

### Document Failures
- [ ] Note what failed in report
- [ ] Suggest alternative data sources

---

## Theme Extraction

### Quality Requirements
| Papers | Action |
|--------|--------|
| ≥10 | Major theme (full section) |
| 3-9 | Minor theme (subsection) |
| <3 | Note "limited evidence" or merge |

### Required Per Theme
- [ ] Paper count
- [ ] Evidence quality summary
- [ ] ≥3 representative papers
- [ ] Narrative description

---

## Common Anti-Patterns

| Anti-Pattern | Fix |
|--------------|-----|
| Search log in report | Keep methodology internal |
| No collision handling | Add disambiguation phase |
| No evidence grading | Add T1-T4 labels |
| Missing sections | Use completeness checklist |
| No synthesis | Add biological model + hypotheses |
| Papers embedded in narrative | Separate JSON bibliography |
| Silent tool failures | Add retry + fallback + documentation |

---

## Quick Quality Check

Before finalizing any ToolUniverse skill:

1. **Does it disambiguate first?** (for biological targets)
2. **Is the report content-focused?** (not process-focused)
3. **Are claims evidence-graded?** (T1-T4)
4. **Are all sections present?** (even if "limited")
5. **Is there a synthesis section?** (model + hypotheses)
6. **Is bibliography separate?** (JSON/CSV)
7. **Are tool failures handled?** (retry + fallback)

If any answer is NO → optimize the skill.
