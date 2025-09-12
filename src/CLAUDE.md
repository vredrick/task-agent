# Source Code Documentation

## Purpose

This directory contains the core implementation of the Task Agent system, including both the MCP server components and the new SDK integration layer that enables direct agent execution without containers or MCP protocol overhead.

## Structure

```
src/
├── task_agents_mcp/         # MCP server implementation (v4.0.0)
│   ├── __init__.py         # Package metadata and version
│   ├── server.py           # FastMCP server with multi-tool registration
│   ├── agent_manager.py    # Agent loading and configuration
│   ├── resource_manager.py # MCP resource registration
│   ├── session_store.py    # Conversation session persistence
│   └── cli.py              # Command-line interface and aliases
├── sdk_integration/         # Python SDK execution layer
│   ├── __init__.py         # Package exports
│   ├── agent_executor.py   # High-level agent management
│   └── sdk_executor.py     # Claude SDK integration
└── sdk_integration_ts/      # TypeScript SDK execution layer
    ├── agent_manager.ts    # Agent loading from .md files
    ├── sdk_executor.ts     # Claude SDK with session management
    ├── session_store.ts    # Session persistence (TypeScript)
    ├── oauth_handler.ts    # OAuth credential management
    └── index.ts            # Barrel exports for clean API
```

## Key Components

### MCP Server Implementation (`task_agents_mcp/`)

#### server.py
- **Purpose**: Main MCP server using FastMCP framework
- **Key Features**:
  - Dynamic tool registration (each agent = MCP tool)
  - Tool name sanitization (spaces → underscores)
  - Session management integration
  - Resource exposure for agent configs
- **Entry Point**: `main()` function for CLI execution

#### agent_manager.py
- **Purpose**: Load and manage agent configurations
- **Key Classes**:
  - `AgentConfig`: Pydantic model for agent YAML frontmatter
  - `AgentManager`: Loader for `.md` agent files
- **Agent Discovery**:
  - Loads from `TASK_AGENTS_PATH` or `./task-agents`
  - Parses YAML frontmatter from markdown files
  - Validates required fields (name, tools, model)

#### resource_manager.py
- **Purpose**: Expose agent configurations as MCP resources
- **Resource URIs**: Format `{Agent-Name}://` (spaces → hyphens)
- **Content Types**: 
  - `text/markdown` for agent prompts
  - `application/json` for metadata

#### session_store.py
- **Purpose**: Maintain conversation context across calls
- **Storage**: JSON file at `/tmp/task_agents_sessions.json`
- **Features**:
  - Session persistence between calls
  - Optional session reset
  - Automatic cleanup of old sessions

#### cli.py
- **Purpose**: Enhanced CLI with aliases and REPL mode
- **Features**:
  - Alias management (`agent-cli alias`)
  - Interactive REPL mode
  - Direct agent invocation

### Python SDK Integration Layer (`sdk_integration/`)

#### agent_executor.py
- **Purpose**: High-level interface for agent management
- **Key Class**: `AgentExecutor`
- **Responsibilities**:
  - Load agents from directory
  - Create SDK executors for agents
  - Manage OAuth authentication
  - Handle streaming responses
- **Integration Points**:
  - Used by Web UI backend
  - Direct SDK calls without MCP

#### sdk_executor.py
- **Purpose**: Direct Claude SDK integration
- **Key Class**: `SDKExecutor`
- **Features**:
  - OAuth credential loading
  - Tool registration from agent config
  - Streaming response handling
  - Session context management with chaining
- **Credential Paths**:
  - `~/.claude/.credentials.json`
  - `/home/task-agent/.claude/.credentials.json`
- **Session Resumption**:
  - SDK returns new `session_id` with each response
  - Each new session_id is used for the next message
  - Creates a conversation chain for context continuity
  - Only works when agent has `resume-session: true`

### TypeScript SDK Integration Layer (`sdk_integration_ts/`)

#### agent_manager.ts
- **Purpose**: Load and parse agent configurations from `.md` files
- **Key Classes**:
  - `AgentConfig`: Interface matching Python's Pydantic model
  - `AgentManager`: TypeScript agent loader
- **Features**:
  - YAML frontmatter parsing
  - Agent validation
  - Support for `maxTurns` configuration
  - Directory scanning for `.md` files
- **Agent Discovery**: Mirrors Python implementation

#### sdk_executor.ts
- **Purpose**: TypeScript Claude SDK integration
- **Key Class**: `SDKExecutor`
- **Features**:
  - OAuth credential management
  - Tool registration and invocation
  - Streaming with `includePartialMessages: true`
  - Session ID extraction from system/init messages
  - Session chaining for conversation continuity
