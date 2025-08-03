#!/usr/bin/env python3
"""
Task-Agents MCP Server

A Model Context Protocol server that enables specialized AI agents by delegating 
tasks to Claude Code CLI with custom configurations.
"""
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from fastmcp import FastMCP

from agent_manager import AgentManager
from enhanced_dynamic_helpers import create_enhanced_agents_list_resource
from enhanced_prompt_helpers import register_enhanced_prompts

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/task_agents_server.log')
    ]
)
logger = logging.getLogger(__name__)

# Log startup information
logger.info("=== Task Agents Server Starting ===")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"TASK_AGENTS_PATH env: {os.environ.get('TASK_AGENTS_PATH', 'NOT SET')}")
logger.info(f"CLAUDE_EXECUTABLE_PATH env: {os.environ.get('CLAUDE_EXECUTABLE_PATH', 'NOT SET')}")

# Initialize FastMCP server
mcp = FastMCP("task-agents")

# Look for task-agents directory
# 1. First check environment variable (for Claude Desktop and other MCP clients)
# 2. Fall back to current working directory (for Claude Code CLI)
config_dir = os.environ.get('TASK_AGENTS_PATH')
if not config_dir:
    # Default to task-agents subdirectory in current working directory
    config_dir = os.path.join(os.getcwd(), "task-agents")

# Ensure config directory exists
if not os.path.exists(config_dir):
    logger.error(f"Config directory not found: {config_dir}")
    if os.environ.get('TASK_AGENTS_PATH'):
        logger.error(f"Check that TASK_AGENTS_PATH points to a valid directory")
    else:
        logger.error(f"Either set TASK_AGENTS_PATH environment variable or add 'task-agents' directory to your project")

# Initialize agent manager and load agents
agent_manager = AgentManager(config_dir)
agent_manager.load_agents()

logger.info("Starting task-agents MCP server...")
logger.info(f"Loaded {len(agent_manager.agents)} agents")

# Log available agents
agents_info = agent_manager.get_agents_info()
for name, info in agents_info.items():
    logger.info(f"  - {name}: {info['description']}")

# ============= DYNAMIC RESOURCE =============
# Register the enhanced agents list resource
agents_list_func = create_enhanced_agents_list_resource(agent_manager)
agents_list_resource = mcp.resource("agents://list")(agents_list_func)
logger.info("Registered dynamic resource: agents://list")

# ============= DYNAMIC PROMPTS =============
# Register dynamic prompts for all agents
prompt_count = register_enhanced_prompts(mcp, agent_manager)
logger.info(f"Registered {prompt_count} dynamic prompts")


def get_dynamic_tool_description():
    """Generate tool description with available agents."""
    agents_info = agent_manager.get_agents_info()
    
    if not agents_info:
        return "No agents are currently configured."
    
    description = """Delegate specialized tasks to expert AI agents, each optimized for specific software engineering domains.

## How to Select an Agent:
Choose the agent whose expertise best matches your task. Each agent is specialized for particular types of work.

## Available Agents:
"""
    
    # Add each agent with enhanced description
    for agent_name, info in agents_info.items():
        description += f"\n**{agent_name}**\n"
        description += f"{info['description']}\n"
    
    description += "\n## Selection Tips:\n"
    description += "- Match your task to the agent's specialty described above\n"
    description += "- For general tasks, use the Default Assistant\n"
    description += "- Be specific in your prompt to get the best results\n"
    description += "\n## Enhanced Features:\n"
    description += f"- Query 'agents://list' resource for detailed agent information\n"
    description += f"- Use agent-specific prompts (e.g., 'code_reviewer_task') for guided task creation"
    
    return description.strip()


def generate_dynamic_examples():
    """Generate example usage based on available agents."""
    agents_info = agent_manager.get_agents_info()
    if not agents_info:
        return ""
    
    examples = []
    
    # Generate examples based on agent types
    for agent_name, info in list(agents_info.items())[:3]:  # Limit to 3 examples
        desc_lower = info['description'].lower()
        
        # Generate contextual examples based on description keywords
        if 'review' in desc_lower or 'quality' in desc_lower:
            example_prompt = "Review the payment processing module for security vulnerabilities and code quality"
        elif 'debug' in desc_lower or 'fix' in desc_lower or 'error' in desc_lower:
            example_prompt = "Fix the TypeError occurring in the user authentication flow"
        elif 'test' in desc_lower:
            example_prompt = "Run the test suite and fix any failing tests"
        elif 'document' in desc_lower:
            example_prompt = "Create API documentation for the new endpoints"
        elif 'performance' in desc_lower or 'optim' in desc_lower:
            example_prompt = "Analyze and optimize the database query performance"
        else:
            # Default example for general agents
            example_prompt = "Help me implement a new feature for user notifications"
        
        examples.append(f'    agent: "{agent_name}"\n    prompt: "{example_prompt}"')
    
    return "\n\n".join(examples)


# Define the tool function first
async def delegate_impl(agent: str, prompt: str) -> str:
    """Implementation of delegate tool."""
    try:
        logger.info(f"=== Delegate Tool Called ===")
        logger.info(f"Current process working directory: {os.getcwd()}")
        logger.info(f"Agent requested: {agent}")
        logger.info(f"Task: {prompt[:100]}...")
        
        # Find the agent by display name
        agent_config = agent_manager.get_agent_by_display_name(agent)
        
        if not agent_config:
            available_agents = list(agent_manager.get_agents_info().keys())
            return f"Error: Agent '{agent}' not found. Available agents: {', '.join(available_agents)}"
        
        logger.info(f"Found agent config: {agent_config.agent_name}")
        logger.info(f"Agent cwd setting: {agent_config.cwd}")
        
        # Create the selected agent dict format expected by execute_task
        selected_agent = {
            'name': agent_config.name,  # Internal name for logging
            'config': agent_config
        }
        
        # Execute the task using the selected agent
        result = await agent_manager.execute_task(selected_agent, prompt)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in delegate: {str(e)}")
        return f"Error executing task: {str(e)}"


# Generate dynamic description and examples
dynamic_description = get_dynamic_tool_description()
dynamic_examples = generate_dynamic_examples()

# Create docstring with dynamic content
delegate_impl.__doc__ = f"""{dynamic_description}

## Parameters:
    agent: Name of the agent to use (must match exactly as listed above)
    prompt: The specific task, question, or request for the agent to perform

## Returns:
    Text response from the selected agent after task completion

## Usage Examples:
{dynamic_examples if dynamic_examples else '    agent: "Default Assistant"' + chr(10) + '    prompt: "Help me understand this codebase"'}
"""

# Register the tool with the dynamic description and proper name
delegate = mcp.tool(name="delegate")(delegate_impl)

# Log summary of what's available
logger.info("\n=== MCP Server Configuration ===")
logger.info(f"Resources: agents://list (dynamic agent information)")
logger.info(f"Prompts: {prompt_count} agent-specific prompts")
logger.info(f"Tools: delegate (run specialized agents)")

# List the registered prompts
try:
    from enhanced_prompt_helpers import sanitize_function_name
    logger.info("\nRegistered prompts:")
    for agent_name in agents_info.keys():
        prompt_name = f"{sanitize_function_name(agent_name)}_task"
        logger.info(f"  - {prompt_name}")
except Exception as e:
    logger.error(f"Could not list prompts: {e}")

logger.info("\nServer ready to handle requests")

if __name__ == "__main__":
    # Run the server
    mcp.run()