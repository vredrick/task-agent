# Session Resumption Feature

The task-agents MCP server now supports session resumption, allowing agents to maintain context across multiple exchanges using Claude CLI's `-r` (resume) flag.

## Overview

When enabled, agents can resume previous sessions to maintain context for complex, multi-step tasks. Each resumed session creates a NEW session ID that's automatically tracked for the next resume.

## Configuration

Add the `optional` section to your agent configuration with the `resume-session` field:

```yaml
---
agent-name: My Agent
description: Agent with session resumption
tools: Read, Write, Edit
model: opus
cwd: .
optional:
  resume-session: true 5    # Enable with 5 exchange limit
  # OR
  resume-session: true      # Enable with default 5 exchange limit
  # OR
  resume-session: false     # Disable (default)
  # OR
  resume-session: 10        # Just a number (implies enabled)
---
```

### Configuration Options

- `false` (default): No session resumption, each request starts fresh
- `true`: Enable resumption with default 5 exchange limit
- `true <number>`: Enable resumption with custom exchange limit
- `<number>`: Enable resumption with specified exchange limit

## How It Works

1. **First Request**: Creates a new session (e.g., `session-123`)
2. **Second Request**: Resumes `session-123`, creates new session `session-456`
3. **Third Request**: Resumes `session-456`, creates new session `session-789`
4. **...continues until exchange limit**
5. **After Limit**: Starts fresh with a new session

## Session Chain Tracking

The server tracks session chains in `/tmp/task_agents_sessions.json`:

```json
{
  "My Agent": {
    "current_session_id": "session-789",
    "exchange_count": 3,
    "previous_sessions": ["session-123", "session-456"],
    "created_at": "2024-01-15T10:00:00",
    "last_updated": "2024-01-15T10:30:00"
  }
}
```

## Response Format

When session resumption is enabled, responses include session information:

```
Session: clqx8zy4k0001qwer5t6y7u8i
Exchange: 2/5
Tools used: Read, Edit

[Agent response content...]
```

## Use Cases

### Long-Running Development Tasks
```yaml
optional:
  resume-session: 20  # Allow up to 20 exchanges
```

Perfect for:
- Feature implementation across multiple files
- Refactoring with incremental changes
- Debugging sessions with iterative fixes

### Quick Assistance
```yaml
optional:
  resume-session: false  # Each request is independent
```

Best for:
- One-off questions
- Independent code reviews
- Simple file edits

### Balanced Approach
```yaml
optional:
  resume-session: true  # Default 5 exchanges
```

Good for:
- Moderate complexity tasks
- Multi-step but focused work
- General development assistance

## Important Notes

1. **Session Persistence**: Sessions are stored in `/tmp/` and may be cleared on system restart
2. **Agent-Specific**: Each agent maintains its own session chain
3. **Manual Reset**: Delete `/tmp/task_agents_sessions.json` to reset all sessions
4. **Claude CLI Required**: This feature requires Claude Code CLI with `-r` flag support

## Example Workflow

```bash
# First request - starts new session
$ claude "Use my_agent to implement a new feature"
Session: abc123
Exchange: 1/5
[Implementation begins...]

# Second request - resumes context
$ claude "Use my_agent to add tests for the feature"  
Session: def456
Exchange: 2/5
[Continues with context from abc123...]

# Fifth request - last in chain
$ claude "Use my_agent to add documentation"
Session: xyz789
Exchange: 5/5
[Completes with full context...]

# Sixth request - starts fresh
$ claude "Use my_agent to review the implementation"
Session: new123
Exchange: 1/5
[Fresh start, no previous context...]
```