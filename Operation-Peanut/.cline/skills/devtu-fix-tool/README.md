# ToolUniverse Tool Fix Skill

Comprehensive skill for diagnosing and fixing failing ToolUniverse tools based on real-world experience.

## Overview

This skill provides a systematic workflow for fixing ToolUniverse tools that fail tests, including:
- Binary response handling (images, PDFs, files)
- Schema validation issues
- API endpoint errors
- Parameter type mismatches
- Response parsing problems

## Structure

- **SKILL.md** - Main skill file with complete workflow (415 lines)
- **EXAMPLES.md** - Real-world examples including the ChEMBL image fix
- **QUICK-REFERENCE.md** - Command cheat sheet and common patterns
- **README.md** - This file

## When to Use

The agent will automatically apply this skill when:
- ToolUniverse tests fail
- Tools return errors or exceptions
- Schema validation fails
- User asks to debug or fix ToolUniverse tools
- Working with `scripts/test_new_tools.py` output

## Key Features

### Complete Workflow
1. Diagnosis (identify error type)
2. Root cause analysis
3. Implementation (apply fix pattern)
4. Regeneration (update tool files)
5. Verification (confirm fix works)
6. Documentation (create summary)

### Error Type Coverage
- JSON parsing errors (binary responses)
- Schema validation mismatches
- 404 endpoint errors
- Parameter type errors
- API response handling

### Fix Patterns
- Binary Response Pattern (images, files)
- Schema Validation Pattern
- Parameter Schema Pattern
- Endpoint URL Pattern
- Custom response handling

### Testing Tools
- Direct tool execution snippets
- Schema validation tests
- API endpoint testing with curl
- Debugging techniques

## Quick Start

For the most common case (test failure):

```bash
# 1. Run test to identify failure
python scripts/test_new_tools.py <tool-pattern> -v

# 2. Apply appropriate fix from SKILL.md

# 3. Regenerate tools
python -m tooluniverse.generate_tools

# 4. Verify fix
python scripts/test_new_tools.py <tool-pattern>
```

## Example Usage

Based on the ChEMBL image endpoint fix documented in EXAMPLES.md:

**Problem**: Tool failed with JSON parsing error when fetching binary image
**Solution**: Added binary detection and special handling in tool class
**Result**: All 64 tests passing with 100% schema validation

## Files Modified by Typical Fix

| Type | Files |
|------|-------|
| Binary response | `src/tooluniverse/*_tool.py`, `data/*_tools.json` |
| Schema mismatch | `data/*_tools.json` only |
| Endpoint error | `data/*_tools.json` only |
| Parameter error | `data/*_tools.json` only |

## Progressive Disclosure

- **SKILL.md** contains essential workflow and patterns (read first)
- **EXAMPLES.md** provides detailed real-world examples (read when implementing similar fix)
- **QUICK-REFERENCE.md** offers command cheat sheet (reference during work)

## Skill Statistics

- Main file: 415 lines (under 500 line guideline)
- Examples: Includes complete ChEMBL image fix walkthrough
- Commands: 20+ testing and debugging commands
- Patterns: 5 major fix patterns covered
- Coverage: All common ToolUniverse test failures

## Integration with Workflow

This skill integrates naturally with:
- Testing workflows (`test_new_tools.py`, `test_all_tools.py`)
- Tool development (`generate_tools.py`)
- Git workflows (commit, diff, status)
- API debugging (curl, requests)

## Updates

Created: 2026-02-02
Based on: ChEMBL image endpoint fix experience
Version: 1.0
