---
name: create-tooluniverse-skill
description: Create high-quality ToolUniverse skills following test-driven, implementation-agnostic methodology. Integrates tools from ToolUniverse's 1,264+ tool library, creates missing tools when needed using devtu-create-tool, tests thoroughly, and produces skills with Python SDK + MCP support. Use when asked to create new ToolUniverse skills, build research workflows, or develop domain-specific analysis capabilities for biology, chemistry, or medicine.
---

# Create ToolUniverse Skill

Systematic workflow for creating production-ready ToolUniverse skills that integrate multiple scientific tools, follow implementation-agnostic standards, and achieve 100% test coverage.

## Core Principles (Critical)

**CRITICAL - Read devtu-optimize-skills**: This skill builds on principles from `devtu-optimize-skills`. Invoke that skill first or review its 10 pillars:

1. **TEST FIRST** - Never write documentation without testing tools
2. **Verify tool contracts** - Don't trust function names
3. **Handle SOAP tools** - Add `operation` parameter where needed
4. **Implementation-agnostic docs** - Separate SKILL.md from code
5. **Foundation first** - Use comprehensive aggregators
6. **Disambiguate carefully** - Resolve IDs properly
7. **Implement fallbacks** - Primary → Fallback → Default
8. **Grade evidence** - T1-T4 tiers on claims
9. **Require quantified completeness** - Numeric minimums
10. **Synthesize** - Models and hypotheses, not just lists

## When to Use This Skill

Use this skill when:
- Creating new ToolUniverse skills for specific domains
- Building research workflows using scientific tools
- Developing analysis capabilities (e.g., metabolomics, single-cell, cancer genomics)
- Integrating multiple databases into coherent pipelines
- Following up on "create [domain] skill" requests

## Overview: 7-Phase Workflow

```
Phase 1: Domain Analysis →
Phase 2: Tool Discovery & Testing →
Phase 3: Tool Creation (if needed) →
Phase 4: Implementation →
Phase 5: Documentation →
Phase 6: Testing & Validation →
Phase 7: Packaging
```

**Time per skill**: ~1.5-2 hours (tested and documented)

---

## Phase 1: Domain Analysis

**Objective**: Understand the scientific domain and identify required capabilities

**Duration**: 15 minutes

### 1.1 Understand Use Cases

Gather concrete examples of how the skill will be used:
- "What analyses should this skill perform?"
- "Can you give examples of typical queries?"
- "What outputs do users expect?"

**Example queries to clarify**:
- For metabolomics: "Identify metabolites in a sample" vs "Find pathways for metabolites" vs "Compare metabolite profiles"
- For cancer genomics: "Interpret mutations" vs "Find therapies" vs "Match clinical trials"

### 1.2 Identify Required Data Types

List what the skill needs to work with:
- **Input types**: Gene lists, protein IDs, compound names, disease names, etc.
- **Output types**: Reports, tables, visualizations, data files
- **Intermediate data**: ID mappings, enrichment results, annotations

### 1.3 Define Analysis Phases

Break the workflow into logical phases:

**Example - Metabolomics Skill**:
1. Phase 1: Metabolite identification (name → IDs)
2. Phase 2: Metabolite annotation (properties, pathways)
3. Phase 3: Pathway enrichment (statistical analysis)
4. Phase 4: Comparative analysis (samples/conditions)

**Example - Cancer Genomics Skill**:
1. Phase 1: Mutation validation (check databases)
2. Phase 2: Clinical significance (actionability)
3. Phase 3: Therapy matching (FDA approvals)
4. Phase 4: Trial matching (clinical trials)

### 1.4 Review Related Skills

Check existing ToolUniverse skills for relevant patterns:
- Read similar skills in `skills/` directory
- Note tool usage patterns
- Identify reusable approaches

**Useful related skills**:
- `tooluniverse-systems-biology` - Multi-database integration
- `tooluniverse-target-research` - Comprehensive profiling
- `tooluniverse-drug-research` - Pharmaceutical workflows

