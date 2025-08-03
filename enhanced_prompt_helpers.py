#!/usr/bin/env python3
"""
Enhanced prompt generation for Phase 3
Creates rich, contextual prompts for each agent
"""
from typing import Dict, Any, Callable, List, Optional
import logging

logger = logging.getLogger(__name__)


def create_enhanced_agent_prompt(agent_name: str, agent_info: Dict[str, Any]) -> Callable:
    """
    Create an enhanced prompt function for a specific agent.
    
    Args:
        agent_name: Display name of the agent
        agent_info: Full agent information including tools, model, etc.
    
    Returns:
        A prompt function with rich parameter options
    """
    def agent_task_prompt(
        task_description: str = "",
        context: Optional[str] = None,
        requirements: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
        output_format: Optional[str] = None,
        include_tips: bool = True
    ) -> str:
        """
        Generate a structured task prompt for the {agent_name} agent.
        
        Args:
            task_description: The main task to perform
            context: Additional context about the project/codebase
            requirements: List of specific requirements
            constraints: List of constraints or limitations
            output_format: Desired output format
            include_tips: Whether to include usage tips
        
        Returns:
            A well-structured prompt for the agent
        """
        # Start with the agent selection
        prompt_parts = [f"Please use the {agent_name} agent for the following task:"]
        
        # Add main task description
        if task_description:
            prompt_parts.append(f"\n**Task:** {task_description}")
        else:
            prompt_parts.append("\n**Task:** [Please specify your task]")
        
        # Add context if provided
        if context:
            prompt_parts.append(f"\n**Context:** {context}")
        
        # Add requirements
        if requirements:
            prompt_parts.append("\n**Requirements:**")
            for req in requirements:
                prompt_parts.append(f"- {req}")
        
        # Add constraints
        if constraints:
            prompt_parts.append("\n**Constraints:**")
            for constraint in constraints:
                prompt_parts.append(f"- {constraint}")
        
        # Add output format preference
        if output_format:
            prompt_parts.append(f"\n**Expected Output Format:** {output_format}")
        
        # Add agent capabilities reminder
        prompt_parts.append(f"\n**Agent Capabilities:** {agent_info.get('description', 'Specialized agent')}")
        
        # Add available tools summary
        tools = agent_info.get('tools', [])
        if tools:
            tool_summary = get_tool_summary(tools)
            prompt_parts.append(f"\n**Available Tools:** {tool_summary}")
        
        # Add contextual tips
        if include_tips:
            tips = generate_enhanced_tips(agent_name, agent_info)
            if tips:
                prompt_parts.append(f"\n**Tips:** {tips}")
        
        # Add best practices for the agent type
        best_practices = get_agent_best_practices(agent_name, agent_info)
        if best_practices:
            prompt_parts.append(f"\n**Best Practices:** {best_practices}")
        
        return "\n".join(prompt_parts)
    
    # Set function metadata
    clean_name = sanitize_function_name(agent_name)
    agent_task_prompt.__name__ = f"{clean_name}_task"
    agent_task_prompt.__doc__ = f"""Generate a structured task prompt for the {agent_name} agent.

This agent specializes in: {agent_info.get('description', 'Various tasks')}

Available tools: {', '.join(agent_info.get('tools', [])[:5])}{'...' if len(agent_info.get('tools', [])) > 5 else ''}

Example usage:
    prompt = {clean_name}_task(
        task_description="Review the authentication module",
        requirements=["Check for security vulnerabilities", "Evaluate code quality"],
        output_format="Detailed report with actionable items"
    )
"""
    
    return agent_task_prompt


def get_tool_summary(tools: List[str]) -> str:
    """Create a concise summary of available tools."""
    if not tools:
        return "No specific tools"
    
    # Group tools by category
    categories = {
        'read': ['Read', 'Grep', 'Search', 'Glob', 'LS'],
        'write': ['Write', 'Edit', 'MultiEdit'],
        'execute': ['Bash'],
        'web': ['WebSearch', 'WebFetch'],
        'notebook': ['NotebookRead', 'NotebookEdit'],
        'other': []
    }
    
    tool_groups = []
    categorized = set()
    
    for category, cat_tools in categories.items():
        matching = [t for t in tools if t in cat_tools]
        if matching:
            if category == 'read':
                tool_groups.append("Code reading/searching")
            elif category == 'write':
                tool_groups.append("Code modification")
            elif category == 'execute':
                tool_groups.append("Command execution")
            elif category == 'web':
                tool_groups.append("Web research")
            elif category == 'notebook':
                tool_groups.append("Jupyter notebooks")
            categorized.update(matching)
    
    # Add any uncategorized tools
    other_tools = [t for t in tools if t not in categorized]
    if other_tools:
        tool_groups.append(f"Specialized ({', '.join(other_tools[:3])})")
    
    return ", ".join(tool_groups)


