# CLAUDE.md - Task Agent Multi-Tool MCP Server

## 🎯 Quick Context

You're working with a **multi-tool MCP server** where each user-defined AI agent is exposed as its own tool. This is v5.0.0 with dual SDK architecture - both Python and TypeScript backends for maximum flexibility. **NEW**: TypeScript backend with @anthropic-ai/claude-code SDK providing enhanced session management and real-time streaming!

### Key Architecture Points
- Each agent = separate MCP tool (e.g., `analyst`, `dev`, `qa`)
- No built-in agents - users define all agents
- Ships with `example-agent.md` template
- Tool names: lowercase with underscores (e.g., "Code Reviewer" → `code_reviewer`)
- Built on FastMCP with dynamic tool registration
- Python 3.11+ required for MCP server
- **Web UI**: React frontend with choice of backends:
  - **TypeScript Backend** (port 8001): Express + WebSocket with @anthropic-ai/claude-code SDK v1.0.112
  - **Python Backend** (port 8000): FastAPI + WebSocket with subprocess SDK
- **Session Architecture**: Backend-managed sessions with connectionId → sdkSessionId mapping
- **SDK Integration**: Direct agent execution without MCP overhead in both Python and TypeScript

## 📁 Project Structure

```
task-agent/
├── src/                     
│   ├── task_agents_mcp/     # MCP server implementation
│   │   ├── __init__.py      # Version: 5.0.0
│   │   ├── server.py        # Multi-tool MCP server (main entry)
│   │   ├── agent_manager.py # Agent loader/executor
│   │   ├── resource_manager.py # MCP resource registration
│   │   └── session_store.py # Session management
│   └── sdk_integration/     # Direct SDK execution layer (Python)
│       ├── agent_executor.py # High-level agent management
│       └── sdk_executor.py  # Claude SDK integration (subprocess)
├── web-ui/                  # Web interface with dual backend support
│   ├── backend/            # Python: FastAPI + WebSocket server (port 8000)
│   ├── backend-ts/         # TypeScript: Express + WebSocket (port 8001)
│   │   ├── src/
│   │   │   └── server.ts   # Main TypeScript server with session management
│   │   ├── package.json    # Dependencies including @anthropic-ai/claude-code
│   │   └── tsconfig.json   # TypeScript configuration
│   └── frontend/           # React + TypeScript UI (port 5173)
├── task-agents/            # User agent configs (ships with example)
│   └── example-agent.md    # Template showing agent structure
├── pyproject.toml          # Package config (name: task-agents-mcp)
├── README.md               # User documentation
├── CLAUDE.md               # This file
└── MANIFEST.in             # Package manifest
```

## 🔧 Key Technical Details

### Package Info
- **PyPI Name**: `task-agents-mcp`
- **Command**: `task-agent` (no 's' at end!)
- **Current Version**: 5.0.0
- **Entry Point**: `task_agents_mcp.server:main`
- **Python Requirement**: 3.11+ (MCP server)
- **Node Requirement**: 18+ (TypeScript backend)

### Tool Registration Flow
```python
# server.py - Simplified logic
for agent_name, agent_config in agent_manager.agents.items():
    tool_func = create_agent_tool_function(agent_config.agent_name, agent_config)
    tool_name = sanitize_tool_name(agent_config.agent_name)  # spaces→underscores, lowercase
    mcp.tool(name=tool_name)(tool_func)
```

### Environment Variables
- `TASK_AGENTS_PATH`: Custom agents directory
  - Claude Code: Optional (defaults to `./task-agents`)
  - Claude Desktop: Set to your agents directory
- `CLAUDE_EXECUTABLE_PATH`: Auto-detected from PATH

### Agent Loading
```python
# Only loads from one directory now:
config_dir = os.environ.get('TASK_AGENTS_PATH') or './task-agents'
agent_manager = AgentManager(config_dir)
agent_manager.load_agents()
```

## 🌐 Web UI Architecture

### Quick Start
```bash
cd web-ui

# Option 1: Use TypeScript backend (recommended)
cd backend-ts && npm run dev  # Port 8001
cd ../frontend && npm run dev  # Port 5173

# Option 2: Use Python backend
cd backend && python server.py  # Port 8000
cd ../frontend && npm run dev   # Port 5173

# Or use the convenience script:
./start.sh  # Starts Python backend + frontend
```

### Session Management Architecture

The Web UI implements a sophisticated two-tier session system:

