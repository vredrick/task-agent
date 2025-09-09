# CLAUDE.md - Task Agent Multi-Tool MCP Server

## 🎯 Quick Context

You're working with a **multi-tool MCP server** where each user-defined AI agent is exposed as its own tool. This is v4.0.0 with simplified architecture - no built-in agents, only user-defined ones. **NEW**: Web UI with direct SDK integration for browser-based agent interaction!

### Key Architecture Points
- Each agent = separate MCP tool (e.g., `analyst`, `dev`, `qa`)
- No built-in agents - users define all agents
- Ships with `example-agent.md` template
- Tool names: lowercase with underscores (e.g., "Code Reviewer" → `code_reviewer`)
- Built on FastMCP with dynamic tool registration
- Python 3.11+ required
- **Web UI**: React frontend + FastAPI backend with WebSocket streaming
- **SDK Integration**: Direct agent execution without MCP overhead

## 📁 Project Structure

```
task-agent/
├── src/                     
│   ├── task_agents_mcp/     # MCP server implementation
│   │   ├── __init__.py      # Version: 4.0.0
│   │   ├── server.py        # Multi-tool MCP server (main entry)
│   │   ├── agent_manager.py # Agent loader/executor
│   │   ├── resource_manager.py # MCP resource registration
│   │   └── session_store.py # Session management
│   └── sdk_integration/     # Direct SDK execution layer
│       ├── agent_executor.py # High-level agent management
│       └── sdk_executor.py  # Claude SDK integration
├── web-ui/                  # Web interface (NEW!)
│   ├── backend/            # FastAPI + WebSocket server
│   └── frontend/           # React + TypeScript UI
├── task-agents/            # User agent configs (ships with example)
│   └── example-agent.md    # Template showing agent structure
├── pyproject.toml          # Package config (name: task-agents-mcp)
├── README.md               # User documentation
├── CLAUDE.md               # This file
└── MANIFEST.in             # Package manifest
```

## 🔧 Key Technical Details

### Package Info
- **PyPI Name**: `task-agents-mcp`
- **Command**: `task-agent` (no 's' at end!)
- **Current Version**: 4.0.0
- **Entry Point**: `task_agents_mcp.server:main`
- **Python Requirement**: 3.11+

### Tool Registration Flow
```python
# server.py - Simplified logic
for agent_name, agent_config in agent_manager.agents.items():
    tool_func = create_agent_tool_function(agent_config.agent_name, agent_config)
    tool_name = sanitize_tool_name(agent_config.agent_name)  # spaces→underscores, lowercase
    mcp.tool(name=tool_name)(tool_func)
```

### Environment Variables
- `TASK_AGENTS_PATH`: Custom agents directory
  - Claude Code: Optional (defaults to `./task-agents`)
  - Claude Desktop: Set to your agents directory
- `CLAUDE_EXECUTABLE_PATH`: Auto-detected from PATH

### Agent Loading
```python
# Only loads from one directory now:
config_dir = os.environ.get('TASK_AGENTS_PATH') or './task-agents'
agent_manager = AgentManager(config_dir)
agent_manager.load_agents()
```

## 🌐 Web UI (NEW!)

### Quick Start
```bash
cd web-ui
./start.sh  # Starts both backend and frontend
# Open http://localhost:5173 in your browser
```

### Features
- Visual agent selection interface with card-based layout
- Real-time streaming chat with word-by-word animation (40ms/word)
- Rich markdown rendering with syntax-highlighted code blocks
- Tool usage visualization with dark blue accent theme
- Session management with reset capability
- Direct SDK integration (no MCP overhead)
- Custom AI Elements components for professional UI
- Smooth text streaming that fills processing gaps

## 📝 Common User Tasks

### Installation
```bash
# Must use Python 3.11 or higher
python3.11 -m pip install task-agents-mcp

# Add to Claude Code
claude mcp add task-agent task-agent -s project
```

### Creating Agents
Users create `.md` files in `task-agents/` directory:
```markdown
---
agent-name: My Agent
description: What it does
tools: Read, Grep, Bash
model: opus
cwd: .
optional:
  resume-session: true 10
  resource_dirs: ./data
---

System-prompt:
You are...
```

