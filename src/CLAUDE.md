# Source Code Documentation

## Purpose

This directory contains the core implementation of the Task Agent system, including both the MCP server components and the new SDK integration layer that enables direct agent execution without containers or MCP protocol overhead.

## Structure

```
src/
├── task_agents_mcp/         # MCP server implementation (v4.0.0)
│   ├── __init__.py         # Package metadata and version
│   ├── server.py           # FastMCP server with multi-tool registration
│   ├── agent_manager.py    # Agent loading and configuration
│   ├── resource_manager.py # MCP resource registration
│   ├── session_store.py    # Conversation session persistence
│   └── cli.py              # Command-line interface and aliases
└── sdk_integration/         # Direct SDK execution layer
    ├── __init__.py         # Package exports
    ├── agent_executor.py   # High-level agent management
    └── sdk_executor.py     # Claude SDK integration
```

## Key Components

### MCP Server Implementation (`task_agents_mcp/`)

#### server.py
- **Purpose**: Main MCP server using FastMCP framework
- **Key Features**:
  - Dynamic tool registration (each agent = MCP tool)
  - Tool name sanitization (spaces → underscores)
  - Session management integration
  - Resource exposure for agent configs
- **Entry Point**: `main()` function for CLI execution

#### agent_manager.py
- **Purpose**: Load and manage agent configurations
- **Key Classes**:
  - `AgentConfig`: Pydantic model for agent YAML frontmatter
  - `AgentManager`: Loader for `.md` agent files
- **Agent Discovery**:
  - Loads from `TASK_AGENTS_PATH` or `./task-agents`
  - Parses YAML frontmatter from markdown files
  - Validates required fields (name, tools, model)

#### resource_manager.py
- **Purpose**: Expose agent configurations as MCP resources
- **Resource URIs**: Format `{Agent-Name}://` (spaces → hyphens)
- **Content Types**: 
  - `text/markdown` for agent prompts
  - `application/json` for metadata

#### session_store.py
- **Purpose**: Maintain conversation context across calls
- **Storage**: JSON file at `/tmp/task_agents_sessions.json`
- **Features**:
  - Session persistence between calls
  - Optional session reset
  - Automatic cleanup of old sessions

#### cli.py
- **Purpose**: Enhanced CLI with aliases and REPL mode
- **Features**:
  - Alias management (`agent-cli alias`)
  - Interactive REPL mode
  - Direct agent invocation

### SDK Integration Layer (`sdk_integration/`)

#### agent_executor.py
- **Purpose**: High-level interface for agent management
- **Key Class**: `AgentExecutor`
- **Responsibilities**:
  - Load agents from directory
  - Create SDK executors for agents
  - Manage OAuth authentication
  - Handle streaming responses
- **Integration Points**:
  - Used by Web UI backend
  - Direct SDK calls without MCP

#### sdk_executor.py
- **Purpose**: Direct Claude SDK integration
- **Key Class**: `SDKExecutor`
- **Features**:
  - OAuth credential loading
  - Tool registration from agent config
  - Streaming response handling
  - Session context management with chaining
- **Credential Paths**:
  - `~/.claude/.credentials.json`
  - `/home/task-agent/.claude/.credentials.json`
- **Session Resumption**:
  - SDK returns new `session_id` with each response
  - Each new session_id is used for the next message
  - Creates a conversation chain for context continuity
  - Only works when agent has `resume-session: true`

## Patterns & Conventions

### Agent Configuration Format
```yaml
---
agent-name: Agent Name
description: What the agent does
tools: Read, Grep, Bash  # Comma-separated
model: opus  # or sonnet, haiku
cwd: .  # Working directory
optional:
  resume-session: true 10  # Enable with timeout
  resource_dirs: ./data  # Additional resources
---

System prompt content here...
```

### Tool Name Sanitization
```python
# Agent name → Tool name
"Code Reviewer" → "code_reviewer"
"Data Analyst" → "data_analyst"

# Resource URI format
"Code Reviewer" → "Code-Reviewer://"
```

### Session Management Pattern
```python
# Session key format
session_key = f"{agent_name}_{session_id}"

# Session data structure
{
    "messages": [...],
    "context": {...},
    "timestamp": "..."
}
```

## Dependencies

### External Packages
- `fastmcp>=0.1.0` - MCP server framework
- `pydantic>=2.0` - Data validation
- `PyYAML>=6.0` - YAML parsing
- `anthropic>=0.8.0` - Claude SDK
- `click>=8.0` - CLI framework

### Internal Dependencies
- Agent configurations from `task-agents/` directory
- OAuth credentials from `.claude/` directory
- Python 3.11+ for all components

## Usage Examples

### Using MCP Server
```python
# Load and execute through MCP
from task_agents_mcp.server import main
main()  # Starts MCP server
```

### Using SDK Integration
```python
from sdk_integration import AgentExecutor

# Initialize executor
executor = AgentExecutor(agents_path="./task-agents")

# Stream agent response
async for chunk in executor.stream_agent_response(
    agent_name="analyst",
    message="Analyze this data",
    session_id="abc123"
):
    print(chunk)
```

## Environment Variables

- `TASK_AGENTS_PATH`: Custom agents directory
- `CLAUDE_EXECUTABLE_PATH`: Path to Claude CLI
- `PYTHONPATH`: Should include src directory

## Development Guidelines

### Adding New Features
1. SDK integration for direct execution
2. MCP server for protocol compliance
3. Both layers share agent configurations

### Testing Components
```bash
# Test MCP server
python -m task_agents_mcp.server

# Test SDK integration
python -c "from sdk_integration import AgentExecutor; print('OK')"

# Test agent loading
python -m task_agents_mcp.agent_manager
```

### Code Organization
- Keep MCP and SDK layers separate
- Share agent configuration models
- Maintain backward compatibility

## Important Constraints

1. **Python Version**: Requires 3.11+ for all components
2. **Agent Format**: Must use YAML frontmatter in `.md` files
3. **Tool Names**: Automatically sanitized (no manual control)
4. **Session Storage**: Ephemeral in `/tmp` directory
5. **OAuth Required**: SDK integration needs valid credentials

## Troubleshooting

### Import Errors
- Ensure `PYTHONPATH` includes src directory
- Check Python version is 3.11+

### Agent Loading Issues
- Verify `.md` files have valid YAML frontmatter
- Check `TASK_AGENTS_PATH` environment variable

### SDK Authentication
- Verify OAuth credentials exist and are valid
- Check file permissions on `.claude/` directory

## Related Documentation

- Main project: [/CLAUDE.md](/home/vredrick/task-agent/CLAUDE.md)
- Web UI: [/web-ui/CLAUDE.md](/home/vredrick/task-agent/web-ui/CLAUDE.md)
- PyPI Package: https://pypi.org/project/task-agents-mcp/