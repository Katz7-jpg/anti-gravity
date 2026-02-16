# Setup ToolUniverse Skill

Comprehensive skill for installing and configuring ToolUniverse with MCP integration for Cursor or Claude Desktop.

## What This Skill Does

This skill guides you through:

1. ✅ Detecting your environment (OS, Python version, package managers)
2. ✅ Installing ToolUniverse with appropriate method (pip/uv/dev)
3. ✅ Configuring MCP integration for Cursor or Claude Desktop
4. ✅ Setting up compact mode (recommended to avoid context overflow)
5. ✅ Validating installation and configuration
6. ✅ Troubleshooting common setup issues
7. ✅ Testing MCP connection

## When to Use This Skill

Use this skill when:

- Setting up ToolUniverse for the first time
- Configuring MCP servers in Cursor or Claude Desktop
- Troubleshooting ToolUniverse installation issues
- Verifying ToolUniverse setup
- User mentions: "install ToolUniverse", "setup scientific tools", "configure MCP"

## Key Features

### Automated Environment Detection

The skill automatically detects:
- Python version compatibility (3.10-3.13)
- Available package managers (pip, uv)
- Operating system and paths
- Existing MCP configurations

### Validation Scripts

Four comprehensive validation scripts:

1. **check_prerequisites.py** - Verify system requirements before installation
2. **verify_installation.py** - Confirm ToolUniverse is installed correctly
3. **test_mcp_connection.py** - Validate MCP configuration
4. **diagnose_setup.py** - Generate comprehensive diagnostic report

### Compact Mode Warning

⚠️ **Critical Feature**: The skill emphasizes using compact mode because:

- ToolUniverse has 764+ tools
- Loading all tools causes context window overflow
- Compact mode exposes 5 core tools
- All 764+ tools remain accessible via `execute_tool`

## File Structure

```
setup-tooluniverse/
├── SKILL.md              # Main skill instructions
├── README.md             # This file
├── INSTALL.md            # Detailed installation guide
├── MCP_CONFIG.md         # MCP configuration reference
└── scripts/
    ├── check_prerequisites.py      # Pre-installation checks
    ├── verify_installation.py      # Post-installation validation
    ├── test_mcp_connection.py      # MCP configuration testing
    ├── diagnose_setup.py           # Comprehensive diagnostics
    └── list_tool_categories.py     # List available categories
```

## Quick Usage

### For Users

When helping a user set up ToolUniverse, follow the workflow in SKILL.md:

1. Run prerequisite check
2. Install with appropriate method
3. Verify installation
4. Configure MCP with compact mode
5. Test connection

### For Troubleshooting

When diagnosing issues:

1. Run diagnostic script: `python scripts/diagnose_setup.py`
2. Review generated report
3. Follow recommendations
4. Retest with connection test

## Script Usage

All scripts are standalone and can be run directly:

```bash
# Check if system is ready
python scripts/check_prerequisites.py

# Verify installation after pip install
python scripts/verify_installation.py

# Test MCP configuration
python scripts/test_mcp_connection.py

# Generate diagnostic report
python scripts/diagnose_setup.py

# List tool categories
python scripts/list_tool_categories.py
```

## Configuration Templates

### Recommended Configuration (Compact Mode)

```json
{
  "mcpServers": {
    "tooluniverse": {
      "command": "tooluniverse-smcp-stdio",
      "args": ["--compact-mode"]
    }
  }
}
```

See `MCP_CONFIG.md` for advanced configurations.

## Common Issues Covered

The skill handles these common issues:

1. ✅ Python version incompatibility
2. ✅ Command not found errors
3. ✅ Context window overflow
4. ✅ uv directory not found
5. ✅ Import errors for specific tools
6. ✅ MCP server won't start
7. ✅ API key configuration

## Testing

To test this skill itself:

1. Ask: "Help me set up ToolUniverse"
2. Verify skill is activated automatically
3. Follow guided workflow
4. Confirm all scripts work
5. Verify MCP connection successful

## Skill Metadata

- **Name**: setup-tooluniverse
- **Type**: Installation & Configuration
- **Complexity**: Medium
- **Prerequisites**: Python 3.10-3.13
- **Duration**: ~5-10 minutes for full setup

## Updates and Maintenance

This skill is based on ToolUniverse v1.0.17+ and verified against:

- macOS (Darwin)
- Python 3.10, 3.11, 3.12, 3.13
- pip and uv package managers
- Cursor and Claude Desktop MCP integration

## Contributing

To improve this skill:

1. Test with different environments
2. Report issues encountered
3. Add new troubleshooting scenarios
4. Update validation scripts

## Related Skills

- `tooluniverse-sdk` - Using ToolUniverse for research
- `tooluniverse-create-tool` - Creating new tools
- `tooluniverse-fix-tool` - Fixing failing tools

## Support

For ToolUniverse-specific issues:
- GitHub: https://github.com/mims-harvard/ToolUniverse
- Documentation: https://zitniklab.hms.harvard.edu/ToolUniverse/
- Slack: https://join.slack.com/t/tooluniversehq/shared_invite/zt-3dic3eoio-5xxoJch7TLNibNQn5_AREQ
