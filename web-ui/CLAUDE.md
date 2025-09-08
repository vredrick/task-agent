# Web UI Documentation

## Purpose

This directory contains a modern web interface for interacting with task agents through direct SDK integration. The UI provides a user-friendly alternative to CLI interaction, offering real-time streaming responses, session management, and visual feedback for agent operations.

## Architecture Overview

The Web UI implements a client-server architecture with WebSocket support for real-time streaming:

```
web-ui/
├── backend/          # FastAPI server with SDK integration
│   ├── main.py      # API endpoints, WebSocket handler, agent executor
│   └── venv/        # Python virtual environment
└── frontend/        # React TypeScript application
    ├── src/
    │   ├── pages/   # React page components
    │   ├── components/ # Reusable UI components
    │   └── lib/     # API clients and utilities
    └── dist/        # Production build output
```

## Key Components

### Backend (FastAPI + SDK Integration)

**main.py**
- FastAPI application with CORS middleware
- WebSocket endpoint for streaming chat (`/ws/chat/{session_id}`)
- REST endpoints for agent operations:
  - `GET /api/auth/status` - OAuth authentication check
  - `GET /api/agents` - List available agents
  - `GET /api/agents/{name}` - Get agent details
  - `POST /api/chat` - Non-streaming chat endpoint
- Direct integration with `src/sdk_integration/agent_executor.py`
- Session management for conversation continuity

### Frontend (React + TypeScript + Tailwind)

**Pages:**
- `AgentSelection.tsx` - Browse and select available agents
- `Chat.tsx` - Real-time chat interface with WebSocket streaming

**Components:**
- UI components using Radix UI and Tailwind CSS
- Custom theming with class-variance-authority

**Libraries:**
- WebSocket client for real-time communication
- API client for REST endpoints
- Tailwind CSS for styling

## SDK Integration Flow

1. **Agent Loading**: Backend imports `AgentExecutor` from `src/sdk_integration/`
2. **Direct Execution**: No MCP server or containers needed
3. **Streaming Response**: SDK executor streams through WebSocket
4. **Session Persistence**: Maintains conversation context

## Development Setup

### Prerequisites
- Python 3.11+ (for SDK compatibility)
- Node.js 18+ (for frontend)
- Claude OAuth credentials in `~/.claude/.credentials.json`

### Quick Start
```bash
# Option 1: Use the start script
./start.sh

# Option 2: Manual setup
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py  # Runs on port 8000

# Frontend
cd frontend
npm install
npm run dev  # Runs on port 5173
```

## Configuration

### Backend Configuration
- **Port**: 8000 (configured in main.py)
- **CORS Origins**: localhost:5173, localhost:3000
- **Agent Path**: `../task-agents/` (relative to backend)
- **Session Storage**: In-memory (use Redis for production)

### Frontend Configuration
- **Vite Proxy**: Configured to forward API calls to backend
- **WebSocket URL**: `ws://localhost:8000/ws/chat/{session_id}`
- **Build Output**: `dist/` directory

## Dependencies

### Backend Requirements
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
pydantic==2.5.0
```

### Frontend Stack
- React 18.2.0
- TypeScript 5.2.2
- Vite 5.0.0
- Tailwind CSS 3.3.6
- React Router 6.20.0

## WebSocket Protocol

### Message Format
```typescript
// Client -> Server
{
  agent_name: string,
  message: string,
  session_reset?: boolean
}

// Server -> Client
{
  type: "content" | "tool_use" | "error" | "complete",
  content?: string,
  tool?: {
    name: string,
    input: any
  },
  error?: string
}
```

## Session Management

- Sessions identified by UUID
- Stored in backend memory (ephemeral)
- Reset capability through UI button
- Automatic cleanup on disconnect

## Security Considerations

- OAuth credentials read from local filesystem only
- CORS configured for local development
- WebSocket connections use session IDs
- No external authentication (local use only)

## Production Deployment

For production deployment:
1. Build frontend: `npm run build`
2. Serve static files from `dist/`
3. Configure proper authentication
4. Use Redis/database for session storage
5. Enable HTTPS and WSS
6. Update CORS settings

## Troubleshooting

### Common Issues

**"No OAuth credentials found"**
- Check `~/.claude/.credentials.json` exists
- Verify file permissions

**"WebSocket connection failed"**
- Ensure backend is running on port 8000
- Check CORS settings match frontend URL
- Verify no firewall blocking

**"No agents available"**
- Add `.md` files to `task-agents/` directory
- Check agent file format is valid

## Related Documentation

- Main project: [/CLAUDE.md](/home/vredrick/task-agent/CLAUDE.md)
- SDK Integration: [/src/CLAUDE.md](/home/vredrick/task-agent/src/CLAUDE.md)
- Agent configurations: `../task-agents/*.md`