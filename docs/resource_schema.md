# Agents List Resource Schema

## Overview

The `agents://list` resource provides comprehensive information about all available agents in the task-agents MCP server. This resource dynamically reflects the current state of loaded agents.

## Resource URI

```
agents://list
```

## Response Schema

```typescript
{
  // Array of all agents with detailed information
  agents: Agent[]
  
  // Agents grouped by category for easy filtering
  agents_by_category: {
    [category: string]: Agent[]
  }
  
  // Total number of available agents
  total_count: number
  
  // Aggregated statistics
  statistics: {
    by_category: { [category: string]: number }
    by_model: { [model: string]: number }
    total_capabilities: string[]
  }
  
  // Server configuration information
  server_info: {
    dynamic_prompts_enabled: boolean
    prompt_suffix: string
    resource_version: string
    features: string[]
  }
  
  // ISO timestamp of when this data was generated
  generated_at: string
  
  // Usage instructions
  usage_guide: {
    tool_usage: string
    prompt_usage: string
    resource_usage: string
  }
}
```

## Agent Object Schema

Each agent in the `agents` array contains:

```typescript
{
  // Display name of the agent
  name: string
  
  // Description of agent's purpose and capabilities
  description: string
  
  // Category: 'review' | 'debug' | 'test' | 'documentation' | 'performance' | 'general'
  category: string
  
  // Model used: 'opus' | 'sonnet' | 'haiku'
  model: string
  
  // List of available tools
  tools: string[]
  
  // Count of tools for quick reference
  tool_count: number
  
  // Derived capabilities based on tools and description
  capabilities: string[]
  
  // Name of the associated prompt function
  prompt_name: string
  
  // Example usage for this agent
  usage_example: string
  
  // Additional metadata
  metadata: {
    file: string              // Original config filename
    has_system_prompt: boolean // Whether agent has custom instructions
    working_directory: string  // Agent's working directory
  }
}
```

## Categories

Agents are automatically categorized based on their name and description:

- **review**: Code review and quality analysis agents
- **debug**: Debugging and error fixing agents  
- **test**: Testing and test automation agents
- **documentation**: Documentation creation and maintenance agents
- **performance**: Performance optimization agents
- **general**: General-purpose assistant agents

## Capabilities

Capabilities are derived from the agent's tools and description:

- **code_analysis**: Can read and analyze code (has Read/Grep tools)
- **code_modification**: Can modify code (has Write/Edit tools)
- **command_execution**: Can run commands (has Bash tool)
- **web_research**: Can search the web (has WebSearch/WebFetch tools)
- **jupyter_support**: Can work with notebooks (has Notebook tools)
- **security_analysis**: Specializes in security (from description)
- **quality_assurance**: Focuses on quality (from description)

## Example Response

```json
{
  "agents": [
    {
      "name": "Code Reviewer",
      "description": "Expert code review specialist for quality, security, and maintainability analysis",
      "category": "review",
      "model": "opus",
      "tools": ["Read", "Search", "Glob", "Bash", "Grep"],
      "tool_count": 5,
      "capabilities": ["code_analysis", "command_execution", "quality_assurance", "security_analysis"],
      "prompt_name": "code_reviewer_task",
      "usage_example": "Use the Code Reviewer agent to review my authentication module for security issues",
      "metadata": {
        "file": "code-reviewer",
        "has_system_prompt": true,
        "working_directory": "."
      }
    }
    // ... more agents
  ],
  "agents_by_category": {
    "review": [ /* Code Reviewer agent */ ],
    "debug": [ /* Debugger, Test Runner agents */ ],
    // ... more categories
  },
  "total_count": 6,
  "statistics": {
    "by_category": {
      "review": 1,
      "debug": 2,
      "general": 1,
      "documentation": 1,
      "performance": 1
    },
    "by_model": {
      "opus": 2,
      "sonnet": 4
    },
    "total_capabilities": [
      "code_analysis",
      "code_modification", 
      "command_execution",
      "quality_assurance",
      "security_analysis"
    ]
  },
  "server_info": {
    "dynamic_prompts_enabled": true,
    "prompt_suffix": "_task",
    "resource_version": "2.0",
    "features": [
      "dynamic_prompts",
      "categorization",
      "capability_detection",
      "usage_examples"
    ]
  },
  "generated_at": "2025-08-02T08:01:39.144427",
  "usage_guide": {
    "tool_usage": "Use 'task_agents' tool with agent name and prompt",
    "prompt_usage": "Use '{agent_name}_task' prompts for guided task creation",
    "resource_usage": "Query 'agents://list' for current agent information"
  }
}
```

## Usage in MCP Clients

### Claude Desktop / Claude Code CLI

The resource will appear in the resources section and can be queried to:
- Discover available agents before using the `task_agents` tool
- Understand agent capabilities and specializations
- Find the right agent for a specific task
- See which tools each agent has access to

### Example Workflow

1. **Query the resource** to see available agents:
   ```
   Query: agents://list
   ```

2. **Review the response** to find suitable agents for your task

3. **Use the tool** with the chosen agent:
   ```
   Tool: task_agents
   Agent: "Code Reviewer"
   Prompt: "Review the auth module for security issues"
   ```

## Dynamic Updates

The resource reflects the current state of loaded agents:
- Adding new agent markdown files and restarting the server will include them
- Removing agent files and restarting will remove them from the list
- Modifying agent configurations will be reflected after restart
- Each query generates fresh data with a new timestamp

## Benefits

1. **Discovery**: Easily discover what agents are available
2. **Categorization**: Find agents by category for specific needs
3. **Capabilities**: Understand what each agent can do
4. **Tools Visibility**: See which tools each agent has access to
5. **Examples**: Get usage examples for each agent
6. **Statistics**: Overview of the agent ecosystem

## Integration Notes

- The resource is read-only and safe to query frequently
- No authentication required (follows MCP server's auth model)
- Compatible with all MCP-compliant clients
- Resource data is generated on-demand for freshness