# Multi-Tool MCP Server Exploration Plan

## Overview

This project explores an alternative implementation of task-agents where **each agent becomes its own MCP tool** instead of having a single `delegate` tool that routes to different agents.

## Current Architecture (Single Tool)

```
MCP Server
    └── delegate tool
         └── Routes to agents based on agent parameter
              ├── Code Reviewer
              ├── Debugger  
              ├── Test Runner
              └── etc.
```

## Proposed Architecture (Multi-Tool)

```
MCP Server
    ├── code_reviewer tool
    ├── debugger tool
    ├── test_runner tool
    ├── documentation_writer tool
    ├── performance_optimizer tool
    └── default_assistant tool
```

## Key Differences

### 1. Tool Registration
- **Current**: One tool (`delegate`) with agent selection via parameter
- **Proposed**: Multiple tools, one per agent, registered separately

### 2. LLM Decision Making
- **Current**: LLM chooses agent via string parameter
- **Proposed**: LLM chooses which tool to invoke directly

### 3. Tool Discovery
- **Current**: Must query resources or read docs to know available agents
- **Proposed**: Standard MCP tool discovery shows all agent tools

## Implementation Plan

### Phase 1: Refactor Server Structure
1. Modify `server.py` to register each agent as a separate tool
2. Create tool functions for each agent
3. Remove the single `delegate` tool

### Phase 2: Update Agent Manager
1. Modify `agent_manager.py` to support tool-per-agent pattern
2. Each agent's tool function will call agent manager directly
3. Maintain backward compatibility with agent configurations

### Phase 3: Dynamic Tool Generation
1. Dynamically create tool functions from agent markdown files
2. Auto-generate tool descriptions from agent metadata
3. Preserve all existing agent capabilities

### Phase 4: Testing & Comparison
1. Test with Claude Desktop
2. Compare UX between single-tool vs multi-tool approaches
3. Document pros/cons

## Benefits of Multi-Tool Approach

1. **Better Discoverability**: Each agent appears as a distinct tool in MCP tool list
2. **Clearer Intent**: Tool name directly indicates agent purpose
3. **Type Safety**: Each tool can have specific parameters
4. **Parallel Execution**: Multiple agents can run simultaneously
5. **Standard MCP Pattern**: Follows typical MCP server design

## Potential Challenges

1. **Tool Namespace**: Many tools might clutter the tool list
2. **Naming Conflicts**: Need unique, clear tool names
3. **Migration Path**: How to transition existing users
4. **Dynamic Loading**: Tools must be registered at server startup

## Technical Approach

### Tool Registration Pattern
```python
# Instead of:
@mcp.tool
def delegate(agent: str, prompt: str) -> str:
    return agent_manager.run(agent, prompt)

# We'll have:
@mcp.tool
def code_reviewer(prompt: str, focus: str = "quality") -> str:
    return agent_manager.run("Code Reviewer", prompt, focus=focus)

@mcp.tool  
def debugger(prompt: str, error_type: str = None) -> str:
    return agent_manager.run("Debugger", prompt, error_type=error_type)
```

### Dynamic Registration
```python
# Generate tools from agent configs
for agent_name, agent_config in agents.items():
    tool_func = create_agent_tool(agent_name, agent_config)
    mcp.tool(tool_func)
```

## Next Steps

1. Start with a proof-of-concept for 2-3 agents
2. Test with Claude Desktop to evaluate UX
3. Gather feedback on tool discovery and usage
4. Decide whether to proceed with full implementation

## Files to Modify

1. `server.py` - Main changes for tool registration
2. `agent_manager.py` - Support for tool-specific calls
3. `CLAUDE.md` - Update documentation for new approach
4. `README.md` - Add comparison section

## Success Criteria

1. Each agent works as an independent tool
2. No loss of functionality from current implementation
3. Improved discoverability in Claude Desktop
4. Clear documentation of trade-offs
5. Easy to add new agent tools dynamically