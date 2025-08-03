# Claude Code CLI Reference

> **Source**: https://docs.anthropic.com/en/docs/claude-code/cli-reference  
> **Fetched**: August 1, 2025  
> **Description**: Complete command-line interface documentation for Claude Code

## Overview

Claude Code is an agentic coding tool that operates in your terminal, understands your codebase, and helps you code faster through natural language commands. It provides both interactive and programmatic interfaces.

## Installation

```bash
npm install -g @anthropic-ai/claude-code
```

**Requirements:**
- Node.js 18+
- Terminal access
- API authentication (Anthropic, Bedrock, or Vertex AI)

## Core Commands

### Interactive Mode
```bash
claude                    # Start interactive REPL
claude "query"           # Start REPL with initial prompt
claude -c               # Continue most recent conversation
```

### Programmatic Mode
```bash
claude -p "query"       # Query via SDK and exit (print mode)
```

### Utility Commands
```bash
claude update           # Update to latest version
claude mcp             # Configure Model Context Protocol servers
```

## Command-Line Flags

### Input/Output Control

#### `--print`, `-p`
Execute query and exit without interactive mode
```bash
claude -p "Generate a Python function to calculate fibonacci"
```

#### `--output-format`
Specify output format for programmatic usage
- `text` (default): Human-readable text
- `json`: Structured JSON response
- `stream-json`: Streaming JSON for real-time processing

```bash
claude -p "Analyze this code" --output-format json
```

#### `--input-format`
Specify input data format
- `text` (default): Plain text input
- `stream-json`: Streaming JSON input

### Session Management

#### `--resume`
Resume a specific session by ID
```bash
claude --resume session-id-12345
```

#### `--continue`
Load and continue the most recent conversation
```bash
claude --continue
```

#### `--model`
Set the Claude model for the session
```bash
claude --model sonnet    # Use Claude Sonnet
claude --model opus      # Use Claude Opus
```

### Permission and Security

#### `--permission-mode`
Begin session in specified permission mode
```bash
claude --permission-mode strict
claude --permission-mode permissive
```

#### `--allowedTools`
Specify which tools Claude can use
```bash
claude -p "Fix this code" --allowedTools "Edit,Bash"
```

#### `--disallowedTools`
Specify which tools Claude cannot use
```bash
claude -p "Review code" --disallowedTools "Bash,Write"
```

#### `--dangerously-skip-permissions`
Skip all permission prompts (use with caution)
```bash
claude -p "Automated task" --dangerously-skip-permissions
```

### Debugging and Control

#### `--verbose`
Enable detailed logging for debugging
```bash
claude -p "Debug this issue" --verbose
```

#### `--max-turns`
Limit the number of agentic turns in non-interactive mode
```bash
claude -p "Complex task" --max-turns 5
```

#### `--mcp-config`
Load MCP (Model Context Protocol) server configuration
```bash
claude --mcp-config ./mcp-servers.json
```

## Operating Modes

Claude Code operates in three distinct modes (toggle with Shift+Tab in interactive mode):

### Default Mode
- Standard interactive experience
- Claude provides suggestions and waits for approval
- User maintains control over all actions

### Auto Mode
- Autonomous execution mode
- Claude executes tasks without waiting for permission
- Higher productivity but requires careful task specification

### Plan Mode
- Planning-first approach
- Claude creates detailed execution plan before acting
- Ideal for complex features or new applications
- User approves plan before execution begins

## Output Formats

### Text Format (Default)
Human-readable output suitable for terminal display:
```bash
claude -p "Explain this function" --output-format text
```

### JSON Format
Structured output for programmatic parsing:
```bash
claude -p "Generate code" --output-format json
```

Example JSON response structure:
```json
{
  "result": "Generated code content",
  "cost_usd": 0.005,
  "session_id": "session-12345",
  "status": "completed"
}
```

### Stream JSON Format
Real-time streaming JSON for live processing:
```bash
claude -p "Long task" --output-format stream-json
```

## Authentication

### Anthropic API Key
```bash
export ANTHROPIC_API_KEY="your-api-key"
claude -p "Hello world"
```

### Amazon Bedrock
```bash
export CLAUDE_CODE_USE_BEDROCK=1
# Configure AWS credentials separately
claude -p "Hello world"
```

