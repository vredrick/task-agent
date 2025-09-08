# Task Agent Web UI

A web interface for interacting with task agents using direct SDK integration (no containers or MCP server required).

## Features

- 🎯 Agent selection interface with detailed agent information
- 💬 Real-time chat with streaming responses via WebSocket
- 🔐 OAuth authentication using Claude subscription
- 🛠️ Tool usage visualization
- 🔄 Session management with resumption support
- ⚡ Direct SDK execution for fast responses

## Architecture

```
web-ui/
├── backend/          # FastAPI backend with WebSocket support
│   ├── main.py      # API endpoints and WebSocket handler
│   └── requirements.txt
└── frontend/         # React + TypeScript + Tailwind CSS
    ├── src/
    │   ├── pages/    # Agent selection and chat pages
    │   ├── components/
    │   └── lib/      # API and WebSocket clients
    └── package.json
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- Claude OAuth credentials in `~/.claude/.credentials.json` or `/home/task-agent/.claude/.credentials.json`
- Agent configurations in `../task-agents/` directory

## Quick Start

### Option 1: Using the start script

```bash
./start.sh
```

This will:
1. Set up Python virtual environment
2. Install backend dependencies
3. Install frontend dependencies
4. Start both servers
5. Open http://localhost:5173 in your browser

### Option 2: Manual setup

#### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

The backend will run on http://localhost:8000

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will run on http://localhost:5173

## Usage

1. **Agent Selection**: Browse available agents and click "Select Agent"
2. **Chat Interface**: Send messages and receive streaming responses
3. **Session Management**: Use the Reset button to start a new conversation
4. **Tool Usage**: See which tools the agent is using in real-time

## API Endpoints

### REST API
- `GET /api/auth/status` - Check OAuth authentication status
- `GET /api/agents` - List all available agents
- `GET /api/agents/{name}` - Get specific agent details
- `POST /api/chat` - Non-streaming chat (for testing)

### WebSocket
- `WS /ws/chat/{session_id}` - Streaming chat interface

## Configuration

### Backend
- Edit `backend/main.py` to change ports or CORS settings
- Agents are loaded from `../task-agents/` directory

### Frontend
- Edit `frontend/vite.config.ts` to change proxy settings
- Styling uses Tailwind CSS with custom theme

## Troubleshooting

### "No OAuth credentials found"
Ensure Claude credentials exist at:
- `~/.claude/.credentials.json` (user)
- `/home/task-agent/.claude/.credentials.json` (system)

### "No agents available"
Add agent `.md` files to the `../task-agents/` directory

### WebSocket connection fails
- Check that backend is running on port 8000
- Verify CORS settings in `backend/main.py`

### SDK timeout errors
- Use agents with appropriate models (Sonnet recommended)
- Check that OAuth token hasn't expired

## Development

### Backend Development
```bash
cd backend
source venv/bin/activate
python main.py  # Auto-reloads on changes
```

### Frontend Development
```bash
cd frontend
npm run dev  # Hot module replacement enabled
```

### Building for Production
```bash
cd frontend
npm run build  # Creates dist/ directory
```

## Integration with Task Agents

This UI directly uses the SDK integration layer:
- Imports from `src/sdk_integration/`
- Uses `AgentExecutor` for agent management
- Streams responses through `SDKExecutor`
- No MCP server or containers needed

## Security Notes

- OAuth credentials are read from local filesystem
- WebSocket connections use session IDs
- CORS is configured for local development
- In production, use proper authentication and HTTPS

## License

Part of the Task Agent project