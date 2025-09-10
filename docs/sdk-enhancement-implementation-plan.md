# SDK Enhancement Implementation Plan

## Overview
Phased approach to improve SDK integration, message parsing, and frontend streaming experience while maintaining the current working architecture.

## Current State Analysis

### Working Well
- OAuth authentication (separated in oauth_handler.py)
- Session chaining and conversation persistence
- Basic text streaming to frontend
- WebSocket connection and message flow

### Needs Improvement
- Message type differentiation (flattened to generic JSON)
- Tool execution results not captured
- Frontend receives unstructured chunks
- No interrupt/cancellation support
- Limited streaming UI feedback

## Implementation Phases

### Phase 1: Enhanced Message Parsing & Type Differentiation
**Goal:** Properly parse SDK message types and structure output

#### 1.1 Create Message Parser Module
```python
# src/sdk_integration/message_parser.py
class SDKMessageParser:
    """Parse SDK messages into structured format for frontend"""
    
    def parse_assistant_message(self, message) -> dict:
        # Extract content blocks (text, tool_use)
        # Return structured JSON with type info
    
    def parse_system_message(self, message) -> dict:
        # Handle tool results and system notifications
    
    def parse_result_message(self, message) -> dict:
        # Extract metadata, usage, session info
```

#### 1.2 Update sdk_executor.py
- Import and use message parser
- Check actual message types (not just __name__)
- Stream structured message events:
  ```json
  {
    "type": "assistant_message",
    "blocks": [
      {"type": "text", "content": "..."},
      {"type": "tool_use", "name": "...", "input": {...}}
    ]
  }
  ```

#### 1.3 Testing Points
- Verify all message types are captured
- Ensure tool blocks are properly extracted
- Validate session_id preservation

### Phase 2: Tool Result Capture & Streaming
**Goal:** Capture tool execution results and stream them properly

#### 2.1 Enhanced Tool Block Processing
```python
# In message parser
def parse_tool_result(self, tool_result) -> dict:
    return {
        "type": "tool_result",
        "tool_use_id": tool_result.tool_use_id,
        "output": tool_result.output,
        "is_error": tool_result.is_error
    }
```

#### 2.2 Stream Tool Execution Flow
- Before tool execution: `{"type": "tool_start", "name": "...", "input": {...}}`
- During execution: `{"type": "tool_progress", "output": "..."}`
- After execution: `{"type": "tool_complete", "result": {...}}`

#### 2.3 Backend WebSocket Updates
Update main.py to handle new message types and forward appropriately

### Phase 3: Frontend AI Elements Improvements
**Goal:** Better streaming UI with structured content rendering

#### 3.1 Create Enhanced Message Components
```tsx
// web-ui/frontend/src/components/ai-elements/enhanced-response.tsx
interface MessageBlock {
  type: 'text' | 'tool_use' | 'tool_result';
  content?: string;
  tool?: ToolInfo;
}

export const EnhancedResponse: React.FC<{
  blocks: MessageBlock[];
  streaming: boolean;
}> = ({ blocks, streaming }) => {
  // Render different block types appropriately
  // Show tool usage with collapsible details
  // Stream text with word-by-word animation
};
```

#### 3.2 Tool Usage Display Component
```tsx
// web-ui/frontend/src/components/ai-elements/tool-display.tsx
export const ToolDisplay: React.FC<{
  name: string;
  input: any;
  result?: any;
  status: 'pending' | 'running' | 'complete' | 'error';
}> = ({ name, input, result, status }) => {
  // Show tool invocation with status
  // Collapsible input/output sections
  // Loading spinner while running
};
```

#### 3.3 Update Chat Component
- Parse incoming WebSocket messages
- Build structured message blocks
- Use EnhancedResponse for rendering
- Maintain tool execution state

### Phase 4: Interrupt Support & Stop Button
**Goal:** Add ability to cancel running agent tasks

**Status:** Requires fundamental SDK client lifecycle changes

**Root Cause:** The SDK client is destroyed immediately after yielding messages due to context manager pattern. By the time user clicks Stop, there's no client to interrupt.

#### 4.1 SDK Client Lifecycle Refactor (REQUIRED)

**Problem:** Current implementation uses context manager that exits too early:
```python
# BROKEN - Client dies before interrupt possible
async with ClaudeSDKClient() as client:
    await client.query(task)
    async for message in client.receive_messages():
        yield message
# Client destroyed here - too early!
```

