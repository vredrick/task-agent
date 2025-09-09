# Session Management Implementation Plan

## Overview
Implement a comprehensive session management system for the Task Agent Web UI that allows users to view, select, and resume previous conversations while maintaining backward compatibility with the current automatic session chaining.

## Key Design Decisions

### CWD Agent Tagging Strategy
- Pattern: `{base_path}/{agent_name}/{user_subdirs}`
- Example: `/home/vredrick/task-agent/analyst/research/project1`
- This creates project directories like: `-home-vredrick-task-agent-analyst-research-project1`
- Benefits:
  - Automatic agent identification from path
  - Users can organize work in subdirectories
  - Sessions naturally grouped by agent and project

## Implementation Phases

### Phase 1: Backend Session Discovery (Week 1)
**Goal**: Create infrastructure to discover and read existing sessions

#### 1.1 Session Discovery Service
```python
# web-ui/backend/session_service.py
- Create SessionDiscoveryService class
- Scan ~/.claude/projects/ for relevant directories
- Parse JSONL files to extract session metadata
- Cache results for performance
```

#### 1.2 API Endpoints
```python
# web-ui/backend/main.py additions
GET /api/sessions
  - List all available sessions
  - Filter by agent_name (optional)
  - Include: id, summary, timestamp, message_count, agent

GET /api/sessions/{session_id}
  - Get full session history
  - Parse JSONL for complete conversation
  - Return formatted messages
```

#### 1.3 Session Metadata Storage
```python
# web-ui/backend/session_metadata.json
{
  "sessions": {
    "session-id": {
      "agent": "analyst",
      "created_at": "2025-01-09T10:00:00Z",
      "last_updated": "2025-01-09T11:00:00Z",
      "summary": "Analyzed project architecture",
      "chain_ids": ["id1", "id2", "id3"],
      "tags": ["architecture", "review"],
      "cwd": "/home/vredrick/task-agent/analyst"
    }
  }
}
```

### Phase 2: Agent CWD Configuration (Week 1-2)
**Goal**: Modify agent execution to use tagged CWD paths

#### 2.1 Update SDK Executor
```python
# src/sdk_integration/sdk_executor.py
- Modify working_dir resolution
- Inject agent name into path: f"{base_cwd}/{agent_name}"
- Ensure subdirectories are preserved
```

#### 2.2 Update Agent Executor
```python
# src/sdk_integration/agent_executor.py
- Pass agent-specific CWD to SDK executor
- Handle user-specified subdirectories
- Validate and create directories as needed
```

#### 2.3 Configuration Updates
```yaml
# task-agents/example-agent.md
cwd: ./analyst  # Relative to task-agent root
# OR
cwd: /home/vredrick/task-agent/analyst  # Absolute path
```

### Phase 3: WebSocket Enhancement (Week 2)
**Goal**: Add session resumption capabilities to WebSocket

#### 3.1 Enhanced WebSocket Protocol
```typescript
// Client → Server message format
interface ChatMessage {
  agent_name: string;
  message: string;
  session_reset?: boolean;
  
  // NEW optional fields
  conversation_id?: string;     // Resume specific session
  resume_chain?: string;         // Resume latest in chain
  create_in_subdir?: string;     // Optional subdir under agent CWD
}
```

#### 3.2 Backend WebSocket Handler
```python
# web-ui/backend/main.py
- Accept conversation_id in WebSocket messages
- Look up session chains when resume_chain provided
- Create new sessions in specified subdirectories
- Maintain backward compatibility (all new fields optional)
```

### Phase 4: Frontend Session UI - Basic (Week 2-3)
**Goal**: Add basic session selection UI

#### 4.1 Session List Component
```typescript
// frontend/src/components/SessionList.tsx
- Fetch and display available sessions
- Group by agent
- Show summary, date, message count
- Click to select session for resumption
```

#### 4.2 Chat Page Integration
```typescript
// frontend/src/pages/Chat.tsx
- Add "Previous Sessions" button
- Show SessionList in modal/sidebar
- Pass selected conversation_id to WebSocket
- Maintain current auto-chaining as default
```

