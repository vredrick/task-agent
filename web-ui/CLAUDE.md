# Web UI Documentation

## Purpose

This directory contains a modern web interface for interacting with task agents through direct SDK integration. The UI provides a user-friendly alternative to CLI interaction, offering real-time streaming responses with word-by-word animation, backend-managed session persistence, and visual feedback for agent operations.

## Architecture Overview

The Web UI implements a clean client-server architecture with complete separation of concerns:

```
web-ui/
├── backend-ts/       # TypeScript backend (PORT 8001) - PRIMARY
│   ├── src/
│   │   └── server.ts     # Express + WebSocket server with SDK integration
│   ├── package.json      # Dependencies including @anthropic-ai/claude-code
│   └── tsconfig.json     # TypeScript configuration
├── backend/          # Python FastAPI backend (PORT 8000) - LEGACY
│   ├── main.py      # API endpoints, WebSocket handler
│   └── venv/        # Python virtual environment
└── frontend/        # React TypeScript application (PORT 5173)
    ├── src/
    │   ├── pages/          # React page components
    │   ├── components/     # Reusable UI components
    │   │   ├── ai-elements/  # AI-specific UI components
    │   │   └── ui/           # Base UI components (shadcn/ui)
    │   ├── hooks/          # Custom React hooks
    │   └── lib/            # API clients and utilities
    └── dist/            # Production build output
```

### Backend-Managed Sessions (NEW)

The TypeScript backend completely manages SDK sessions, creating a clean separation of concerns:

**Backend Responsibilities:**
- Maintains `ConnectionInfo` for each WebSocket connection
- Tracks SDK session IDs independently from connection IDs
- Extracts and stores SDK session IDs from Claude's responses
- Maps connectionId → sdkSessionId for session continuity
- Updates session mapping after each agent response

**Frontend Simplification:**
- Uses `connectionId` only for WebSocket connection tracking
- No session management logic or state
- Pure presentation and UI interaction layer
- Sends minimal data: `agentName`, `prompt`, `sessionReset`

## Key Components

### TypeScript Backend (Express + @anthropic-ai/claude-code SDK)

**server.ts (Port 8001)**
- Express server with WebSocket support via `ws` library
- Full streaming with `includePartialMessages: true` for real-time text deltas
- Backend-managed session architecture:
  ```typescript
  interface ConnectionInfo {
    ws: WebSocket;
    abortController: AbortController;
    sdkSessionId: string | null;  // SDK session for continuity
    agentName: string | null;      // Current agent being used
  }
  ```
- REST endpoints matching Python backend:
  - `GET /api/health` - Backend health check
  - `GET /api/info` - Backend information and features
  - `GET /api/auth/status` - OAuth authentication status
  - `GET /api/agents` - List available agents
  - `GET /api/agents/{name}` - Get agent details
  - `GET /api/sessions` - List active SDK sessions
  - `DELETE /api/sessions/{id}` - Clear specific session
- WebSocket endpoint: `/ws/chat/{connectionId}`
- Direct integration with TypeScript SDK layer (`src/sdk_integration_ts/`)

### Python Backend (FastAPI - Legacy)

**main.py (Port 8000)**
- FastAPI application with CORS middleware
- WebSocket endpoint for streaming chat (`/ws/chat/{session_id}`)
- REST endpoints for agent operations
- Direct integration with `src/sdk_integration/agent_executor.py`
- Being phased out in favor of TypeScript backend

### Frontend (React + TypeScript + Tailwind)

**Pages:**
- `AgentSelection.tsx` - Browse and select available agents with card-based UI
- `Chat.tsx` - Real-time chat interface with streaming animation and tool visualization

**Core Components:**

**AI Elements Components (NEW):**
- `Response` - Markdown renderer using Streamdown for rich text display
- `CodeBlock` - Syntax-highlighted code blocks with copy functionality
- `Loader` - Animated thinking indicator for processing states
- `Tool` - Tool usage visualization with input/output display
- `Conversation` - Chat container with auto-scrolling
- `Message` - Individual message wrapper with avatar support

**Custom Components:**
- `StreamingMessage` - Wraps Response with word-by-word streaming animation
- `ChatMessage` - Legacy message component (being phased out)
- `AgentCard` - Card display for agent selection
- `AuthStatus` - OAuth authentication status indicator

**UI Components (shadcn/ui):**
- `Button`, `Textarea`, `Select` - Form controls
- `Avatar`, `Badge` - Display components
- `Collapsible` - Expandable content sections

**Custom Hooks:**
- `useStreamingText` - Manages word-by-word text streaming animation
  - 40ms delay between words for natural reading pace
  - Buffers incoming chunks and streams smoothly
  - Fills processing gaps to reduce perceived latency