- **Session Management Pattern**:
  ```typescript
  // Extract session ID from initial response
  if (chunk.type === 'event' && chunk.event.type === 'system' ||
      chunk.type === 'event' && chunk.event.type === 'init') {
    const sessionId = chunk.event.session_id;
    // Store for next message in chain
  }
  ```
- **Streaming Configuration**:
  - Word-by-word animation (40ms/word)
  - Partial message support for smooth UX
  - Fills processing gaps with continuous text flow

#### session_store.ts
- **Purpose**: TypeScript session persistence
- **Storage**: JSON file at `/tmp/task_agents_sessions_ts.json`
- **Key Class**: `SessionStore`
- **Features**:
  - Session save/load operations
  - Session chaining support
  - Timestamp tracking
  - Mirrors Python session store API
- **Session Structure**:
  ```typescript
  interface SessionData {
    messages: Message[];
    context: Record<string, any>;
    timestamp: string;
    nextSessionId?: string;  // For chaining
  }
  ```

#### oauth_handler.ts
- **Purpose**: Manage OAuth credentials for TypeScript SDK
- **Key Class**: `OAuthHandler`
- **Features**:
  - Credential loading from `.claude/` directory
  - Token validation
  - Refresh token handling
  - Shared credential paths with Python SDK
- **Integration**: Used by SDKExecutor for authentication

#### index.ts
- **Purpose**: Barrel exports for clean API surface
- **Exports**:
  - `AgentManager` - Agent configuration loading
  - `SDKExecutor` - Claude SDK execution
  - `SessionStore` - Session persistence
  - `OAuthHandler` - OAuth management
  - Type definitions (`AgentConfig`, `SessionData`, etc.)
- **Usage**: Single import point for TypeScript consumers

## Patterns & Conventions

### Agent Configuration Format
```yaml
---
agent-name: Agent Name
description: What the agent does
tools: Read, Grep, Bash  # Comma-separated
model: opus  # or sonnet, haiku
cwd: .  # Working directory
optional:
  resume-session: true 10  # Enable with timeout
  resource_dirs: ./data  # Additional resources
---

System prompt content here...
```

### Tool Name Sanitization
```python
# Agent name → Tool name
"Code Reviewer" → "code_reviewer"
"Data Analyst" → "data_analyst"

# Resource URI format
"Code Reviewer" → "Code-Reviewer://"
```

### Session Management Pattern

#### Python Implementation
```python
# Session key format
session_key = f"{agent_name}_{session_id}"

# Session data structure
{
    "messages": [...],
    "context": {...},
    "timestamp": "...",
    "next_session_id": "..."  # For chaining
}
```

#### TypeScript Implementation
```typescript
// Session extraction from SDK response
const extractSessionId = (chunk: SDKChunk) => {
  if (chunk.type === 'event') {
    if (chunk.event.type === 'system' || chunk.event.type === 'init') {
      return chunk.event.session_id;
    }
  }
  return null;
};

// Session chaining for context continuity
const chainSessions = async (previousId: string, newId: string) => {
  const previousSession = await sessionStore.getSession(previousId);
  await sessionStore.saveSession(newId, {
    ...previousSession,
    nextSessionId: newId
  });
};
```

#### Session Storage Locations
- **Python**: `/tmp/task_agents_sessions.json`
- **TypeScript**: `/tmp/task_agents_sessions_ts.json`
- **Format**: JSON with agent-prefixed keys
- **Persistence**: Ephemeral (cleared on system restart)

## Dependencies

### Python Packages
- `fastmcp>=0.1.0` - MCP server framework
- `pydantic>=2.0` - Data validation
- `PyYAML>=6.0` - YAML parsing
- `anthropic>=0.8.0` - Claude SDK
- `click>=8.0` - CLI framework

### TypeScript Packages
- `@anthropic-ai/claude-sdk` - Claude TypeScript SDK
- `yaml` - YAML parsing for agent configs
- `gray-matter` - Frontmatter extraction
- `glob` - File pattern matching
- TypeScript 5.0+ with strict mode

### Internal Dependencies
- Agent configurations from `task-agents/` directory
- OAuth credentials from `.claude/` directory
- Python 3.11+ for Python components
- Node.js 18+ for TypeScript components

## Usage Examples

### Using MCP Server
```python
# Load and execute through MCP
from task_agents_mcp.server import main
main()  # Starts MCP server
```