### Testing
```bash
# Test with example agent
claude "Use example_agent to explain how agents work"

# Test custom agent
claude "Use my_agent to perform task"
```

## 🐛 Known Issues & Fixes

### 1. "No agents loaded!"
- **Cause**: No `.md` files in agents directory
- **Fix**: Add agent files to `task-agents/` or set `TASK_AGENTS_PATH`

### 2. "spawn task-agent ENOENT"
- **Cause**: Package not installed or wrong Python version
- **Fix**: Install with Python 3.11: `python3.11 -m pip install task-agents-mcp`

### 3. Agent names with spaces
- **Note**: "Code Reviewer" becomes tool `code_reviewer`
- **Resource URI**: "Code-Reviewer://" (spaces become hyphens)

## 🚀 Development Workflow

### Making Changes
1. Edit source files in `src/task_agents_mcp/`
2. Update version in both:
   - `pyproject.toml`
   - `src/task_agents_mcp/__init__.py`
3. Test locally: `python3.11 -m pip install -e .`
4. Test with Claude Code: `claude "Use example_agent..."`

### Testing Without Installing
```bash
# Run directly from source
python3.11 -c "import sys; sys.path.insert(0, '.'); from src.task_agents_mcp.server import main; main()"
```

### Publishing to PyPI
```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build (requires Python 3.11+)
python3.11 -m build

# Upload
python3.11 -m twine upload dist/*
```

## 🎯 Key Changes in v4.0.0

### What Changed
- **Removed**: Built-in agents directory (`src/task_agents_mcp/agents/`)
- **Removed**: Dual-directory loading logic
- **Added**: Example agent template in `task-agents/`
- **Simplified**: Only loads from one agents directory
- **Standardized**: Python 3.11+ requirement

### Migration from v3.x
Users upgrading from v3.x need to:
1. Copy any BMad agents they want from examples
2. Place them in their `task-agents/` directory
3. No other changes needed

## 💡 Implementation Details

### Agent Discovery
1. Server checks `TASK_AGENTS_PATH` or defaults to `./task-agents`
2. Loads all `.md` files with valid YAML frontmatter
3. Registers each as an MCP tool
4. Shows helpful messages if no agents found

### Resource URI Sanitization
Agent names are sanitized for URI format:
```python
# "Example Agent" → "Example-Agent://"
sanitized_name = agent_config.agent_name.replace(' ', '-')
resource_uri = f"{sanitized_name}://"
```

### Session Management
- Sessions stored in `/tmp/task_agents_sessions.json`
- Each agent can maintain conversation context
- `session_reset` parameter available for agents with `resume-session: true`

## 🚨 Important Reminders

1. **Package name vs command**: 
   - Package: `task-agents-mcp` (with 's')
   - Command: `task-agent` (no 's')

2. **Python version**: Must use Python 3.11+

3. **Empty default**: Ships with only example template, not functional agents

4. **Project scope**: Recommend `-s project` for Claude Code

5. **Agent names**: Spaces become underscores in tool names

## 📍 Navigation Guide

### Subdirectory Documentation
For detailed information about specific components, see:

- **[/src/CLAUDE.md](/home/vredrick/task-agent/src/CLAUDE.md)** - Source code documentation
  - MCP server implementation details
  - SDK integration layer architecture
  - Agent management and execution flow
  - Session handling and persistence

- **[/web-ui/CLAUDE.md](/home/vredrick/task-agent/web-ui/CLAUDE.md)** - Web UI documentation
  - Frontend React architecture
  - Backend FastAPI implementation
  - WebSocket streaming protocol
  - Development and deployment guide

### Quick Navigation by Task

**Want to understand the MCP server?**
→ See `/src/CLAUDE.md` for server implementation

**Working on the Web UI?**
→ See `/web-ui/CLAUDE.md` for frontend/backend details

**Need SDK integration details?**
→ Check `/src/CLAUDE.md` SDK Integration section

**Setting up agent configurations?**
→ Review agent format in this file and examples in `task-agents/`

## 📚 Resources

- **GitHub**: https://github.com/vredrick/task-agent
- **PyPI**: https://pypi.org/project/task-agents-mcp/
- **MCP Docs**: https://modelcontextprotocol.io/
- **FastMCP**: https://github.com/jlowin/fastmcp