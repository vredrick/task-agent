#!/bin/bash

# Setup script for task-agents MCP server in a project

echo "Setting up task-agents MCP server..."

# Create task-agents directory if it doesn't exist
if [ ! -d "task-agents" ]; then
    echo "Creating task-agents directory..."
    mkdir -p task-agents
    
    echo "Creating example agent configuration..."
    cat > task-agents/default.md << 'EOF'
---
agent-name: Default Assistant
description: General-purpose AI assistant for various software engineering tasks
tools: Read, Write, Edit, MultiEdit, Bash, Grep, Search, Glob
model: sonnet
cwd: .
---

System-prompt:
You are a helpful AI assistant for software engineering tasks. You can help with:
- Code writing and refactoring
- Debugging and troubleshooting
- Documentation and explanations
- Project setup and configuration
- General programming questions

Always strive to provide clear, accurate, and helpful responses.
EOF

    echo "✅ Created task-agents directory with default agent"
else
    echo "✅ task-agents directory already exists"
fi

echo ""
echo "To add the MCP server to your project, run:"
echo "  claude mcp add task-agents -s project -- uvx task-agents-mcp"
echo ""
echo "Or if you need to specify TASK_AGENTS_PATH:"
echo "  claude mcp add task-agents -s project -- uvx task-agents-mcp --env TASK_AGENTS_PATH=$(pwd)/task-agents"