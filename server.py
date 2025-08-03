#!/usr/bin/env python3
"""
Task-Agents MCP Server - Multi-Tool Architecture

A Model Context Protocol server that exposes each specialized AI agent as its own tool,
providing direct access to Claude Code CLI with custom configurations.

This is the multi-tool version where each agent is a separate MCP tool.
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
mcp = FastMCP("task-agent")

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


# ============= HELPER FUNCTIONS =============
def sanitize_tool_name(agent_name: str) -> str:
    """Convert agent display name to valid tool name.
    
    Examples:
        'Code Reviewer' -> 'code_reviewer'
        'Default Assistant' -> 'default_assistant'
    """
    return agent_name.lower().replace(' ', '_').replace('-', '_')


def create_agent_tool_function(agent_name: str, agent_config):
    """Create a tool function for a specific agent."""
    async def agent_tool_impl(prompt: str) -> str:
        """Execute agent task."""
        try:
            logger.info(f"=== {agent_name} Tool Called ===")
            logger.info(f"Current process working directory: {os.getcwd()}")
            logger.info(f"Task: {prompt[:100]}...")
            
            # Create the selected agent dict format expected by execute_task
            selected_agent = {
                'name': agent_config.name,  # Internal name for logging
                'config': agent_config
            }
            
            # Execute the task using the selected agent
            result = await agent_manager.execute_task(selected_agent, prompt)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in {agent_name}: {str(e)}")
            return f"Error executing task: {str(e)}"
    
    # Set function metadata
    agent_tool_impl.__name__ = sanitize_tool_name(agent_name)
    agent_tool_impl.__doc__ = f"""{agent_config.description}

Available tools: {', '.join(agent_config.tools)}
Model: {agent_config.model}
Working directory: {agent_config.cwd}

Parameters:
    prompt: The specific task, question, or request for the agent to perform

Returns:
    Text response from the {agent_name} agent after task completion
"""
    
    return agent_tool_impl


# ============= DYNAMIC TOOL REGISTRATION =============
# Register each agent as its own tool
logger.info("\n=== Registering Individual Agent Tools ===")
registered_tools = []

for agent_name, agent_config in agent_manager.agents.items():
    try:
        # Create the tool function for this agent
        tool_func = create_agent_tool_function(agent_config.agent_name, agent_config)
        
        # Register it as an MCP tool
        tool_name = sanitize_tool_name(agent_config.agent_name)
        mcp.tool(name=tool_name)(tool_func)
        
        registered_tools.append(tool_name)
        logger.info(f"Registered tool: {tool_name} for agent: {agent_config.agent_name}")
        
    except Exception as e:
        logger.error(f"Failed to register tool for {agent_name}: {str(e)}")

# Log summary of what's available
logger.info("\n=== MCP Server Configuration ===")
logger.info(f"Resources: agents://list (dynamic agent information)")
logger.info(f"Prompts: {prompt_count} agent-specific prompts")
logger.info(f"Tools: {len(registered_tools)} individual agent tools")

# List the registered tools
logger.info("\nRegistered tools:")
for tool_name in registered_tools:
    logger.info(f"  - {tool_name}")

# List the registered prompts
try:
    from enhanced_prompt_helpers import sanitize_function_name
    logger.info("\nRegistered prompts:")
    agents_info = agent_manager.get_agents_info()
    for agent_name in agents_info.keys():
        prompt_name = f"{sanitize_function_name(agent_name)}_task"
        logger.info(f"  - {prompt_name}")
except Exception as e:
    logger.error(f"Could not list prompts: {e}")

logger.info("\nServer ready to handle requests")

if __name__ == "__main__":
    # Run the server
    mcp.run()