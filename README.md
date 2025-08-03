# Task Agent MCP Server

A Model Context Protocol (MCP) server that exposes specialized AI agents as individual tools. Each agent (code reviewer, debugger, test runner, etc.) appears as a separate tool in MCP clients, providing direct access to specialized capabilities.

## Overview

Task Agent gives you a team of specialized AI agents, each accessible as its own tool:
- **Direct Access**: Each agent is a separate tool (`code_reviewer`, `debugger`, etc.)
- **Better Discovery**: All agents immediately visible in tool lists
- **Specialized Capabilities**: Each agent has focused tools and instructions
- **No Routing**: Direct invocation without intermediate delegate function

### Available Agent Tools

| Tool Name | Purpose | Specialized For |
|-----------|---------|-----------------|
| `code_reviewer` | Code quality & security analysis | Pull requests, security audits |
| `debugger` | Bug identification & fixing | Error diagnosis, debugging |
| `default_assistant` | General development tasks | Versatile coding help |
| `documentation_writer` | Technical documentation | API docs, guides, READMEs |
| `performance_optimizer` | Performance analysis | Optimization, efficiency |
| `test_runner` | Test automation | Test creation, coverage |

## Installation

### From PyPI

```bash
# Requires Python 3.10 or higher
python3.11 -m pip install task-agents-mcp

# Or if you have Python 3.10+ as your default python3:
pip install task-agents-mcp
```

### From Source

```bash
git clone https://github.com/vredrick/task-agent.git
cd task-agent
python3.11 -m pip install -e .
```

## Quick Start

### For Claude Desktop

1. If installed from PyPI:
   ```json
   {
     "mcpServers": {
       "task-agent": {
         "command": "task-agent"
       }
     }
   }
   ```

2. If running from source:
   ```bash
   git clone https://github.com/vredrick/task-agent.git
   cd task-agent
   ```

   Add to Claude Desktop config:
   ```json
   {
     "mcpServers": {
       "task-agent": {
         "command": "python3.11",
         "args": ["/path/to/task-agent/server.py"],
         "env": {
           "TASK_AGENTS_PATH": "/path/to/task-agent/task-agents",
           "CLAUDE_EXECUTABLE_PATH": "/path/to/claude"
         }
       }
     }
   }
   ```

Restart Claude Desktop and use the tools:
   - "Use code_reviewer to analyze my authentication module"
   - "Run debugger on this error message"
   - "Have test_runner create unit tests"

### For Claude Code CLI

#### Option 1: Using PyPI Package (Recommended)

```bash
# Add to project scope
claude mcp add task-agent -s project -- task-agent

# Or add globally
claude mcp add task-agent -- task-agent
```

#### Option 2: From Source

```bash
# Clone and navigate to project
git clone https://github.com/vredrick/task-agent.git
cd task-agent

# Add to project scope
claude mcp add task-agent -s project -- python3.11 server.py
```

This creates a `.mcp.json` file in your project root:

```json
{
  "mcpServers": {
    "task-agent": {
      "command": "python3.11",
      "args": ["server.py"],
      "env": {}
    }
  }
}
```

**Note**: Claude Code will prompt for approval when using project-scoped servers for security.

## How It Works

### Architecture

```
┌─────────────────┐     ┌──────────────────┐
│  Claude Desktop │     │  Claude Code CLI  │
└────────┬────────┘     └────────┬─────────┘
         │                       │
         └───────────┬───────────┘
                     │
            ┌────────▼────────┐
            │  MCP Server     │
            │ (Multi-Tool)    │
            └────────┬────────┘
                     │
       ┌─────────────┴─────────────┐
       │                           │
┌──────▼──────┐           ┌────────▼────────┐
│code_reviewer│           │    debugger     │
└──────┬──────┘           └────────┬────────┘
       │                           │
       └─────────┬─────────────────┘
                 │
         ┌───────▼────────┐
         │ Agent Manager  │
         │ (Unchanged)    │
         └───────┬────────┘
                 │
         ┌───────▼────────┐
         │ Claude CLI     │
         │ Execution      │
         └────────────────┘
```

### Key Components

1. **Multi-Tool Server** (`server.py`)
   - Registers each agent as a separate MCP tool
   - Maintains tool name mapping (spaces to underscores)
   - Preserves all resources and prompts

2. **Agent Manager** (`agent_manager.py`)
   - Loads agent configurations
   - Executes via Claude Code CLI
   - Unchanged from single-tool version

3. **Agent Configurations** (`task-agents/*.md`)
   - Markdown files with YAML frontmatter
   - Define agent behavior and capabilities
   - No changes needed for multi-tool

### Tool Registration

```python
# Simplified registration logic
for agent_name, agent_config in agent_manager.agents.items():
    tool_name = agent_name.lower().replace(' ', '_')
    mcp.tool(name=tool_name)(create_agent_function(agent_config))
```

## Creating Custom Agents

1. Create a new file in `task-agents/`:
   ```markdown
   ---
   agent-name: Security Auditor
   description: Security vulnerability detection specialist
   tools: Read, Grep, Search, Bash
   model: opus
   cwd: .
   ---
   
   System-prompt:
   You are a security specialist focused on finding vulnerabilities...
   ```

2. Restart the server
3. New tool `security_auditor` is automatically available

## Features

### 🎯 Individual Tools
Each agent appears as its own tool with:
- Specific documentation
- Direct invocation
- No agent parameter needed

### 📚 Rich Resources
Query `agents://list` to see:
- All available agents
- Their capabilities
- Usage examples
- Tool metadata

### 📝 Agent-Specific Prompts
Pre-configured prompts for each agent:
- `code_reviewer_task`
- `debugger_task`
- `documentation_writer_task`
- etc.

### 🔧 Flexible Configuration
- Custom system prompts
- Tool restrictions per agent
- Model selection (Opus/Sonnet/Haiku)
- Working directory control

## Comparison with Single-Tool Version

| Feature | Multi-Tool | Single-Tool |
|---------|------------|-------------|
| Tool Count | One per agent | One total |
| Discovery | Immediate | Via description |
| Usage | Direct tool | delegate + agent param |
| Best For | <10 agents | Many agents |

## Advanced Usage

### Environment Variables

- `TASK_AGENTS_PATH`: Path to task-agents directory
- `CLAUDE_EXECUTABLE_PATH`: Path to Claude executable (required for Claude Desktop)

### Working Directory Resolution

- `cwd: .` - Parent of task-agents folder
- `cwd: /absolute/path` - Specific directory
- `cwd: ${HOME}/projects` - With env variables

### Adding to Existing Projects

```bash
# Copy task-agents folder to your project
cp -r task-agents /your/project/

# Agents will work in your project directory
```

## Troubleshooting

### Server won't start
- Check Python version (3.9+ required)
- Verify task-agents directory exists
- Check file permissions

### Tools not appearing
- Restart Claude Desktop
- Check server logs: `/tmp/task_agents_server.log`
- Verify agent files have correct YAML frontmatter

### Agent execution fails
- Ensure Claude Code CLI is installed
- Check CLAUDE_EXECUTABLE_PATH for Claude Desktop
- Verify agent has required tools in config

## Contributing

1. Fork the repository
2. Create new agent configurations
3. Test with both Claude Desktop and CLI
4. Submit pull request

## License

MIT License - see LICENSE file

## Acknowledgments

Built on:
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [Model Context Protocol](https://github.com/anthropics/mcp) - Anthropic's MCP
- Claude Code CLI - Agent execution engine