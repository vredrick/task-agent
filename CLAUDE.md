# CLAUDE.md - Task Agent Multi-Tool MCP Server

## 🎯 Quick Context

You're working with a **multi-tool MCP server** where each AI agent is exposed as its own tool. This is NOT the single-tool version (that's a separate repo).

### Key Architecture Points
- Each agent = separate MCP tool (e.g., `analyst`, `dev`, `qa`)
- No routing/delegate function - direct tool invocation
- Tool names: lowercase with underscores (e.g., "ux-expert" → `ux_expert`)
- Built on FastMCP with dynamic tool registration
- BMad methodology agents for complete development workflow

## 📁 Project Structure

```
task-agent/
├── src/task_agents_mcp/
│   ├── __init__.py          # Version: 2.4.2
│   ├── server.py            # Multi-tool MCP server (main entry)
│   └── agent_manager.py     # Agent loader/executor (unchanged from single-tool)
├── task-agents/             # Built-in agent configs (BMad agents)
│   ├── analyst.md           # Business Analyst
│   ├── pm.md                # Product Manager
│   ├── ux-expert.md         # UX Designer
│   ├── architect.md         # Solution Architect
│   ├── po.md                # Product Owner
│   ├── sm.md                # Scrum Master
│   ├── dev.md               # Full Stack Developer
│   ├── qa.md                # Senior Dev & QA
│   ├── default-assistant.md # General assistant
│   └── session-tester.md    # Session testing
├── pyproject.toml           # Package config (name: task-agents-mcp)
├── README.md                # User documentation
└── CLAUDE.md                # This file
```

## 🔧 Key Technical Details

### Package Info
- **PyPI Name**: `task-agents-mcp`
- **Command**: `task-agent` (no 's' at end!)
- **Current Version**: 2.8.0
- **Entry Point**: `task_agents_mcp.server:main`

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
  - Claude Desktop: Required for custom agents
- `CLAUDE_EXECUTABLE_PATH`: Auto-detected from PATH

### Claude CLI Detection (agent_manager.py)
```python
# Searches in order:
1. Environment variable CLAUDE_EXECUTABLE_PATH
2. System PATH (using shutil.which)
3. Common installation paths:
   - macOS: /usr/local/bin/claude, ~/bin/claude
   - Linux: /usr/local/bin/claude, ~/.local/bin/claude
   - Windows: %LOCALAPPDATA%/claude/claude.exe
```

## 📝 Common User Tasks

### Installation Issues
```bash
# User reports "spawn task-agent ENOENT"
# Must use Python 3.10 or higher
python3.10 -m pip install task-agents-mcp
# or
python3.11 -m pip install task-agents-mcp

# Or from source
python3.10 -m pip install -e /path/to/task-agent
```

### Adding to Claude Code
```bash
# Correct syntax (needs both name and command)
claude mcp add task-agent task-agent -s project

# Creates .mcp.json:
{
  "mcpServers": {
    "task-agent": {
      "command": "task-agent",
      "args": [],
      "env": {}
    }
  }
}
```

### Testing
```bash
# Quick test with BMad agents
claude "Use analyst to brainstorm ideas for a todo app"

# Test the full workflow
claude "Use pm to create a PRD for a shopping cart feature"

# List all agents
claude "Show available agents using agents://list"
```

## 🐛 Known Issues & Fixes

### 1. "spawn task-agent ENOENT"
- **Cause**: Package not installed or not in PATH
- **Fix**: Install with Python 3.10+: `python3.10 -m pip install task-agents-mcp`

### 2. "missing required argument 'commandOrUrl'"
- **Cause**: Wrong `claude mcp add` syntax in docs
- **Fix**: Use `claude mcp add task-agent task-agent -s project`

### 3. Custom agents not loading
- **Claude Code**: Check `task-agents/` exists in project root
- **Claude Desktop**: Must set `TASK_AGENTS_PATH` env var

## 🚀 Development Workflow

### Making Changes
1. Edit source files in `src/task_agents_mcp/`
2. Update version in both:
   - `pyproject.toml`
   - `src/task_agents_mcp/__init__.py`
3. Test locally: `python3.10 -m pip install -e .` (or python3.11)
4. Test with Claude Code: `claude "Use code_reviewer..."`

### Publishing to PyPI
```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build (requires Python 3.10+)
python3.10 -m build

# Upload
python3.10 -m twine upload dist/*
```

### Version History Notes
- 2.9.0: Session reset parameter for agents with resume-session
- 2.8.0: Dynamic resource path resolution, improved agent initialization
- 2.7.0: Interactive protocols for all BMad agents
- 2.6.0: Python 3.10+ requirement, BMad agents
- 2.5.0: Session resumption support
- 2.4.2: Fixed `claude mcp add` documentation
- 2.4.0: Removed CLAUDE_EXECUTABLE_PATH requirement

