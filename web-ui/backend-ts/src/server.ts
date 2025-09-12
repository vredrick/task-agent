/**
 * TypeScript backend for Task Agent Web UI
 * Using @anthropic-ai/claude-code SDK for full feature support
 * Runs on port 8001 (parallel to Python backend on 8000)
 */

import express, { Request, Response } from 'express';
import cors from 'cors';
import { WebSocketServer, WebSocket } from 'ws';
import http from 'http';
import path from 'path';
import dotenv from 'dotenv';
import { oauthManager, AgentManager, SDKExecutor } from '../../../src/sdk_integration_ts';
import type { SDKMessage, AuthStatus } from '../../../src/sdk_integration_ts';

// Load environment variables
dotenv.config();

// Constants
const PORT = process.env.PORT || 8001;
const AGENTS_PATH = process.env.TASK_AGENTS_PATH || path.join(__dirname, '../../../task-agents');

// Initialize agent manager and SDK executor
const agentManager = new AgentManager(AGENTS_PATH);
const sdkExecutor = new SDKExecutor();

// Load agents on startup
(async () => {
  await agentManager.loadAgents();
  console.log(`Loaded ${agentManager.listAgents().length} agents from ${AGENTS_PATH}`);
})();

// Create Express app
const app = express();

// Middleware
app.use(express.json());
app.use(cors({
  origin: ['http://localhost:5173', 'http://localhost:3000'], // Match Python backend
  credentials: true,
}));

// Health check endpoint
app.get('/api/health', (req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    backend: 'typescript',
    port: PORT,
    sdk: '@anthropic-ai/claude-code',
    agentsPath: AGENTS_PATH,
    timestamp: new Date().toISOString()
  });
});

// API info endpoint
app.get('/api/info', (req: Request, res: Response) => {
  res.json({
    name: 'Task Agent TypeScript Backend',
    version: '1.0.0',
    description: 'TypeScript implementation using @anthropic-ai/claude-code SDK',
    features: [
      'Full streaming support with partial messages',
      'Direct SDK integration',
      'Session management',
      'OAuth authentication',
      'WebSocket streaming'
    ],
    endpoints: {
      health: '/api/health',
      info: '/api/info',
      auth: '/api/auth/status',
      agents: '/api/agents',
      agentDetail: '/api/agents/:name',
      execute: '/api/execute (POST)',
      sessions: '/api/sessions',
      deleteSession: '/api/sessions/:sessionId (DELETE)',
      chat: '/ws/chat/:sessionId (Phase 5)'
    }
  });
});

// Authentication status endpoint - matches Python backend exactly
app.get('/api/auth/status', async (req: Request, res: Response) => {
  const status = await oauthManager.getAuthStatus();
  res.json(status);
});

// Agents list endpoint - matches Python backend
app.get('/api/agents', (req: Request, res: Response) => {
  const agents = agentManager.getAllAgentsMetadata();
  res.json({ agents });
});

// Single agent endpoint - matches Python backend
app.get('/api/agents/:name', (req: Request, res: Response) => {
  const { name } = req.params;
  const agent = agentManager.getAgent(name);
  
  if (!agent) {
    return res.status(404).json({
      error: 'Agent not found',
      available: false
    });
  }
  
  res.json({
    ...agent,
    available: true
  });
});

// Session management endpoints
app.get('/api/sessions', (req: Request, res: Response) => {
  const sessions = sdkExecutor.getAvailableSessions();
  res.json({ sessions });
});

app.delete('/api/sessions/:sessionId', (req: Request, res: Response) => {
  const { sessionId } = req.params;
  const deleted = sdkExecutor.clearSession(sessionId);
  res.json({ success: deleted });
});