### Using Python SDK Integration
```python
from sdk_integration import AgentExecutor

# Initialize executor
executor = AgentExecutor(agents_path="./task-agents")

# Stream agent response
async for chunk in executor.stream_agent_response(
    agent_name="analyst",
    message="Analyze this data",
    session_id="abc123"
):
    print(chunk)
```

### Using TypeScript SDK Integration
```typescript
import { AgentManager, SDKExecutor, SessionStore } from './sdk_integration_ts';

// Initialize components
const agentManager = new AgentManager('./task-agents');
await agentManager.loadAgents();

const sessionStore = new SessionStore('/tmp/task_agents_sessions_ts.json');
const executor = new SDKExecutor(agentConfig, sessionStore);

// Stream agent response with session chaining
const stream = await executor.streamResponse(
  message,
  sessionId,
  { includePartialMessages: true }
);

let nextSessionId: string | null = null;
for await (const chunk of stream) {
  // Extract session ID for chaining
  if (chunk.type === 'event' && 
      (chunk.event.type === 'system' || chunk.event.type === 'init')) {
    nextSessionId = chunk.event.session_id;
  }
  
  // Process content
  if (chunk.type === 'content') {
    console.log(chunk.content);
  }
}

// Use nextSessionId for the next message in conversation
```

## Environment Variables

- `TASK_AGENTS_PATH`: Custom agents directory
- `CLAUDE_EXECUTABLE_PATH`: Path to Claude CLI
- `PYTHONPATH`: Should include src directory

## Development Guidelines

### Adding New Features
1. Implement in both Python and TypeScript SDK layers
2. Maintain MCP server for protocol compliance
3. Ensure both SDK implementations mirror each other
4. Share agent configuration format across all layers

### Testing Components

#### Python Components
```bash
# Test MCP server
python -m task_agents_mcp.server

# Test Python SDK integration
python -c "from sdk_integration import AgentExecutor; print('OK')"

# Test agent loading
python -m task_agents_mcp.agent_manager
```

#### TypeScript Components
```bash
# Build TypeScript
cd src/sdk_integration_ts
npm run build

# Test TypeScript SDK
npm test

# Test agent loading
node -e "const { AgentManager } = require('./dist'); console.log('OK')"
```

### Code Organization
- Keep MCP and SDK layers separate
- Mirror functionality between Python and TypeScript SDKs
- Share agent configuration format (YAML frontmatter)
- Maintain backward compatibility
- Use consistent session management patterns

### SDK Implementation Guidelines
1. **Session Management**: Both SDKs must support session chaining
2. **Streaming**: Include partial messages for smooth UX
3. **Error Handling**: Graceful fallbacks for missing sessions
4. **Tool Registration**: Dynamic based on agent config
5. **OAuth**: Share credential locations between SDKs

## Important Constraints

1. **Language Versions**: 
   - Python 3.11+ for Python components
   - Node.js 18+ for TypeScript components
   - TypeScript 5.0+ with strict mode
2. **Agent Format**: Must use YAML frontmatter in `.md` files
3. **Tool Names**: Automatically sanitized (no manual control)
4. **Session Storage**: 
   - Ephemeral in `/tmp` directory
   - Separate files for Python and TypeScript
5. **OAuth Required**: Both SDK integrations need valid credentials
6. **Session Chaining**: Only works with `resume-session: true` agents

## Troubleshooting

### Python Import Errors
- Ensure `PYTHONPATH` includes src directory
- Check Python version is 3.11+
- Verify package installation: `pip show task-agents-mcp`

### TypeScript Build Errors
- Check Node.js version is 18+
- Run `npm install` in src/sdk_integration_ts
- Verify TypeScript version: `npx tsc --version`

### Agent Loading Issues
- Verify `.md` files have valid YAML frontmatter
- Check `TASK_AGENTS_PATH` environment variable
- Ensure agent files are readable

### SDK Authentication
- Verify OAuth credentials exist and are valid
- Check file permissions on `.claude/` directory
- Credentials shared between Python and TypeScript SDKs

### Session Management Issues
- Check `/tmp` directory permissions
- Verify session files aren't corrupted
- Session IDs must match between messages
- TypeScript uses different session file than Python

## Related Documentation

- Main project: [/CLAUDE.md](/home/vredrick/task-agent/CLAUDE.md)
- Web UI: [/web-ui/CLAUDE.md](/home/vredrick/task-agent/web-ui/CLAUDE.md)
- PyPI Package: https://pypi.org/project/task-agents-mcp/