# ToolUniverse Fix Tool Skill - Update Summary

## Date
February 2, 2026

## Changes Made
Updated skill from 551 lines to 967 lines (+416 lines, +75% content)

## New Sections Added

### 1. Error Type: Nullable Field Errors (New Section)
**Location**: Error Types section

**What it covers**:
- Symptom: `Schema Mismatch: ... None is not of type 'integer'`
- Cause: API returns `None` for optional fields
- Fix pattern: `{"type": ["string", "null"]}` syntax
- Common nullable fields in scientific APIs

**Why added**: Real scientific APIs (GTEx, PubMed, etc.) frequently return `None` for optional/missing data. This pattern wasn't explicitly documented.

### 2. Nullable Fields Pattern (New Section)
**Location**: Fix Patterns section

**What it covers**:
- When to use nullable types vs when not to
- Pattern by field type (string, number, integer, object)
- Best practices for identifying nullable fields
- Common examples from scientific APIs

**Why added**: Provides comprehensive guidance on handling sparse/optional data, which is common in real-world scientific databases.

### 3. Finding Valid Test Examples (New Section)
**Location**: After Common Pitfalls

**What it covers**:
- **Technique 1**: List → Get Pattern
- **Technique 2**: Search → Details Pattern  
- **Technique 3**: Hierarchy Pattern (for dependent resources like gene+variant+tissue)
- **Technique 4**: Dataset Version Awareness

**Why added**: Original skill said "use valid data" but didn't show HOW to discover valid examples when test examples fail. This is a critical debugging workflow.

**Real example**: Finding valid GTEx eQTL by querying eGenes → getting their variants → constructing valid test.

### 4. Response Structure Consistency (New Section)
**Location**: Tool Class Patterns section

**What it covers**:
- Common inconsistency patterns (mixing `data`, `datasets`, `results`)
- How to scan all methods for consistency
- Fix examples showing before/after
- Consistency checklist
- Quick scan command: `grep -n "return {" ... | grep -v '"data"'`

**Why added**: When fixing one method, developers often miss other methods with similar issues. This systematic approach prevents partial fixes.

### 5. Complete Fix Example: GTEx Tools (New Section)
**Location**: End of skill (Quick Reference section)

**What it covers**:
- Real-world example tying together multiple fix patterns
- Shows initial problem (9 schema invalid)
- Demonstrates all 5 fixes applied:
  1. Schema structure correction
  2. Inconsistent field names
  3. Spread syntax issue
  4. Nullable fields
  5. Invalid test example discovery
- Final result: 100% pass rate

**Why added**: Concrete example showing how multiple patterns combine in real fixes. Bridges theory to practice.

## Updated Sections

### Common Pitfalls
**Added items**:
7. Inconsistent return structures across methods
8. Not allowing nullable fields  
9. Dataset version mismatches

**Why**: These were lessons learned from GTEx fix that weren't in original pitfalls list.

## Key Improvements

### 1. More Practical
- Added 4 concrete code examples for finding valid test data
- Included real API interactions (GTEx, scientific databases)
- Shell commands for scanning consistency issues

### 2. More Comprehensive
- Covers nullable fields extensively (syntax, when to use, field types)
- Documents version-specific API behavior
- Systematic approach to checking all methods

### 3. Better Organization
- New sections flow logically: Error → Pattern → Discovery → Consistency → Example
- Complete example ties everything together
- Each pattern has clear before/after code

### 4. Real-World Focus
- Based on actual GTEx tool fix (12 tools, 100% success)
- Addresses issues from scientific APIs specifically
- Shows discovery workflows, not just fixes

## Lines Added by Section

```
Error Types (Nullable Field Errors):        ~35 lines
Fix Patterns (Nullable Fields Pattern):     ~40 lines
Finding Valid Test Examples:                ~120 lines
Response Structure Consistency:             ~85 lines
Complete Fix Example:                       ~135 lines
Total new content:                          ~415 lines
```

## Impact

### Before Update
- Covered 4 error types
- 3 main fix patterns
- Basic troubleshooting
- Limited real-world examples

### After Update  
- Covers 5 error types (+ nullable fields)
- 4 main fix patterns (+ nullable fields pattern)
- Advanced discovery techniques (4 methods)
- Consistency checking workflow
- Complete real-world example

### Use Cases Now Covered
✅ Handling sparse/optional data in APIs  
✅ Discovering valid test examples when docs are insufficient  
✅ Checking consistency across all methods in a class  
✅ Dealing with multi-version APIs  
✅ End-to-end fix workflow with real example

## Testing
Skill successfully used to fix GTEx tools (gtex and gtex_v2):
- 10 tools with schema issues → Fixed
- 1 tool with invalid test → Fixed
- 3 tools with nullable fields → Fixed
- 100% test pass rate achieved

## Files Modified
- `/Users/shgao/.cursor/skills/tooluniverse-fix-tool/SKILL.md`
  - Original: 551 lines
  - Updated: 967 lines
  - Change: +416 lines (+75%)

## Backward Compatibility
✅ All original content preserved  
✅ New sections added, not replacing  
✅ Existing patterns still valid  
✅ Only additions and enhancements
