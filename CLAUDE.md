# CLAUDE.md - Task Agent Multi-Tool MCP Server

## 🎯 Quick Context

You're working with a **multi-tool MCP server** where each user-defined AI agent is exposed as its own tool. This is v4.3.0 with project-scoped MCP/skill isolation, enriched tool descriptions, and capabilities support.

### Key Architecture Points
- Each agent = separate MCP tool (e.g., `analyst`, `dev`, `qa`)
- No built-in agents - users define all agents
- Ships with `example-agent.md` template
- Tool names: lowercase with underscores (e.g., "Code Reviewer" → `code_reviewer`)
- Built on FastMCP with dynamic tool registration
- Python 3.11+ required

## 📁 Project Structure

```
task-agent/
├── src/task_agents_mcp/
│   ├── __init__.py          # Version: 4.3.0
│   ├── server.py            # Multi-tool MCP server (main entry)
│   ├── agent_manager.py     # Agent loader/executor
│   ├── resource_manager.py  # MCP resource registration
│   └── session_store.py     # Session management
├── task-agents/             # User agent configs (ships with example)
│   └── example-agent.md     # Template showing agent structure
├── pyproject.toml           # Package config (name: task-agents-mcp)
├── README.md                # User documentation
├── CLAUDE.md                # This file
└── MANIFEST.in              # Package manifest
```

## 🔧 Key Technical Details

### Package Info
- **PyPI Name**: `task-agents-mcp`
- **Command**: `task-agent` (no 's' at end!)
- **Current Version**: 4.3.0
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
  disallowed-tools: WebSearch, WebFetch
  capabilities:
    - Can send and read Slack messages
    - Can create and review GitHub PRs
---

System-prompt:
You are...
```

#### MCP Servers & Skills per Agent (Project-Scoped)
MCP servers and skills are isolated per agent via the agent's `cwd`. Configure from the agent's working directory:
```bash
cd /path/to/agent/cwd
claude mcp add slack-server npx slack-mcp -s project
```
This writes to `{cwd}/.claude/settings.json` — the agent subprocess picks it up automatically.

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

## 🎯 Key Changes

### What Changed (v4.3.0)
- **Removed**: `mcp-config` optional config field and `--mcp-config`/`--strict-mcp-config` CLI flags
- **Changed**: MCP servers and skills now isolated per agent via project-scoped settings in the agent's `cwd`
- **Changed**: MCP server discovery reads from `{cwd}/.claude/settings.json` + `settings.local.json`
- **Added**: `_resolve_agent_cwd()` helper for early cwd resolution at load time
- **Updated**: Users configure agent MCP/skills with `claude mcp add ... -s project` from the agent's cwd

### What Changed (v4.2.0)
- **Added**: `capabilities` optional config field — human-readable capability descriptions shown in tool description
- **Added**: MCP server auto-discovery — reads `mcp-config` JSON at load time, extracts server names
- **Added**: `mcp_server_names` field on `AgentConfig` — auto-populated from project-scoped settings
- **Added**: `build_tool_description()` helper in server.py — richer tool descriptions with capabilities + MCP servers
- **Updated**: Resource manager prefers config-defined capabilities over hardcoded BMad map

### What Changed (v4.1.0)
- **Replaced**: `--allowedTools` with `--tools` (comma-separated, explicit tool control)
- **Added**: `--name` flag auto-generated from agent name for session identification
- **Added**: `--include-partial-messages` for real-time token streaming via progress notifications
- **Added**: `disallowed-tools` optional config field with `--disallowed-tools` CLI flag

### What Changed (v4.0.0)
- **Removed**: Built-in agents directory (`src/task_agents_mcp/agents/`)
- **Removed**: Dual-directory loading logic
- **Added**: Example agent template in `task-agents/`
- **Simplified**: Only loads from one agents directory
- **Standardized**: Python 3.11+ requirement

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
- Sessions tagged with `--name` for identification in `/resume`

### CLI Flags Used by Agent Subprocess
```
claude -p "task" --output-format stream-json --verbose
       --include-partial-messages       # Real-time token streaming
       --tools Read,Write,Bash          # Comma-separated (replaces --allowedTools)
       --model sonnet
       --name agent_name                # Auto-generated from agent-name
       --disallowed-tools WebSearch     # Optional, from config
       --system-prompt "..."
       --append-system-prompt "..."
       -r <session_id>                  # When resuming
       --add-dir <path>                 # When resource_dirs set
       # MCP servers: inherited from {cwd}/.claude/settings.json (project-scoped)
```

## 🚨 Important Reminders

1. **Package name vs command**: 
   - Package: `task-agents-mcp` (with 's')
   - Command: `task-agent` (no 's')

2. **Python version**: Must use Python 3.11+

3. **Empty default**: Ships with only example template, not functional agents

4. **Project scope**: Recommend `-s project` for Claude Code

5. **Agent names**: Spaces become underscores in tool names

## 📚 Resources

- **GitHub**: https://github.com/vredrick/task-agent
- **PyPI**: https://pypi.org/project/task-agents-mcp/
- **MCP Docs**: https://modelcontextprotocol.io/
- **FastMCP**: https://github.com/jlowin/fastmcp