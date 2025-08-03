# Implementation Roadmap: Multi-Tool MCP Server

## Quick Start for Next Session

When you open this project, this is a **fork exploring a different architecture** where each agent is its own MCP tool. The main task-agents project uses a single `delegate` tool.

## Step-by-Step Implementation Guide

### Step 1: Create Proof of Concept (Start Here!)
**File**: `server_multi_tool.py` (new file)

```python
# 1. Copy server.py to server_multi_tool.py
# 2. Replace single delegate tool with multiple tools:

@mcp.tool
def code_reviewer(prompt: str) -> str:
    """Expert code review specialist"""
    return agent_manager.run_agent("Code Reviewer", prompt)

@mcp.tool  
def debugger(prompt: str) -> str:
    """Debugging specialist"""
    return agent_manager.run_agent("Debugger", prompt)

# 3. Test with: python server_multi_tool.py
```

### Step 2: Refactor Agent Manager
**File**: `agent_manager.py`

Current method to keep:
- `run_agent(agent_name, task)` - Works for both approaches

No changes needed initially!

### Step 3: Dynamic Tool Registration
**File**: `server_multi_tool.py`

```python
def register_agent_tools(mcp_instance, agent_manager):
    """Dynamically create and register tools for each agent"""
    for agent_name in agent_manager.agents:
        # Create tool function
        tool_func = create_tool_for_agent(agent_name)
        # Register with MCP
        mcp_instance.tool(tool_func)
```

### Step 4: Test & Compare

1. **Run original server**: `python server.py`
   - Note how `delegate` tool works
   - Test with Claude Desktop

2. **Run multi-tool server**: `python server_multi_tool.py`
   - See all agents as separate tools
   - Compare discoverability

### Step 5: Full Implementation (If POC succeeds)

1. **Update all imports** in `src/task_agents_mcp/`
2. **Create migration guide** for users
3. **Update PyPI package** configuration
4. **Test with all agents**

## Key Files to Create/Modify

### New Files
1. `server_multi_tool.py` - Multi-tool implementation
2. `comparison_results.md` - Document findings
3. `examples/multi_tool_usage.py` - Usage examples

### Modified Files  
1. `server.py` - Will be replaced if multi-tool wins
2. `README.md` - Add section on architecture choice
3. `pyproject.toml` - Update if changing main entry point

## Decision Criteria

### Choose Multi-Tool If:
- ✅ Better tool discovery in Claude Desktop
- ✅ Clearer which agent to use
- ✅ Can run agents in parallel
- ✅ Each agent can have specific parameters

### Stay with Single Tool If:
- ✅ Cleaner tool list (only one tool)
- ✅ Easier to add new agents
- ✅ More flexible routing logic
- ✅ Better for programmatic use

## Code Snippets to Get Started

### 1. Tool Creation Helper
```python
def create_tool_for_agent(agent_name: str):
    """Factory to create tool function for an agent"""
    def agent_tool(prompt: str) -> str:
        return agent_manager.run_agent(agent_name, prompt)
    
    # Set function metadata
    agent_tool.__name__ = agent_name.lower().replace(" ", "_")
    agent_tool.__doc__ = agent_manager.agents[agent_name].get("description", "")
    
    return agent_tool
```

### 2. Testing Script
```python
# test_multi_tool.py
import asyncio
from server_multi_tool import mcp

async def test():
    # List all tools
    tools = await mcp.list_tools()
    print(f"Available tools: {[t.name for t in tools]}")
    
    # Test code_reviewer tool
    result = await mcp.call_tool("code_reviewer", {"prompt": "Review this code"})
    print(result)

asyncio.run(test())
```

## Environment Variables (Same as Original)
- `TASK_AGENTS_PATH`: Path to agents directory
- `CLAUDE_EXECUTABLE_PATH`: Path to Claude CLI

## Next Session Checklist

- [ ] Read `EXPLORATION_PLAN.md` first
- [ ] Check if `server_multi_tool.py` exists
- [ ] Run comparison tests if not done
- [ ] Document findings in `comparison_results.md`
- [ ] Make architecture decision
- [ ] Implement chosen approach fully

## Questions to Answer

1. How does tool discovery feel in Claude Desktop?
2. Is it clearer which agent to use?
3. Any performance differences?
4. Which approach do users prefer?
5. Maintenance complexity comparison?

## Remember

This is an **exploration project** - the goal is to determine if multiple tools is better than a single delegate tool. Keep both implementations working until a decision is made!