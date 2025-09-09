"""Agent Executor for direct agent execution.

This module provides high-level agent execution functionality for the web UI,
handling agent loading and execution via SDK or CLI subprocess.
"""

import asyncio
import json
import logging
from typing import AsyncGenerator, Optional, Dict, Any
from pathlib import Path

from src.task_agents_mcp.agent_manager import AgentManager
from src.task_agents_mcp.session_store import SessionChainStore as SessionStore
from .sdk_executor import get_sdk_executor

logger = logging.getLogger(__name__)


class AgentExecutor:
    """High-level executor for agents using SDK or CLI subprocess."""
    
    def __init__(self, agents_path: str = './task-agents', use_sdk: bool = True):
        """Initialize the agent executor.
        
        Args:
            agents_path: Path to the agents directory
            use_sdk: Whether to try using SDK first (falls back to CLI if unavailable)
        """
        self.agents_path = agents_path
        self.agent_manager = AgentManager(agents_path)
        self.agent_manager.load_agents()
        self.session_store = SessionStore()
        self.use_sdk = use_sdk
        self.sdk_executor = get_sdk_executor() if use_sdk else None
        
        if self.use_sdk and self.sdk_executor and not self.sdk_executor.is_available():
            logger.warning("SDK not available - agent execution will fail")
            self.use_sdk = False
    
    def list_agents(self) -> Dict[str, Dict[str, Any]]:
        """List all available agents.
        
        Returns:
            Dictionary of agent names to their configurations
        """
        agents = {}
        for name, config in self.agent_manager.agents.items():
            agents[name] = {
                'name': config.agent_name,
                'description': config.description,
                'model': config.model,
                'tools': config.tools,
                'resume_session': getattr(config, 'resume_session', False),
                'max_exchanges': getattr(config, 'max_exchanges', 5)
            }
        return agents
    
    async def execute_agent(
        self,
        agent_name: str,
        prompt: str,
        session_id: Optional[str] = None,
        session_reset: bool = False
    ) -> AsyncGenerator[str, None]:
        """Execute an agent with the given prompt using CLI subprocess.
        
        Args:
            agent_name: Name of the agent to execute
            prompt: The task/prompt to execute
            session_id: Optional session ID for conversation continuity
            session_reset: Whether to reset the session
            
        Yields:
            JSON-formatted response strings
        """
        # Normalize agent name (replace underscores with hyphens)
        normalized_name = agent_name.replace('_', '-')
        
        # Reload agents to pick up any configuration changes
        self.agent_manager.load_agents()
        
        # Find the agent
        agent_config = None
        for name, config in self.agent_manager.agents.items():
            if name == normalized_name or name == agent_name:
                agent_config = config
                break
        
        if not agent_config:
            error = {
                "type": "error",
                "content": {
                    "text": f"Agent '{agent_name}' not found. Available agents: {list(self.agent_manager.agents.keys())}"
                }
            }
            yield json.dumps(error)
            return
        
        # Handle session management for CLI (not SDK)
        cli_session_id = None
        if session_reset:
            self.session_store.clear_chain(agent_config.agent_name)
            cli_session_id = None
        elif agent_config.resume_session:
            # Get the session ID to resume for CLI
            cli_session_id = self.session_store.get_resume_session(
                agent_config.agent_name,
                agent_config.max_exchanges
            )
        
        # Try SDK first if available
        if self.use_sdk and self.sdk_executor and self.sdk_executor.is_available():
            try:
                logger.info(f"Executing agent {agent_name} using SDK")
                # SDK session management is separate from CLI sessions
                # Only use session resumption if the agent has resume-session enabled
                sdk_session_id = None
                if session_reset:
                    # Explicitly requested reset - don't resume even if we have a session
                    logger.info("Session reset requested - starting fresh")
                    sdk_session_id = None
                elif agent_config.resume_session and session_id and '-' in str(session_id):  # Check config AND UUID format
                    sdk_session_id = session_id
                    logger.info(f"Using SDK conversation ID for resumption: {sdk_session_id}")
                elif agent_config.resume_session:
                    logger.info("Agent has resume-session enabled but no valid session_id provided")
                else:
                    logger.info("Agent does not have resume-session enabled, starting fresh")
                
                async for chunk in self.sdk_executor.execute_task(
                    agent_config=agent_config,
                    task_description=prompt,
                    session_id=sdk_session_id
                ):
                    yield chunk  # Already in JSON format from SDK executor
                return
            except Exception as e:
                logger.error(f"SDK execution failed, falling back to CLI: {e}")
                # Fall through to CLI execution
        
        # Fallback to CLI subprocess execution
        try:
            logger.info(f"Executing agent {agent_name} using CLI subprocess")
            async for chunk in self.agent_manager.execute_agent_async(
                agent_config=agent_config,
                prompt=prompt,
                session_id=cli_session_id
            ):
                # Convert to JSON format for WebSocket
                if chunk.strip():
                    # Check if it's already JSON
                    try:
                        json.loads(chunk)
                        yield chunk
                    except json.JSONDecodeError:
                        # Wrap plain text in JSON format
                        wrapped = {
                            "type": "text",
                            "content": {"text": chunk}
                        }
                        yield json.dumps(wrapped)
                
        except Exception as e:
            logger.error(f"Error executing agent {agent_name}: {e}")
            error = {
                "type": "error",
                "content": {
                    "text": f"Error executing agent: {str(e)}"
                }
            }
            yield json.dumps(error)
    
    def get_agent_info(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Agent information or None if not found
        """
        agents = self.list_agents()
        return agents.get(agent_name)