**Solution:** Switch to manual connection management:
```python
# sdk_executor.py - Manual connection pattern
class SDKExecutor:
    def __init__(self):
        self._current_client = None  # Persistent client reference
        self._current_task = None
    
    async def execute_task(self, agent_config, task_description, session_id=None):
        """Execute with manual client lifecycle"""
        # Create client WITHOUT context manager
        options = ClaudeCodeOptions(...)
        self._current_client = ClaudeSDKClient(options)
        
        try:
            # Manual connection
            await self._current_client.connect(task_description)
            
            # Stream messages - client stays alive
            parser = SDKMessageParser()
            async for message in self._current_client.receive_messages():
                parsed = parser.parse_message(message)
                if parsed:
                    # Yield formatted messages
                    yield json.dumps(parsed)
            
            # DO NOT disconnect here - keep alive for interrupts
            
        except Exception as e:
            logger.error(f"SDK execution failed: {e}")
            yield json.dumps({"type": "error", "error": str(e)})
    
    async def interrupt(self) -> bool:
        """Interrupt the currently executing task"""
        if self._current_client:
            try:
                await self._current_client.interrupt()
                logger.info("Interrupt signal sent successfully")
                return True
            except Exception as e:
                logger.error(f"Interrupt failed: {e}")
                return False
        return False
    
    async def cleanup(self):
        """Clean up client when session ends"""
        if self._current_client:
            try:
                await self._current_client.disconnect()
                logger.info("SDK client disconnected")
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
            finally:
                self._current_client = None
                self._current_task = None
```

#### 4.2 WebSocket Lifecycle Management
```python
# main.py - Add cleanup on disconnect
@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Handle interrupt request
            if data.get("type") == "interrupt":
                logger.info(f"Interrupt request for session {session_id}")
                success = await agent_executor.interrupt_current()
                await websocket.send_json({
                    "type": "interrupt_result",
                    "success": success,
                    "message": "Interrupt sent" if success else "No active task"
                })
                continue
            
            # ... existing message handling ...
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    finally:
        # CRITICAL: Clean up SDK client on disconnect
        if hasattr(agent_executor, 'sdk_executor'):
            await agent_executor.sdk_executor.cleanup()
        if session_id in active_connections:
            del active_connections[session_id]
```

#### 4.3 Frontend Stop Button (COMPLETED)
```tsx
// Chat.tsx - Button transforms between Send/Stop
<Button
  onClick={loading ? handleInterrupt : handleSend}
  size="icon"
  variant={loading ? "destructive" : "default"}
>
  {loading ? <Square className="w-4 h-4" /> : <Send className="w-4 h-4" />}
</Button>

// Interrupt handler
const handleInterrupt = () => {
  if (wsRef.current?.readyState === WebSocket.OPEN) {
    wsRef.current.send(JSON.stringify({ type: "interrupt" }));
  }
};
```

## Testing Strategy

### Phase 1 Tests
- [ ] Parse text-only responses
- [ ] Parse tool invocations
- [ ] Parse mixed content messages
- [ ] Verify session_id in metadata

### Phase 2 Tests
- [ ] Capture tool execution start
- [ ] Stream tool output
- [ ] Handle tool errors
- [ ] Complete tool results

### Phase 3 Tests
- [ ] Render text blocks smoothly
- [ ] Display tool usage clearly
- [ ] Handle streaming states
- [ ] Preserve message history

### Phase 4 Tests
- [ ] Interrupt during text generation
- [ ] Interrupt during tool execution
- [ ] UI state updates correctly
- [ ] Resume after interrupt

## Migration Path

1. **Phase 1** can be implemented without breaking current functionality
   - Add parser alongside existing code
   - Gradually migrate to structured format

2. **Phase 2** extends Phase 1 naturally
   - Tool results add to existing stream
   - Frontend can ignore unknown types initially

3. **Phase 3** can run parallel to backend work
   - Keep existing Response component
   - Add EnhancedResponse as option
   - Switch when ready

4. **Phase 4** is independent
   - Add interrupt without breaking existing flow
   - Stop button hidden until backend ready

## Success Metrics

- **Better UX**: Clear indication of what agent is doing
- **Tool Visibility**: Users see tool usage and results
- **Streaming Quality**: Smooth text animation without gaps
- **Control**: Ability to stop long-running tasks
- **Maintainability**: Cleaner separation of concerns

## Timeline Estimate

- Phase 1: 2-3 hours (message parsing)
- Phase 2: 2-3 hours (tool results)
- Phase 3: 3-4 hours (frontend components)
- Phase 4: 1-2 hours (interrupt support)

Total: 8-12 hours for complete implementation

## Next Steps

1. Review and approve plan
2. Start with Phase 1 message parser
3. Test with real agent interactions
4. Iterate based on results