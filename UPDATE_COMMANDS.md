# Updating Task-Agents-MCP

## Quick Update Command

To update to the latest version without reinstalling:

```bash
# Update to latest version from PyPI
python3.11 -m pip install --upgrade task-agents-mcp

# Or with Python 3.10
python3.10 -m pip install --upgrade task-agents-mcp
```

## Check Current Version

```bash
# Check installed version
python3.11 -c "import task_agents_mcp; print(task_agents_mcp.__version__)"
```

## Update from Specific Branch (Development)

If you want to test the latest development version from GitHub:

```bash
# Update from specific branch
python3.11 -m pip install --upgrade git+https://github.com/vredrick/task-agent.git@bmad-agents

# Or from main branch
python3.11 -m pip install --upgrade git+https://github.com/vredrick/task-agent.git
```

## Force Reinstall (if having issues)

```bash
# Uninstall and reinstall
python3.11 -m pip uninstall task-agents-mcp -y
python3.11 -m pip install task-agents-mcp
```

## Update in Claude Code Project

After updating the package, restart Claude Code to load the new version:

```bash
# 1. Update the package
python3.11 -m pip install --upgrade task-agents-mcp

# 2. Verify the update
python3.11 -c "import task_agents_mcp; print(f'Updated to version {task_agents_mcp.__version__}')"

# 3. Test the updated agents
claude "Show available agents using agents://list"
```

## Version History

- **2.9.0**: Session reset parameter for agents with resume-session support
- **2.8.0**: Dynamic resource path resolution, improved agent initialization
- **2.7.0**: Interactive protocols for all BMad agents
- **2.6.0**: Python 3.10+ requirement, BMad agents
- **2.5.0**: Session resumption support
- **2.4.3**: MCP server fixes
- **2.4.0**: Removed CLAUDE_EXECUTABLE_PATH requirement

## Troubleshooting Updates

### If update fails with dependency conflicts:
```bash
# Use --force-reinstall
python3.11 -m pip install --force-reinstall task-agents-mcp
```

### If agents don't reflect updates:
1. Restart Claude Code completely
2. Clear any cached MCP configurations
3. Re-add the MCP server if needed:
   ```bash
   claude mcp add task-agent task-agent -s project
   ```

### Check what version is actually running:
```bash
# Run the server directly to see version
task-agent --version 2>/dev/null || echo "Version flag not supported, check logs"

# Or check in Python
python3.11 -c "import task_agents_mcp; print(task_agents_mcp.__version__)"
```

## Automatic Update Check (Future Feature)

You can add this to your shell profile for update reminders:

```bash
# Add to ~/.bashrc or ~/.zshrc
check_task_agents_update() {
    local current=$(python3.11 -c "import task_agents_mcp; print(task_agents_mcp.__version__)" 2>/dev/null)
    local latest=$(pip index versions task-agents-mcp 2>/dev/null | grep "task-agents-mcp" | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
    if [ "$current" != "$latest" ]; then
        echo "Task-agents-mcp update available: $current → $latest"
        echo "Run: python3.11 -m pip install --upgrade task-agents-mcp"
    fi
}
```