1. **Connection ID**: Frontend-generated UUID for WebSocket connections
   - Format: `/ws/chat/{connectionId}`
   - Tracks individual browser connections
   - Persists only for WebSocket lifetime

2. **SDK Session ID**: Backend-managed conversation continuity
   - Created on first SDK response
   - Mapped to Connection ID by backend
   - Enables conversation history across messages
   - Can be reset via `session_reset` parameter

```typescript
// Backend session tracking (TypeScript)
interface ConnectionInfo {
  ws: WebSocket;
  sdkSessionId: string | null;  // SDK session for continuity
  agentName: string | null;
}

// Mapping: connectionId → sdkSessionId
const connectionToSDKSession = new Map<string, string | null>();
```

### Features
- **Dual Backend Support**: Choose between TypeScript or Python backends
- **Visual agent selection**: Card-based interface with agent descriptions
- **Real-time streaming**: WebSocket with `includePartialMessages` for smooth text flow
- **Rich markdown rendering**: Syntax-highlighted code blocks with copy functionality
- **Tool usage visualization**: Dark blue accent theme for tool interactions
- **Session management**: Backend-controlled with reset capability
- **Direct SDK integration**: No MCP overhead for web interactions
- **Custom AI Elements**: Professional UI components
- **Smooth text streaming**: 40ms/word animation with gap filling

## 📝 Common User Tasks

### Installation
```bash
# Must use Python 3.11 or higher
python3.11 -m pip install task-agents-mcp

# Add to Claude Code
claude mcp add task-agent task-agent -s project
```

### Creating Agents
Users create `.md` files in `task-agents/` directory:
```markdown
---
agent-name: My Agent
description: What it does
tools: Read, Grep, Bash
model: opus
cwd: .
optional:
  resume-session: true 10
  resource_dirs: ./data
---

System-prompt:
You are...
```

### Testing
```bash
# Test with example agent
claude "Use example_agent to explain how agents work"

# Test custom agent
claude "Use my_agent to perform task"
```

## 🐛 Known Issues & Fixes

### 1. "No agents loaded!"
- **Cause**: No `.md` files in agents directory
- **Fix**: Add agent files to `task-agents/` or set `TASK_AGENTS_PATH`

### 2. "spawn task-agent ENOENT"
- **Cause**: Package not installed or wrong Python version
- **Fix**: Install with Python 3.11: `python3.11 -m pip install task-agents-mcp`

### 3. Agent names with spaces
- **Note**: "Code Reviewer" becomes tool `code_reviewer`
- **Resource URI**: "Code-Reviewer://" (spaces become hyphens)

## 🚀 Development Workflow

### Making Changes
1. Edit source files in `src/task_agents_mcp/`
2. Update version in both:
   - `pyproject.toml`
   - `src/task_agents_mcp/__init__.py`
3. Test locally: `python3.11 -m pip install -e .`
4. Test with Claude Code: `claude "Use example_agent..."`

### Testing Without Installing
```bash
# Run directly from source
python3.11 -c "import sys; sys.path.insert(0, '.'); from src.task_agents_mcp.server import main; main()"
```

### Publishing to PyPI
```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build (requires Python 3.11+)
python3.11 -m build

# Upload
python3.11 -m twine upload dist/*
```

## 🎯 Key Changes in v5.0.0

### What's New
- **TypeScript Backend**: Full Express + WebSocket implementation with @anthropic-ai/claude-code SDK
- **Dual Backend Support**: Choose between Python (port 8000) or TypeScript (port 8001)
- **Enhanced Session Management**: Backend-managed SDK sessions with proper connectionId mapping
- **Real-time Streaming**: WebSocket with `includePartialMessages` for smooth text flow
- **TypeScript SDK Integration**: Native Claude Code SDK v1.0.112 support
- **Improved Architecture**: Clear separation between connection and session management

### v4.0.0 Changes (Previous)
- **Removed**: Built-in agents directory (`src/task_agents_mcp/agents/`)
- **Removed**: Dual-directory loading logic
- **Added**: Example agent template in `task-agents/`
- **Simplified**: Only loads from one agents directory
- **Standardized**: Python 3.11+ requirement

### Migration Notes
- **From v4.x**: Web UI frontend now defaults to TypeScript backend on port 8001
- **From v3.x**: Copy any BMad agents to `task-agents/` directory
- **Backend Choice**: Update frontend config to point to desired backend port

## 💡 Implementation Details

