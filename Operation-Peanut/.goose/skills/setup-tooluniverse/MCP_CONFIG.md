# MCP Configuration Guide

Advanced configuration options for ToolUniverse MCP integration.

## Configuration File Locations

### Cursor

- **macOS**: `~/Library/Application Support/Cursor/User/mcp.json`
- **Windows**: `%APPDATA%\Cursor\User\mcp.json`
- **Linux**: `~/.config/Cursor/User/mcp.json`

### Claude Desktop

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

## Configuration Templates

### Basic Configuration (Recommended)

Simplest setup using installed command:

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

### UV-Based Configuration

Using uv for better isolation:

```json
{
  "mcpServers": {
    "tooluniverse": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/tooluniverse-env",
        "run",
        "tooluniverse-smcp-stdio",
        "--compact-mode"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

### Development Configuration

Using development installation:

```json
{
  "mcpServers": {
    "tooluniverse": {
      "command": "python3",
      "args": [
        "-m",
        "tooluniverse.smcp_server",
        "--compact-mode"
      ],
      "cwd": "/path/to/ToolUniverse-main"
    }
  }
}
```

## Configuration Options

### Compact Mode (Recommended)

Exposes only 5 core tools, prevents context overflow:

```json
"args": ["--compact-mode"]
```

**Core tools exposed**:
- `list_tools` - List all available tools
- `grep_tools` - Search tools by keyword
- `get_tool_info` - Get tool details
- `execute_tool` - Execute any tool by name
- `find_tools` - Find tools by description

### Specific Categories

Load only specific tool categories:

```json
"args": [
  "--categories",
  "uniprot",
  "ChEMBL",
  "opentarget",
  "pdb"
]
```

**Available categories**: Run `tooluniverse-smcp-stdio --list-categories` to see all.

**Warning**: Multiple categories may still cause context issues.

### Exclude Categories

Load all except specific categories:

```json
"args": [
  "--exclude-categories",
  "mcp_auto_loader_boltz",
  "mcp_auto_loader_expert_feedback"
]
```

### Specific Tools Only

Load only named tools:

```json
"args": [
  "--include-tools",
  "UniProt_get_entry_by_accession",
  "ChEMBL_get_molecule_by_chembl_id"
]
```

### Enable Hooks

Enable output processing hooks (disabled by default for stdio):

```json
"args": [
  "--compact-mode",
  "--hooks",
  "--hook-type",
  "SummarizationHook"
]
```

**Hook types**:
- `SummarizationHook` - Summarize long outputs
- `FileSaveHook` - Save outputs to files

### Verbose Logging

Enable detailed logging for debugging:

```json
"args": [
  "--compact-mode",
  "--verbose"
]
```

## Environment Variables

### Standard Variables

```json
"env": {
  "PYTHONIOENCODING": "utf-8",
  "PYTHONPATH": "/custom/python/path",
  "TOOLUNIVERSE_CACHE_DIR": "/custom/cache/dir"
}
```

### API Keys

For tools requiring authentication:

```json
"env": {
  "PYTHONIOENCODING": "utf-8",
  "OPENAI_API_KEY": "your-key-here",
  "ANTHROPIC_API_KEY": "your-key-here",
  "UMLS_API_KEY": "your-key-here"
}
```

**Security Note**: Avoid hardcoding keys. Use environment variables or .env files.

### Better API Key Management

Use environment variables from shell:

```json
"env": {
  "PYTHONIOENCODING": "utf-8",
  "OPENAI_API_KEY": "${OPENAI_API_KEY}"
}
```

Then set in shell:
```bash
export OPENAI_API_KEY=your-key-here
```

## Multiple MCP Servers

Configure multiple servers:

```json
{
  "mcpServers": {
    "tooluniverse": {
      "command": "tooluniverse-smcp-stdio",
      "args": ["--compact-mode"]
    },
    "other-server": {
      "command": "other-mcp-server",
      "args": []
    }
  }
}
```

## Working Directory

Specify working directory:

```json
{
  "mcpServers": {
    "tooluniverse": {
      "command": "tooluniverse-smcp-stdio",
      "args": ["--compact-mode"],
      "cwd": "/path/to/working/directory"
    }
  }
}
```

## Testing Configuration

### Validate JSON

Before saving, validate JSON syntax:

```bash
# macOS/Linux
cat mcp.json | python3 -m json.tool

# Or use online validator
```

### Test Command Directly

Test the MCP command in terminal:

```bash
tooluniverse-smcp-stdio --compact-mode
# Should start without errors
# Press Ctrl+C to exit
```

### Check Logs

After restarting application, check logs:

**Cursor logs**:
- macOS: `~/Library/Application Support/Cursor/logs/`
- Look for files with "mcp" in the name

**Claude Desktop logs**:
- Access via app: Help → View Logs

## Troubleshooting Configuration

### Issue: Server Won't Start

1. Test command directly in terminal
2. Check JSON syntax (no trailing commas)
3. Verify paths are absolute, not relative
4. Check file permissions

### Issue: Context Overflow

- Ensure `--compact-mode` is in args
- Reduce number of categories
- Use specific tools only

### Issue: Command Not Found

- Verify installation: `pip show tooluniverse`
- Check PATH: `which tooluniverse-smcp-stdio`
- Use full path to command if needed

### Issue: Environment Variables Not Working

- Use absolute paths
- Avoid ~ expansion (use full path)
- Check variable syntax in JSON

## Performance Optimization

### Fast Startup

Use compact mode and minimal categories:

```json
"args": [
  "--compact-mode",
  "--categories",
  "special_tools"
]
```

### Memory Optimization

Reduce tool loading:

```json
"args": [
  "--compact-mode",
  "--exclude-categories",
  "mcp_auto_loader_boltz"
]
```

## Security Considerations

1. **API Keys**: Never commit config files with hardcoded keys
2. **Paths**: Use absolute paths to avoid ambiguity
3. **Permissions**: Restrict config file permissions (chmod 600)
4. **Validation**: Always validate JSON before saving

## Example Configurations

### Research Use Case

For scientific research with common tools:

```json
{
  "mcpServers": {
    "tooluniverse": {
      "command": "tooluniverse-smcp-stdio",
      "args": [
        "--compact-mode"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

### Development Use Case

For tool development and testing:

```json
{
  "mcpServers": {
    "tooluniverse-dev": {
      "command": "python3",
      "args": [
        "-m",
        "tooluniverse.smcp_server",
        "--compact-mode",
        "--verbose"
      ],
      "cwd": "/path/to/ToolUniverse-main"
    }
  }
}
```

### Production Use Case

For production with specific tools:

```json
{
  "mcpServers": {
    "tooluniverse-prod": {
      "command": "uv",
      "args": [
        "--directory",
        "/opt/tooluniverse",
        "run",
        "tooluniverse-smcp-stdio",
        "--categories",
        "uniprot",
        "ChEMBL",
        "opentarget"
      ]
    }
  }
}
```

## Advanced Features

### Space Configuration

Load preset tool configurations:

```json
"args": [
  "--compact-mode",
  "--load",
  "community/proteomics-toolkit"
]
```

### Custom Hook Configuration

Use custom hook configuration file:

```json
"args": [
  "--compact-mode",
  "--hooks",
  "--hook-config-file",
  "/path/to/hook_config.json"
]
```
