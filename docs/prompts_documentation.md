# Dynamic Prompts Documentation

## Overview

The task-agents MCP server dynamically generates one prompt for each loaded agent. These prompts provide structured templates for creating tasks, making it easier to leverage each agent's specific capabilities.

## Prompt Naming Convention

All prompts follow a consistent naming pattern:

```
{agent_name}_task
```

Where `agent_name` is the sanitized version of the agent's display name:
- Spaces replaced with underscores
- Lowercase conversion
- Special characters removed
- Numbers prefixed with "agent_" if they start the name

### Examples:
- "Code Reviewer" → `code_reviewer_task`
- "Test Runner" → `test_runner_task`
- "Default Assistant" → `default_assistant_task`

## Prompt Parameters

Each generated prompt accepts the following parameters:

```python
def agent_task_prompt(
    task_description: str = "",      # Main task to perform
    context: Optional[str] = None,   # Additional project context
    requirements: Optional[List[str]] = None,  # Specific requirements
    constraints: Optional[List[str]] = None,   # Limitations
    output_format: Optional[str] = None,       # Desired output format
    include_tips: bool = True        # Include usage tips
) -> str:
```

## Prompt Structure

Generated prompts include:

1. **Task Description** - The main request
2. **Context** - Background information (optional)
3. **Requirements** - Bulleted list of must-haves (optional)
4. **Constraints** - Limitations to consider (optional)
5. **Output Format** - How results should be structured (optional)
6. **Agent Capabilities** - What the agent specializes in
7. **Available Tools** - Summary of tools the agent can use
8. **Tips** - Context-specific usage tips
9. **Best Practices** - Agent-specific recommendations

## Usage Examples

### Basic Usage

```python
# Simple task
prompt = code_reviewer_task(
    task_description="Review the authentication module"
)
```

Output:
```
Please use the Code Reviewer agent for the following task:

**Task:** Review the authentication module

**Agent Capabilities:** Expert code review specialist for quality, security, and maintainability analysis

**Available Tools:** Code reading/searching, Command execution

**Tips:** Specify files/modules to review | Mention specific concerns | The agent can search for patterns

**Best Practices:** This agent uses Opus for complex reasoning | Provide specific review criteria
```

### Advanced Usage

```python
# Comprehensive task with all parameters
prompt = debugger_task(
    task_description="Fix the memory leak in the data processor",
    context="Production system experiencing gradual memory increase over 24 hours",
    requirements=[
        "Identify the root cause",
        "Provide a fix",
        "Add monitoring to prevent recurrence"
    ],
    constraints=[
        "Minimize code changes",
        "Maintain backward compatibility"
    ],
    output_format="Step-by-step analysis with code patches"
)
```

## Dynamic Features

### Agent-Specific Tips

Tips are generated based on agent type:

- **Review agents**: "Specify files/modules to review | Mention specific concerns"
- **Debug agents**: "Include error messages and stack traces | Specify affected files"
- **Test agents**: "Specify test framework and coverage requirements"
- **Documentation agents**: "Specify documentation type and target audience"
- **Performance agents**: "Describe performance issues or metrics to improve"

### Tool Summaries

Tools are categorized for clarity:
- "Code reading/searching" (Read, Grep, Search, Glob)
- "Code modification" (Write, Edit, MultiEdit)
- "Command execution" (Bash)
- "Web research" (WebSearch, WebFetch)
- "Jupyter notebooks" (NotebookRead, NotebookEdit)

### Model-Aware Best Practices

Prompts include model-specific guidance:
- **Opus agents**: "This agent uses Opus for complex reasoning tasks"
- **Sonnet agents**: "This agent uses Sonnet for balanced performance"

## Integration with MCP

### In Claude Desktop

1. Prompts appear in the prompts section
2. Select a prompt (e.g., `code_reviewer_task`)
3. Fill in the parameters
4. The generated prompt can be used with the `delegate` tool

### Workflow Example

```
1. User selects: performance_optimizer_task
2. Fills in:
   - task_description: "Optimize database queries"
   - requirements: ["Reduce query time by 50%", "Maintain data accuracy"]
3. Generated prompt is ready for the delegate tool
4. Execute: delegate("Performance Optimizer", <generated_prompt>)
```

## Benefits

1. **Consistency**: All tasks follow a structured format
2. **Discoverability**: Users can see what parameters each agent accepts
3. **Guidance**: Built-in tips and best practices
4. **Flexibility**: Optional parameters for simple or complex tasks
5. **Context-Aware**: Tips and practices adapt to agent type

## Automatic Updates

- Adding new agent markdown files creates new prompts
- Removing agents removes their prompts
- Modifying agent descriptions updates prompt content
- Changes take effect on server restart

## Complete List of Generated Prompts

For a server with the default agents:

1. `code_reviewer_task` - For code quality and security reviews
2. `debugger_task` - For fixing bugs and errors
3. `default_assistant_task` - For general development tasks
4. `documentation_writer_task` - For creating documentation
5. `performance_optimizer_task` - For optimization tasks
6. `test_runner_task` - For test automation

## Technical Implementation

Prompts are generated using:
- `enhanced_prompt_helpers.py` - Core prompt generation logic
- `create_enhanced_agent_prompt()` - Factory function
- `register_enhanced_prompts()` - Bulk registration
- Agent metadata from markdown frontmatter

The system ensures each agent gets exactly one prompt with consistent naming and structure.