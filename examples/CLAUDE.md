# CLAUDE.md - examples/

## Directory Purpose

This directory contains **practical examples and templates** demonstrating how to create custom agents and use the task-agents MCP server effectively. Examples here serve as starting points for users creating their own agents.

## Current Examples

### session-resume-agent.md
**Purpose**: Template for creating agents with session resumption capability

**Key Features**:
- Shows YAML frontmatter configuration
- Demonstrates `resume-session` syntax options
- Includes example system prompts
- Explains exchange counting behavior

### task-agents-command.md
**Purpose**: Command-line usage examples for the task-agent server

**Key Topics**:
- Installation commands for different scenarios
- Claude MCP add syntax
- Testing and verification commands
- Troubleshooting common issues

## Example Categories

### Agent Templates
Templates for different agent types:
- Session-aware agents (with resumption)
- Stateless agents (single exchange)
- Specialized role agents
- Multi-tool agents

### Configuration Examples
Different configuration patterns:
- Basic agent setup
- Advanced with resource directories
- Model selection strategies
- Tool restriction patterns

### Usage Scenarios
Real-world usage examples:
- Development workflows
- Analysis tasks
- Documentation generation
- Code review processes

## Creating New Examples

When adding examples, follow this structure:

```markdown
# Example Name

## Purpose
Brief description of what this example demonstrates

## Use Case
When and why you would use this pattern

## Configuration
```yaml
[YAML frontmatter example]
```

## Implementation
[Code or system prompt example]

## Usage
```bash
# Command examples
```

## Expected Behavior
What should happen when using this example

## Customization
How to adapt this example for different needs
```

## Example Patterns

### Basic Agent Template
```markdown
---
agent-name: my-agent
description: Description for tool list
tools: Read, Write, Edit
model: sonnet
cwd: .
---

System-prompt:
You are [persona description]...
```

### Session-Enabled Agent
```markdown
---
agent-name: stateful-agent
description: Agent with context persistence
tools: Read, Write, Edit, Bash
model: opus
cwd: .
optional:
  resume-session: true 10
---

System-prompt:
You maintain context across exchanges...
```

### Resource-Aware Agent
```markdown
---
agent-name: resource-agent
description: Agent with additional directories
tools: Read, Grep, Bash
model: sonnet
cwd: .
optional:
  resource_dirs: ./templates, ./configs
---

System-prompt:
You have access to templates and configs...
```

## Example Usage Patterns

### Development Workflow Example
```bash
# Start with analysis
claude "Use analyst to explore the codebase structure"

# Create documentation
claude "Use documentation_writer to create API docs"

# Implement features
claude "Use dev to implement the user authentication"

# Review and test
claude "Use qa to review the implementation"
```

### Session Continuity Example
```bash
# First call - starts new session
claude "Use analyst to begin market research"

# Second call - resumes previous session
claude "Use analyst to continue the research"

# After exchange limit - starts fresh
claude "Use analyst to research a different topic"
```

### Custom Agent Example
```bash
# Create custom agent
cat > task-agents/researcher.md << 'EOF'
---
agent-name: researcher
description: Deep research specialist
tools: WebSearch, Read, Write
model: opus
cwd: .
optional:
  resume-session: true 20
---

System-prompt:
You are a research specialist...
EOF

# Use custom agent
claude "Use researcher to investigate quantum computing"
```

## Testing Examples

### Verification Commands
```bash
# List available agents
claude "Show all available tools"

# Test specific agent
claude "Use dev to write a hello world function"

# Check session resumption
claude "Use analyst to start a new analysis"
claude "Use analyst to continue"  # Should resume
```

### Debugging Commands
```bash
# Check if server is running
task-agent

# Verify installation
which task-agent

# Check package version
python -c "import task_agents_mcp; print(task_agents_mcp.__version__)"
```

## Example Conventions

### File Naming
- Descriptive names with hyphens: `session-resume-agent.md`
- Category prefixes: `template-*.md`, `workflow-*.md`
- Version suffixes if needed: `agent-v2.md`

### Content Standards
- Working code/configuration only
- Clear comments explaining choices
- Realistic use cases
- Progressive complexity

### Documentation Links
Each example should reference:
- Related documentation in `/docs/`
- Relevant agent configurations
- API or tool documentation

## Common Example Requests

Users frequently ask for examples of:

1. **Custom Agents**:
   - Domain-specific experts
   - Language-specific developers
   - Testing specialists
   - Documentation writers

2. **Workflows**:
   - Full development cycle
   - Bug investigation
   - Code review process
   - Documentation updates

3. **Configurations**:
   - Multi-directory access
   - Tool restrictions
   - Model optimization
   - Session management

## Example Maintenance

Keep examples current by:
- Testing after version updates
- Updating syntax for new features
- Adding examples for new capabilities
- Removing deprecated patterns
- Fixing reported issues

## Contributing Examples

When contributing examples:

1. **Test Thoroughly**: Ensure example works as described
2. **Document Clearly**: Explain what and why
3. **Show Real Use**: Practical, not theoretical
4. **Include Output**: Show expected results
5. **Provide Variations**: Different approaches

## Example Quality Checklist

Before adding an example:
- [ ] Configuration is valid YAML
- [ ] System prompt is clear and focused
- [ ] Commands work as shown
- [ ] Use case is realistic
- [ ] Customization notes included
- [ ] Related docs referenced

## Future Examples Planned

Upcoming example additions:
- BMad workflow complete example
- Multi-agent collaboration patterns
- Error handling and recovery
- Performance optimization configs
- Security-restricted agents

## Resources for Examples

### Internal References
- `/src/task_agents_mcp/agents/` - Built-in agent examples
- `/docs/` - Technical documentation
- Root `README.md` - Usage basics

### External Resources
- Claude CLI documentation
- MCP protocol examples
- FastMCP usage patterns

## Example Categories Reference

| Category | Purpose | Example Files |
|----------|---------|---------------|
| Templates | Starting points for custom agents | `session-resume-agent.md` |
| Commands | CLI usage patterns | `task-agents-command.md` |
| Workflows | Multi-step processes | (planned) |
| Configs | Configuration patterns | (planned) |

## Quick Start Examples

### Minimal Agent
```markdown
---
agent-name: simple
description: Basic agent
tools: Read, Write
model: sonnet
cwd: .
---

System-prompt:
You are a helpful assistant.
```

### Full-Featured Agent
```markdown
---
agent-name: advanced
description: Advanced agent with all features
tools: Read, Write, Edit, Bash, WebSearch
model: opus
cwd: .
optional:
  resume-session: true 15
  resource_dirs: ./templates, ./docs, ./configs
---

System-prompt:
You are an advanced assistant with full capabilities...
```