**Libraries:**
- WebSocket client for real-time communication
- API client for REST endpoints
- Tailwind CSS with custom dark blue theme (#1e40af)
- Streamdown for markdown parsing and rendering

## SDK Integration Flow

### TypeScript Backend Flow (backend-ts)

1. **Agent Loading**: Backend imports `AgentManager` from `src/sdk_integration_ts/`
2. **Session Chain Management**:
   - Frontend sends chat with `connectionId` (WebSocket identifier)
   - Backend looks up existing `sdkSessionId` for this connection
   - Executes agent with SDK session ID (or null for new conversation)
   - SDK returns new session ID in `system/init` message
   - Backend updates `connectionInfo.sdkSessionId` for next message
3. **Streaming Pipeline**:
   - SDK configured with `includePartialMessages: true`
   - Transforms `stream_event` → `text_delta` for frontend
   - Filters duplicate messages (skips final complete `assistant` message)
4. **Session Reset**: When `sessionReset: true`, clears stored SDK session

### Message Flow Diagram

```
Frontend                    TypeScript Backend              Claude SDK
   |                              |                              |
   |-- Chat Message ------------->|                              |
   |   {agentName, prompt}        |                              |
   |                              |                              |
   |                              |-- Check connectionInfo ------|
   |                              |   Get sdkSessionId or null   |
   |                              |                              |
   |                              |-- Execute Agent ------------>|
   |                              |   with sessionId             |
   |                              |                              |
   |                              |<-- Stream Events ------------|
   |                              |   Including new session_id   |
   |                              |                              |
   |                              |-- Store new session_id ------|
   |                              |   in connectionInfo          |
   |                              |                              |
   |<-- Text Deltas --------------|                              |
   |    Real-time streaming       |                              |
   |                              |                              |
```

## Development Setup

### Prerequisites
- Python 3.11+ (for SDK compatibility)
- Node.js 18+ (for frontend)
- Claude OAuth credentials in `~/.claude/.credentials.json`

### Quick Start

#### TypeScript Backend (Recommended)
```bash
# Option 1: Use the start script for TypeScript backend
./start-ts.sh

# Option 2: Manual setup
# TypeScript Backend
cd backend-ts
npm install
npm run dev  # Runs on port 8001

# Frontend (configured for TypeScript backend)
cd frontend
npm install
npm run dev  # Runs on port 5173, proxies to 8001
```

#### Python Backend (Legacy)
```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py  # Runs on port 8000

# Frontend (requires vite.config.ts update to proxy to 8000)
cd frontend
npm install
npm run dev  # Runs on port 5173
```

## Configuration

### TypeScript Backend Configuration
- **Port**: 8001 (configured in server.ts)
- **CORS Origins**: localhost:5173, localhost:3000
- **Agent Path**: `../task-agents/` or `TASK_AGENTS_PATH` env var
- **Session Storage**: In-memory with ConnectionInfo mapping
- **SDK Version**: @anthropic-ai/claude-code v1.0.112
- **Streaming**: Real-time with `includePartialMessages: true`

### Python Backend Configuration (Legacy)
- **Port**: 8000 (configured in main.py)
- **CORS Origins**: localhost:5173, localhost:3000
- **Agent Path**: `../task-agents/` (relative to backend)
- **Session Storage**: In-memory dictionary

### Frontend Configuration
- **Vite Proxy**: Configured to forward API calls to backend (port 8001 for TypeScript)
- **WebSocket URL**: `ws://localhost:8001/ws/chat/{connectionId}` (TypeScript backend)
- **Build Output**: `dist/` directory
- **Connection Management**: Uses UUID for connectionId, backend handles SDK sessions

## Dependencies

### TypeScript Backend Dependencies
```json
{
  "@anthropic-ai/claude-code": "^1.0.112",  // Claude SDK with streaming
  "express": "^4.18.2",                      // Web framework
  "ws": "^8.16.0",                           // WebSocket server
  "cors": "^2.8.5",                          // CORS middleware
  "dotenv": "^16.3.1",                       // Environment variables
  "typescript": "^5.3.3",                    // TypeScript compiler
  "tsx": "^4.7.0"                           // TypeScript runner
}
```

### Python Backend Requirements (Legacy)
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
- Streamdown (markdown rendering)
- Radix UI (component primitives)
- class-variance-authority (component variants)
- lucide-react (icons)

## Streaming Architecture (NEW)

### Text Streaming Animation
The frontend implements a sophisticated streaming system that creates a smooth word-by-word animation effect:

1. **Backend Behavior**: SDK returns complete responses, but frontend creates streaming illusion
2. **Chunk Buffering**: WebSocket messages are buffered and streamed word-by-word
3. **Animation Speed**: 40ms per word for natural reading pace
4. **Gap Filling**: Continuous animation fills processing gaps, reducing perceived latency
5. **Message Marking**: Messages flagged with `isStreaming: true` for animation control

### UI Design Principles

**Message Styling:**
- **User Messages**: Dark bubble with rounded corners (`rounded-xl`), user avatar inside
- **AI Messages**: Plain text without background for cleaner appearance
- **Tool Usage**: Dark blue borders (`border-blue-900/30 dark:border-blue-400/30`)
- **Code Blocks**: Syntax highlighting with copy button, line numbers for long snippets

**Color Theme:**
- Primary accent: Dark blue (`#1e40af`) replacing previous orange theme
- Consistent blue tones throughout UI components
- Dark mode optimized with `blue-400` variants

**Input Area Design:**
- Fixed position at bottom of screen
- Textarea expands upward as content grows
- Button controls remain fixed at bottom
- Separated textarea container from action buttons

### Custom CSS Styling

The application includes custom prose styling in `index.css` for optimal markdown rendering:

```css
/* Custom prose classes for Response component */
.prose {
  @apply text-base leading-relaxed text-gray-900 dark:text-gray-100;
}

/* Typography scaling and spacing */
.prose p { @apply mb-4; }
.prose h1 { @apply text-3xl font-bold mb-4 mt-6; }
.prose h2 { @apply text-2xl font-semibold mb-3 mt-5; }
.prose h3 { @apply text-xl font-medium mb-2 mt-4; }

/* Code and blockquote styling */
.prose code:not(pre code) {
  @apply px-1 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-sm;
}
.prose blockquote {
  @apply border-l-4 border-gray-300 dark:border-blue-400/30 pl-4 italic;
}
```

Theme colors are defined using CSS variables for consistency:
- Primary color: Dark blue (`--primary: 213 94% 27%` → `#1e40af`)
- All orange references replaced with blue variants
- Dark mode uses lighter blue shades for contrast

## WebSocket Protocol

### Message Format

#### Client → Server (Frontend to Backend)
```typescript
{
  type: "chat",           // Message type
  agentName: string,      // Agent to use (kebab-case key)
  prompt: string,         // User's message
  sessionReset?: boolean, // Reset conversation context
  maxTurns?: number       // Max conversation turns
}
```

#### Server → Client (Backend to Frontend)
```typescript
// Text streaming delta
{
  type: "text_delta",
  content: { text: string }  // Partial text chunk
}

// Tool usage
{
  type: "tool_use" | "tool_result",
  content: {
    tool_name: string,
    tool_params?: any,      // For tool_use
    result?: any,           // For tool_result
    is_error?: boolean      // For tool_result
  }
}

// Metadata events
{
  type: "metadata",
  content: {
    event: "session_init" | "usage" | "stream_complete",
    session_id?: string,    // SDK session ID (not connection ID)
    model?: string,
    connection_id?: string,
    has_session?: boolean,
    // Usage data for "usage" event
    input_tokens?: number,
    output_tokens?: number,
    total_tokens?: number
  }
}

// Error messages
{
  type: "error",
  content: { text: string }
}
```

## Session Management

### Backend-Managed Architecture

The TypeScript backend completely owns session management:

1. **Connection Tracking**:
   - Frontend generates a UUID `connectionId` for WebSocket connection
   - Backend maintains `ConnectionInfo` object per connection
   - Maps `connectionId` → `sdkSessionId` internally

2. **Session Chain Flow**:
   ```
   Initial Message:
   - Frontend sends: {agentName, prompt}
   - Backend checks: connectionInfo.sdkSessionId (null for new)
   - SDK executes with: sessionId: null
   - SDK returns: new session_id in system/init
   - Backend stores: connectionInfo.sdkSessionId = new_id
   
   Subsequent Messages:
   - Frontend sends: {agentName, prompt}
   - Backend checks: connectionInfo.sdkSessionId (has value)
   - SDK executes with: sessionId: stored_id
   - SDK returns: new session_id for next turn
   - Backend updates: connectionInfo.sdkSessionId = new_id
   ```

3. **Session Reset**:
   - Frontend sends: `sessionReset: true`
   - Backend clears: `connectionInfo.sdkSessionId = null`
   - Next message starts fresh conversation chain

4. **Session Persistence**:
   - Only active when agent has `resume-session: true` in config
   - Each response generates new session ID for chaining
   - Backend transparently manages the session chain
   - Frontend remains stateless regarding sessions

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

**"Session not resuming / Context not maintained"**
- Verify agent has `resume-session: true` in config
- Check backend logs for SDK session ID extraction
- Confirm `connectionInfo.sdkSessionId` is being updated
- Verify WebSocket connection isn't dropping between messages
- Note: Each message creates a new SDK session ID that chains to the previous one

## Related Documentation

- Main project: [/CLAUDE.md](/home/vredrick/task-agent/CLAUDE.md)
- SDK Integration: [/src/CLAUDE.md](/home/vredrick/task-agent/src/CLAUDE.md)
- Agent configurations: `../task-agents/*.md`