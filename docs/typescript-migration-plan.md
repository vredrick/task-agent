# TypeScript SDK Migration Plan

## Overview

This document outlines the phase-by-phase plan to implement a TypeScript-based backend using `@anthropic-ai/claude-code` SDK alongside the existing Python implementation, allowing for a smooth transition without breaking current functionality.

## Goals

1. **Parallel Implementation**: Build TypeScript backend alongside Python without dependencies
2. **Feature Parity**: Match all current Python SDK functionality
3. **Shared Resources**: Both implementations share:
   - Frontend (React)
   - Authentication (OAuth credentials in `.claude/`)
   - Agent configurations (`task-agents/*.md`)
4. **Zero Downtime**: Switch between implementations without breaking anything
5. **Clean Separation**: Easy removal of Python once TypeScript is proven

## Architecture Overview

```
                    Shared Resources
    ┌──────────────────────────────────────────┐
    │  • React Frontend (port 5173)             │
    │  • OAuth Auth (~/.claude/.credentials)    │
    │  • Agent Configs (task-agents/*.md)       │
    └──────────────────────────────────────────┘
                    ↓               ↓
    ┌──────────────────────┐  ┌──────────────────────┐
    │  Python Backend       │  │  TypeScript Backend  │
    │  (FastAPI)           │  │  (Express/Fastify)   │
    │  Port: 8000          │  │  Port: 8001          │
    │  • SDK: claude-code  │  │  • SDK: @anthropic-  │
    │    -sdk (limited)    │  │    ai/claude-code    │
    └──────────────────────┘  └──────────────────────┘
```

## Phase-by-Phase Implementation

### Phase 1: TypeScript Backend Setup
**Goal**: Create basic TypeScript/Node.js backend structure

**Tasks**:
1. Create new directory structure: `web-ui/backend-ts/`
2. Initialize Node.js project with TypeScript
3. Install dependencies:
   - `@anthropic-ai/claude-code` (the SDK)
   - `express` or `fastify` (web framework)
   - `ws` or `socket.io` (WebSocket support)
   - `typescript`, `tsx` (for development)
4. Set up TypeScript configuration
5. Create basic Express server on port 8001
6. Add CORS configuration matching Python backend

**Deliverables**:
- [ ] `backend-ts/package.json`
- [ ] `backend-ts/tsconfig.json`
- [ ] `backend-ts/src/server.ts` (basic server)
- [ ] Health check endpoint working

### Phase 2: Authentication Integration
**Goal**: Share OAuth authentication with Python implementation

**Tasks**:
1. Create auth module to read `.claude/.credentials.json`
2. Implement credential validation
3. Create `/api/auth/status` endpoint matching Python
4. Ensure both backends can read same auth files
5. Test subscription type detection

**Deliverables**:
- [ ] `backend-ts/src/auth/oauth.ts`
- [ ] `/api/auth/status` endpoint
- [ ] Verified reading shared credentials

### Phase 3: Agent Management
**Goal**: Load and parse agent configurations

**Tasks**:
1. Create agent loader for `.md` files
2. Parse YAML frontmatter
3. Create `/api/agents` endpoint
4. Create `/api/agents/:name` endpoint
5. Ensure identical agent listing as Python

**Deliverables**:
- [ ] `backend-ts/src/agents/loader.ts`
- [ ] `backend-ts/src/agents/types.ts`
- [ ] Agent endpoints matching Python output

### Phase 4: Claude Code SDK Integration
**Goal**: Implement core SDK functionality

**Tasks**:
1. Initialize `@anthropic-ai/claude-code` SDK
2. Configure SDK with OAuth credentials
3. Create agent executor using SDK
4. Implement session management
5. Test basic query execution

**Deliverables**:
- [ ] `backend-ts/src/sdk/executor.ts`
- [ ] `backend-ts/src/sdk/session.ts`
- [ ] Basic query execution working

### Phase 5: WebSocket Streaming
**Goal**: Implement real-time streaming matching Python

