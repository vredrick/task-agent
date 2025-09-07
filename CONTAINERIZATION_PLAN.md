# Containerized Web Agents - Implementation Plan

## Executive Summary

Transform the current local task-agents system into a containerized web platform where users can create, configure, and interact with AI agents through a web UI. The system will maintain all existing functionality while replacing the Claude CLI subprocess calls with the Claude Code SDK for better container compatibility.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Web Browser                          │
│  ┌────────────────────┐      ┌──────────────────────────┐  │
│  │   Agent Builder    │      │    Agent Chat Interface   │  │
│  │  (Create/Edit)     │      │   (Like REPL but in Web)  │  │
│  └────────────────────┘      └──────────────────────────┘  │
└─────────────┬──────────────────────┬───────────────────────┘
              │                      │
              ▼                      ▼
┌─────────────────────────────────────────────────────────────┐
│            FastAPI Web Server (Container)                   │
│  ┌────────────────────┐      ┌──────────────────────────┐  │
│  │   Agent Manager    │      │   WebSocket Handler      │  │
│  │  (CRUD Operations) │      │  (Real-time Chat)        │  │
│  └────────────────────┘      └──────────────────────────┘  │
└─────────────┬──────────────────────┬───────────────────────┘
              │                      │
              ▼                      ▼
┌─────────────────────────────────────────────────────────────┐
│         Agent Execution Layer (SDK-based)                   │
│  ┌────────────────────┐      ┌──────────────────────────┐  │
│  │  Claude Code SDK   │      │   JSON Stream Parser     │  │
│  │  (Replaces CLI)    │      │   (Existing Logic)       │  │
│  └────────────────────┘      └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Phase 1: SDK Integration (Week 1)

### Goal
Replace Claude CLI subprocess calls with Claude Code SDK while maintaining exact same functionality.

### Tasks

#### 1.1 Install Claude Code SDK
```bash
# Option 1: Standard SDK + claude-max for subscription support
pip install claude-code-sdk claude-max

# Option 2: Just the standard SDK (will use OAuth if no API key)
pip install claude-code-sdk
```

#### 1.2 Create SDK Adapter Module
Create `src/task_agents_mcp/sdk_executor.py`:
```python
# Option A: Using claude-max package (recommended for subscriptions)
try:
    from claude_max import ClaudeMaxClient
    HAS_CLAUDE_MAX = True
except ImportError:
    HAS_CLAUDE_MAX = False
    from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions

import asyncio
import json
import os

class SDKExecutor:
    """Drop-in replacement for CLI subprocess execution"""
    
    async def execute_task(self, agent_config, task_description, 
                          session_id=None, progress_callback=None):
        """Execute agent task using SDK instead of CLI subprocess"""
        
        # IMPORTANT: Don't set ANTHROPIC_API_KEY to use subscription OAuth
        # SDK will automatically use ~/.claude/credentials.json
        if 'ANTHROPIC_API_KEY' in os.environ and HAS_CLAUDE_MAX:
            del os.environ['ANTHROPIC_API_KEY']  # Force OAuth fallback
        
        if HAS_CLAUDE_MAX:
            # Use claude-max for subscription support
            client = ClaudeMaxClient(
                system_prompt=agent_config.system_prompt,
                allowed_tools=agent_config.tools,
                model=agent_config.model,
                cwd=agent_config.cwd,
                continue_conversation=session_id,
                output_format="stream-json",  # Same as CLI
                verbose=True
            )
        else:
            # Fallback to standard SDK (will use OAuth if no API key)
            options = ClaudeCodeOptions(
                system_prompt=agent_config.system_prompt,
                allowed_tools=agent_config.tools,
                model=agent_config.model,
                cwd=agent_config.cwd,
                continue_conversation=session_id,
                output_format="stream-json",  # Same as CLI
                verbose=True
            )
            client = ClaudeSDKClient(options=options)
        
        # Execute and stream results (same JSON format as CLI)
        async with client as c:
            await c.query(task_description)
            
            # Stream responses in same format as subprocess
            async for message in c.receive_response():
                # SDK outputs same stream-json format
                yield message
```

