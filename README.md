# Task Agent MCP Server

Get a team of specialized AI agents in Claude Code with just 2 commands! Each agent (code reviewer, debugger, test runner, etc.) appears as a separate tool, giving you instant access to focused expertise.

## 🎯 What You Get

| Agent Tool | What it does | Perfect for |
|------------|--------------|-------------|
| `code_reviewer` | Reviews code quality & security | PRs, security checks |
| `debugger` | Finds and fixes bugs | Error messages, crashes |
| `test_runner` | Creates and runs tests | Unit tests, coverage |
| `documentation_writer` | Writes technical docs | READMEs, API docs |
| `performance_optimizer` | Makes code faster | Bottlenecks, optimization |
| `default_assistant` | General coding help | Everything else |

## 🚀 Quick Install (2 Steps)

### Step 1: Install the package
```bash
python3 -m pip install task-agents-mcp
```

### Step 2: Add to Claude Code
```bash
claude mcp add task-agent task-agent -s project
```

That's it! ✅ Claude Code will ask for approval, then you're ready to use your agents.

## 💬 How to Use

Just ask Claude to use any agent:

```
"Use code_reviewer to check my authentication code"
"Have debugger help with this error message"
"Get test_runner to create unit tests for user.py"
```

## 📦 Requirements

- Python 3.10 or higher
- Claude Code CLI ([Download here](https://claude.ai/download))

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

### Code Review
```
"Use code_reviewer to check the security of my login.py file"
```

### Debugging
```
"I'm getting a TypeError in line 42. Use debugger to help fix it"
```

### Writing Tests
```
"Have test_runner create comprehensive tests for the User class"
```

### Documentation
```
"Use documentation_writer to create API docs for the payment module"
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
   ---
   
   System-prompt:
   You are a security specialist focused on finding vulnerabilities...
   ```

2. That's it! Use with: `"Have security_auditor check for SQL injection"`

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
# Quick test
claude "Use code_reviewer to analyze this: def add(a, b): return a + b"

# See all agents
claude "Show available agents using agents://list"
```

## ❓ Troubleshooting

### "command not found: task-agent"
```bash
# Make sure you installed it:
python3 -m pip install task-agents-mcp
```

### "spawn task-agent ENOENT"
```bash
# Reinstall the package:
python3 -m pip install --upgrade task-agents-mcp
```

### Agents not showing up?
- Restart Claude Code/Desktop
- Check Python version: `python3 --version` (need 3.10+)

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