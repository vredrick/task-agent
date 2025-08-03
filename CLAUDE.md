# CLAUDE.md - Task Agent Multi-Tool MCP Server

## 🎯 Quick Context

You're working with a **multi-tool MCP server** where each AI agent is exposed as its own tool. This is NOT the single-tool version (that's a separate repo).

### Key Architecture Points
- Each agent = separate MCP tool (e.g., `code_reviewer`, `debugger`)
- No routing/delegate function - direct tool invocation
- Tool names: lowercase with underscores (e.g., "Code Reviewer" → `code_reviewer`)
- Built on FastMCP with dynamic tool registration

## 📁 Project Structure

```
task-agent/
├── src/task_agents_mcp/
│   ├── __init__.py          # Version: 2.4.2
│   ├── server.py            # Multi-tool MCP server (main entry)
│   └── agent_manager.py     # Agent loader/executor (unchanged from single-tool)
├── task-agents/             # Built-in agent configs
│   ├── code-reviewer.md
│   ├── debugger.md
│   ├── default-assistant.md
│   ├── documentation-writer.md
│   ├── performance-optimizer.md
│   └── test-runner.md
├── pyproject.toml           # Package config (name: task-agents-mcp)
├── README.md                # User documentation
└── CLAUDE.md                # This file
```

## 🔧 Key Technical Details

### Package Info
- **PyPI Name**: `task-agents-mcp`
- **Command**: `task-agent` (no 's' at end!)
- **Current Version**: 2.4.2
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
python3.11 -m pip install task-agents-mcp

# Or from source
python3.11 -m pip install -e /path/to/task-agent
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
# Quick test
claude "Use code_reviewer to analyze this: def add(a, b): return a + b"

# List all agents
claude "Show available agents using agents://list"
```

## 🐛 Known Issues & Fixes

### 1. "spawn task-agent ENOENT"
- **Cause**: Package not installed or not in PATH
- **Fix**: Install with `python3.11 -m pip install task-agents-mcp`

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
3. Test locally: `python3.11 -m pip install -e .`
4. Test with Claude Code: `claude "Use code_reviewer..."`

### Publishing to PyPI
```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build
python3.11 -m build

# Upload
python3.11 -m twine upload dist/*
```

### Version History Notes
- 2.4.0: Removed CLAUDE_EXECUTABLE_PATH requirement
- 2.4.2: Fixed `claude mcp add` documentation

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

## 🔍 Quick Debugging Commands

```bash
# Check if installed
which task-agent

# Check Python version
python3 --version  # Need 3.10+

# Test server directly
task-agent

# Check package version
python3 -c "import task_agents_mcp; print(task_agents_mcp.__version__)"

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