#### 1.3 Update AgentManager
Modify `src/task_agents_mcp/agent_manager.py`:
- Add SDK/CLI switch based on environment variable
- Keep all JSON parsing logic unchanged
- Maintain session management as-is

#### 1.4 Test Compatibility
- Verify SDK outputs identical JSON format
- Ensure session resumption works
- Test all existing agents

### Deliverables
- [ ] SDK executor module
- [ ] Updated agent_manager.py with SDK option
- [ ] Test suite comparing CLI vs SDK outputs
- [ ] Documentation updates

## Authentication Strategy for Claude Subscriptions

### Using OAuth with Claude Max/Pro Subscriptions

The SDK can authenticate using your Claude subscription (Pro/Max) instead of API keys. This is crucial for cost savings and utilizing your subscription benefits.

#### Key Insights
1. **Authentication Precedence**: API Key > OAuth > Subscription
2. **Force OAuth**: Remove `ANTHROPIC_API_KEY` to use subscription
3. **Credentials Location**: OAuth tokens stored in `~/.claude/.credentials.json`
4. **Context Window**: API keys provide 1M tokens vs 200K for subscriptions

#### Implementation Options

**Option 1: claude-max Package (Recommended)**
```python
pip install claude-max  # Arthur Colle's package
# Automatically uses subscription OAuth
```

**Option 2: Standard SDK with OAuth Fallback**
```python
# Don't set ANTHROPIC_API_KEY
# SDK will use ~/.claude/.credentials.json automatically
```

**Option 3: Container Credential Mounting**
```yaml
volumes:
  - ~/.claude:/root/.claude:ro  # Mount credentials read-only
```

## Phase 2: Containerization (Week 1-2)

### Goal
Package the application in Docker containers with proper isolation and resource management.

### Tasks

#### 2.1 Create Base Dockerfile
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN pip install -e . claude-code-sdk claude-max fastapi uvicorn

# Copy agent configurations
COPY task-agents/ ./task-agents/

# Environment setup
ENV TASK_AGENTS_PATH=/app/task-agents
ENV USE_SDK=true
# IMPORTANT: Don't set ANTHROPIC_API_KEY to use subscription OAuth
# The SDK will use mounted credentials from ~/.claude/credentials.json

# Agent workspace
RUN mkdir -p /workspace
RUN mkdir -p /root/.claude  # For OAuth credentials

EXPOSE 8000

CMD ["python", "-m", "task_agents_mcp.web_server"]
```

#### 2.2 Docker Compose for Development
```yaml
# docker-compose.yml
version: '3.8'

services:
  web-agents:
    build: .
    ports:
      - "8000:8000"
    environment:
      # Don't set ANTHROPIC_API_KEY - use OAuth from mounted credentials
      - DATABASE_URL=postgresql://postgres:password@db:5432/agents
      - USE_SDK=true
    volumes:
      - ./task-agents:/app/task-agents:ro
      - agent-workspaces:/workspace
      # Mount Claude OAuth credentials (read-only)
      - ~/.claude:/root/.claude:ro
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=agents
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  agent-workspaces:
  postgres-data:
```

#### 2.3 Security & Resource Limits
```yaml
# Add to docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 1G
```

### Deliverables
- [ ] Dockerfile with SDK integration
- [ ] Docker Compose configuration
- [ ] Container security hardening
- [ ] Resource limit configuration

## Phase 3: Web API Development (Week 2)

### Goal
Create FastAPI backend for agent management and execution.

### Tasks

#### 3.1 Create Web Server Module
Create `src/task_agents_mcp/web_server.py`:
```python
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI(title="Task Agents Web API")

# CORS for web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agent CRUD endpoints
@app.get("/api/agents")
async def list_agents():
    """List all available agents"""
    return agent_manager.get_agents_info()

@app.post("/api/agents")
async def create_agent(agent_config: dict):
    """Create new agent configuration"""
    # Save to task-agents directory
    # Return agent ID

@app.put("/api/agents/{agent_id}")
async def update_agent(agent_id: str, agent_config: dict):
    """Update existing agent"""
    # Update .md file
    # Reload agent