### Google Vertex AI
```bash
export CLAUDE_CODE_USE_VERTEX=1
# Configure Google Cloud credentials separately
claude -p "Hello world"
```

## MCP Server Configuration

Create an MCP configuration file to extend Claude Code capabilities:

```json
{
  "mcpServers": {
    "database": {
      "command": "python",
      "args": ["database_server.py"],
      "env": {
        "DB_URL": "postgresql://localhost/mydb"
      }
    },
    "api_tools": {
      "command": "node",
      "args": ["api_server.js"]
    }
  }
}
```

Load configuration:
```bash
claude --mcp-config ./mcp-config.json
```

## Programmatic Usage Patterns

### Simple Query Execution
```bash
result=$(claude -p "Generate unit tests" --output-format json)
code=$(echo "$result" | jq -r '.result')
```

### Error Handling
```bash
if ! claude -p "$prompt" 2>error.log; then
    echo "Error occurred:" >&2
    cat error.log >&2
    exit 1
fi
```

### Batch Processing
```bash
for file in *.py; do
    claude -p "Analyze $file for bugs" --output-format json > "${file}.analysis"
done
```

### Tool Restriction for Security
```bash
# Only allow file editing and git operations
claude -p "Refactor codebase" --allowedTools "Edit,Bash(git commit:*)"
```

## Advanced Usage Examples

### Large-Scale Migration
```bash
# Generate task list
claude -p "Create migration plan for React to Vue" --output-format json > tasks.json

# Process each task
jq -r '.tasks[]' tasks.json | while read task; do
    claude -p "migrate $task" --allowedTools "Edit,Bash(git commit:*)"
done
```

### Automated Code Review
```bash
# Review changed files
git diff --name-only | while read file; do
    claude -p "Review $file for issues" --output-format json >> review.json
done
```

### Context-Aware Processing
```bash
# Include CLAUDE.md context automatically
claude -p "Implement new feature following project patterns"
```

## Context Files (CLAUDE.md)

Claude Code automatically loads context from CLAUDE.md files found in:

1. **Project root** (most common): `./CLAUDE.md`
2. **Parent directories**: Useful for monorepos
3. **Child directories**: Loaded on-demand when accessing files
4. **Home directory**: `~/.claude/CLAUDE.md` (global context)

### CLAUDE.md Best Practices
- Document repository conventions
- Include setup instructions
- Note project-specific patterns
- Specify coding standards
- List common workflows

Example CLAUDE.md:
```markdown
# Project Context

## Architecture
- React frontend with TypeScript
- Node.js backend with Express
- PostgreSQL database

## Conventions
- Use camelCase for variables
- Prefer async/await over Promises
- Write tests for all new features

## Setup
- Run `npm install` in both frontend/ and backend/
- Use `npm run dev` for development

## Common Tasks
- Database migrations: `npm run migrate`
- Run tests: `npm test`
- Build production: `npm run build`
```

## Error Handling and Debugging

### Common Issues
- **Authentication failures**: Check API key and environment variables
- **Permission errors**: Use `--verbose` flag to debug tool restrictions
- **Context limits**: Break large tasks into smaller chunks
- **Network issues**: Verify internet connection and API endpoints

### Debugging Commands
```bash
# Verbose logging
claude -p "debug task" --verbose

# Check session status
claude --continue --verbose

# Test authentication
claude -p "echo hello" --output-format json
```

## Integration Best Practices

### Security
- Use `--allowedTools` to restrict capabilities
- Avoid `--dangerously-skip-permissions` in production
- Review generated code before execution
- Use dedicated API keys for automation

### Performance
- Use JSON output for programmatic parsing
- Implement proper error handling
- Consider rate limits for batch operations
- Cache session state when possible

### Reliability
- Test prompts thoroughly before automation
- Implement retry logic for network failures
- Monitor usage costs and limits
- Use version control for generated code

## Next Steps

- Review [Claude Code SDK Integration](./claude-code-sdk-integration.md) for programmatic usage
- See [Claude Code Configuration](./claude-code-configuration.md) for setup details
- Follow [Building Claude Code MCP Wrapper](./claude-code-mcp-wrapper.md) for MCP integration