### Agent Discovery
1. Server checks `TASK_AGENTS_PATH` or defaults to `./task-agents`
2. Loads all `.md` files with valid YAML frontmatter
3. Registers each as an MCP tool
4. Shows helpful messages if no agents found

### Resource URI Sanitization
Agent names are sanitized for URI format:
```python
# "Example Agent" → "Example-Agent://"
sanitized_name = agent_config.agent_name.replace(' ', '-')
resource_uri = f"{sanitized_name}://"
```

### Session Management
- **Python Backend**: Sessions stored in `/tmp/task_agents_sessions.json`
- **TypeScript Backend**: In-memory session tracking with SDK session IDs
- Each agent can maintain conversation context
- `session_reset` parameter available for agents with `resume-session: true`

### TypeScript SDK Integration

The TypeScript backend uses the official `@anthropic-ai/claude-code` SDK:

```typescript
import { ClaudeCodeClient } from '@anthropic-ai/claude-code';

// Initialize SDK with OAuth credentials
const client = new ClaudeCodeClient({
  credentialsPath: '~/.claude/.credentials'
});

// Execute agent with streaming
const generator = await client.execute({
  agentConfig,
  prompt,
  sessionId,  // SDK session for continuity
  includePartialMessages: true  // Enable text_delta streaming
});

// Stream responses via WebSocket
for await (const event of generator) {
  if (event.type === 'text_delta') {
    ws.send(JSON.stringify({
      type: 'stream',
      content: { text: event.text }
    }));
  }
}
```

### WebSocket Protocol

Both backends implement the same WebSocket protocol:

```javascript
// Frontend → Backend
{
  type: 'chat',
  agentName: 'example_agent',
  prompt: 'User message',
  sessionReset?: boolean,
  maxTurns?: number
}

// Backend → Frontend
{
  type: 'stream',        // Streaming text
  content: { text: '...' }
}
{
  type: 'tool_use',      // Tool execution
  content: { tool: '...', input: {...} }
}
{
  type: 'metadata',      // Connection info
  content: { connection_id: '...', has_session: true }
}
```

## 🚨 Important Reminders

1. **Package name vs command**: 
   - Package: `task-agents-mcp` (with 's')
   - Command: `task-agent` (no 's')

2. **Language requirements**:
   - Python 3.11+ for MCP server and Python backend
   - Node.js 18+ for TypeScript backend

3. **Backend choice**:
   - **TypeScript (port 8001)**: Recommended for production, native SDK integration
   - **Python (port 8000)**: Legacy support, subprocess-based SDK

4. **Session handling**:
   - Frontend uses `connectionId` (UUID per WebSocket)
   - Backend manages `sdkSessionId` (conversation continuity)
   - Never expose SDK session IDs to frontend

5. **Empty default**: Ships with only example template, not functional agents

6. **Project scope**: Recommend `-s project` for Claude Code

7. **Agent names**: Spaces become underscores in tool names

## 📍 Navigation Guide

### Subdirectory Documentation
For detailed information about specific components, see:

- **[/src/CLAUDE.md](/home/vredrick/task-agent/src/CLAUDE.md)** - Source code documentation
  - MCP server implementation details
  - SDK integration layer architecture
  - Agent management and execution flow
  - Session handling and persistence

- **[/web-ui/CLAUDE.md](/home/vredrick/task-agent/web-ui/CLAUDE.md)** - Web UI documentation
  - Frontend React architecture
  - Dual backend implementations:
    - Python: FastAPI + subprocess SDK
    - TypeScript: Express + @anthropic-ai/claude-code SDK
  - WebSocket streaming protocol
  - Session management architecture
  - Development and deployment guide

### Quick Navigation by Task

**Want to understand the MCP server?**
→ See `/src/CLAUDE.md` for server implementation

**Working on the Web UI?**
→ See `/web-ui/CLAUDE.md` for frontend/backend details

**Need SDK integration details?**
→ Python SDK: Check `/src/CLAUDE.md` SDK Integration section
→ TypeScript SDK: See `/web-ui/backend-ts/src/server.ts` implementation

**Working with the TypeScript backend?**
→ See session management in this file's TypeScript SDK Integration section

**Setting up agent configurations?**
→ Review agent format in this file and examples in `task-agents/`

## 📚 Resources

- **GitHub**: https://github.com/vredrick/task-agent
- **PyPI**: https://pypi.org/project/task-agents-mcp/
- **MCP Docs**: https://modelcontextprotocol.io/
- **FastMCP**: https://github.com/jlowin/fastmcp