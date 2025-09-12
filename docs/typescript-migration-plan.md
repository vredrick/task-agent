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
    │  (FastAPI)           │  │  (Express + ws)      │
    │  Port: 8000          │  │  Port: 8001          │
    │  • SDK: subprocess   │  │  • SDK: @anthropic-  │
    │    claude CLI        │  │    ai/claude-code    │
    └──────────────────────┘  └──────────────────────┘
           ↓                           ↓
    ┌──────────────────────────────────────────┐
    │        Shared SDK Implementation         │
    │  /src/sdk_integration/   (Python)        │
    │  /src/sdk_integration_ts/ (TypeScript)   │
    └──────────────────────────────────────────┘
```

## Phase-by-Phase Implementation

### Phase 1: TypeScript Backend Setup ✅
**Goal**: Create basic TypeScript/Node.js backend structure

**Tasks** (Completed):
1. ✅ Create new directory structure: `web-ui/backend-ts/`
2. ✅ Initialize Node.js project with TypeScript
3. ✅ Install dependencies:
   - `@anthropic-ai/claude-code` (the SDK)
   - `express` (web framework)
   - `ws` (WebSocket support)
   - `typescript`, `tsx` (for development)
4. ✅ Set up TypeScript configuration with path aliases
5. ✅ Create basic Express server on port 8001
6. ✅ Add CORS configuration matching Python backend

**Deliverables**:
- ✅ `backend-ts/package.json`
- ✅ `backend-ts/tsconfig.json` 
- ✅ `backend-ts/src/server.ts` (basic server with health check)
- ✅ Health check endpoint working at `/health`

### Phase 2: Authentication Integration ✅
**Goal**: Share OAuth authentication with Python implementation

**Tasks** (Completed):
1. ✅ Create auth module to read `~/.claude/.credentials.json`
2. ✅ Implement credential validation
3. ✅ Create `/api/auth/status` endpoint matching Python
4. ✅ Ensure both backends can read same auth files
5. ✅ Test subscription type detection (Pro/Free tier)

**Deliverables**:
- ✅ `/src/sdk_integration_ts/oauth_handler.ts` (mirrors Python structure)
- ✅ `/api/auth/status` endpoint
- ✅ Verified reading shared credentials
- ✅ TypeScript SDK integration module at `/src/sdk_integration_ts/`

### Phase 3: Agent Management
**Goal**: Load and parse agent configurations from shared `task-agents/*.md` files

**Tasks**:
1. Create TypeScript agent loader for `.md` files
2. Parse YAML frontmatter using `gray-matter`
3. Create `/api/agents` endpoint to list all agents
4. Create `/api/agents/:name` endpoint for specific agent details
5. Ensure identical agent listing as Python backend
6. Share agent directory via environment variable (`TASK_AGENTS_PATH`)

**Deliverables**:
- [ ] `/src/sdk_integration_ts/agent_manager.ts` (mirrors Python)
- [ ] `/src/sdk_integration_ts/types/agent.ts` (agent types)
- [ ] `/api/agents` and `/api/agents/:name` endpoints
- [ ] Verified identical agent loading with Python

### Phase 4: Claude Code SDK Integration
**Goal**: Implement core SDK functionality using `@anthropic-ai/claude-code`

**Tasks**:
1. Initialize `@anthropic-ai/claude-code` SDK with OAuth
2. Create SDK executor that matches Python's `sdk_executor.py`
3. Implement agent execution with proper tool configuration
4. Add session management and persistence
5. Test basic query execution through SDK

**Key Considerations**:
- SDK provides direct API access (no subprocess needed)
- Native partial message streaming support
- Session IDs for conversation continuity

**Deliverables**:
- [ ] `/src/sdk_integration_ts/sdk_executor.ts` (mirrors Python)
- [ ] `/src/sdk_integration_ts/session_store.ts` 
- [ ] Basic query execution working
- [ ] Session persistence to `/tmp/task_agents_sessions.json`

### Phase 5: WebSocket Streaming
**Goal**: Implement real-time streaming with partial message support

**Tasks**:
1. Set up WebSocket server using `ws` library
2. Create `/ws/chat/:sessionId` endpoint matching Python
3. Stream SDK responses with partial message deltas
4. Match exact JSON message format of Python backend
5. Implement interrupt/cancel handling
6. Add connection management and cleanup

**Message Types to Support**:
- `text` - Full text blocks
- `text_delta` - Partial text streaming
- `tool_use` - Tool invocations
- `tool_result` - Tool responses
- `metadata` - Session info
- `error` - Error messages

**Deliverables**:
- [ ] WebSocket handler in `backend-ts/src/server.ts`
- [ ] Message streaming from SDK
- [ ] Partial message support (`content_block_delta`)
- [ ] Interrupt/cancel support
- [ ] Connection lifecycle management

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
- Direct SDK calls via `@anthropic-ai/claude-code` (no subprocess)
- Native partial message streaming support
- Strong TypeScript types throughout
- Native async/await patterns
- Same update cycle as Claude CLI
- Better performance (no process overhead)

### Shared Components:
- Agent configurations (`task-agents/*.md`)
- OAuth credentials (`~/.claude/.credentials.json`)
- Frontend React app (unchanged)
- WebSocket message format (for compatibility)
- Session storage (`/tmp/task_agents_sessions.json`)
- Environment variables (`TASK_AGENTS_PATH`)

## Success Criteria

- [x] Both backends running simultaneously (Python:8000, TypeScript:8001)
- [ ] Frontend can switch between backends
- [ ] Identical functionality in both
- [ ] Better streaming performance in TypeScript
- [ ] No regression in features
- [x] Clean separation allows easy removal

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

## Current Status

### ✅ Completed Phases
- **Phase 1**: TypeScript Backend Setup - Express server running on port 8001
- **Phase 2**: Authentication Integration - OAuth shared with Python

### 🚧 Next Steps
1. **Phase 3**: Agent Management - Load and parse agent configurations
2. **Phase 4**: Claude Code SDK Integration - Implement SDK executor
3. **Phase 5**: WebSocket Streaming - Real-time message streaming

## Notes

- Each phase can be tested independently
- No changes to Python backend until Phase 9
- Frontend remains unchanged except for backend selector
- Focus on feature parity first, optimizations later