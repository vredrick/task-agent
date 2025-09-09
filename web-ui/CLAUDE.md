# Web UI Documentation

## Purpose

This directory contains a modern web interface for interacting with task agents through direct SDK integration. The UI provides a user-friendly alternative to CLI interaction, offering real-time streaming responses with word-by-word animation, session management, and visual feedback for agent operations.

## Architecture Overview

The Web UI implements a client-server architecture with WebSocket support for real-time streaming:

```
web-ui/
├── backend/          # FastAPI server with SDK integration
│   ├── main.py      # API endpoints, WebSocket handler, agent executor
│   └── venv/        # Python virtual environment
└── frontend/        # React TypeScript application
    ├── src/
    │   ├── pages/          # React page components
    │   ├── components/     # Reusable UI components
    │   │   ├── ai-elements/  # AI-specific UI components
    │   │   └── ui/           # Base UI components (shadcn/ui)
    │   ├── hooks/          # Custom React hooks
    │   └── lib/            # API clients and utilities
    └── dist/            # Production build output
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
```typescript
// Client -> Server
{
  agent_name: string,
  message: string,
  session_reset?: boolean
}

// Server -> Client
{
  type: "text" | "tool_use" | "error" | "complete" | "metadata",
  content?: {
    text?: string        // For text chunks
  },
  name?: string,         // For tool use
  input?: any,           // For tool use
  error?: string,        // For errors
  data?: {               // For metadata
    cost: number,
    duration: number,
    tokens: number,
    session_id: string
  }
}
```

## Session Management

- Sessions identified by UUID
- Stored in backend memory (ephemeral)
- Reset capability through UI button
- Automatic cleanup on disconnect
- **Session Resumption Chain**:
  - Each SDK response includes a new `session_id`
  - Backend extracts and stores this from metadata
  - Next message uses the latest `session_id` for continuity
  - Only active when agent has `resume-session: true`
  - Creates conversation chains maintaining full context

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
- Check that backend is extracting session_id from metadata
- Ensure frontend is maintaining WebSocket session UUID
- Note: Each message gets a new session_id for chaining

## Related Documentation

- Main project: [/CLAUDE.md](/home/vredrick/task-agent/CLAUDE.md)
- SDK Integration: [/src/CLAUDE.md](/home/vredrick/task-agent/src/CLAUDE.md)
- Agent configurations: `../task-agents/*.md`