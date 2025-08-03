# Multi-Tool Task Agents - Architecture Exploration

## ⚠️ This is an Exploration Fork

This repository is exploring an alternative architecture for task-agents where each agent is exposed as its own MCP tool rather than using a single delegate tool.

**Status**: Exploration Phase  
**Original Project**: [task-agents](https://github.com/vredrick/task-agents)  
**Key Question**: Is it better to have multiple agent-specific tools or one routing tool?

## Quick Comparison

### Original (Single Tool)
```typescript
// One tool that routes to agents
claude.use_tool("delegate", {
  agent: "Code Reviewer",
  prompt: "Review this code"
})
```

### This Fork (Multi-Tool)
```typescript
// Direct tool for each agent
claude.use_tool("code_reviewer", {
  prompt: "Review this code"
})
```

## For Next Session

1. **Start Here**: Read `EXPLORATION_PLAN.md`
2. **Implementation**: Follow `IMPLEMENTATION_ROADMAP.md`
3. **Key File**: Create `server_multi_tool.py` if not exists
4. **Test Both**: Compare UX between approaches

## Key Documents

- `EXPLORATION_PLAN.md` - Detailed exploration plan
- `IMPLEMENTATION_ROADMAP.md` - Step-by-step guide
- `CLAUDE.md` - Updated with fork information
- `comparison_results.md` - (Create after testing)

## Current State

- Original single-tool code is preserved
- No multi-tool implementation yet
- Ready for proof-of-concept development

## Next Steps

1. Implement 2-3 agents as separate tools
2. Test with Claude Desktop
3. Document pros/cons
4. Make architecture decision
5. Fully implement chosen approach