# CLAUDE.md - src/task_agents_mcp/

## Directory Purpose

This is the **core Python package** that implements the multi-tool MCP server. Each AI agent is exposed as a separate MCP tool, allowing direct invocation without routing.

## Directory Structure

```
task_agents_mcp/
├── __init__.py           # Package initialization, version info
├── __main__.py          # Entry point for direct module execution
├── server.py            # Main MCP server implementation
├── agent_manager.py     # Agent discovery, loading, and execution
├── resource_manager.py  # MCP resource registration for agents
└── session_store.py     # Session persistence for resume functionality
```

## Key Components

### server.py
**Purpose**: Main MCP server entry point using FastMCP framework

**Key Responsibilities**:
- Initializes FastMCP server with multi-tool architecture
- Discovers and loads agents from configured directories
- Registers each agent as a separate MCP tool
- Handles tool name sanitization (spaces→underscores, lowercase)
- Manages environment variable configuration

**Important Functions**:
- `sanitize_tool_name()`: Converts agent names to valid tool names
- `create_agent_tool_function()`: Creates tool functions with optional session_reset parameter
- `main()`: Server entry point called by the CLI command

**Configuration Priority**:
1. Environment variable `TASK_AGENTS_PATH` (for Claude Desktop)
2. Default to `./task-agents` in current directory (for Claude Code)

### agent_manager.py
**Purpose**: Core agent management and execution logic

**Key Responsibilities**:
- Loads agent configurations from Markdown files
- Parses YAML frontmatter and system prompts
- Manages Claude CLI execution with proper arguments
- Handles session resumption and chaining
- Resolves resource directories dynamically

**Key Classes**:
- `AgentConfig`: Dataclass holding agent configuration
- `AgentManager`: Main manager class for all agents

**Agent Execution Flow**:
1. Parse agent configuration from .md file
2. Build Claude CLI command with flags: `--tools`, `--name`, `--model`, `--system-prompt`, plus optional `--disallowed-tools`, `--mcp-config`, `--strict-mcp-config`, `-r`, `--add-dir`
3. Handle session resumption if enabled
4. Execute via subprocess and stream output
5. Update session chain for next resume

**AgentConfig Fields**:
- Required: name, agent_name, description, tools, model, cwd, system_prompt
- Optional: resume_session, resource_dirs, disallowed_tools, mcp_config

### resource_manager.py
**Purpose**: MCP resource registration for agent discovery

**Key Responsibilities**:
- Registers one MCP resource per agent
- Provides structured information about each agent
- Supports BMad workflow ordering
- Helps LLM clients understand agent capabilities

**Resource Format**:
- URI: `{agent-name}://` (e.g., `analyst://`, `dev://`)
- Contains: description, tools, model, session info
- Includes workflow position for BMad agents

### session_store.py
**Purpose**: Persistent session management for resume functionality

**Key Responsibilities**:
- Tracks session ID chains for each agent
- Persists to `/tmp/task_agents_sessions.json`
- Manages exchange counting and limits
- Handles session reset requests

**Session Chain Flow**:
1. First call creates initial session
2. Each resume creates new session ID
3. Chain continues until exchange limit
4. Resets to fresh session after limit

## Integration Points

### With Claude CLI
- Uses subprocess to execute `claude` command with `--output-format stream-json --verbose`
- Uses `--tools` (comma-separated) instead of `--allowedTools`
- Tags sessions with `--name` (auto-generated from agent name)
- Supports `--disallowed-tools` and `--mcp-config` + `--strict-mcp-config`
- Handles streaming output with proper encoding
- Manages session IDs for resumption via `-r`

### With FastMCP
- Each agent registered as separate tool
- Tools exposed with proper descriptions
- Resources registered for discovery
- Context passed for execution

### With File System
- Agent configs loaded from .md files
- Session data persisted to /tmp
- Resource directories validated at runtime
- Working directory management per agent

## Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `TASK_AGENTS_PATH` | Custom agents directory | No (Claude Desktop: Yes) |
| `CLAUDE_EXECUTABLE_PATH` | Claude CLI location | No (auto-detected) |

## Error Handling

- Missing agents directory: Logs warning, server runs with no tools
- Claude CLI not found: Detailed error with installation instructions
- Invalid agent config: Logged and skipped, server continues
- Session corruption: Resets to fresh session

## Security Considerations

- Subprocess execution with shell=False
- Input sanitization for prompts
- Temporary file permissions
- No arbitrary code execution

## Performance Notes

- Agents loaded once at startup
- Session chains cached in memory
- Subprocess streaming for real-time output
- Minimal overhead per tool invocation

## Testing Entry Points

Direct module execution:
```bash
python -m task_agents_mcp
```

Via installed command:
```bash
task-agent
```

## Version Management

Version defined in two places (must be synchronized):
- `__init__.py`: Package version
- `pyproject.toml`: Distribution version

Current version: 4.1.0 (New CLI flags: --tools, --name, --disallowed-tools, --mcp-config)