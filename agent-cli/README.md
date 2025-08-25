# Agent CLI - Direct Terminal Access to Task Agents

The `agent-cli` directory contains a separate, extensible system for generating and managing direct terminal aliases to your task agents. This allows you to run agents directly from your shell without going through the MCP server.

## Quick Start

```bash
# List available agents
task-agent list
task-agent list --verbose

# Generate aliases for all agents
task-agent generate-aliases

# Use your agents directly
example-agent "count to 10"
example-agent --reset "start fresh session" 
```

## Directory Structure

```
agent-cli/
├── README.md           # This file
├── ARCHITECTURE.md     # Technical documentation
└── agent_cli/          # Python package
    ├── __init__.py     # Package exports
    ├── alias_generator.py  # Core alias generation logic
    └── cli.py          # Future CLI interface (expandable)
```

## How It Works

1. **Scans your `task-agents/` directory** for `.md` configuration files
2. **Generates shell scripts** that wrap Claude CLI commands
3. **Installs aliases** to `~/.local/bin/` for global access
4. **Each alias dynamically loads** agent config on execution

## Features

### ✅ Currently Implemented
- **Dynamic config loading**: Always uses latest agent settings
- **Session resumption**: Support for `resume-session: true` agents  
- **Identical output**: Same JSON parsing as MCP server
- **Auto-installation**: One-command setup
- **Working directory resolution**: Proper `cwd: "."` handling

### ✅ Additional Commands  
These commands are now integrated into the main `task-agent` CLI:

- `task-agent list` - ✅ Show all available agents
- `task-agent list --verbose` - ✅ Show detailed agent information  
- `task-agent watch` - 🚧 Auto-regenerate on file changes (planned)
- `task-agent install <agent>` - 🚧 Install single agent alias (planned)

### 🚧 Future Expansions
Planned features for the agent-cli system:

- `task-agent config` - Manage agent configurations
- `task-agent logs` - Execution logging and debugging  
- `task-agent benchmark` - Performance monitoring
- `task-agent validate` - Validate agent configurations
- `task-agent template` - Create new agent templates

## Generated Alias Structure

Each alias is a bash script that:
1. Validates input arguments
2. Dynamically parses the agent's `.md` file  
3. Builds the exact Claude CLI command that MCP server uses
4. Executes with stream-json output
5. Parses and formats results identically to MCP server

**Example command structure:**
```bash
claude -p "your query" \
  --output-format stream-json \
  --verbose \
  --allowedTools Read Write Edit \
  --model haiku \
  --system-prompt-file /tmp/prompt.txt \
  --append-system-prompt "WORKING DIRECTORY CONTEXT: ..." \
  [-r session_id]  # If resume-session enabled
```

## Adding New Agents

1. **Create agent file**: `task-agents/my-agent.md`
2. **Regenerate aliases**: `python -m src.task_agents_mcp.cli generate-aliases`  
3. **Use immediately**: `my-agent "your query"`

The alias name is auto-generated from the agent name:
- "Code Reviewer" → `code-reviewer`
- "Data Analyst" → `data-analyst`  
- "Example Agent" → `example-agent`

## Benefits Over MCP Server

- **Direct execution**: No MCP server overhead
- **Always current**: Reads latest config on each run
- **Portable**: Works anywhere Claude CLI is installed
- **Debugging friendly**: Can inspect generated scripts
- **Extensible**: Easy to add custom features

## Technical Notes

- **Python 3.11+ required** (matches main project)
- **Claude CLI dependency**: Must have Claude Code installed
- **Session storage**: Uses `/tmp/task_agents_sessions.json`
- **Config parsing**: Embedded Python YAML parser
- **Working directory**: Resolves relative paths to project root

See `ARCHITECTURE.md` for detailed technical documentation.