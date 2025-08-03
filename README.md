# Task Agents MCP Server

A Model Context Protocol (MCP) server that delegates tasks to specialized Claude Code CLI instances with custom configurations. Create a team of AI agents (code reviewer, debugger, test runner, etc.) accessible through any MCP-compatible client.

## Overview

Task Agents allows you to create specialized AI agents that excel at specific tasks. Each agent has its own:
- System prompt with detailed instructions
- Allowed tools (Read, Write, Bash, etc.)
- Model selection (Opus, Sonnet, Haiku)
- Working directory configuration

### New in v1.0.11
- **Import Fix**: Fixed module import issues for package distribution
- **Version Sync**: Synchronized version numbers across all package files
- **PyPI Publishing**: Automated publishing workflow with version management
- **Dynamic Resource**: Query `agents://list` for comprehensive agent information
- **Agent-Specific Prompts**: Each agent gets a dedicated prompt template (e.g., `code_reviewer_task`)
- **Rich Metadata**: View agent categories, capabilities, tools, and usage examples
- **Tool Usage Tracking**: See which tools agents use during execution
- **Token Count Display**: View input/output token usage and costs
- **Enhanced Output Format**: Cleaner, more informative agent responses

## Installation & Setup

### Prerequisites

- **Python 3.9+** installed
- **Claude Code CLI** installed (for agent execution)
- **pip** or **uvx** package manager

### For Claude Code CLI

#### Option 1: Using uvx (Recommended)
```bash
# Install at project scope
claude mcp add task-agents -s project -- uvx task-agents-mcp
```

#### Option 2: Using Python Module
```bash
# First install the package
pip install task-agents-mcp

# Then add to Claude Code CLI
claude mcp add task-agents -s project -- python3.11 -m task_agents_mcp
```

#### Option 3: Using Local Source
```bash
# Clone the repository
git clone https://github.com/vredrick/task-agents.git

# Add to Claude Code CLI
claude mcp add task-agents -s project python3.11 /path/to/task-agents/server.py
```

### For Claude Desktop

#### Option 1: Using Python Module (Recommended)
1. Install the package:
   ```bash
   pip install task-agents-mcp
   ```

2. Add to Claude Desktop config:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

   ```json
   {
     "mcpServers": {
       "task-agents": {
         "command": "python3.11",
         "args": ["-m", "task_agents_mcp"],
         "env": {
           "TASK_AGENTS_PATH": "/path/to/your/task-agents",
           "CLAUDE_EXECUTABLE_PATH": "/path/to/claude"
         }
       }
     }
   }
   ```

#### Option 2: Using uvx
```json
{
  "mcpServers": {
    "task-agents": {
      "command": "/path/to/uvx",  
      "args": ["task-agents-mcp"],
      "env": {
        "TASK_AGENTS_PATH": "/path/to/your/task-agents",
        "CLAUDE_EXECUTABLE_PATH": "/path/to/claude"
      }
    }
  }
}
```

**Note**: You may need the full path to uvx. Find it with: `which uvx`

#### Option 3: Using Local Source
```json
{
  "mcpServers": {
    "task-agents": {
      "command": "python3.11",
      "args": ["/path/to/task-agents/server.py"],
      "env": {
        "TASK_AGENTS_PATH": "/path/to/your/task-agents",
        "CLAUDE_EXECUTABLE_PATH": "/path/to/claude"
      }
    }
  }
}
```

### Finding Required Paths

**Claude executable path:**
- macOS: `~/.claude/local/claude` (after installing Claude Code CLI)
- Windows: `%USERPROFILE%\.claude\local\claude.exe`
- Find it with: `which claude`

**Task agents directory:**
- Create a `task-agents` folder in your project or home directory
- Add agent configuration files (see examples below)

## Creating Custom Agents

Create `.md` files in your `task-agents` directory with YAML frontmatter:

```markdown
---
agent-name: Code Reviewer
description: Expert code review specialist for quality, security, and maintainability analysis
tools: Read, Glob, Grep
model: opus
cwd: .
---

You are an expert code reviewer specializing in quality analysis, security reviews, and maintainability assessments.

Focus on:
1. Code quality and best practices
2. Security vulnerabilities
3. Performance implications
4. Maintainability concerns
5. Potential bugs or edge cases

Provide constructive feedback with specific suggestions for improvement.
```

### Agent Configuration Fields

| Field | Description | Example |
|-------|-------------|---------|
| `agent-name` | Display name shown to users | `Code Reviewer` |
| `description` | Brief description of agent's purpose | `Expert code review specialist...` |
| `tools` | Space-separated list of allowed tools | `Read Write Edit Bash` |
| `model` | AI model to use | `opus`, `sonnet`, `haiku` |
| `cwd` | Working directory | `.` (parent of task-agents) |

### Available Tools

- `Read` - Read files
- `Write` - Write files
- `Edit` - Edit existing files
- `MultiEdit` - Multiple edits in one operation
- `Bash` - Execute bash commands
- `Grep` - Search file contents
- `Search` - Advanced search
- `Glob` - Find files by pattern

## Default Agents

The package includes these pre-configured agents:

| Agent | Purpose | Key Tools |
|-------|---------|-----------|
| **Code Reviewer** | Quality, security, and maintainability analysis | Read, Glob, Grep |
| **Debugger** | Bug identification and fixing | Read, Edit, Bash, Grep |
| **Test Runner** | Test automation and coverage improvement | Read, Write, Edit, Bash |
| **Documentation Writer** | Technical documentation creation | Read, Write, Edit |
| **Performance Optimizer** | Code efficiency analysis | Read, Edit, Grep, Search |
| **Default Assistant** | General-purpose development tasks | All tools |

