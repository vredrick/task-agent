# Task Agent MCP Server

A flexible MCP server that lets you create specialized AI agents as individual tools in Claude. Each agent appears as its own tool with custom prompts, models, and capabilities.

**v4.0.0** - Simplified architecture with user-defined agents only

## 🎯 What is This?

Task Agent MCP Server turns markdown files into specialized AI agents. Each agent:
- Appears as a separate tool in Claude
- Has its own system prompt and personality
- Can use specific Claude models (opus, sonnet, haiku)
- Maintains conversation context (optional)
- Access specific directories and resources

## 🚀 Quick Install (2 Steps)

### Step 1: Install the package
```bash
# Requires Python 3.11 or higher
python3.11 -m pip install task-agents-mcp
```

### Step 2: Add to Claude Code
```bash
claude mcp add task-agent task-agent -s project
```

That's it! ✅ The server comes with an example agent template to get you started.

## 💬 How to Use

### Your First Agent

The package includes `task-agents/example-agent.md` as a template. Try it:

```
"Use example_agent to explain how task agents work"
```

### Creating Your Own Agents

1. Copy the example template:
   ```bash
   cp task-agents/example-agent.md task-agents/my-agent.md
   ```

2. Edit `my-agent.md` to customize:
   - Agent name and description
   - System prompt (the agent's personality and instructions)
   - Tools it can use
   - Model (opus for complex reasoning, sonnet for implementation)

3. Use your new agent:
   ```
   "Use my_agent to [your task]"
   ```

## 📝 Agent Configuration

Each agent is a markdown file with YAML frontmatter:

```markdown
---
# REQUIRED FIELDS
agent-name: My Assistant
description: Brief description of what this agent does
tools: Read, Write, Edit, Glob, Grep, Bash
model: sonnet
cwd: .

# OPTIONAL FIELDS
optional:
  # Enable session memory (remembers context between calls)
  resume-session: true 10  # Remember last 10 exchanges
  
  # Additional directories the agent can access
  resource_dirs: ./docs, ./data
---

System-prompt:
You are a specialized assistant that...
[Your detailed instructions here]
```

### Available Tools

Agents can use any combination of these tools:
- **File Operations**: Read, Write, Edit, MultiEdit
- **Search**: Glob, Grep, LS  
- **Shell**: Bash, BashOutput, KillBash
- **Web**: WebSearch, WebFetch
- **Other**: TodoWrite, NotebookEdit, Task

### Available Models

- **opus**: Best for complex reasoning, planning, analysis
- **sonnet**: Best for implementation, coding, execution
- **haiku**: Fast responses for simple tasks

## 🖥️ Also Works with Claude Desktop

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "task-agent": {
      "command": "task-agent",
      "env": {
        "TASK_AGENTS_PATH": "/path/to/your/agents"
      }
    }
  }
}
```

## 💡 Example Agents

### Code Review Agent
```markdown
---
agent-name: Code Reviewer
description: Reviews code for bugs, performance, and best practices
tools: Read, Grep, Glob
model: opus
cwd: .
---

System-prompt:
You are an expert code reviewer. Focus on:
- Finding bugs and potential issues
- Suggesting performance improvements
- Ensuring code follows best practices
- Checking for security vulnerabilities
```

### DevOps Agent
```markdown
---
agent-name: DevOps Engineer
description: Manages deployments, CI/CD, and infrastructure
tools: Read, Write, Edit, Bash
model: sonnet
cwd: .
optional:
  resume-session: true 5
---

System-prompt:
You are a DevOps engineer specializing in:
- Docker and Kubernetes configurations
- CI/CD pipeline setup
- Infrastructure as Code
- Deployment automation
```

## 🔧 Advanced Features

### Session Management

Enable conversation memory for multi-step tasks:

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

### Resource Directories

Give agents access to additional directories:

```yaml
optional:
  resource_dirs: ./templates, ./data, ./scripts
```

### Working Directory

Set where the agent operates from:

```yaml
cwd: .                    # Project root (default)
cwd: ./src               # Specific subdirectory
cwd: /absolute/path      # Absolute path
```

## 📦 Requirements

- **Python 3.11 or higher**
- Claude Code CLI ([Download here](https://claude.ai/download))

## 🛠️ Troubleshooting

### No agents loaded
- Check that your `.md` files are in the `task-agents/` directory
- Verify the YAML frontmatter is valid
- Ensure all required fields are present

### Agent not appearing
- Agent names with spaces become underscores in tool names
- "Code Reviewer" becomes `code_reviewer` tool
- Check server logs: `/tmp/task_agents_server.log`

### Python version issues
```bash
# Check your Python version
python3 --version

# If less than 3.11, install Python 3.11
# macOS: brew install python@3.11
# Ubuntu: sudo apt install python3.11
```

## 📚 Project Structure

```
your-project/
├── task-agents/           # Your agent configurations
│   ├── example-agent.md   # Template/example agent
│   ├── my-agent.md        # Your custom agents
│   └── ...
└── .mcp.json             # MCP configuration (auto-created)
```

## 🔗 Links

- **GitHub**: [https://github.com/vredrick/task-agent](https://github.com/vredrick/task-agent)
- **PyPI**: [https://pypi.org/project/task-agents-mcp/](https://pypi.org/project/task-agents-mcp/)
- **MCP Protocol**: [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)

## 📄 License

MIT License - See LICENSE file for details