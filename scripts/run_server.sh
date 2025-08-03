#!/bin/bash

# Task-Agents MCP Server Launch Script
# This script sets up the environment and runs the MCP server

# Set the Claude executable path
export CLAUDE_EXECUTABLE_PATH="${CLAUDE_EXECUTABLE_PATH:-/Users/vredrick/.claude/local/claude}"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Get the parent directory (project root)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Starting Task-Agents MCP Server..."
echo "Config directory: task-agents (in current directory)"
echo "Claude executable: $CLAUDE_EXECUTABLE_PATH"
echo ""

# Run the server from project root
cd "$PROJECT_ROOT"
python3.11 server.py