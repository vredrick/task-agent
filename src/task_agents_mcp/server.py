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

from .agent_manager import AgentManager

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
logger.info(f"CLAUDE_EXECUTABLE_PATH env: {os.environ.get('CLAUDE_EXECUTABLE_PATH', 'NOT SET (will auto-detect)')}")

# Initialize FastMCP server
mcp = FastMCP("task-agent")

# Look for task-agents directory
# 1. First check environment variable (for Claude Desktop and other MCP clients)
# 2. Fall back to current working directory (for Claude Code CLI)
config_dir = os.environ.get('TASK_AGENTS_PATH')
if not config_dir:
    # Default to task-agents subdirectory in current working directory
    config_dir = os.path.join(os.getcwd(), "task-agents")

# Check if config directory exists
if not os.path.exists(config_dir):
    if os.environ.get('TASK_AGENTS_PATH'):
        logger.error(f"Config directory not found: {config_dir}")
        logger.error(f"Check that TASK_AGENTS_PATH points to a valid directory")
    else:
        logger.warning(f"No task-agents directory found at: {config_dir}")
        logger.info("Server will start with built-in agents only")
        logger.info("To add custom agents:")
        logger.info("  - For Claude Code: Create a 'task-agents' directory in your project")
        logger.info("  - For Claude Desktop: Set TASK_AGENTS_PATH environment variable")

# Initialize agent manager and load agents
agent_manager = AgentManager(config_dir)
agent_manager.load_agents()

logger.info("Starting task-agents MCP server...")
logger.info(f"Loaded {len(agent_manager.agents)} agents")

# Log available agents
agents_info = agent_manager.get_agents_info()
for name, info in agents_info.items():
    logger.info(f"  - {name}: {info['description']}")

# Enhanced resources and prompts removed - most MCP clients don't support them yet


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
    
    # Check if agent supports session resumption
    if agent_config.resume_session:
        # Create function with session_reset parameter
        async def agent_tool_impl(prompt: str, session_reset: bool = False) -> str:
            """Execute agent task with optional session reset."""
            try:
                logger.info(f"=== {agent_name} Tool Called ===")
                logger.info(f"Current process working directory: {os.getcwd()}")
                logger.info(f"Task: {prompt[:100]}...")
                if session_reset:
                    logger.info(f"Session reset requested for {agent_name}")
                
                # Create the selected agent dict format expected by execute_task
                selected_agent = {
                    'name': agent_config.name,  # Internal name for logging
                    'config': agent_config
                }
                
                # Execute the task using the selected agent with session_reset
                result = await agent_manager.execute_task(selected_agent, prompt, session_reset=session_reset)
                
                return result
                
            except Exception as e:
                logger.error(f"Error in {agent_name}: {str(e)}")
                return f"Error executing task: {str(e)}"
        
        # Set function metadata with session_reset parameter
        agent_tool_impl.__name__ = sanitize_tool_name(agent_name)
        agent_tool_impl.__doc__ = f"""{agent_config.description}

Available tools: {', '.join(agent_config.tools)}
Model: {agent_config.model}
Working directory: {agent_config.cwd}
Session support: Enabled (max {agent_config.resume_session if isinstance(agent_config.resume_session, int) else 5} exchanges)

Parameters:
    prompt: The specific task, question, or request for the agent to perform
    session_reset: Optional. Reset the session context before executing (default: False)

Returns:
    Text response from the {agent_name} agent after task completion
"""
    else:
        # Create function without session_reset parameter (original version)
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
        
        # Set function metadata without session_reset parameter
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
# Prompts feature removed - most MCP clients don't support them yet
logger.info(f"Tools: {len(registered_tools)} individual agent tools")

# List the registered tools
logger.info("\nRegistered tools:")
for tool_name in registered_tools:
    logger.info(f"  - {tool_name}")

# Prompts feature removed - most MCP clients don't support them yet

logger.info("\nServer ready to handle requests")

def main():
    """Main entry point for the server."""
    mcp.run()

if __name__ == "__main__":
    # Run the server
    main()