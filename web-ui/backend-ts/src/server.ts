/**
 * TypeScript backend for Task Agent Web UI
 * Using @anthropic-ai/claude-code SDK for full feature support
 * Runs on port 8001 (parallel to Python backend on 8000)
 */

import express, { Request, Response } from 'express';
import cors from 'cors';
import { WebSocketServer } from 'ws';
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
  path: '/ws' // Will handle /ws/chat/:sessionId later
});

// WebSocket connection handler (placeholder)
wss.on('connection', (ws) => {
  console.log('New WebSocket connection');
  
  ws.on('message', (message) => {
    console.log('Received:', message.toString());
    // TODO: Implement agent execution
    ws.send(JSON.stringify({
      type: 'info',
      content: { text: 'TypeScript backend connected (not yet implemented)' }
    }));
  });
  
  ws.on('close', () => {
    console.log('WebSocket connection closed');
  });
  
  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
  });
});

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
║  Status: Ready for Phase 2 implementation                 ║
╚════════════════════════════════════════════════════════════╝
  `);
});