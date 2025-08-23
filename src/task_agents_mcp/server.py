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
from fastmcp import FastMCP, Context
import re

from .agent_manager import AgentManager
from .resource_manager import AgentResourceManager

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

# Initialize FastMCP server with duplicate resource handling
mcp = FastMCP("task-agent", on_duplicate_resources="replace")

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
        logger.warning(f"Agents directory not found: {config_dir}")
        logger.info(f"Check that TASK_AGENTS_PATH points to a valid directory")
    else:
        logger.warning(f"No task-agents directory found at: {config_dir}")
        logger.info("To add agents:")
        logger.info("  - For Claude Code: Create .md agent files in './task-agents' directory in your project")
        logger.info("  - For Claude Desktop: Set TASK_AGENTS_PATH to your agents directory")

# Initialize agent manager and load agents
agent_manager = AgentManager(config_dir)
agent_manager.load_agents()

# Check if any agents were loaded
if not agent_manager.agents:
    logger.warning("No agents loaded!")
    logger.info("The server is running but no agent tools are available.")
    logger.info("Add .md agent configuration files to your agents directory:")
    logger.info(f"  Current agents directory: {config_dir}")
    logger.info("  Example agent format: https://github.com/vredrick/task-agent/tree/main/examples/agents")
else:
    logger.info(f"Loaded {len(agent_manager.agents)} agents from {config_dir}")

# Log available agents
agents_info = agent_manager.get_agents_info()
for name, info in agents_info.items():
    logger.info(f"  - {name}: {info['description']}")

# Initialize resource manager and register resources
resource_manager = AgentResourceManager(mcp, agent_manager)
resource_manager.register_all_resources()


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
        async def agent_tool_impl(prompt: str, ctx: Context, session_reset: bool = False) -> str:
            """Execute agent task with optional session reset."""
            try:
                logger.info(f"=== {agent_name} Tool Called ===")
                logger.info(f"Current process working directory: {os.getcwd()}")
                logger.info(f"Task: {prompt[:100]}...")
                if session_reset:
                    logger.info(f"Session reset requested for {agent_name}")
                
                # Create progress bridge function
                async def progress_bridge(message: str):
                    """Bridge between agent progress messages and MCP context."""
                    try:
                        # Log if we have a progress token (for debugging)
                        if hasattr(ctx, '_progress_token') and ctx._progress_token:
                            logger.debug(f"Progress token present: {ctx._progress_token}")
                        
                        # Parse different types of progress messages
                        if "🚀 Starting" in message or "Starting" in message:
                            await ctx.report_progress(0, 100)
                            await ctx.info(message)
                        elif "🔧 Using tool" in message or "Using tool" in message:
                            # Extract tool number from message like "🔧 Using tool: Read (#1)"
                            match = re.search(r'#(\d+)', message)
                            if match:
                                tool_num = int(match.group(1))
                                # Progress: 10% base + 15% per tool, max 90%
                                progress = min(10 + (tool_num * 15), 90)
                                await ctx.report_progress(progress, 100)
                            await ctx.info(message)
                        elif "🔄 Session reset" in message:
                            await ctx.report_progress(5, 100)
                            await ctx.info(message)
                        elif "✅ Task completed" in message or "completed" in message.lower():
                            await ctx.report_progress(100, 100)
                            await ctx.info(message)
                        elif "⚠️" in message:
                            # Warning but still complete
                            await ctx.report_progress(100, 100)
                            await ctx.warning(message)
                        else:
                            # Just log other messages
                            await ctx.info(message)
                    except Exception as e:
                        logger.debug(f"Progress bridge error (non-critical): {e}")
                
                # Create the selected agent dict format expected by execute_task
                selected_agent = {
                    'name': agent_config.name,  # Internal name for logging
                    'config': agent_config
                }
                
                # Execute the task using the selected agent with session_reset and progress callback
                result = await agent_manager.execute_task(
                    selected_agent, 
                    prompt, 
                    session_reset=session_reset,
                    progress_callback=progress_bridge
                )
                
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
        async def agent_tool_impl(prompt: str, ctx: Context) -> str:
            """Execute agent task."""
            try:
                logger.info(f"=== {agent_name} Tool Called ===")
                logger.info(f"Current process working directory: {os.getcwd()}")
                logger.info(f"Task: {prompt[:100]}...")
                
                # Create progress bridge function (same as above)
                async def progress_bridge(message: str):
                    """Bridge between agent progress messages and MCP context."""
                    try:
                        # Log if we have a progress token (for debugging)
                        if hasattr(ctx, '_progress_token') and ctx._progress_token:
                            logger.debug(f"Progress token present: {ctx._progress_token}")
                        
                        # Parse different types of progress messages
                        if "🚀 Starting" in message or "Starting" in message:
                            await ctx.report_progress(0, 100)
                            await ctx.info(message)
                        elif "🔧 Using tool" in message or "Using tool" in message:
                            # Extract tool number from message like "🔧 Using tool: Read (#1)"
                            match = re.search(r'#(\d+)', message)
                            if match:
                                tool_num = int(match.group(1))
                                # Progress: 10% base + 15% per tool, max 90%
                                progress = min(10 + (tool_num * 15), 90)
                                await ctx.report_progress(progress, 100)
                            await ctx.info(message)
                        elif "✅ Task completed" in message or "completed" in message.lower():
                            await ctx.report_progress(100, 100)
                            await ctx.info(message)
                        elif "⚠️" in message:
                            # Warning but still complete
                            await ctx.report_progress(100, 100)
                            await ctx.warning(message)
                        else:
                            # Just log other messages
                            await ctx.info(message)
                    except Exception as e:
                        logger.debug(f"Progress bridge error (non-critical): {e}")
                
                # Create the selected agent dict format expected by execute_task
                selected_agent = {
                    'name': agent_config.name,  # Internal name for logging
                    'config': agent_config
                }
                
                # Execute the task using the selected agent with progress callback
                result = await agent_manager.execute_task(
                    selected_agent, 
                    prompt,
                    progress_callback=progress_bridge
                )
                
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
logger.info(f"Resources: {len(resource_manager.registered_resources)} registered")
for resource_uri in resource_manager.registered_resources.keys():
    logger.info(f"  - {resource_uri}")
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