// Test execution endpoint (for Phase 4 testing)
app.post('/api/execute', async (req: Request, res: Response) => {
  const { agentName, prompt, sessionId, sessionReset, maxTurns, includePartialMessages } = req.body;
  
  if (!agentName || !prompt) {
    return res.status(400).json({
      error: 'Missing required parameters: agentName and prompt'
    });
  }
  
  const agent = agentManager.getAgent(agentName);
  if (!agent) {
    return res.status(404).json({
      error: `Agent "${agentName}" not found`
    });
  }
  
  try {
    const messages: SDKMessage[] = [];
    const generator = await sdkExecutor.executeAgent(agent, prompt, {
      sessionId,
      sessionReset,
      maxTurns,
      includePartialMessages,
      abortController: new AbortController()
    });
    
    // Collect all messages
    for await (const message of generator) {
      messages.push(message);
    }
    
    // Return collected messages
    res.json({
      success: true,
      messages,
      sessionId: messages.find(m => m.type === 'system' && m.subtype === 'init')?.session_id
    });
  } catch (error: any) {
    res.status(500).json({
      error: 'Execution failed',
      details: error.message
    });
  }
});

// Create HTTP server
const server = http.createServer(app);

// Create WebSocket server
const wss = new WebSocketServer({ 
  server,
  path: '/ws'
});

// Active WebSocket connections mapped by session ID
const activeConnections = new Map<string, { ws: WebSocket; abortController: AbortController }>();

// WebSocket connection handler
wss.on('connection', (ws, req) => {
  // Extract session ID from URL path
  const url = req.url || '';
  const pathMatch = url.match(/^\/chat\/([^?]+)/);
  const sessionId = pathMatch ? pathMatch[1] : null;
  
  if (!sessionId) {
    ws.send(JSON.stringify({
      type: 'error',
      content: { text: 'Session ID required in path: /ws/chat/:sessionId' }
    }));
    ws.close();
    return;
  }
  
  console.log(`New WebSocket connection for session: ${sessionId}`);
  
  // Create abort controller for this connection
  const abortController = new AbortController();
  activeConnections.set(sessionId, { ws, abortController });
  
  // Send initial connection confirmation
  ws.send(JSON.stringify({
    type: 'metadata',
    content: {
      session_id: sessionId,
      backend: 'typescript',
      connected: true,
      timestamp: new Date().toISOString()
    }
  }));
  
  ws.on('message', async (message) => {
    try {
      const data = JSON.parse(message.toString());
      console.log('Received message:', data);
      
      // Handle different message types
      switch (data.type) {
        case 'chat':
          await handleChatMessage(ws, sessionId, data, abortController);
          break;
        case 'interrupt':
          handleInterrupt(sessionId);
          break;
        case 'ping':
          ws.send(JSON.stringify({ type: 'pong' }));
          break;
        default:
          ws.send(JSON.stringify({
            type: 'error',
            content: { text: `Unknown message type: ${data.type}` }
          }));
      }
    } catch (error: any) {
      console.error('WebSocket message error:', error);
      ws.send(JSON.stringify({
        type: 'error',
        content: { text: error.message || 'Failed to process message' }
      }));
    }
  });
  
  ws.on('close', () => {
    console.log(`WebSocket connection closed for session: ${sessionId}`);
    // Clean up and abort any running operations
    const connection = activeConnections.get(sessionId);
    if (connection) {
      connection.abortController.abort();
      activeConnections.delete(sessionId);
    }
  });
  
  ws.on('error', (error) => {
    console.error(`WebSocket error for session ${sessionId}:`, error);
  });
});

