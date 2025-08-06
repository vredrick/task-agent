# Task Agent MCP Server

Get a team of specialized AI agents in Claude Code with just 2 commands! Each agent (code reviewer, debugger, test runner, etc.) appears as a separate tool, giving you instant access to focused expertise.

**v2.8.0** - Dynamic resource paths and improved agent initialization

## 🎯 What You Get

### BMad Methodology Agents (NEW!)
A complete development workflow using specialized AI agents:

| Agent Tool | Role | When to Use |
|------------|------|-------------|
| `analyst` | Business Analyst | Project discovery, market research, requirements gathering |
| `pm` | Product Manager | Create PRDs, define features, prioritize backlog |
| `ux_expert` | UX Designer | UI/UX specs, wireframes, design systems |
| `architect` | Solution Architect | Technical design, API design, database schema |
| `po` | Product Owner | Validate artifacts, shard docs into epics |
| `sm` | Scrum Master | Create developer-ready stories from epics |
| `dev` | Full Stack Developer | Implement code from stories |
| `qa` | Senior Dev & QA | Code review, refactoring, test coverage |

**BMad Workflow**: `analyst` → `pm` → `ux_expert` → `architect` → `po` → `sm` → `dev` → `qa`

### Test Agents
| Agent Tool | What it does |
|------------|--------------|  
| `default_assistant` | General coding help |

## 🚀 Quick Install (2 Steps)

### Step 1: Install the package
```bash
# Requires Python 3.10 or higher
python3.10 -m pip install task-agents-mcp
# or
python3.11 -m pip install task-agents-mcp
```

### Step 2: Add to Claude Code
```bash
claude mcp add task-agent task-agent -s project
```

That's it! ✅ Claude Code will ask for approval, then you're ready to use your agents.

## 💬 How to Use

### BMad Workflow Example
Follow the BMad methodology for complete project development:

```
# 1. Start with discovery
"Use analyst to research the market for a task management app"

# 2. Define product requirements  
"Use pm to create a PRD based on the analysis"

# 3. Design the user experience
"Use ux_expert to create UI specifications"

# 4. Create technical architecture
"Use architect to design the system architecture"

# 5. Validate and prepare work
"Use po to validate the PRD and architecture alignment"

# 6. Create developer stories
"Use sm to create the next story for development"

# 7. Implement the code
"Use dev to implement the story"

# 8. Review and improve
"Use qa to review the implementation"
```

### Quick Agent Commands
```
"Use analyst to brainstorm ideas for [project]"
"Use pm to create a PRD for [feature]"
"Use architect to design API for [service]"
"Use dev to implement [story]"
"Use qa to review recent changes"
```

## 📦 Requirements

- **Python 3.10 or higher** (required by fastmcp dependency)
- Claude Code CLI ([Download here](https://claude.ai/download))

⚠️ **Important**: If `python3 --version` shows less than 3.10, use `python3.10` or `python3.11` explicitly in all commands.

## 🛠️ Custom Agents

Want to create your own specialized agents? Just:

1. Create a `task-agents` folder in your project:
   - **Quick way**: Run `/task-agents` in Claude Code to copy all default agents
   - **Manual way**: Create the folder and add your own agent files
2. Add agent config files (`.md` with YAML frontmatter)
3. Restart - your custom agents appear automatically!

[See examples below](#creating-custom-agents)

## 🖥️ Also Works with Claude Desktop

Add this to your Claude Desktop config:

```json
{
  "mcpServers": {
    "task-agent": {
      "command": "task-agent"
    }
  }
}
```

For custom agents in Claude Desktop, add the path:
```json
{
  "mcpServers": {
    "task-agent": {
      "command": "task-agent",
      "env": {
        "TASK_AGENTS_PATH": "/path/to/your/task-agents"
      }
    }
  }
}
```

Restart Claude Desktop and use the same commands!

## 💡 Examples

### BMad Agent Examples
```
# Research and ideation
"Use analyst to research competitors in the e-commerce space"

# Product planning
"Use pm to create a PRD for a shopping cart feature"

# Design
"Use ux_expert to create UI mockups for the checkout flow"

# Architecture
"Use architect to design microservices architecture"

# Story creation
"Use sm to create the next implementation story"

# Development
"Use dev to implement story-001 from /docs/stories/"

# Quality assurance
"Use qa to review and refactor the shopping cart implementation"
```

## Creating Custom Agents

1. Create `task-agents/my-agent.md`:
   ```markdown
   ---
   agent-name: Security Auditor
   description: Security vulnerability detection specialist
   tools: Read, Grep, Search, Bash
   model: opus
   cwd: .
   optional:
     resume-session: true 10  # Enable session resumption
     resource_dirs: ./security-tools  # Access additional directories
   ---
   
   System-prompt:
   You are a security specialist focused on finding vulnerabilities...
   ```

2. That's it! Use with: `"Have security_auditor check for SQL injection"`

### Resource Directories (v2.8.0 - Enhanced!)
Agents can now access additional directories with dynamic path resolution:

```yaml
optional:
  resource_dirs: ./.bmad-core  # Hidden directory (with dot prefix)
  # OR
  resource_dirs: ./templates, ./data, ./scripts  # Multiple directories
```

**New in v2.8.0**: 
- Dynamic resource path resolution - agents are informed of actual paths at runtime
- Better error reporting when resources are missing
- Support for hidden directories (e.g., `.bmad-core`)

### Session Resumption (v2.5.0+)

Agents can now maintain context across multiple exchanges! Add to any agent:

```yaml
optional:
  resume-session: true      # 5 exchanges (default)
  resume-session: true 10   # 10 exchanges  
  resume-session: false     # Disabled
```

Perfect for:
- Multi-step debugging sessions
- Feature implementation across multiple files
- Extended code reviews
- Iterative optimization

## 🧪 Test It Out

```bash
# Quick test with BMad agents
claude "Use analyst to brainstorm ideas for a todo app"

# See all available agents
claude "Show available agents using agents://list"

# Start a full BMad workflow
claude "Use analyst to research the market for a project management tool"
```

## ❓ Troubleshooting

### "command not found: task-agent"
```bash
# Make sure you installed it with Python 3.10+:
python3.10 -m pip install task-agents-mcp
# or
python3.11 -m pip install task-agents-mcp
```

### "spawn task-agent ENOENT"
```bash
# Reinstall with the correct Python version:
python3.10 -m pip install --upgrade task-agents-mcp
```

### "ResolutionImpossible" or dependency conflicts?
This happens when using Python < 3.10. Solution:
```bash
# Use Python 3.10 or higher explicitly:
python3.10 -m pip install task-agents-mcp
```

### Agents not showing up?
- Restart Claude Code/Desktop
- Check Python version: `python3 --version` (must be 3.10+)
- If less than 3.10, use `python3.10` or `python3.11` in all commands

## 📚 Advanced Usage

For more details on:
- Creating complex custom agents
- Environment variables
- Claude Desktop configuration
- Working with multiple projects

[See the full documentation](https://github.com/vredrick/task-agent)

## 📄 License

MIT License

## 🙏 Built With

- [FastMCP](https://github.com/jlowin/fastmcp)
- [Model Context Protocol](https://github.com/anthropics/mcp)
- Claude Code CLI