---

## Phase 2: Tool Discovery & Testing

**Objective**: Find and verify tools needed for each analysis phase

**Duration**: 30-45 minutes

**CRITICAL**: Following test-driven development from devtu-optimize-skills

### 2.1 Search Available Tools

**Tool locations**: `/src/tooluniverse/data/*.json` (186 tool files)

**Search strategies**:
1. **Keyword search**: `grep -r "keyword" src/tooluniverse/data/*.json`
2. **Tool listing**: List all tools from specific database
3. **Function search**: Search by domain (metabolomics, genomics, etc.)

**Example searches**:
```bash
# Find metabolomics tools
grep -l "metabol" src/tooluniverse/data/*.json

# Find cancer-related tools
grep -l "cancer\|tumor\|oncology" src/tooluniverse/data/*.json

# Find single-cell tools
grep -l "single.cell\|scRNA" src/tooluniverse/data/*.json
```

### 2.2 Read Tool Configurations

For each relevant tool file, read to understand:
- Tool names and descriptions
- **Parameters** (CRITICAL - don't assume from function names!)
- Return schemas
- Test examples

**Check for**:
- SOAP tools (require `operation` parameter)
- Parameter name patterns
- Response format variations

### 2.3 Create Test Script (REQUIRED)

**NEVER skip this step** - Testing before documentation is the #1 lesson

**Template**: See `scripts/test_tools_template.py`

**Test script structure**:
```python
#!/usr/bin/env python3
"""
Test script for [Domain] tools
Following TDD: test ALL tools BEFORE creating skill documentation
"""

from tooluniverse import ToolUniverse
import json

def test_database_1():
    """Test Database 1 tools"""
    tu = ToolUniverse()
    tu.load_tools()

    # Test tool 1
    result = tu.tools.TOOL_NAME(param="value")
    print(f"Status: {result.get('status')}")
    # Verify response format
    # Check data structure

def test_database_2():
    """Test Database 2 tools"""
    # Similar structure

def main():
    """Run all tests"""
    tests = [
        ("Database 1", test_database_1),
        ("Database 2", test_database_2),
    ]

    results = {}
    for name, test_func in tests:
        try:
            test_func()
            results[name] = "✅ PASS"
        except Exception as e:
            results[name] = f"❌ FAIL: {e}"

    # Print summary
    for name, result in results.items():
        print(f"{name}: {result}")

if __name__ == "__main__":
    main()
```

### 2.4 Run Tests and Document Findings

**Execute**:
```bash
python test_[domain]_tools.py
```

**Document discoveries**:
- Response format variations (standard, direct list, direct dict)
- Parameter mismatches (function name ≠ parameter name)
- SOAP tools requiring `operation`
- Tools that don't work / return errors

**Create parameter corrections table**:
| Tool | Common Mistake | Correct Parameter | Evidence |
|------|----------------|-------------------|----------|
| TOOL_NAME | assumed_param | actual_param | Test result |

---

## Phase 3: Tool Creation (If Needed)

**Objective**: Create missing tools using devtu-create-tool

**Duration**: 30-60 minutes per tool (if needed)

**When to create tools**:
- Required functionality not available in existing tools
- Critical analysis step has no tool support
- Alternative tools exist but are inferior

**When NOT to create tools**:
- Adequate tools already exist
- Analysis can use alternative approach
- Tool would duplicate existing functionality

### 3.1 Use devtu-create-tool Skill

If tools are missing, invoke the devtu-create-tool skill:

**Example invocation**:
```
"I need to create a tool for [database/API]. The API endpoint is [URL],
it takes parameters [list], and returns [format]. Can you help create this tool?"
```

### 3.2 Test New Tools

After creating tools, add them to test script:
```python
def test_new_tool():
    """Test newly created tool"""
    tu = ToolUniverse()
    tu.load_tools()

    result = tu.tools.NEW_TOOL_NAME(param="test_value")
    assert result.get('status') == 'success', "New tool failed"
    # Verify data structure matches expectations
```

### 3.3 Use devtu-fix-tool If Needed

If new tools fail tests, invoke devtu-fix-tool:
```
"The tool [TOOL_NAME] is returning errors: [error message].
Can you help fix it?"
```

---

## Phase 4: Implementation

**Objective**: Create working Python pipeline with tested tools

**Duration**: 30-45 minutes

**CRITICAL**: Build from tested tools, not assumptions

### 4.1 Create Skill Directory

```bash
mkdir -p skills/tooluniverse-[domain-name]
cd skills/tooluniverse-[domain-name]
```

### 4.2 Write python_implementation.py

**Template**: See `assets/skill_template/python_implementation.py`

**Structure**:
```python
#!/usr/bin/env python3
"""
[Domain Name] - Python SDK Implementation
Tested implementation following TDD principles
"""

from tooluniverse import ToolUniverse
from datetime import datetime

def domain_analysis_pipeline(
    input_param_1=None,
    input_param_2=None,
    output_file=None
):
    """
    [Domain] analysis pipeline.

    Args:
        input_param_1: Description
        input_param_2: Description
        output_file: Output markdown file path

    Returns:
        Path to generated report file
    """

    tu = ToolUniverse()
    tu.load_tools()

    # Generate output filename
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"domain_analysis_{timestamp}.md"

    # Initialize report
    report = []
    report.append("# [Domain] Analysis Report\n")
    report.append(f"**Generated**: {datetime.now()}\n\n")

    # Phase 1: [Description]
    report.append("## 1. [Phase Name]\n")
    try:
        result = tu.tools.TOOL_NAME(param=value)
        if result.get('status') == 'success':
            data = result.get('data', [])
            # Process and add to report
        else:
            report.append("*[Phase] data unavailable.*\n")
    except Exception as e:
        report.append(f"*Error in [Phase]: {str(e)}*\n")

    # Phase 2, 3, 4... (similar structure)

    # Write report
    with open(output_file, 'w') as f:
        f.write(''.join(report))

    print(f"\n✅ Report generated: {output_file}")
    return output_file

if __name__ == "__main__":
    # Example usage
    domain_analysis_pipeline(
        input_param_1="example",
        output_file="example_analysis.md"
    )
```

**Key principles**:
- Use tested tools only
- Handle errors gracefully (try/except)
- Continue if one phase fails
- Progressive report writing
- Clear status messages

### 4.3 Create test_skill.py

**Template**: See `assets/skill_template/test_skill.py`

**Test cases**:
1. Test each input type
2. Test combined inputs
3. Verify report sections exist
4. Check error handling

```python
#!/usr/bin/env python3
"""Test script for [Domain] skill"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from python_implementation import domain_analysis_pipeline

def test_basic_analysis():
    """Test basic analysis workflow"""
    output = domain_analysis_pipeline(
        input_param_1="test_value",
        output_file="test_basic.md"
    )
    assert os.path.exists(output), "Output file not created"

def test_combined_analysis():
    """Test with multiple inputs"""
    output = domain_analysis_pipeline(
        input_param_1="value1",
        input_param_2="value2",
        output_file="test_combined.md"
    )

    # Verify report has all sections
    with open(output, 'r') as f:
        content = f.read()
        assert "Phase 1" in content
        assert "Phase 2" in content

def main():
    tests = [
        ("Basic Analysis", test_basic_analysis),
        ("Combined Analysis", test_combined_analysis),
    ]

    results = {}
    for name, test_func in tests:
        try:
            test_func()
            results[name] = "✅ PASS"
        except Exception as e:
            results[name] = f"❌ FAIL: {e}"

    for name, result in results.items():
        print(f"{name}: {result}")

    all_passed = all("PASS" in r for r in results.values())
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
```

### 4.4 Run Tests

```bash
python test_skill.py
```

**Fix bugs until 100% pass rate**

---

## Phase 5: Documentation

**Objective**: Create implementation-agnostic documentation

**Duration**: 30-45 minutes

**CRITICAL**: SKILL.md must have ZERO Python/MCP specific code

### 5.1 Write SKILL.md

**Template**: See `assets/skill_template/SKILL.md`

**Structure**:
```markdown
---
name: tooluniverse-[domain-name]
description: [What it does]. [Capabilities]. [Databases used]. Use when [triggers].
---

# [Domain Name] Analysis

[One paragraph overview]

## When to Use This Skill

**Triggers**:
- "Analyze [domain] for [input]"
- "Find [data type] related to [query]"
- "[Domain-specific action]"

**Use Cases**:
1. [Use case 1 with description]
2. [Use case 2 with description]

## Core Databases Integrated

| Database | Coverage | Strengths |
|----------|----------|-----------|
| **Database 1** | [Scope] | [What it's good for] |
| **Database 2** | [Scope] | [What it's good for] |

## Workflow Overview

```
Input → Phase 1 → Phase 2 → Phase 3 → Report
```

---

## Phase 1: [Phase Name]

**When**: [Conditions]

**Objective**: [What this phase achieves]

### Tools Used

**TOOL_NAME**:
- **Input**:
  - `parameter1`: Description
  - `parameter2`: Description
- **Output**: Description
- **Use**: What it's used for

### Workflow

1. [Step 1]
2. [Step 2]
3. [Step 3]

### Decision Logic

- **Condition 1**: Action to take
- **Empty results**: How to handle
- **Errors**: Fallback strategy

---

## Phase 2, 3, 4... (similar structure)

---

## Output Structure

[Description of report format]

### Report Format

**Required Sections**:
1. Header with parameters
2. Phase 1 results
3. Phase 2 results
...

---

## Tool Parameter Reference

**Critical Parameter Notes** (from testing):

| Tool | Parameter | CORRECT Name | Common Mistake |
|------|-----------|--------------|----------------|
| TOOL_NAME | `param` | ✅ `actual_param` | ❌ `assumed_param` |

**Response Format Notes**:
- **TOOL_1**: Returns [format]
- **TOOL_2**: Returns [format]

---

## Fallback Strategies

[Document Primary → Fallback → Default for critical tools]

---

## Limitations & Known Issues

### Database-Specific
- **Database 1**: [Limitations]
- **Database 2**: [Limitations]

### Technical
- **Response formats**: [Notes]
- **Rate limits**: [If any]

---

## Summary

[Domain] skill provides:
1. ✅ [Capability 1]
2. ✅ [Capability 2]

**Outputs**: [Description]
**Best for**: [Use cases]
```

**Key principles**:
- NO Python/MCP code in SKILL.md
- Describe WHAT to do, not HOW in specific language
- Tool parameters conceptually described
- Decision logic and fallback strategies
- Response format variations documented

### 5.2 Write QUICK_START.md

**Template**: See `assets/skill_template/QUICK_START.md`

**Structure**:
```markdown
## Quick Start: [Domain] Analysis

[One paragraph overview]

---

## Choose Your Implementation

### Python SDK

#### Option 1: Complete Pipeline (Recommended)

```python
from skills.tooluniverse_[domain].python_implementation import domain_pipeline

# Example 1
domain_pipeline(
    input_param="value",
    output_file="analysis.md"
)
```

#### Option 2: Individual Tools

```python
from tooluniverse import ToolUniverse

tu = ToolUniverse()
tu.load_tools()

# Tool 1
result = tu.tools.TOOL_NAME(param="value")

# Tool 2
result = tu.tools.TOOL_NAME2(param="value")
```

---

### MCP (Model Context Protocol)

#### Option 1: Conversational (Natural Language)

```
"Analyze [domain] for [input]"

"Find [data] related to [query]"
```

#### Option 2: Direct Tool Calls

```json
{
  "tool": "TOOL_NAME",
  "parameters": {
    "param": "value"
  }
}
```

---

## Tool Parameters (All Implementations)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `param1` | string | Yes | [Description] |
| `param2` | integer | No | [Description] |

---

## Common Recipes

### Recipe 1: [Use Case Name]

**Python SDK**:
```python
[Code example]
```

**MCP**:
```
[Conversational example]
```

### Recipe 2, 3... (similar)

---

## Expected Output

[Show example report structure]

---

## Troubleshooting

### Issue: [Problem]
**Solution**: [Fix]

---

## Next Steps

After running this skill:
1. [Follow-up action 1]
2. [Follow-up action 2]
```

**Key principles**:
- Equal treatment of Python SDK and MCP
- Concrete examples for both
- Parameter table applies to both
- Clear recipes

---

## Phase 6: Testing & Validation

**Objective**: Verify skill meets all quality standards

**Duration**: 15-30 minutes

### 6.1 Run Complete Test Suite

```bash
cd skills/tooluniverse-[domain]
python test_skill.py
```

**Requirements**:
- ✅ 100% test pass rate
- ✅ All reports generated successfully
- ✅ No exceptions or errors
- ✅ Output files contain expected sections

### 6.2 Validate Against Checklist

**Use**: See `references/skill_standards_checklist.md`

**Implementation & Testing**:
- [ ] All tool calls tested with real ToolUniverse instance
- [ ] Test script passes with 100% success
- [ ] Working pipeline runs without errors
- [ ] 2-3 complete examples tested end-to-end
- [ ] Error cases handled gracefully
- [ ] SOAP tools have `operation` parameter (if applicable)
- [ ] Fallback strategies implemented and tested
- [ ] Parameters verified via testing

**Documentation**:
- [ ] SKILL.md is implementation-agnostic (NO Python/MCP code)
- [ ] python_implementation.py contains working code
- [ ] QUICK_START.md includes both Python SDK and MCP
- [ ] Tool parameter table notes "applies to all implementations"
- [ ] SOAP tool warnings displayed (if applicable)
- [ ] Fallback strategies documented
- [ ] Known limitations documented
- [ ] Example reports referenced

**Quality**:
- [ ] Reports are readable (not debug logs)
- [ ] All sections present even if "no data"
- [ ] Source databases clearly attributed
- [ ] Completes in reasonable time (<5 min)

### 6.3 Manual Verification

Test with fresh environment:
1. Load ToolUniverse
2. Import python_implementation
3. Run example from QUICK_START
4. Verify output matches expectations

---

## Phase 7: Packaging & Documentation

**Objective**: Create distributable skill and summary

**Duration**: 15 minutes

### 7.1 Create Summary Document

**File**: `NEW_SKILL_[DOMAIN].md`

**Content**:
```markdown
# New Skill Created: [Domain] Analysis

**Date**: [Date]
**Status**: ✅ COMPLETE AND TESTED

## Overview

[Brief description]

### Key Features
- [Feature 1]
- [Feature 2]

## Skill Details

**Location**: `skills/tooluniverse-[domain]/`

**Files Created**:
1. ✅ `python_implementation.py` ([lines]) - Working pipeline
2. ✅ `SKILL.md` ([lines]) - Implementation-agnostic docs
3. ✅ `QUICK_START.md` ([lines]) - Multi-implementation guide
4. ✅ `test_skill.py` ([lines]) - Test suite

**Total**: [total lines]

## Tools Integrated

- **Database 1**: [X tools]
- **Database 2**: [Y tools]
**Total**: [N tools]

## Test Results

```
✅ Test 1 - PASS
✅ Test 2 - PASS
✅ Test 3 - PASS

100% test pass rate
```

## Capabilities

[List key capabilities]

## Impact & Value

[Describe impact]

## Next Steps

[Suggest enhancements]
```

### 7.2 Update Session Tracking

If creating multiple skills in session, update tracking document with:
- Skills created count
- Total tools utilized
- Test coverage metrics
- Time per skill

---

## Tool Parameter Verification Workflow

**From devtu-optimize-skills - CRITICAL**

### Common Parameter Mistakes to Avoid

| Pattern | Don't Assume | Always Verify |
|---------|--------------|---------------|
| Function name includes param name | `drugbank_get_drug_by_name(name=...)` | Test reveals uses `query` |
| Descriptive function name | `map_uniprot_to_pathways(uniprot_id=...)` | Test reveals uses `id` |
| Consistent naming | All similar functions use same param | Each tool may differ |

### SOAP Tools Detection

**Indicators**:
- Error: "Parameter validation failed: 'operation' is a required property"
- Tool name includes: IMGT, SAbDab, TheraSAbDab
- Tool config shows `operation` in schema

**Fix**: Add `operation` parameter as first argument with method name

### Response Format Variations

**Standard**: `{status: "success", data: [...]}`
**Direct list**: Returns `[...]` without wrapper
**Direct dict**: Returns `{field1: ..., field2: ...}` without status

**Solution**: Handle all three in implementation with `isinstance()` checks

---

## Integration with Other Skills

### When to Use devtu-create-tool

**Invoke when**:
- Critical functionality has no existing tool
- Analysis phase completely blocked
- Alternative approaches inadequate

**Don't invoke when**:
- Similar tool exists with minor differences
- Can restructure analysis to use existing tools
- Tool would duplicate functionality

### When to Use devtu-fix-tool

**Invoke when**:
- Test reveals tool returns errors
- Tool fails validation
- Response format unexpected
- Parameter validation fails

### When to Use devtu-optimize-skills

**Reference when**:
- Need evidence grading patterns
- Want report optimization strategies
- Implementing completeness checking
- Designing synthesis sections

---

## Quality Indicators

**High-Quality Skill Has**:
✅ 100% test coverage before documentation
✅ Implementation-agnostic SKILL.md
✅ Multi-implementation QUICK_START (Python SDK + MCP)
✅ Complete error handling with fallbacks
✅ Tool parameter corrections table
✅ Response format documentation
✅ All tools verified through testing
✅ Working examples in both interfaces

**Red Flags**:
❌ Documentation written before testing tools
❌ Python code in SKILL.md
❌ Assumed parameters from function names
❌ No fallback strategies
❌ SOAP tools missing `operation`
❌ No test script or failing tests
❌ Single implementation only

---

## Time Investment Guidelines

**Per Skill Breakdown**:
- Phase 1 (Domain Analysis): 15 min
- Phase 2 (Tool Testing): 30-45 min
- Phase 3 (Tool Creation): 0-60 min (if needed)
- Phase 4 (Implementation): 30-45 min
- Phase 5 (Documentation): 30-45 min
- Phase 6 (Validation): 15-30 min
- Phase 7 (Packaging): 15 min

**Total**: ~1.5-2 hours per skill (without tool creation)
**With tool creation**: +30-60 minutes per tool

---

## References

- **Tool testing workflow**: See `references/tool_testing_workflow.md`
- **Implementation-agnostic format**: See `references/implementation_agnostic_format.md`
- **Standards checklist**: See `references/skill_standards_checklist.md`
- **devtu-optimize integration**: See `references/devtu_optimize_integration.md`

---

## Templates

All templates available in `assets/skill_template/`:
- `python_implementation.py` - Pipeline template
- `SKILL.md` - Documentation template
- `QUICK_START.md` - Multi-implementation guide
- `test_skill.py` - Test suite template

---

## Summary

**Create ToolUniverse Skill** provides systematic 7-phase workflow:

1. ✅ **Domain Analysis** - Understand requirements
2. ✅ **Tool Testing** - Verify before documenting (TEST FIRST!)
3. ✅ **Tool Creation** - Add missing tools if needed
4. ✅ **Implementation** - Build working pipeline
5. ✅ **Documentation** - Implementation-agnostic format
6. ✅ **Validation** - 100% test coverage
7. ✅ **Packaging** - Complete summary

**Result**: Production-ready skills with Python SDK + MCP support, complete testing, and quality documentation

**Time**: ~1.5-2 hours per skill (tested and documented)
