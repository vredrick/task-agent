# Claude Code Slash Command: /task-agents

This file contains a Claude Code slash command that creates the `task-agents` directory with all default agent configurations.

## Installation

1. Create the commands directory in your project:
   ```bash
   mkdir -p .claude/commands
   ```

2. Copy this file to `.claude/commands/task-agents.md`:
   ```bash
   cp task-agents-command.md .claude/commands/task-agents.md
   ```

3. Use the command in Claude Code:
   ```
   /task-agents
   ```

## Command Source

```markdown
---
description: Create task-agents directory with default agent configurations in your project
allowed-tools: Bash, Write
---

Create the task-agents directory with all default agent configurations in your current project.

!echo "🤖 Initializing task-agents directory for your project..."
!
!# Create task-agents directory in current project
!mkdir -p task-agents
!
!# Try to find Python with task-agents-mcp installed
!PYTHON_CMD=""
!for PY in python3.11 python3.12 python3.10 python3 python; do
!    if command -v $PY >/dev/null 2>&1; then
!        if $PY -c "import task_agents_mcp" 2>/dev/null; then
!            PYTHON_CMD=$PY
!            break
!        fi
!    fi
!done
!
!if [ -z "$PYTHON_CMD" ]; then
!    echo "❌ Error: task-agents-mcp package not found in any Python installation."
!    echo ""
!    echo "Please install it with one of these commands:"
!    echo "  python3.10 -m pip install task-agents-mcp  # Requires Python 3.10+"
!    echo "  python3.11 -m pip install task-agents-mcp"
!    echo "  pip install task-agents-mcp"
!    exit 1
!fi
!
!echo "📦 Found task-agents-mcp using: $PYTHON_CMD"
!
!# Find where task-agents-mcp package is installed
!PACKAGE_DIR=$($PYTHON_CMD -c "import task_agents_mcp, os; print(os.path.dirname(task_agents_mcp.__file__))" 2>/dev/null)
!
!if [ -z "$PACKAGE_DIR" ]; then
!    echo "❌ Error: Could not locate package directory"
!    exit 1
!fi
!
!# Copy all default agents from the package
!if [ -d "$PACKAGE_DIR/agents" ]; then
!    cp "$PACKAGE_DIR/agents/"*.md task-agents/ 2>/dev/null || {
!        echo "❌ Error: Could not copy agent files from $PACKAGE_DIR/agents/"
!        exit 1
!    }
!    echo "✅ Created task-agents/ directory with default agents:"
!    echo ""
!    ls -1 task-agents/*.md | sed 's/task-agents\//  • /' | sed 's/\.md$//'
!    echo ""
!    echo "🎉 Your agents are ready to use!"
!    echo ""
!    echo "Try these commands:"
!    echo "  • Use code_reviewer to analyze my code"
!    echo "  • Use debugger to help fix this error"
!    echo "  • Use test_runner to run the tests"
!else
!    echo "❌ Error: Default agents not found in package"
!    echo "Package location: $PACKAGE_DIR"
!    echo ""
!    echo "This might be an older version of task-agents-mcp."
!    echo "Try updating: $PYTHON_CMD -m pip install --upgrade task-agents-mcp"
!    exit 1
!fi
```