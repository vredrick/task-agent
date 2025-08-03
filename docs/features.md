# Task-Agents Features Documentation

## Overview

Task-Agents MCP Server provides a comprehensive set of features for delegating tasks to specialized AI agents. This document details all available features and how to use them.

## Core Features

### 1. Dynamic Tool: `delegate`

The main tool for running specialized agents.

**Parameters:**
- `agent`: Name of the agent to use (must match exactly)
- `prompt`: The task description or request

**Example:**
```
agent: "Code Reviewer"
prompt: "Review the authentication module for security vulnerabilities"
```

### 2. Dynamic Resource: `agents://list`

A comprehensive resource that provides detailed information about all available agents.

**Returns:**
- Complete agent list with metadata
- Agent categorization (review, debug, general, documentation, performance)
- Capability detection based on tools and descriptions
- Usage statistics and examples
- Server configuration information

**Data Structure:**
```json
{
  "agents": [...],
  "agents_by_category": {...},
  "total_count": 6,
  "statistics": {
    "by_category": {...},
    "by_model": {...},
    "total_capabilities": [...]
  },
  "server_info": {...},
  "usage_guide": {...}
}
```

### 3. Dynamic Prompts

Each agent automatically receives a dedicated prompt template.

**Naming Pattern:** `{agent_name}_task`
- Code Reviewer → `code_reviewer_task`
- Debugger → `debugger_task`
- Default Assistant → `default_assistant_task`

**Parameters:**
- `task_description` (required): Main task to perform
- `context` (optional): Additional background information
- `requirements` (optional): List of specific requirements
- `constraints` (optional): Limitations to consider
- `output_format` (optional): Desired output structure
- `include_tips` (optional): Include usage tips (default: true)

## Agent Categories

Agents are automatically categorized based on their purpose:

1. **Review**: Code review and quality analysis
2. **Debug**: Bug fixing and error resolution
3. **General**: General-purpose development tasks
4. **Documentation**: Technical writing and documentation
5. **Performance**: Optimization and efficiency improvements

## Capability Detection

The system automatically detects agent capabilities:

- **code_analysis**: Can analyze and review code
- **debugging**: Can identify and fix bugs
- **testing**: Can run and create tests
- **documentation**: Can write technical documentation
- **optimization**: Can improve performance
- **general_development**: Can handle various tasks

## Enhanced Output Format

All agents now provide:
- **Tool Usage Tracking**: See which tools were called during execution
- **Token Counts**: View input/output tokens and usage
- **Structured Messages**: Clean, formatted output
- **Execution Metadata**: Timing and performance information

## Working with Agents

### Finding Available Agents

1. **Query the Resource**:
   - In Claude Desktop: Click `agents://list` in resources
   - Ask Claude: "What agents are available?"

2. **Check Agent Details**:
   - View capabilities, tools, and model
   - See usage examples for each agent
   - Understand category and specialization

### Creating Structured Requests

1. **Select a Prompt**:
   - Choose appropriate agent prompt (e.g., `code_reviewer_task`)
   - Fill in parameters based on your needs

2. **Example Flow**:
   ```
   Prompt: code_reviewer_task
   Parameters:
   - task_description: "Review authentication module"
   - requirements: ["Security focus", "Check for SQL injection"]
   - output_format: "Detailed security report"
   ```

3. **Generated Output**:
   A well-structured request ready for the delegate tool

## Dynamic Updates

All features update automatically when agents change:

1. **Add New Agent**: Create `.md` file in task-agents directory
2. **Restart Server**: Changes take effect
3. **Automatic Updates**:
   - New agent appears in tool description
   - Resource includes new agent data
   - Prompt created for new agent

## Best Practices

1. **Agent Selection**:
   - Match agent specialization to your task
   - Use Default Assistant for general tasks
   - Leverage specialized agents for better results

2. **Prompt Usage**:
   - Use prompts for complex, structured tasks
   - Include requirements for specific needs
   - Add constraints to guide behavior

3. **Resource Queries**:
   - Check available agents before starting
   - Review capabilities to choose best agent
   - Use category information for quick selection

## Technical Implementation

- **FastMCP Framework**: Powers the MCP server
- **Dynamic Registration**: Features register at startup
- **Metadata Extraction**: Automatic capability detection
- **Category Assignment**: Smart categorization logic
- **Prompt Generation**: Template-based system

## Troubleshooting

1. **Agent Not Found**:
   - Check exact name in agents://list
   - Ensure agent file has correct frontmatter
   - Restart server after adding agents

2. **Prompt Not Available**:
   - Verify agent is loaded
   - Check prompt naming pattern
   - Ensure server started successfully

3. **Resource Empty**:
   - Confirm task-agents directory exists
   - Check agent files have valid YAML
   - Review server logs for errors