## 🎯 Key Differences from Single-Tool Version

| Aspect | Multi-Tool (This) | Single-Tool |
|--------|-------------------|-------------|
| Tools | One per agent | One total |
| Usage | Direct: `code_reviewer` | Via delegate |
| Config | No agent param | Needs agent name |
| Discovery | Immediate in tool list | Via description |

## 💡 Implementation Tips

### When Users Want Custom Agents
1. Tell them to create `task-agents/` in project root
2. Agent file format:
   ```markdown
   ---
   agent-name: My Agent
   description: What it does
   tools: Read, Grep, Bash
   model: opus
   cwd: .
   ---
   
   System-prompt:
   You are...
   ```
3. Tool name will be `my_agent` (auto-converted)

### Common Customizations Users Ask For
- New agent types → Add .md file to task-agents/
- Different models → Change `model:` in agent config
- Tool restrictions → Modify `tools:` list
- Working directory → Adjust `cwd:` setting
- Resource access → Add `resource_dirs:` for additional directories

## 🚨 BMad Agents Overview

The project now includes BMad methodology agents for complete development workflow:

### Agent Workflow Pipeline
```
analyst → pm → ux_expert → architect → po → sm → dev → qa
```

### Key Features
- **Each agent has specific persona**: Defined roles and responsibilities
- **Resource directories**: All BMad agents access `./bmad-core` resources
- **Model optimization**: Strategic agents use opus, tactical use sonnet
- **Session resumption**: Configured exchanges per agent role
- **Structured workflow**: Clear handoffs between agents

### Agent Configurations
| Agent | Model | Exchanges | Purpose |
|-------|-------|-----------|---------|
| analyst | opus | 15 | Discovery & research |
| pm | opus | 15 | Product requirements |
| ux_expert | opus | 15 | UI/UX design |
| architect | opus | 15 | Technical design |
| po | sonnet | 5 | Validation & sharding |
| sm | sonnet | 5 | Story creation |
| dev | sonnet | 8 | Implementation |
| qa | sonnet | 8 | Review & refactoring |

### Resource Directories Feature (Enhanced in v2.8.0)
Agents can access additional directories via `resource_dirs`:
```yaml
optional:
  resource_dirs: ./.bmad-core  # Hidden directory (with dot prefix)
  # OR
  resource_dirs: ./templates, ./data  # Multiple directories
```

**v2.8.0 Improvements**:
- Dynamic path resolution - agents informed of actual paths at runtime
- Automatic `--add-dir` flags for all configured resource directories
- Better error reporting when resources are missing
- Support for hidden directories (e.g., `.bmad-core`)
- Agent system prompts updated to use `[resource_dir]` placeholders

### Session Management Features (v2.9.0)

#### Session Resumption
Agents can maintain context across multiple exchanges:
```yaml
optional:
  resume-session: true      # 5 exchanges (default)
  resume-session: true 10   # 10 exchanges  
  resume-session: false     # Disabled
```

#### Session Reset Parameter (NEW in v2.9.0)
For agents with `resume-session: true`, a `session_reset` parameter is available:

**Usage in Claude:**
```python
# Normal call - maintains session context
analyst(prompt="Continue our analysis")

# Reset session - starts fresh
analyst(prompt="Start new analysis", session_reset=True)
```

**Key Features:**
- Only appears for agents with session support
- Default: `session_reset=False` (maintains session)
- When `True`: Clears session history before execution
- Useful when user wants to start fresh with an agent

**Example Scenario:**
```
User: "Reset the analyst session and start analyzing a new project"
Claude: [Calls analyst with session_reset=True]
```

## 🔍 Quick Debugging Commands

```bash
# Check if installed
which task-agent

# Check Python version
python3 --version  # Must be 3.10+
# If less than 3.10, use python3.10 or python3.11 explicitly

# Test server directly
task-agent

# Check package version (use Python 3.10+)
python3.10 -c "import task_agents_mcp; print(task_agents_mcp.__version__)"

# See MCP config
cat .mcp.json
```

## ⚠️ Important Reminders

1. **Package name vs command**: 
   - Package: `task-agents-mcp` (with 's')
   - Command: `task-agent` (no 's')

2. **Claude Code priority**: This project prioritizes Claude Code CLI over Claude Desktop

3. **No CLAUDE_EXECUTABLE_PATH needed**: Auto-detects from v2.4.0+

4. **Project vs global scope**: Recommend project scope for Claude Code (`-s project`)

5. **Security**: Claude Code prompts for approval on project-scoped servers

## 📚 Resources

- **GitHub**: https://github.com/vredrick/task-agent
- **PyPI**: https://pypi.org/project/task-agents-mcp/
- **MCP Docs**: https://modelcontextprotocol.io/
- **FastMCP**: https://github.com/jlowin/fastmcp