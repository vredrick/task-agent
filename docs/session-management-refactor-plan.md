# Session Management Refactor Plan

## Executive Summary

Refactor the Web UI to implement backend-managed session architecture where the backend is the source of truth for SDK session management, and the frontend becomes a simple display layer.

## Current Problem

1. **Frontend generates random UUID** for WebSocket connection
2. **Backend incorrectly uses this UUID** as SDK session ID  
3. **SDK creates its own session IDs** that are ignored
4. **No conversation continuity** - every message starts a new conversation
5. **Session chain is broken** - SDK's session IDs aren't used for next message

## Proposed Solution

Implement a clean separation where:
- **Frontend**: Only displays messages and sends user input
- **Backend**: Manages all session logic and SDK communication
- **SDK**: Provides session IDs for conversation continuity

## Architecture Overview

```
┌─────────────┐     ┌─────────────────┐     ┌────────────┐
│   Frontend  │────▶│     Backend     │────▶│    SDK     │
│             │◀────│                 │◀────│            │
│ (Display)   │     │ (Session Mgmt)  │     │ (AI Agent) │
└─────────────┘     └─────────────────┘     └────────────┘
```

### Session Flow

```
1. First Message:
   Frontend → Backend: {message: "hello", agent: "example-agent"}
   Backend → SDK: {prompt: "hello", resume: null}
   SDK → Backend: {session_id: "sdk-123", response: "..."}
   Backend stores: connectionId → "sdk-123"
   Backend → Frontend: {text: "...", metadata: {connected: true}}

2. Second Message:  
   Frontend → Backend: {message: "follow up", agent: "example-agent"}
   Backend retrieves: connectionId → "sdk-123"
   Backend → SDK: {prompt: "follow up", resume: "sdk-123"}
   SDK → Backend: {session_id: "sdk-456", response: "..."}
   Backend updates: connectionId → "sdk-456"
   Backend → Frontend: {text: "...", metadata: {continuing: true}}
```

## Implementation Steps

### Phase 1: Backend Session Management

#### 1.1 Update `server.ts` Session Store
```typescript
// Add at top level
const connectionToSDKSession = new Map<string, string | null>();

// Track WebSocket connections
const activeConnections = new Map<string, {
  ws: WebSocket,
  abortController: AbortController,
  sdkSessionId: string | null,
  agentName: string | null
}>();
```

#### 1.2 Modify WebSocket Handler
- Store connection with null SDK session initially
- After SDK response, extract and store SDK session ID
- Use stored SDK session for subsequent messages

#### 1.3 Update `handleChatMessage` Function
```typescript
async function handleChatMessage(ws, connectionId, data, abortController) {
  const { agentName, prompt, sessionReset } = data;
  
  // Get stored SDK session for this connection
  const connection = activeConnections.get(connectionId);
  let sdkSessionId = connection?.sdkSessionId || null;
  
  // Reset session if requested
  if (sessionReset) {
    sdkSessionId = null;
    connection.sdkSessionId = null;
  }
  
  // Execute with SDK session (not connection ID!)
  const generator = await sdkExecutor.executeAgent(agent, prompt, {
    sessionId: sdkSessionId,  // Use SDK session or null
    includePartialMessages: true,
    abortController
  });
  
  // Stream and capture new session ID
  let newSDKSessionId = null;
  for await (const message of generator) {
    if (message.type === 'system' && message.subtype === 'init') {
      newSDKSessionId = message.session_id;
      // Update stored session immediately
      if (connection) {
        connection.sdkSessionId = newSDKSessionId;
      }
    }
    // ... stream to frontend
  }
}
```

### Phase 2: SDK Executor Improvements

#### 2.1 Return Session ID in Response
Modify `sdk_executor.ts` to properly communicate session IDs:

```typescript
// Add to SDKMessage interface
export interface SDKExecutorResult {
  messages: AsyncGenerator<SDKMessage>;
  getSessionId: () => string | null;
}

// Update executeAgent to return both generator and session accessor
async executeAgent(agent, prompt, options): Promise<SDKExecutorResult> {
  let currentSessionId = options.sessionId;
  
  const generator = this.streamMessages(prompt, sdkOptions, currentSessionId);
  
  return {
    messages: generator,
    getSessionId: () => currentSessionId
  };
}
```

