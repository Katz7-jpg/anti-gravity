# Quick Start: Auto-Discover APIs

Get started with automated API discovery and tool creation in 5 minutes.

## Table of Contents

1. [Using the Skill (MCP/Claude)](#using-the-skill-mcpclaude)
2. [Using Python SDK](#using-python-sdk)
3. [Common Workflows](#common-workflows)
4. [Examples](#examples)

---

## Using the Skill (MCP/Claude)

### Option 1: Full Automated Pipeline

```
I want to discover new life science APIs and create ToolUniverse tools for them.
Focus on metabolomics and single-cell genomics domains.
```

The skill will:
1. ✅ Analyze current ToolUniverse coverage
2. ✅ Identify gaps in metabolomics and single-cell domains
3. ✅ Search for APIs in these domains
4. ✅ Score and prioritize API candidates
5. ✅ Generate tools for high-priority APIs
6. ✅ Validate all tools
7. ✅ Prepare integration PR

**Output**: Complete PR ready for review with:
- New tool `.py` files
- JSON configurations
- Validation reports
- Discovery documentation

### Option 2: Discovery Only

```
Analyze ToolUniverse tool coverage and identify gaps.
Generate a discovery report with API recommendations.
```

**Output**: `discovery_report.md` with prioritized API candidates

### Option 3: Create from Specific API

```
Create ToolUniverse tools for the MetaboLights API.
API documentation: https://www.ebi.ac.uk/metabolights/ws/api/spec/
```

**Output**: Tool files ready for validation

### Option 4: Validate Existing Tools

```
Validate the MetaboLights tools against devtu requirements.
Check schema structure, test examples, and tool loading.
```

**Output**: `validation_report.md` with issues and fixes

---

## Using Python SDK

### Installation

```bash
cd skills/devtu-auto-discover-apis
chmod +x python_implementation.py
```

### Full Pipeline

```bash
# Discover APIs → Create Tools → Validate → Prepare PR
python python_implementation.py --mode full --focus-domains metabolomics single-cell
```

**Output**:
```
./api_discovery_output/
├── discovery_report_20260212_143022.md
├── metabolights_tool.py
├── metabolights_tools.json
├── validation_report_MetaboLights_20260212_143045.md
├── commit_message_MetaboLights.txt
└── pr_description_MetaboLights.md
```

### Discovery Only

```bash
# Just analyze coverage and find API candidates
python python_implementation.py --mode discovery
```

### Create Tools for Specific API

```bash
# After discovery, create tools for chosen APIs
python python_implementation.py --mode create --apis MetaboLights GNPS
```

### Validate Tools

```bash
# Validate generated tools
python python_implementation.py --mode validate --tools MetaboLights_*
```

### Prepare Integration

```bash
# Generate commit message and PR description
python python_implementation.py --mode integrate --branch feature/add-metabolomics
```

---

## Common Workflows

### Workflow 1: Quarterly Gap Analysis

**Goal**: Identify new APIs to add every quarter

```bash
# 1. Run discovery
python python_implementation.py --mode discovery

# 2. Review discovery_report.md
cat ./api_discovery_output/discovery_report_*.md

# 3. Select high-priority APIs and create tools
python python_implementation.py --mode full --focus-domains <chosen_domains>
```

**Frequency**: Every 3 months

### Workflow 2: Target Specific Domain

**Goal**: Comprehensive coverage in one domain

**Via MCP/Claude**:
```
I want to expand ToolUniverse coverage in metabolomics.
Discover all available metabolomics APIs, create tools for the top 3,
validate them, and prepare an integration PR.
```

**Via Python SDK**:
```bash
python python_implementation.py --mode full --focus-domains metabolomics
```

### Workflow 3: Validate Existing Tools

**Goal**: Ensure existing tools meet devtu standards

**Via MCP/Claude**:
```
Validate all PubChem tools against devtu requirements.
Generate a validation report with any issues found.
```

**Via Python SDK**:
```bash
python python_implementation.py --mode validate --tools PubChem_*
```

### Workflow 4: Emergency Gap Fill

**Goal**: Quickly add tools for urgent research need

**Via MCP/Claude**:
```
We urgently need tools for spatial transcriptomics analysis.
Find the best API, create tools, validate, and prepare PR immediately.
```

**Result**: Complete PR in ~30 minutes

---

## Examples

### Example 1: Discovery Report

**Input**:
```
Analyze ToolUniverse coverage and identify the top 3 gap domains.
```

**Output** (`discovery_report.md`):
```markdown
# API Discovery Report

## Executive Summary
- Total APIs discovered: 8
- High priority: 3
- Gap domains addressed: 4

## Coverage Analysis
Total tools in ToolUniverse: 487

| Domain | Tool Count | Status |
|--------|------------|--------|
| metabolomics | 2 | 🔴 Critical |
| single_cell | 0 | 🔴 Critical |
| imaging | 5 | ⚠️ Gap |
| systems_biology | 8 | ⚠️ Gap |

## Prioritized API Candidates

### High Priority

#### MetaboLights
- **Domain**: metabolomics
- **Score**: 85/100
- **Base URL**: https://www.ebi.ac.uk/metabolights/ws
- **Auth**: public
- **Endpoints**: 5
- **Rationale**: EBI-maintained, well-documented, fills critical gap
```

### Example 2: Tool Creation

**Input**:
```
Create ToolUniverse tools for MetaboLights API.
Base URL: https://www.ebi.ac.uk/metabolights/ws
Documentation: https://www.ebi.ac.uk/metabolights/ws/api/spec/
```

**Output Files**:

**`metabolights_tool.py`** (excerpt):
```python
@register_tool("MetaboLightsTool")
class MetaboLightsTool(BaseTool):
    """MetaboLights database API integration."""

    BASE_URL = "https://www.ebi.ac.uk/metabolights/ws"

    def _list_studies(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List all metabolomics studies."""
        try:
            response = requests.get(
                f"{self.BASE_URL}/studies",
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            return {
                "status": "success",
                "data": data.get("content", []),
                "metadata": {"total": len(data.get("content", []))}
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
```

**`metabolights_tools.json`** (excerpt):
```json
[
  {
    "name": "MetaboLights_list_studies",
    "class": "MetaboLightsTool",
    "description": "List all metabolomics studies in MetaboLights. Returns study IDs and metadata.",
    "parameter": {
      "type": "object",
      "required": ["operation"],
      "properties": {
        "operation": {
          "const": "list_studies",
          "description": "Operation identifier"
        }
      }
    },
    "return_schema": {
      "oneOf": [
        {
          "type": "object",
          "properties": {
            "data": {"type": "array"},
            "metadata": {"type": "object"}
          }
        },
        {
          "type": "object",
          "properties": {"error": {"type": "string"}},
          "required": ["error"]
        }
      ]
    },
    "test_examples": [
      {"operation": "list_studies"}
    ]
  }
]
```

### Example 3: Validation Report

**Input**:
```
Validate MetaboLights tools against devtu requirements.
```

**Output** (`validation_report.md`):
```markdown
# Validation Report: MetaboLights

## Summary
- Total checks: 4
- Passed: 4
- Failed: 0

## Schema Validation
✅ **PASSED** (3 tools)

## Test Examples Validation
✅ **PASSED** (3 tools)

## Tool Loading
⚠️ Requires manual verification

## devtu Compliance Checklist
1. [ ] Tool Loading: Verify 3-step registration
2. [ ] API Verification: Check against official docs
3. [ ] Error Pattern Detection: Review error handling
4. [x] Schema Validation: oneOf + data wrapper
5. [x] Test Examples: Real IDs, no placeholders
6. [ ] Parameter Verification: Match API requirements

## Conclusion
Ready for integration tests with live API.
```

### Example 4: Integration PR

**Input**:
```
Prepare integration PR for MetaboLights tools.
```

**Output** (`pr_description.md`):
```markdown
# Add MetaboLights Tools

## Summary
Adds 3 new tools integrating the MetaboLights API for metabolomics research.

## Tools Added

| Tool Name | Description |
|-----------|-------------|
| MetaboLights_list_studies | List all metabolomics studies |
| MetaboLights_get_study | Get detailed study information |
| MetaboLights_get_metabolites | Get metabolites from a study |

## Validation Results
✅ Schema: All checks passed
✅ Test Examples: All checks passed
⚠️ Tool Loading: Manual verification needed
⚠️ Integration Tests: Manual testing needed

## Files Changed
- `src/tooluniverse/metabolights_tool.py` - Tool implementation
- `src/tooluniverse/data/metabolights_tools.json` - Tool configurations
- `src/tooluniverse/default_config.py` - Registration

## Checklist
- [x] Schema validation complete
- [x] Real test examples
- [x] No placeholder values
- [x] Tool names ≤55 chars
- [ ] default_config.py updated
- [ ] Integration tests passing
```

---

## Configuration Options

### Optional Configuration File

Create `config.yaml` for custom settings:

```yaml
discovery:
  focus_domains:
    - "metabolomics"
    - "single_cell"
  max_apis_per_batch: 5

search:
  max_results_per_query: 20
  date_filter: "2024-2026"

creation:
  architecture: "multi-operation"
  timeout_seconds: 30

validation:
  require_100_percent_pass: true

integration:
  auto_create_pr: false
  branch_prefix: "feature/add-"
```

**Use in Python**:
```python
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f)

agent = APIDiscoveryAgent(config=config)
```

---

## Troubleshooting

### Issue: "No gaps found"

**Solution**: Lower threshold or specify focus domains
```bash
python python_implementation.py --mode discovery --focus-domains metabolomics
```

### Issue: "API documentation not accessible"

**Solution**: Check URL, try alternative search queries
```
The API documentation URL returned 404.
Search for alternative documentation or API reference for [API name].
```

### Issue: "Schema validation failed"

**Solution**: Review return_schema structure
```
The tool return_schema is missing the oneOf structure.
Fix the schema in [tool].json to include:
{
  "oneOf": [
    {"type": "object", "properties": {"data": {...}}},
    {"type": "object", "properties": {"error": {"type": "string"}}}
  ]
}
```

### Issue: "Test examples have placeholders"

**Solution**: Find real IDs from API
```
The test_examples contain placeholder values like "TEST_123".
Call the list endpoint to discover real IDs:
curl https://api.example.com/list
```

---

## Next Steps

After generating tools:

1. **Review Generated Files**: Check tool implementation and JSON configs
2. **Copy to Repository**: Move files to `src/tooluniverse/`
3. **Update Configuration**: Add entry to `default_config.py`
4. **Run Integration Tests**: `python scripts/test_new_tools.py <tool_name> -v`
5. **Create Git Branch**: `git checkout -b feature/add-<api>-tools`
6. **Commit and Push**: Follow generated commit message
7. **Create PR**: Use generated PR description

---

## Support

- **Skill Documentation**: See `SKILL.md` for comprehensive guide
- **ToolUniverse Docs**: See `devtu-create-tool` skill for tool creation details
- **Validation Guide**: See `devtu-fix-tool` skill for debugging
- **GitHub Issues**: Report bugs or request features

---

## Summary

The `devtu-auto-discover-apis` skill provides three interfaces:

1. **MCP/Claude**: Natural language commands for conversational workflow
2. **Python SDK**: Programmatic access for automation and scripting
3. **Manual**: Step-by-step guidance for hands-on control

**Choose based on your needs**:
- 🗣️ **MCP**: Quick, interactive, good for exploring
- 🐍 **Python**: Automated, reproducible, good for batches
- 📖 **Manual**: Educational, controlled, good for learning

All interfaces produce the same high-quality, validated tools following ToolUniverse best practices.