# WebSocket for chat interface
@app.websocket("/ws/agent/{agent_id}")
async def agent_chat(websocket: WebSocket, agent_id: str):
    """WebSocket endpoint for agent interaction"""
    await websocket.accept()
    
    # Get agent config
    agent = agent_manager.get_agent(agent_id)
    if not agent:
        await websocket.close(code=4004)
        return
    
    # Create SDK executor for this session
    executor = SDKExecutor()
    
    while True:
        # Receive query from web UI
        data = await websocket.receive_text()
        query = json.loads(data)
        
        # Execute via SDK (same as REPL)
        async for response in executor.execute_task(
            agent, 
            query['prompt'],
            session_id=query.get('session_id')
        ):
            # Send stream-json responses to UI
            await websocket.send_text(response)
```

#### 3.2 Session Management API
```python
@app.get("/api/sessions/{agent_id}")
async def get_sessions(agent_id: str):
    """Get session history for agent"""
    return session_store.get_agent_sessions(agent_id)

@app.post("/api/sessions/{agent_id}/reset")
async def reset_session(agent_id: str):
    """Reset agent session"""
    session_store.clear_chain(agent_id)
    return {"status": "reset"}
```

### Deliverables
- [ ] FastAPI web server module
- [ ] Agent CRUD endpoints
- [ ] WebSocket chat handler
- [ ] Session management API
- [ ] API documentation (OpenAPI)

## Phase 4: Web UI Development (Week 2-3)

### Goal
Create React-based web interface for agent management and interaction.

### Tasks

#### 4.1 Project Setup
```bash
# Create React app with TypeScript
npx create-react-app agent-web-ui --template typescript
cd agent-web-ui
npm install axios socket.io-client @mui/material
```

#### 4.2 Agent Builder Interface
```typescript
// src/components/AgentBuilder.tsx
interface AgentConfig {
  agentName: string;
  description: string;
  tools: string[];
  model: 'haiku' | 'sonnet' | 'opus';
  systemPrompt: string;
  resumeSession: boolean | number;
}

function AgentBuilder() {
  const [config, setConfig] = useState<AgentConfig>({
    agentName: '',
    description: '',
    tools: ['Read', 'Write'],
    model: 'haiku',
    systemPrompt: '',
    resumeSession: false
  });

  const saveAgent = async () => {
    const response = await axios.post('/api/agents', config);
    // Handle response
  };

  return (
    <form>
      {/* Form fields for agent configuration */}
      {/* Tool selection checkboxes */}
      {/* Model dropdown */}
      {/* System prompt textarea */}
    </form>
  );
}
```

#### 4.3 Chat Interface (Like REPL)
```typescript
// src/components/AgentChat.tsx
function AgentChat({ agentId }: { agentId: string }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const ws = useRef<WebSocket>();

  useEffect(() => {
    // Connect WebSocket
    ws.current = new WebSocket(`ws://localhost:8000/ws/agent/${agentId}`);
    
    ws.current.onmessage = (event) => {
      // Parse stream-json response
      const data = JSON.parse(event.data);
      // Update messages (same parsing as REPL)
    };
  }, [agentId]);

  const sendMessage = () => {
    ws.current?.send(JSON.stringify({ prompt: input }));
    setInput('');
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {/* Render messages with syntax highlighting */}
      </div>
      <input 
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
      />
    </div>
  );
}
```

#### 4.4 Features from REPL
- Session indicator
- Token usage display
- Tool usage tracking
- Conversation history
- Session reset button

### Deliverables
- [ ] React TypeScript application
- [ ] Agent builder component
- [ ] Chat interface (REPL-like)
- [ ] Agent selector/list view
- [ ] Session management UI

## Phase 5: Remote MCP Server Support (Week 3)

### Goal
Add streamable HTTP transport to expose containerized agents via MCP protocol.

### Tasks

#### 5.1 Add HTTP Transport to Server
Update `src/task_agents_mcp/server.py`:
```python
def main():
    """Main entry point for the server."""
    import sys
    
    if "--http" in sys.argv or os.environ.get("MCP_TRANSPORT") == "http":
        # Run as remote MCP server with streamable HTTP
        mcp.run(
            transport="streamable-http",
            host="0.0.0.0",
            port=8080,
            path="/mcp"
        )
    else:
        # Run as local stdio (current behavior)
        mcp.run()