## Working Directory Resolution

The `cwd` field in agent configurations determines where agents run:

### For Project-Specific Usage (Recommended)

1. Add `task-agents` folder to your project:
   ```
   my-project/
   ├── src/
   ├── tests/
   └── task-agents/
       ├── code-reviewer.md
       └── debugger.md
   ```

2. Use `cwd: .` in agent configs
3. Agents will work in your project directory

### Working Directory Options

| Setting | Description | Example |
|---------|-------------|---------|
| `cwd: .` | Parent of task-agents folder | Agents run in project root |
| `cwd: /absolute/path` | Specific directory | `/Users/me/projects/app` |
| `cwd: ${HOME}/projects` | With environment variables | Expands to user's home |

## Usage

Once configured, you can:

### In Claude Desktop

#### Using the Tool
Use natural language to invoke agents:
- "Use the Code Reviewer agent to analyze my pull request"
- "Ask the Debugger agent to fix this error"
- "Have the Test Runner check coverage"

#### Using Resources
Query agent information:
- Click on `agents://list` in the resources section
- Ask Claude: "What agents are available?" (Claude will query the resource)
- View comprehensive agent metadata including categories and capabilities

#### Using Prompts
Each agent has a dedicated prompt template:
1. Click on a prompt (e.g., `code_reviewer_task`) in the prompts section
2. Fill in the parameters:
   - Task description
   - Context (optional)
   - Requirements (optional)
   - Constraints (optional)
   - Output format (optional)
3. Use the generated text with the agent

### In Claude Code CLI
The agents appear as the `delegate` tool that Claude can use when appropriate. All features (tool, resource, prompts) are available programmatically.

## Installation Methods Summary

| Method | Claude Code CLI | Claude Desktop | Notes |
|--------|----------------|----------------|-------|
| uvx | ✅ Recommended | ⚠️ Needs full path | Zero-install, always latest |
| Python Module | ✅ Works | ✅ Works | Requires pip install |
| Local Source | ✅ Works | ✅ Works | For development |

## Troubleshooting

### "spawn uvx ENOENT" Error (Claude Desktop)
Use the full path to uvx:
```bash
which uvx  # Find the path
# Then use it in your config: "/Users/me/.local/bin/uvx"
```

### "No agents configured"
- For Claude Code CLI: Ensure `task-agents` folder exists in your project
- For Claude Desktop: Set `TASK_AGENTS_PATH` environment variable correctly

### "Failed to reconnect to task-agents" (Claude Code CLI)
This happens when the `task-agents` directory is missing. Create it:
```bash
# Option 1: Use the setup script
bash /path/to/task-agents/scripts/setup_project.sh

# Option 2: Create manually
mkdir task-agents
# Add at least one agent configuration file
```

### "Claude CLI not found"
- For Claude Desktop: Set `CLAUDE_EXECUTABLE_PATH` to full path
- For Claude Code CLI: This shouldn't happen (finds automatically)

### Python Module Not Found
```bash
pip install --upgrade task-agents-mcp
```

### Testing Your Setup
```bash
# Test the server directly
python3.11 -m task_agents_mcp

# Should show: "Loaded X agents"
```

## Development

### Running from Source
```bash
# Clone repository
git clone https://github.com/vredrick/task-agents.git
cd task-agents

# Install dependencies
pip install -r requirements.txt

# Run server
./scripts/run_server.sh  # or python server.py
```

### Building Package
```bash
./scripts/build_pypi.sh
```

### Publishing to PyPI

#### Quick Publish (with environment variable)
```bash
export PYPI_TOKEN='your-pypi-token'
./scripts/quick_publish.sh
```

#### Automated Release (with version bump)
```bash
# Bump patch version (1.0.2 -> 1.0.3)
python scripts/publish_pypi.py patch

# Bump minor version (1.0.3 -> 1.1.0)
python scripts/publish_pypi.py minor

# Bump major version (1.0.3 -> 2.0.0)
python scripts/publish_pypi.py major
```

#### Setting up PyPI Authentication

Choose one of these methods:

1. **Environment Variable** (temporary):
   ```bash
   export PYPI_TOKEN='your-token-here'
   ```

2. **Local .pypirc** (git-ignored, project-specific):
   ```bash
   cp .pypirc.template .pypirc
   # Edit .pypirc with your token
   ```

3. **Global .pypirc** (for all projects):
   ```bash
   cp .pypirc.template ~/.pypirc
   # Edit ~/.pypirc with your token
   ```

#### GitHub Actions (automated releases)
1. Add `PYPI_TOKEN` to GitHub repository secrets
2. Create a release on GitHub, or
3. Manually trigger the workflow with version

### Testing
```bash
python tests/test_server.py
```

## How It Works

1. **MCP Client** (Claude) receives user request
2. **Claude** analyzes request and selects appropriate agent
3. **Task Agents Server** receives agent selection and task
4. **Server** executes Claude Code CLI with agent's configuration
5. **Results** returned through MCP protocol to user

## Contributing

1. Fork the repository
2. Create your feature branch
3. Add your custom agents to `task-agents/`
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Check existing [GitHub issues](https://github.com/vredrick/task-agents/issues)
- Create new issue with reproduction steps
- Include relevant logs and configurations