def generate_enhanced_tips(agent_name: str, agent_info: Dict[str, Any]) -> str:
    """Generate enhanced, contextual tips for the agent."""
    description = agent_info.get('description', '').lower()
    tools = agent_info.get('tools', [])
    
    tips = []
    
    # Category-specific tips
    if 'review' in description or 'quality' in description:
        tips.append("Specify files/modules to review, or ask for a full codebase analysis")
        tips.append("Mention specific concerns (security, performance, style, best practices)")
        if 'Grep' in tools:
            tips.append("The agent can search for patterns across the codebase")
            
    elif 'debug' in description or 'fix' in description:
        tips.append("Include error messages, stack traces, and reproduction steps")
        tips.append("Specify which files are affected if known")
        if 'Bash' in tools:
            tips.append("The agent can run commands to reproduce and test fixes")
            
    elif 'test' in description:
        tips.append("Specify test framework and coverage requirements")
        tips.append("Mention if you need unit tests, integration tests, or both")
        if 'Bash' in tools:
            tips.append("The agent can run tests and analyze results")
            
    elif 'document' in description:
        tips.append("Specify documentation type (API, user guide, code comments, README)")
        tips.append("Mention target audience and preferred format")
        if 'Write' in tools:
            tips.append("The agent can create new documentation files")
            
    elif 'performance' in description or 'optim' in description:
        tips.append("Describe performance issues or metrics to improve")
        tips.append("Mention current benchmarks if available")
        if 'Bash' in tools:
            tips.append("The agent can run profiling tools and benchmarks")
    
    # Tool-specific tips
    if 'MultiEdit' in tools and len(tips) < 3:
        tips.append("The agent can make multiple coordinated changes efficiently")
    
    if 'WebSearch' in tools and len(tips) < 3:
        tips.append("The agent can research best practices and solutions online")
    
    return " | ".join(tips[:3])  # Limit to 3 tips


def get_agent_best_practices(agent_name: str, agent_info: Dict[str, Any]) -> str:
    """Get best practices for using this type of agent."""
    description = agent_info.get('description', '').lower()
    model = agent_info.get('model', 'unknown')
    
    practices = []
    
    # Model-specific practices
    if model == 'opus':
        practices.append("This agent uses Opus for complex reasoning tasks")
    elif model == 'sonnet':
        practices.append("This agent uses Sonnet for balanced performance")
    
    # Task-specific practices
    if 'review' in description:
        practices.append("Provide specific review criteria for best results")
    elif 'debug' in description:
        practices.append("Share all relevant error context upfront")
    elif 'test' in description:
        practices.append("Specify test naming conventions and patterns")
    elif 'document' in description:
        practices.append("Provide examples of desired documentation style")
    elif 'performance' in description:
        practices.append("Define clear performance targets and constraints")
    
    return " | ".join(practices[:2])


def sanitize_function_name(name: str) -> str:
    """Convert agent display name to valid Python identifier."""
    clean = name.lower().replace(' ', '_').replace('-', '_')
    clean = ''.join(c if c.isalnum() or c == '_' else '' for c in clean)
    
    if clean and clean[0].isdigit():
        clean = f"agent_{clean}"
    if not clean:
        clean = "agent_unknown"
    
    return clean


def register_enhanced_prompts(mcp_instance, agent_manager) -> int:
    """
    Register all enhanced agent prompts dynamically.
    
    Returns:
        Number of prompts successfully registered
    """
    count = 0
    
    # Get full agent data
    for agent_name, basic_info in agent_manager.get_agents_info().items():
        try:
            # Get full agent config for tools
            agent_config = agent_manager.get_agent_by_display_name(agent_name)
            
            if agent_config:
                # Build complete info
                full_info = {
                    'description': basic_info['description'],
                    'model': basic_info['model'],
                    'tools': agent_config.tools,
                    'cwd': agent_config.cwd
                }
                
                # Create enhanced prompt
                prompt_func = create_enhanced_agent_prompt(agent_name, full_info)
                
                # Register with MCP
                mcp_instance.prompt(prompt_func)
                
                logger.info(f"Registered enhanced prompt: {prompt_func.__name__}")
                count += 1
            
        except Exception as e:
            logger.error(f"Failed to register prompt for {agent_name}: {e}")
    
    return count


# Test the enhanced prompts
if __name__ == "__main__":
    # Test data
    test_agent = {
        'description': 'Expert code review specialist for quality and security',
        'model': 'opus',
        'tools': ['Read', 'Grep', 'Search', 'Glob', 'Bash']
    }
    
    # Create prompt function
    prompt_func = create_enhanced_agent_prompt("Code Reviewer", test_agent)
    
    print(f"Function name: {prompt_func.__name__}")
    print(f"\nDocstring:\n{prompt_func.__doc__}")
    
    # Test basic usage
    print("\n=== Basic Usage ===")
    print(prompt_func(task_description="Review the authentication module"))
    
    # Test advanced usage
    print("\n=== Advanced Usage ===")
    print(prompt_func(
        task_description="Review the payment processing module",
        context="This is a critical financial system handling user payments",
        requirements=[
            "Check for security vulnerabilities",
            "Verify PCI compliance",
            "Evaluate error handling"
        ],
        constraints=[
            "Focus on files in src/payments/",
            "Must maintain backward compatibility"
        ],
        output_format="Detailed report with severity levels for each finding"
    ))