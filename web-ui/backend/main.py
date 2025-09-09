"""FastAPI backend for Task Agent Web UI.

This backend provides:
- Agent listing and execution endpoints
- WebSocket streaming for real-time responses
- OAuth authentication status checking
- Direct SDK integration (no containers/MCP)
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
import json
import logging
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.sdk_integration.agent_executor import AgentExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Task Agent Web UI", version="1.0.0")

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent executor
agent_executor = AgentExecutor(agents_path=str(Path(__file__).parent.parent.parent / "task-agents"))

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

# Session storage (in production, use Redis or similar)
sessions: Dict[str, Dict[str, Any]] = {}


class ChatRequest(BaseModel):
    """Request model for chat messages."""
    agent_name: str
    message: str
    session_id: Optional[str] = None
    session_reset: bool = False


class AuthStatus(BaseModel):
    """Authentication status response."""
    authenticated: bool
    subscription_type: Optional[str] = None
    message: str


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Task Agent Web UI API", "version": "1.0.0"}


@app.get("/api/auth/status", response_model=AuthStatus)
async def get_auth_status():
    """Check OAuth authentication status."""
    try:
        # Check if credentials file exists
        cred_path = Path.home() / ".claude" / ".credentials.json"
        if not cred_path.exists():
            # Try task-agent user path
            cred_path = Path("/home/task-agent/.claude/.credentials.json")
        
        if cred_path.exists():
            with open(cred_path) as f:
                creds = json.load(f)
                if "claudeAiOauth" in creds:
                    oauth = creds["claudeAiOauth"]
                    return AuthStatus(
                        authenticated=True,
                        subscription_type=oauth.get("subscriptionType", "unknown"),
                        message="Claude authenticated"
                    )
        
        return AuthStatus(
            authenticated=False,
            subscription_type=None,
            message="No OAuth credentials found"
        )
    except Exception as e:
        logger.error(f"Error checking auth status: {e}")
        return AuthStatus(
            authenticated=False,
            subscription_type=None,
            message=f"Error checking authentication: {str(e)}"
        )


@app.get("/api/agents")
async def list_agents():
    """List all available agents."""
    try:
        agents = agent_executor.list_agents()
        return {"agents": agents}
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/{agent_name}")
async def get_agent(agent_name: str):
    """Get details for a specific agent."""
    try:
        agent_info = agent_executor.get_agent_info(agent_name)
        if not agent_info:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
        return agent_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for streaming chat responses."""
    await websocket.accept()
    active_connections[session_id] = websocket
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            agent_name = data.get("agent_name")
            message = data.get("message")
            session_reset = data.get("session_reset", False)
            
            if not agent_name or not message:
                await websocket.send_json({
                    "type": "error",
                    "content": "Missing agent_name or message"
                })
                continue
            
            # Get or create session
            if session_id not in sessions:
                sessions[session_id] = {
                    "agent_name": agent_name,
                    "conversation_id": None,
                    "messages": []
                }
                logger.info(f"Created new session {session_id}")
            
            session = sessions[session_id]
            logger.info(f"Session {session_id} - conversation_id: {session.get('conversation_id')}, reset: {session_reset}")
            
            # Stream response from agent
            try:
                response_complete = False
                async for chunk in agent_executor.execute_agent(
                    agent_name=agent_name,
                    prompt=message,
                    session_id=session.get("conversation_id"),
                    session_reset=session_reset
                ):
                    # Parse and forward the chunk
                    try:
                        chunk_data = json.loads(chunk)
                        
                        # Extract conversation ID from metadata
                        if chunk_data.get("type") == "metadata":
                            metadata = chunk_data.get("data", {})
                            new_conv_id = metadata.get("conversation_id") or metadata.get("session_id")
                            if new_conv_id:
                                session["conversation_id"] = new_conv_id
                                logger.info(f"Updated session {session_id} with conversation_id: {new_conv_id}")
                            response_complete = True  # Metadata usually means response is complete
                        
                        # Log tool use for debugging
                        if chunk_data.get("type") == "tool_use":
                            logger.info(f"Sending tool_use to frontend: {chunk_data}")
                        
                        # Send to client
                        await websocket.send_json(chunk_data)
                    except json.JSONDecodeError:
                        # Send raw text if not JSON
                        await websocket.send_json({
                            "type": "text",
                            "content": {"text": chunk}
                        })
                
                # Send completion signal if we didn't get session info
                if not response_complete:
                    await websocket.send_json({
                        "type": "complete",
                        "content": {"message": "Response complete"}
                    })
                        
            except Exception as e:
                logger.error(f"Error executing agent: {e}")
                await websocket.send_json({
                    "type": "error",
                    "content": str(e)
                })
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if session_id in active_connections:
            del active_connections[session_id]


@app.post("/api/chat", response_model=Dict[str, Any])
async def chat(request: ChatRequest):
    """Non-streaming chat endpoint (for testing)."""
    try:
        result = ""
        async for chunk in agent_executor.execute_agent(
            agent_name=request.agent_name,
            prompt=request.message,
            session_id=request.session_id,
            session_reset=request.session_reset
        ):
            try:
                chunk_data = json.loads(chunk)
                if chunk_data.get("type") == "text":
                    result += chunk_data["content"]["text"]
            except:
                result += chunk
                
        return {"response": result}
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)