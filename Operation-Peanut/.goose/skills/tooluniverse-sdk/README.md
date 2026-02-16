# ToolUniverse SDK Skill

This skill teaches Cursor's AI agent how to use the ToolUniverse Python SDK for scientific research workflows.

## Skill Structure

- **SKILL.md**: Main instructions (concise, <500 lines) - read by agent automatically
- **REFERENCE.md**: Detailed reference material - read only when needed
- **README.md**: This file - documentation for developers

## What This Skill Teaches

The agent learns to:

1. **Install and configure ToolUniverse**
   - Package installation options
   - Environment setup with API keys
   - Verification steps

2. **Find scientific tools**
   - Three discovery methods (keyword, LLM, embedding)
   - When to use each method
   - Handle nested result structures

3. **Execute tools correctly**
   - Two execution patterns (dict API, function API)
   - Batch execution for parallel tasks
   - Proper error handling

4. **Build scientific workflows**
   - Multi-step pipelines
   - Drug discovery workflows
   - Protein analysis patterns

5. **Avoid common pitfalls**
   - Always call `load_tools()`
   - Check tool finder result structure
   - Use appropriate caching strategy
   - Validate parameters before execution

## When This Skill Activates

The skill activates when users mention:

- ToolUniverse, scientific tools, AI scientist
- Drug discovery, protein analysis, genomics
- Literature search, research pipelines
- ADMET prediction, structure prediction
- Disease-target associations
- Scientific workflows, computational biology

## Usage by Agent

When activated, the agent:

1. Reads **SKILL.md** for quick reference and common patterns
2. Consults **REFERENCE.md** for detailed configuration or troubleshooting
3. Applies best practices and avoids documented pitfalls
4. Provides complete, working code examples
5. Handles errors appropriately

## Skill Maintenance

To update this skill:

1. Edit **SKILL.md** for quick reference changes
2. Edit **REFERENCE.md** for detailed documentation updates
3. Keep SKILL.md under 500 lines (concise)
4. Use progressive disclosure (main info in SKILL.md, details in REFERENCE.md)

## Local Testing

To verify the skill works:

```python
# Test basic workflow
from tooluniverse import ToolUniverse

tu = ToolUniverse()
tu.load_tools()

# Find tools
tools = tu.run({
    "name": "Tool_Finder_Keyword",
    "arguments": {"description": "protein", "limit": 3}
})

# Execute tool
result = tu.tools.UniProt_get_entry_by_accession(accession="P05067")
print("✅ Skill examples work correctly")
```

## Resources

- **Main Docs**: https://zitniklab.hms.harvard.edu/ToolUniverse/
- **GitHub**: https://github.com/mims-harvard/ToolUniverse
- **Examples**: `/examples/` directory in repository
- **Community**: https://join.slack.com/t/tooluniversehq/shared_invite/zt-3dic3eoio-5xxoJch7TLNibNQn5_AREQ