```

#### 5.2 MCP Endpoint in Web Server
```python
@app.post("/mcp")
async def mcp_endpoint(request: dict):
    """MCP protocol endpoint for Claude Code clients"""
    # Forward to FastMCP server
    # Return streamable HTTP response
```

### Deliverables
- [ ] Streamable HTTP transport support
- [ ] MCP endpoint in web server
- [ ] Client connection instructions
- [ ] Testing with Claude Code

## Phase 6: Deployment (Week 3-4)

### Goal
Deploy to cloud platforms with proper production configuration.

### Tasks

#### 6.1 Railway Deployment
```json
// railway.json
{
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "python -m task_agents_mcp.web_server",
    "healthcheckPath": "/health",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

#### 6.2 Environment Configuration
```bash
# .env.production
# Option A: For subscription users (recommended)
# Don't set ANTHROPIC_API_KEY - use OAuth from mounted credentials
USE_SDK=true
USE_CLAUDE_MAX=true  # If using claude-max package

# Option B: For API key users
# ANTHROPIC_API_KEY=sk-ant-api03-xxx  # Only if not using subscription

DATABASE_URL=postgresql://...
REDIS_URL=redis://...
ALLOWED_ORIGINS=https://yourdomain.com
```

#### 6.3 Production Optimizations
- Redis for session caching
- PostgreSQL for agent persistence
- CDN for static assets
- SSL/TLS termination

### Deliverables
- [ ] Railway configuration
- [ ] Production environment setup
- [ ] Monitoring and logging
- [ ] Deployment documentation

## Migration Path

### For Existing Users
1. **Export agents**: Copy `.md` files from local `task-agents/`
2. **Import to web**: Upload via web UI or API
3. **Update connection**: Point Claude Code to remote MCP server
4. **Verify functionality**: Test all agents work as before

### Backward Compatibility
- Local MCP server continues to work
- CLI aliases remain functional
- REPL mode unchanged
- Only backend execution changes (CLI → SDK)

## Success Metrics

### Functional Requirements
- [ ] All existing agents work unchanged
- [ ] JSON parsing produces identical output
- [ ] Session management maintains state
- [ ] Web UI replicates REPL functionality

### Performance Requirements
- [ ] Agent response time < 2s initial
- [ ] WebSocket latency < 100ms
- [ ] Container startup < 5s
- [ ] Concurrent users: 100+

### Security Requirements
- [ ] OAuth token authentication
- [ ] Container isolation per user
- [ ] Resource limits enforced
- [ ] No direct file system access

## Risk Mitigation

### Technical Risks
1. **SDK output format differs**: Maintain compatibility layer
2. **Session state loss**: Implement persistent storage
3. **WebSocket disconnections**: Add reconnection logic
4. **Container resource exhaustion**: Set hard limits

### Mitigation Strategies
- Extensive testing of SDK vs CLI outputs
- Database-backed session storage
- WebSocket heartbeat and auto-reconnect
- Kubernetes horizontal pod autoscaling

## Timeline

### Week 1
- SDK integration
- Basic containerization
- Local testing

### Week 2
- Web API development
- WebSocket implementation
- Basic UI components

### Week 3
- Complete web UI
- MCP HTTP transport
- Integration testing

### Week 4
- Production deployment
- Performance optimization
- Documentation

## Next Steps

1. **Set up development environment**
   ```bash
   git checkout containerized-web-agents
   pip install claude-code-sdk
   ```

2. **Create SDK executor module**
   - Start with `sdk_executor.py`
   - Test with existing agents

3. **Build container locally**
   - Create Dockerfile
   - Test with docker-compose

4. **Begin web API development**
   - Set up FastAPI structure
   - Implement first endpoint

## Conclusion

This plan transforms the task-agents system from a local CLI tool to a scalable web platform while maintaining all existing functionality. The key insight is that the Claude Code SDK outputs the same stream-json format as the CLI, allowing us to reuse all existing parsing logic and focus on building the new web interface and containerization layer.

The phased approach ensures each component is tested before moving forward, with clear deliverables and success metrics at each stage.