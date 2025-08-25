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
example-agent "count to 10"                    # Direct query
example-agent --reset "start fresh session"    # Reset session
example-agent                                   # Interactive REPL mode

# Interactive REPL mode (new!)
code-reviewer                                   # Start REPL for Code Reviewer
```

## Directory Structure

```
agent-cli/
├── README.md           # This file
├── ARCHITECTURE.md     # Technical documentation
├── CLAUDE.md           # Claude Code documentation
└── agent_cli/          # Python package
    ├── __init__.py     # Package exports
    ├── alias_generator.py  # Core alias generation logic
    ├── repl.py         # Interactive REPL functionality
    └── cli.py          # CLI interface (expandable)
```

## How It Works

1. **Scans your `task-agents/` directory** for `.md` configuration files
2. **Generates shell scripts** that wrap Claude CLI commands
3. **Installs aliases** to `~/.local/bin/` for global access
4. **Each alias dynamically loads** agent config on execution

## Features

### ✅ Currently Implemented
- **Interactive REPL mode**: Call any agent without arguments for chat interface
- **Dynamic config loading**: Always uses latest agent settings
- **Session resumption**: Support for `resume-session: true` agents  
- **Session-based conversation history**: Proper chat memory per session
- **Identical output**: Same JSON parsing as MCP server
- **Auto-installation**: One-command setup with fixed installer
- **Working directory resolution**: Proper `cwd: "."` handling
- **Stream-JSON parsing**: Robust JSON parsing with proper escaping

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

Each alias is a bash script that supports two modes:

### Interactive REPL Mode (No Arguments)
When called without arguments, starts an interactive chat session:
1. Parses agent config from `.md` file
2. Starts Python REPL with prompt-toolkit interface
3. Maintains session-based conversation history
4. Supports session resumption with exchange limits
5. Dynamic config reloading on each query

### Direct Query Mode (With Arguments)  
When called with arguments, executes single query:
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
2. **Regenerate aliases**: `task-agent generate-aliases`  
3. **Use immediately**: 
   ```bash
   my-agent "your query"    # Direct query
   my-agent                 # Interactive REPL
   ```

The alias name is auto-generated from the agent name:
- "Code Reviewer" → `code-reviewer`
- "Data Analyst" → `data-analyst`  
- "Example Agent" → `example-agent`

## REPL Mode Features

When you run an agent without arguments:
- **Colored interface**: User input in green, agent responses in blue
- **Session tracking**: Shows current session ID and conversation history
- **Dynamic reload**: Agent config reloaded from `.md` file on each query
- **Memory management**: Session-specific chat history with proper isolation
- **Tool feedback**: Shows which tools were used and token usage
- **Easy exit**: `Ctrl+C` to exit gracefully

## Benefits Over MCP Server

- **Interactive REPL**: Built-in chat interface for each agent
- **Direct execution**: No MCP server overhead
- **Always current**: Reads latest config on each run
- **Portable**: Works anywhere Claude CLI is installed
- **Debugging friendly**: Can inspect generated scripts
- **Extensible**: Easy to add custom features
- **Better UX**: Colored terminal interface with history

## Technical Notes

- **Python 3.11+ required** (matches main project)
- **Claude CLI dependency**: Must have Claude Code installed
- **REPL dependencies**: Requires `prompt-toolkit` for interactive mode
- **Session storage**: Uses `/tmp/task_agents_sessions.json` (shared with MCP server)
- **Config parsing**: Embedded Python YAML parser
- **Working directory**: Resolves relative paths to project root
- **Session management**: Integrates with MCP server's SessionChainStore
- **JSON parsing**: Robust stream-JSON parsing with proper escaping

See `ARCHITECTURE.md` for detailed technical documentation.