**Tasks**:
1. Set up WebSocket server on `/ws/chat/:sessionId`
2. Implement message streaming from SDK
3. Add partial message support (content_block_delta)
4. Match JSON message format of Python backend
5. Implement interrupt handling

**Deliverables**:
- [ ] `backend-ts/src/websocket/handler.ts`
- [ ] Streaming messages to frontend
- [ ] Partial message streaming working
- [ ] Interrupt support

### Phase 6: Frontend Configuration
**Goal**: Allow frontend to switch between backends

**Tasks**:
1. Add environment variable for backend selection
2. Create backend switcher in UI (dev mode only)
3. Update WebSocket connection logic
4. Test both backends from same frontend
5. Add backend indicator in UI

**Deliverables**:
- [ ] Frontend `.env` configuration
- [ ] Backend switcher component
- [ ] Both backends working with frontend

### Phase 7: Testing & Validation
**Goal**: Ensure feature parity

**Tasks**:
1. Create test suite comparing both backends
2. Test all agent executions
3. Verify streaming performance
4. Test session persistence
5. Validate tool execution
6. Compare response quality

**Deliverables**:
- [ ] `test/backend-comparison.ts`
- [ ] Performance metrics
- [ ] Feature parity checklist

### Phase 8: Production Readiness
**Goal**: Prepare TypeScript backend for production

**Tasks**:
1. Add proper error handling
2. Implement logging (matching Python)
3. Add health checks and monitoring
4. Create production build configuration
5. Add PM2/systemd service configuration
6. Document deployment process

**Deliverables**:
- [ ] Production build scripts
- [ ] Deployment documentation
- [ ] Service configuration files

### Phase 9: Migration & Cleanup (Future)
**Goal**: Remove Python backend once TypeScript is proven

**Tasks**:
1. Switch default backend to TypeScript
2. Monitor for issues (1-2 weeks)
3. Remove Python backend code
4. Update documentation
5. Clean up dependencies

**Deliverables**:
- [ ] Updated default configuration
- [ ] Removed Python dependencies
- [ ] Updated documentation

## Implementation Order

1. **Start with Phase 1-3**: Get basic structure running
2. **Focus on Phase 4-5**: Core functionality
3. **Phase 6**: Frontend integration
4. **Phase 7**: Validation
5. **Phase 8**: Production prep
6. **Phase 9**: Future cleanup (only after proven stable)

## Key Differences to Leverage

### TypeScript SDK Advantages:
- Direct SDK calls (no subprocess)
- Partial message streaming support
- Better TypeScript types
- Native async/await
- Same update cycle as CLI

### Shared Components:
- Agent configurations (`task-agents/*.md`)
- OAuth credentials (`~/.claude/.credentials.json`)
- Frontend React app
- WebSocket message format (for compatibility)

## Success Criteria

- [ ] Both backends running simultaneously
- [ ] Frontend can switch between backends
- [ ] Identical functionality in both
- [ ] Better streaming performance in TypeScript
- [ ] No regression in features
- [ ] Clean separation allows easy removal

## Development Workflow

1. Keep both backends running during development
2. Test changes against both backends
3. Use feature flags for backend selection
4. Maintain backward compatibility
5. Document differences as they arise

## Risk Mitigation

- **Risk**: Breaking current functionality
  - **Mitigation**: Complete separation, different ports
  
- **Risk**: Authentication issues
  - **Mitigation**: Read-only access to shared credentials
  
- **Risk**: Different SDK behaviors
  - **Mitigation**: Extensive testing, comparison suite
  
- **Risk**: Frontend compatibility
  - **Mitigation**: Match message formats exactly

## Next Steps

1. Review and approve this plan
2. Start with Phase 1: TypeScript Backend Setup
3. Create `backend-ts/` directory structure
4. Begin implementation following the phases

## Notes

- Each phase can be tested independently
- No changes to Python backend until Phase 9
- Frontend remains unchanged except for backend selector
- Focus on feature parity first, optimizations later