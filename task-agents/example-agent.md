---
# REQUIRED FIELDS
agent-name: Example Agent
description: This is an example agent template showing the structure of agent configuration files
tools: Read, Write, Edit, Glob, Grep, Bash
model: sonnet
cwd: .

# OPTIONAL FIELDS
optional:
  # Enable session resumption with max exchanges (true = 5, or specify number)
  resume-session: false
  
  # Additional directories the agent can access (comma-separated)
  # resource_dirs: ./docs, ./data
---

System-prompt:
You are an example agent demonstrating the agent configuration structure.

## Agent Configuration Guide

This file shows how to create custom agents for the task-agents MCP server.

### Required Fields:
- **agent-name**: Display name for your agent (shown in tool list)
- **description**: Brief description of what the agent does
- **tools**: Comma-separated list of tools the agent can use
- **model**: Which Claude model to use (opus, sonnet, haiku)
- **cwd**: Working directory (. = project root)

### Optional Fields:
- **resume-session**: Enable conversation memory across calls
  - `false` = no session (default)
  - `true` = 5 exchanges
  - `true 10` = 10 exchanges
  - `10` = 10 exchanges
- **resource_dirs**: Additional directories the agent can access

### Available Tools:
- Read, Write, Edit, MultiEdit - File operations
- Glob, Grep, LS - File search and listing
- Bash, BashOutput, KillBash - Shell commands
- WebSearch, WebFetch - Web access
- TodoWrite - Task management
- NotebookEdit - Jupyter notebooks
- Task - Launch sub-agents

### Available Models:
- **opus**: Best for complex reasoning, planning, analysis
- **sonnet**: Best for implementation, coding, execution
- **haiku**: Fast responses for simple tasks

### Tips for Writing System Prompts:
1. Define the agent's role and expertise clearly
2. Specify how it should approach tasks
3. Include any specific guidelines or constraints
4. Consider adding examples of expected behavior

## Creating Your Own Agent

1. Copy this file and rename it (e.g., `my-agent.md`)
2. Update all the required fields
3. Customize the system prompt for your use case
4. Adjust tools and model based on needs
5. Save in the task-agents/ directory

The agent will automatically be available as a tool when the server starts!