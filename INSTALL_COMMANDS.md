# Installation Commands for Testing BMad Agents

⚠️ **Python 3.10+ Required**: The package requires Python 3.10 or higher due to the fastmcp dependency.

## Option 1: Install from Source (Recommended for Testing)

```bash
# 1. Navigate to your Claude Code project where you want to test
cd /path/to/your/test-project

# 2. Install directly from PyPI (now published!)
python3.10 -m pip install task-agents-mcp
# or if you have Python 3.11+
python3.11 -m pip install task-agents-mcp

# 3. Add to Claude Code (project-specific)
claude mcp add task-agent task-agent -s project

# 4. Test the agents
claude "Show available agents using agents://list"
claude "Use analyst to brainstorm ideas for a todo app"
```

## Option 2: Local Development Install

```bash
# 1. Clone the repository
git clone https://github.com/vredrick/task-agent.git
cd task-agent
git checkout bmad-agents

# 2. Install in development mode (requires Python 3.10+)
python3.10 -m pip install -e .
# or
python3.11 -m pip install -e .

# 3. Add to Claude Code
claude mcp add task-agent task-agent -s project

# 4. Test the agents
claude "Show available agents using agents://list"
```

## Option 3: Install in Existing Project with BMad Resources

```bash
# 1. Install the package from PyPI
python3.10 -m pip install task-agents-mcp
# or
python3.11 -m pip install task-agents-mcp

# 2. Create BMad resource directory (optional, for full functionality)
mkdir -p bmad-core/tasks
mkdir -p bmad-core/templates
mkdir -p bmad-core/checklists
mkdir -p bmad-core/data

# 3. Add to Claude Code
claude mcp add task-agent task-agent -s project

# 4. Test BMad workflow
claude "Use analyst to research competitors for a task management app"
claude "Use pm to create a PRD based on the analysis"
claude "Use architect to design the system architecture"
```

## Quick Test Commands

Once installed, test the BMad agents:

```bash
# List all available agents
claude "Show available agents using agents://list"

# Test individual agents
claude "Use analyst to brainstorm ideas for an e-commerce platform"
claude "Use pm to create a PRD for a shopping cart feature"
claude "Use ux_expert to design UI for a checkout flow"
claude "Use architect to design API endpoints for user authentication"
claude "Use dev to explain how you would implement a login system"
claude "Use qa to review this code: def add(a, b): return a + b"

# Test the workflow
claude "Use analyst to research the market for a project management tool"
# Then follow up with:
claude "Use pm to create a PRD based on the analyst's research"
```

## Verify Installation

```bash
# Check if task-agent is available
which task-agent

# Check version (use Python 3.10+)
python3.10 -c "import task_agents_mcp; print(task_agents_mcp.__version__)"

# Check MCP configuration
cat .mcp.json

# Run server directly to see agents loading
task-agent
# Press Ctrl+C to stop
```

## Troubleshooting

If you encounter issues:

1. **"spawn task-agent ENOENT"**: Package not in PATH
   ```bash
   python3.10 -m pip uninstall task-agents-mcp
   python3.10 -m pip install task-agents-mcp
   ```

2. **"ResolutionImpossible" error**: Using Python < 3.10
   ```bash
   # Check your Python version
   python3 --version
   # If less than 3.10, use python3.10 or python3.11 explicitly
   python3.10 -m pip install task-agents-mcp
   ```

3. **Agents not showing up**: Check the installation
   ```bash
   python3.10 -m pip show task-agents-mcp
   ```

4. **Permission denied**: Claude Code needs approval
   - Claude will prompt you to approve the MCP server
   - Select "Approve" when prompted

## Notes

- BMad agents expect a `./bmad-core` directory with resources (templates, tasks, etc.)
- Without BMad resources, agents will still work but with limited functionality
- All agents use session resumption for context preservation
- The workflow is: analyst → pm → ux_expert → architect → po → sm → dev → qa