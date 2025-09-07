# SDK Integration Documentation

## Overview

The task-agents MCP server now supports using the Claude Code SDK as an alternative to CLI subprocess execution. This enables better container compatibility and subscription-based authentication.

## Key Features

- **Drop-in replacement**: SDK executor mimics CLI behavior exactly
- **Subscription support**: Works with Claude Pro/Max subscriptions via OAuth
- **Container-ready**: No subprocess spawning required
- **Same JSON format**: Maintains compatibility with existing parsing logic

## Configuration

### Enable SDK Mode

Set the environment variable:
```bash
export USE_SDK=true
```

### Authentication Options

#### Option 1: Claude Subscription (Recommended)
```bash
# Don't set ANTHROPIC_API_KEY
# SDK will use ~/.claude/.credentials.json automatically
export USE_SDK=true
```

#### Option 2: API Key
```bash
export ANTHROPIC_API_KEY=sk-ant-api03-xxx
export USE_SDK=true
```

## Installation

```bash
# Install SDK packages
pip install claude-code-sdk

# Optional: Install claude-max for better subscription support
pip install claude-max
```

## Architecture

### SDK Executor Module (`sdk_executor.py`)

The SDK executor provides:
- Async generator interface matching CLI subprocess
- Conversion from SDK message types to stream-json format
- Session management via `resume` parameter
- Error handling with JSON error responses

### Integration with AgentManager

The AgentManager checks `USE_SDK` environment variable:
- If true: Uses `_execute_task_sdk()` method
- If false or unavailable: Falls back to CLI subprocess

### Message Format Conversion

SDK returns typed messages, which are converted to JSON:
```python
AssistantMessage → {"type": "text", "content": {"text": "..."}}
ToolUseBlock → {"type": "tool_use", "name": "...", "input": {...}}
ResultMessage → {"type": "usage", "usage": {...}}
```

## Testing

Run the integration test:
```bash
python3 test_sdk_integration.py
```

This tests:
1. SDK availability
2. Basic execution
3. Output format compatibility

## Docker Deployment

### Dockerfile Changes
```dockerfile
# Install SDK packages
RUN pip install claude-code-sdk claude-max

# Don't set API key for subscription users
# ENV ANTHROPIC_API_KEY=xxx  # Remove this

# Mount credentials
VOLUME ~/.claude:/root/.claude:ro
```

### Docker Compose
```yaml
environment:
  - USE_SDK=true
volumes:
  - ~/.claude:/root/.claude:ro  # Mount OAuth credentials
```

## Limitations

- SDK doesn't support all CLI flags (e.g., no `--verbose` flag)
- Session resumption uses `resume` parameter, not `-r` flag
- No direct stream-json output format (requires conversion)

## Migration Path

1. **Phase 1**: Test SDK locally with `USE_SDK=true`
2. **Phase 2**: Deploy containers with SDK enabled
3. **Phase 3**: Remove CLI dependency entirely

## Troubleshooting

### "SDK not available"
- Install: `pip install claude-code-sdk`
- Check: `python3 -c "import claude_code_sdk"`

### "OAuth authentication failed"
- Ensure `~/.claude/.credentials.json` exists (note the dot!)
- Don't set `ANTHROPIC_API_KEY` when using subscription
- Run `claude login` if credentials are missing

### "Unexpected keyword argument"
- SDK API differs from CLI
- Check `sdk_executor.py` for parameter mapping

## Benefits

1. **Container compatibility**: No subprocess spawning
2. **Subscription support**: Direct OAuth authentication
3. **Better error handling**: Structured exceptions
4. **Future-proof**: SDK is actively maintained
5. **Performance**: Potentially faster without subprocess overhead

## Next Steps

- Complete claude-max integration for enhanced subscription support
- Add comprehensive SDK vs CLI comparison tests
- Optimize message conversion for streaming performance
- Consider making SDK the default execution method