### Phase 3: Frontend Simplification

#### 3.1 Remove Session ID State
```typescript
// REMOVE this line from Chat.tsx
const [sessionId] = useState(() => crypto.randomUUID())

// REPLACE with connection ID for WebSocket only
const [connectionId] = useState(() => crypto.randomUUID())
```

#### 3.2 Simplify Message Sending
```typescript
// Update sendMessage in websocket.ts
sendMessage(agentName: string, message: string, sessionReset = false) {
  this.ws.send(JSON.stringify({
    type: 'chat',
    agentName: agentName,
    prompt: message,
    sessionReset: sessionReset
    // NO session ID sent from frontend!
  }));
}
```

#### 3.3 Update WebSocket URL
```typescript
// Use connection ID, not session ID
this.url = `${protocol}//${hostname}:${port}/ws/chat/${connectionId}`
```

### Phase 4: Message Protocol Updates

#### 4.1 Frontend → Backend
```typescript
{
  type: 'chat',
  agentName: string,
  prompt: string,
  sessionReset?: boolean  // Optional session reset
}
```

#### 4.2 Backend → Frontend
```typescript
{
  type: 'text_delta' | 'tool_use' | 'metadata' | 'error',
  content: any,
  // Metadata only for connection status, not session details
  metadata?: {
    connected: boolean,
    streaming: boolean
  }
}
```

## Testing Plan

### 1. Unit Tests
- [ ] Backend session mapping (connection → SDK session)
- [ ] SDK executor session extraction
- [ ] Session reset functionality

### 2. Integration Tests
- [ ] First message creates new SDK session
- [ ] Second message continues conversation
- [ ] Session reset starts new conversation
- [ ] Multiple connections maintain separate sessions

### 3. Manual Testing
- [ ] Open chat, send message, verify response
- [ ] Send follow-up, verify context maintained
- [ ] Reset session, verify new conversation
- [ ] Open multiple tabs, verify isolation

## Migration Notes

### Breaking Changes
- Frontend no longer manages sessions
- WebSocket protocol changes
- Connection ID replaces session ID in URLs

### Backward Compatibility
- None required (Web UI is self-contained)
- Python backend remains unchanged
- MCP server unaffected

## Success Criteria

1. **Conversation Continuity**: Follow-up messages maintain context
2. **Session Isolation**: Multiple connections don't interfere
3. **Clean Architecture**: Frontend only handles display
4. **Proper Session Chain**: Each SDK response's session ID used for next message
5. **Session Reset Works**: Can start new conversation on demand

## Risk Mitigation

### Risk 1: Session Memory Leak
**Mitigation**: Implement connection cleanup on WebSocket close

### Risk 2: Lost Sessions on Backend Restart  
**Mitigation**: Document as known limitation for v1, add Redis in v2

### Risk 3: SDK Session Expiration
**Mitigation**: Handle SDK errors gracefully, create new session if expired

## Timeline

- **Phase 1**: Backend Session Management (2 hours)
- **Phase 2**: SDK Executor Improvements (1 hour)  
- **Phase 3**: Frontend Simplification (1 hour)
- **Phase 4**: Testing & Debugging (2 hours)

**Total Estimated Time**: 6 hours

## File Changes Summary

### Files to Modify
1. `/web-ui/backend-ts/src/server.ts` - Add session mapping
2. `/src/sdk_integration_ts/sdk_executor.ts` - Return session IDs properly
3. `/web-ui/frontend/src/pages/Chat.tsx` - Remove session management
4. `/web-ui/frontend/src/lib/websocket.ts` - Simplify protocol

### Files to Create
- None required

### Files to Delete
- None required

## Next Steps

1. Review this plan with stakeholders
2. Create feature branch: `feature/backend-session-management`
3. Implement Phase 1 (Backend)
4. Test backend changes
5. Implement Phase 2 (SDK)
6. Implement Phase 3 (Frontend)
7. Full integration testing
8. Merge to main branch

## Notes

- This refactor aligns with industry best practices (ChatGPT, Slack, Discord)
- Backend becomes the single source of truth for sessions
- Frontend becomes a pure presentation layer
- Enables future enhancements (Redis, multi-server, session sharing)