#### 4.3 Session Context Display
```typescript
// frontend/src/components/SessionContext.tsx
- Show current session info (agent, created date)
- Display if resuming vs new session
- Option to reset/start fresh
```

### Phase 5: Frontend Session UI - Advanced (Week 3-4)
**Goal**: Add rich session management features

#### 5.1 Session Search & Filter
```typescript
// frontend/src/components/SessionSearch.tsx
- Search sessions by content
- Filter by agent
- Filter by date range
- Filter by tags
```

#### 5.2 Session Organization
```typescript
// frontend/src/components/SessionOrganizer.tsx
- Add tags to sessions
- Create session groups/folders
- Archive old sessions
- Export session history
```

#### 5.3 Session Preview
```typescript
// frontend/src/components/SessionPreview.tsx
- Show first/last few messages
- Display tool usage summary
- Show conversation flow diagram
- Quick resume button
```

### Phase 6: Session Persistence & Sync (Week 4)
**Goal**: Improve session data persistence

#### 6.1 SQLite Integration
```python
# web-ui/backend/database.py
- Replace JSON with SQLite for metadata
- Schema: sessions, chains, tags tables
- Migration from JSON to SQLite
```

#### 6.2 Session Sync Service
```python
# web-ui/backend/sync_service.py
- Background service to sync JSONL with database
- Watch for new sessions in ~/.claude/projects/
- Update metadata automatically
```

#### 6.3 Session Export/Import
```python
# web-ui/backend/export_service.py
- Export sessions as markdown
- Export as JSON
- Import session backups
- Share sessions between users
```

## Testing Strategy

### Phase 1-2 Testing
- Unit tests for session discovery
- Test JSONL parsing
- Verify CWD path generation
- Test agent isolation

### Phase 3-4 Testing
- WebSocket message handling tests
- Frontend component tests
- E2E test for session resumption
- Backward compatibility tests

### Phase 5-6 Testing
- Performance tests with many sessions
- Database migration tests
- Sync service reliability tests
- Export/import round-trip tests

## Rollback Plan

Each phase is independently deployable:
- Phase 1-2: Backend only, no frontend changes needed
- Phase 3: Optional WebSocket fields, old clients work
- Phase 4-5: Progressive enhancement, feature flags
- Phase 6: Database with JSON fallback

## Success Metrics

1. **User Engagement**
   - % of users using session resumption
   - Average sessions resumed per user
   - Time saved by resuming context

2. **Technical Metrics**
   - Session discovery performance < 100ms
   - WebSocket message latency unchanged
   - Zero breaking changes to existing flow

3. **Quality Metrics**
   - Session data integrity 100%
   - Successful resumption rate > 95%
   - User-reported issues < 1%

## Risk Mitigation

### Risk: Large JSONL files slow down parsing
**Mitigation**: 
- Implement caching layer
- Parse only metadata initially
- Load full content on demand

### Risk: CWD changes break existing setups
**Mitigation**:
- Make CWD tagging opt-in initially
- Provide migration tool
- Support both old and new patterns

### Risk: Session proliferation clutters UI
**Mitigation**:
- Auto-archive old sessions
- Implement search/filter early
- Set reasonable retention limits

## Implementation Timeline

- **Week 1**: Phase 1 + Phase 2 start
- **Week 2**: Phase 2 complete + Phase 3 + Phase 4 start  
- **Week 3**: Phase 4 complete + Phase 5 start
- **Week 4**: Phase 5 complete + Phase 6
- **Week 5**: Testing, bug fixes, documentation
- **Week 6**: Release preparation and deployment

## Next Steps

1. Review and approve implementation plan
2. Set up development branch: `feature/session-management`
3. Create issue tickets for each phase
4. Begin Phase 1 implementation
5. Schedule weekly progress reviews

## Dependencies

- Python 3.11+ (backend)
- Node.js 18+ (frontend)
- SQLite3 (Phase 6)
- Claude SDK with session support
- Access to ~/.claude/projects/ directory

## Documentation Deliverables

- API documentation for new endpoints
- WebSocket protocol documentation
- User guide for session management
- Developer guide for CWD configuration
- Migration guide for existing users