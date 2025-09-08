# Task Agent Web UI Implementation

## Overview
The Task Agent Web UI provides a human-friendly interface for interacting with task agents through a web browser. It uses the Claude Code SDK directly for agent execution, avoiding subprocess calls and enabling proper session management.

## Architecture

### Components
1. **Frontend**: React + TypeScript + Vite
   - Material-inspired UI with Tailwind CSS
   - WebSocket client for streaming responses
   - Agent selection grid
   - Chat interface with real-time streaming

2. **Backend**: FastAPI + Uvicorn
   - WebSocket server for bidirectional communication
   - SDK integration for direct agent execution
   - Session management for conversation continuity
   - OAuth authentication status checking

3. **SDK Integration**: Claude Code SDK
   - Direct SDK usage (no CLI subprocess)
   - OAuth subscription authentication (no API keys)
   - Proper session resumption support
   - UUID-based conversation tracking

## Key Features

### Session Management
- **Separate Systems**: CLI and SDK session management are kept separate
  - CLI sessions: Used by MCP server (stored in SessionChainStore)
  - SDK sessions: Used by Web UI (UUID conversation IDs)
- **Session Persistence**: Conversations maintain context across messages
- **UUID Detection**: System automatically detects SDK conversation IDs by UUID format

### Authentication
- Uses OAuth subscription authentication via `~/.claude/.credentials.json`
- No API keys required - works with Claude Max subscription
- Automatic fallback to OAuth when no API key is present

### Real-time Streaming
- WebSocket connection for instant message delivery
- Streaming text responses as they're generated
- Tool use visualization
- Proper completion detection to re-enable input

## Directory Structure
```
web-ui/
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.tsx        # Agent selection grid
│   │   │   └── Chat.tsx        # Chat interface
│   │   ├── components/
│   │   │   ├── AgentCard.tsx   # Agent display card
│   │   │   ├── AuthStatus.tsx  # OAuth status indicator
│   │   │   └── ChatMessage.tsx # Message rendering
│   │   └── lib/
│   │       ├── api.ts          # REST API client
│   │       └── websocket.ts    # WebSocket client
│   └── package.json
└── backend/
    ├── main.py                  # FastAPI server
    └── requirements.txt         # Python dependencies

src/sdk_integration/
├── sdk_executor.py              # SDK execution logic
└── agent_executor.py            # Agent orchestration
```

## Running the Web UI

### Prerequisites
1. Python 3.11+ with virtual environment
2. Node.js 18+ for frontend
3. Claude Code SDK installed
4. OAuth credentials configured

### Start Backend
```bash
cd web-ui/backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend
```bash
cd web-ui/frontend
npm install
npm run dev
```

Access the UI at `http://localhost:5173`

## Session Resumption Flow

1. **First Message**:
   - User sends message via WebSocket
   - Backend creates new session with unique session_id
   - SDK executor starts fresh (no conversation_id)
   - SDK returns conversation_id in response
   - Backend stores conversation_id for session

2. **Subsequent Messages**:
   - User sends message in same WebSocket session
   - Backend retrieves stored conversation_id
   - Passes conversation_id to SDK executor
   - SDK executor detects UUID format and uses it for resumption
   - Agent maintains context from previous messages

## Implementation Details

### SDK Session Detection
```python
# In agent_executor.py
sdk_session_id = None
if session_id and '-' in str(session_id):  # UUID format check
    sdk_session_id = session_id
    logger.info(f"Using SDK conversation ID for resumption: {sdk_session_id}")
```

### WebSocket Message Format
```typescript
interface ChatMessage {
  type: 'text' | 'tool_use' | 'error' | 'session_info' | 'usage' | 'complete'
  content?: any
  conversation_id?: string
  session_id?: string
}
```

### Completion Detection
The frontend detects response completion through:
- `session_info` messages with conversation_id
- `usage` messages with token counts
- Explicit `complete` messages
- This ensures the input field re-enables after responses

## Testing

### Manual Testing
1. Open chat with an agent
2. Send "Remember my favorite color is blue"
3. Send "What's my favorite color?"
4. Agent should recall the color from context

### Direct SDK Testing
```bash
python3 test_sdk_resumption.py
```

## Troubleshooting

### Session Not Persisting
- Check backend logs for conversation_id tracking
- Verify SDK executor receives session_id
- Ensure agent has `resume-session: true` in config

### Input Stuck Loading
- Check for proper completion signals in WebSocket
- Verify backend sends session_info or complete message
- Check browser console for WebSocket errors

### SDK Not Available
- Install in backend venv: `pip install claude-code-sdk`
- Restart backend server after installation
- Check for import errors in logs

## Future Improvements
- Add conversation history persistence
- Implement conversation branching
- Add export functionality
- Support multiple concurrent conversations
- Add user authentication and multi-user support