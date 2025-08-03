# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚀 Task Agent

This is the multi-tool version of task-agent where each AI agent is exposed as its own MCP tool, providing direct access to specialized agents without routing through a delegate function.

## Overview

Task Agent is a Model Context Protocol (MCP) server that exposes specialized AI agents as individual tools. Each agent (code reviewer, debugger, test runner, etc.) appears as a separate tool in MCP clients like Claude Desktop.

### Key Differences from Single-Tool Version
- **Direct Tool Access**: Each agent is its own tool (e.g., `code_reviewer`, `debugger`)
- **Better Discoverability**: All agents visible in tool list
- **No Routing Layer**: Direct invocation without delegate function
- **Simplified Usage**: No need to specify agent parameter

## Available Tools

The server exposes these individual tools:
- `code_reviewer` - Expert code review for quality and security
- `debugger` - Bug identification and fixing specialist
- `default_assistant` - General-purpose development tasks
- `documentation_writer` - Technical documentation creation
- `performance_optimizer` - Code efficiency analysis
- `test_runner` - Test automation and coverage

## Commands

### Running the Server
```bash
# Direct execution
python server.py

# With environment setup
export TASK_AGENTS_PATH=/path/to/task-agents
export CLAUDE_EXECUTABLE_PATH=/path/to/claude
python server.py
```

### Adding to Claude Desktop
```json
{
  "mcpServers": {
    "task-agent": {
      "command": "python3.11",
      "args": ["/path/to/server.py"],
      "env": {
        "TASK_AGENTS_PATH": "/path/to/task-agents",
        "CLAUDE_EXECUTABLE_PATH": "/path/to/claude"
      }
    }
  }
}
```

## Architecture

### Core Components

1. **Multi-Tool Server (`server.py`)**
   - FastMCP server with dynamic tool registration
   - Creates individual tool function for each agent
   - Maintains same resources and prompts as single-tool version
   - Tool names use snake_case (e.g., `code_reviewer`)

2. **Agent Manager (`agent_manager.py`)**
   - Unchanged from single-tool version
   - Loads agent configurations from markdown files
   - Executes tasks via Claude Code CLI
   - Handles working directory resolution

3. **Agent Configurations (`task-agents/*.md`)**
   - Same format as single-tool version
   - No changes needed to agent files
   - Each agent automatically gets its own tool

### Implementation Details

```python
# Tool Registration (simplified)
for agent_name, agent_config in agent_manager.agents.items():
    tool_func = create_agent_tool_function(agent_config.agent_name, agent_config)
    tool_name = sanitize_tool_name(agent_config.agent_name)
    mcp.tool(name=tool_name)(tool_func)
```

### Tool Name Mapping
- Spaces replaced with underscores
- Lowercase conversion
- Examples: "Code Reviewer" → `code_reviewer`

## Usage Examples

### In Claude Desktop
```
"Use the code_reviewer tool to analyze my Python module"
"Run debugger on the authentication error"
"Have test_runner check my test coverage"
```

### Direct Tool Invocation
Each tool accepts a single `prompt` parameter:
```typescript
await mcp.use_tool("code_reviewer", {
  prompt: "Review the security of user authentication"
})
```

## Environment Variables

- `TASK_AGENTS_PATH`: Path to task-agents directory (optional)
- `CLAUDE_EXECUTABLE_PATH`: Path to Claude CLI (required for Claude Desktop)

## Development Notes

### Adding New Agents
1. Create `.md` file in task-agents directory
2. Restart server - new tool automatically registered
3. Tool name derived from `agent-name` field

### Testing
```bash
# Test server startup
python server.py

# Should show all registered tools:
# - code_reviewer
# - debugger
# - default_assistant
# etc.
```

### Key Files
- `server.py` - Multi-tool MCP server
- `agent_manager.py` - Agent execution engine (unchanged)
- `task-agents/*.md` - Agent configurations (unchanged)

## Advantages of Multi-Tool Architecture

1. **Immediate Discovery**: All agents visible in tool list
2. **Direct Access**: No intermediate routing
3. **Type Safety**: Each tool has specific documentation
4. **Intuitive Usage**: Tool name indicates purpose
5. **No Parameter Errors**: Can't misspell agent names

## When to Use This Version

Use the multi-tool version when:
- You have a manageable number of agents (< 10)
- Tool discovery is important
- Direct access is preferred
- Working with Claude Desktop primarily

The single-tool version (separate repo) is better when:
- You have many agents (10+)
- Want a cleaner tool list
- Need flexible agent naming
- Prefer centralized routing