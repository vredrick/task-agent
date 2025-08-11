# MCP Server Resources Implementation Plan for Task Agents

## Executive Summary
Implement dynamic MCP resources to provide contextual information about each agent to client LLMs, automatically updating when agents are added/removed, similar to how tools are currently registered.

## 🎯 Objectives
1. **Dynamic Resource Registration**: Automatically create resources for each agent when loaded
2. **Rich Agent Context**: Provide detailed metadata for better LLM understanding
3. **Resource Templates**: Support both static and dynamic resource URIs
4. **Seamless Integration**: Work alongside existing tool registration without disruption

## 📋 Resource Schema Design

### Resource URI Structure
```
agents://                     # Base namespace
├── list                      # Static: list all agents
├── {agent_name}              # Dynamic: specific agent details
├── {agent_name}/config       # Dynamic: agent configuration
├── {agent_name}/prompt       # Dynamic: agent system prompt
├── {agent_name}/examples     # Dynamic: usage examples (if available)
└── {agent_name}/workflow     # Dynamic: BMad workflow position (if applicable)
```

### Resource Content Schema
```python
# Agent Overview Resource
{
    "name": "analyst",
    "display_name": "Business Analyst",
    "description": "...",
    "model": "opus",
    "tools": ["Read", "Write", "Edit", "WebSearch", "Grep", "Bash"],
    "session_support": {
        "enabled": true,
        "max_exchanges": 15
    },
    "resource_dirs": ["./bmad-core"],
    "workflow_position": 1,  # BMad pipeline position
    "recommended_for": [
        "Market research",
        "Competitive analysis",
        "Project discovery"
    ]
}
```

## 🏗️ Implementation Architecture

### 1. Resource Manager Class
```python
# src/task_agents_mcp/resource_manager.py
class AgentResourceManager:
    """Manages dynamic MCP resources for agents."""
    
    def __init__(self, mcp_server: FastMCP):
        self.mcp = mcp_server
        self.registered_resources = {}
    
    def register_agent_resources(self, agent_config: AgentConfig):
        """Register all resources for a single agent."""
        # Main agent resource
        self._register_agent_overview(agent_config)
        # Sub-resources
        self._register_agent_config(agent_config)
        self._register_agent_prompt(agent_config)
        self._register_agent_examples(agent_config)
        self._register_agent_workflow(agent_config)
    
    def unregister_agent_resources(self, agent_name: str):
        """Remove resources when agent is removed."""
        # Clean up registered resources
```

### 2. Integration Points

#### server.py Modifications
```python
# After line 37: Initialize FastMCP server
mcp = FastMCP("task-agent", on_duplicate_resources="replace")

# After line 61: Initialize resource manager
from .resource_manager import AgentResourceManager
resource_manager = AgentResourceManager(mcp)

# After line 258: Register resources alongside tools
for agent_name, agent_config in agent_manager.agents.items():
    # Existing tool registration...
    
    # NEW: Register resources for this agent
    resource_manager.register_agent_resources(agent_config)
```

#### Dynamic Resource Functions
```python
# Using FastMCP decorators for dynamic resources
@mcp.resource("agents://list")
async def list_agents() -> dict:
    """List all available agents with basic info."""
    return {
        "agents": [
            {
                "name": agent.name,
                "display_name": agent.agent_name,
                "description": agent.description,
                "uri": f"agents://{agent.name}"
            }
            for agent in agent_manager.agents.values()
        ]
    }

@mcp.resource("agents://{agent_name}")
async def get_agent_details(agent_name: str) -> dict:
    """Get detailed information about a specific agent."""
    agent = agent_manager.agents.get(agent_name)
    if not agent:
        return {"error": f"Agent {agent_name} not found"}
    
    return {
        "name": agent.name,
        "display_name": agent.agent_name,
        "description": agent.description,
        "model": agent.model,
        "tools": agent.tools,
        "session_support": {
            "enabled": bool(agent.resume_session),
            "max_exchanges": agent.resume_session if isinstance(agent.resume_session, int) else 5
        },
        "resource_dirs": agent.resource_dirs or [],
        "cwd": agent.cwd
    }

@mcp.resource("agents://{agent_name}/prompt")
async def get_agent_prompt(agent_name: str) -> str:
    """Get the system prompt for an agent."""
    agent = agent_manager.agents.get(agent_name)
    if not agent:
        return f"Agent {agent_name} not found"
    return agent.system_prompt
```

## 📝 Implementation Steps

### Phase 1: Core Infrastructure (Week 1)
1. **Create resource_manager.py**
   - Implement AgentResourceManager class
   - Define resource registration methods
   - Add resource URI helpers

2. **Update server.py**
   - Import and initialize resource manager
   - Add static resource: `agents://list`
   - Test basic resource retrieval

### Phase 2: Dynamic Resources (Week 1-2)
3. **Implement Dynamic Templates**
   - Create `agents://{agent_name}` template
   - Add sub-resources for config, prompt, examples
   - Handle missing agent cases gracefully

4. **Enhance Agent Metadata**
   - Add recommended_for field to agent configs
   - Include workflow position for BMad agents
   - Add usage statistics tracking (optional)

### Phase 3: Advanced Features (Week 2)
5. **Resource Caching**
   - Cache static content (prompts, configs)
   - Invalidate cache on agent reload
   - Optimize for frequent access

6. **Resource Discovery**
   - Add `agents://schema` resource
   - Provide OpenAPI-like documentation
   - Include usage examples in resources

### Phase 4: Testing & Documentation (Week 2-3)
7. **Testing**
   - Unit tests for resource manager
   - Integration tests with FastMCP
   - Test dynamic agent addition/removal

8. **Documentation**
   - Update README with resource examples
   - Add resource usage to CLAUDE.md
   - Create client integration guide

## 🔧 Technical Considerations

### FastMCP Integration
- Use `@mcp.resource()` decorator for static resources
- Use `@mcp.resource("template://{param}")` for dynamic
- Handle async operations properly
- Respect `on_duplicate_resources` setting

### Performance Optimization
- Lazy load system prompts (large text)
- Cache frequently accessed resources
- Use efficient JSON serialization
- Consider pagination for large agent lists

### Error Handling
- Graceful handling of missing agents
- Clear error messages in resources
- Fallback content for missing data
- Logging for debugging

### Security Considerations
- Don't expose sensitive configuration
- Sanitize file paths in resources
- Validate agent names in URIs
- Rate limit resource access (if needed)

## 📊 Success Metrics
- All agents have corresponding resources
- Resources update dynamically with agent changes
- Client LLMs can discover agent capabilities
- No performance degradation
- Backward compatibility maintained

## 🚀 Migration Strategy
1. Deploy with resources disabled by default
2. Test with select agents first
3. Enable for all agents gradually
4. Monitor client usage patterns
5. Iterate based on feedback

## 📅 Timeline
- **Week 1**: Core infrastructure + basic resources
- **Week 2**: Dynamic templates + advanced features
- **Week 3**: Testing, documentation, deployment

## 🔄 Future Enhancements
- Resource versioning for compatibility
- Agent capability matrices
- Performance metrics in resources
- Interactive agent selection via resources
- Resource-based agent chaining workflows
- Agent dependency graphs
- Real-time agent status updates

## 📚 References
- [FastMCP Resources Documentation](https://gofastmcp.com/servers/resources)
- [MCP Specification](https://modelcontextprotocol.io/specification)
- [FastMCP GitHub Examples](https://github.com/jlowin/fastmcp)