// Handle chat messages
async function handleChatMessage(
  ws: WebSocket,
  sessionId: string,
  data: any,
  abortController: AbortController
) {
  const { agentName, prompt, sessionReset, maxTurns } = data;
  
  if (!agentName || !prompt) {
    ws.send(JSON.stringify({
      type: 'error',
      content: { text: 'Missing required fields: agentName and prompt' }
    }));
    return;
  }
  
  const agent = agentManager.getAgent(agentName);
  if (!agent) {
    ws.send(JSON.stringify({
      type: 'error',
      content: { text: `Agent "${agentName}" not found` }
    }));
    return;
  }
  
  try {
    // Execute agent with streaming
    const generator = await sdkExecutor.executeAgent(agent, prompt, {
      sessionId,
      sessionReset,
      maxTurns,
      includePartialMessages: true, // Always enable for WebSocket streaming
      abortController
    });
    
    // Stream messages to client
    for await (const message of generator) {
      // Transform SDK message to frontend format
      const frontendMessage = transformSDKMessage(message);
      if (frontendMessage) {
        ws.send(JSON.stringify(frontendMessage));
      }
    }
    
    // Send completion signal
    ws.send(JSON.stringify({
      type: 'metadata',
      content: {
        event: 'stream_complete',
        session_id: sessionId,
        timestamp: new Date().toISOString()
      }
    }));
    
  } catch (error: any) {
    if (error.name === 'AbortError') {
      ws.send(JSON.stringify({
        type: 'metadata',
        content: {
          event: 'stream_interrupted',
          session_id: sessionId
        }
      }));
    } else {
      ws.send(JSON.stringify({
        type: 'error',
        content: { text: error.message || 'Execution failed' }
      }));
    }
  }
}

// Handle interrupt requests
function handleInterrupt(sessionId: string) {
  const connection = activeConnections.get(sessionId);
  if (connection) {
    console.log(`Interrupting session: ${sessionId}`);
    connection.abortController.abort();
    connection.ws.send(JSON.stringify({
      type: 'metadata',
      content: {
        event: 'interrupt_acknowledged',
        session_id: sessionId
      }
    }));
  }
}

// Transform SDK messages to frontend format
function transformSDKMessage(sdkMessage: SDKMessage): any {
  switch (sdkMessage.type) {
    case 'text':
      return {
        type: 'text',
        content: { text: sdkMessage.text }
      };
    
    case 'text_delta':
      return {
        type: 'text_delta',
        content: { text: sdkMessage.text }
      };
    
    case 'tool_use':
      return {
        type: 'tool_use',
        content: {
          tool_name: sdkMessage.tool_name,
          tool_params: sdkMessage.tool_params
        }
      };
    
    case 'tool_result':
      return {
        type: 'tool_result',
        content: {
          tool_name: sdkMessage.tool_name,
          result: sdkMessage.result,
          is_error: sdkMessage.is_error
        }
      };
    
    case 'system':
      if (sdkMessage.subtype === 'init') {
        return {
          type: 'metadata',
          content: {
            event: 'session_init',
            session_id: sdkMessage.session_id,
            model: sdkMessage.model
          }
        };
      } else if (sdkMessage.subtype === 'usage') {
        return {
          type: 'metadata',
          content: {
            event: 'usage',
            ...sdkMessage.usage
          }
        };
      }
      break;
    
    case 'stream_event':
      // Handle specific stream events if needed
      if (sdkMessage.event === 'content_block_delta' && sdkMessage.delta?.text) {
        return {
          type: 'text_delta',
          content: { text: sdkMessage.delta.text }
        };
      }
      break;
    
    case 'error':
      return {
        type: 'error',
        content: { text: sdkMessage.error }
      };
  }
  
  return null; // Filter out unhandled message types
}

// Start server
server.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║                TypeScript Backend Started                  ║
╠════════════════════════════════════════════════════════════╣
║  Port:        ${PORT}                                         ║
║  Health:      http://localhost:${PORT}/api/health             ║
║  Info:        http://localhost:${PORT}/api/info               ║
║  WebSocket:   ws://localhost:${PORT}/ws/chat/:sessionId       ║
║  Agents Path: ${AGENTS_PATH.padEnd(45, ' ')}║
║                                                            ║
║  Status: Phase 5 - WebSocket Streaming Active             ║
╚════════════════════════════════════════════════════════════╝
  `);
});