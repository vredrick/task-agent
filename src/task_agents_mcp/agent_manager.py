"""Agent Manager module for Task Agents MCP server.

This module handles loading, managing, and executing AI agents defined
in Markdown files with YAML frontmatter.
"""

import os
import re
import subprocess
import yaml
import json
import logging
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, AsyncGenerator
from .session_store import SessionChainStore as SessionStore
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for an AI agent."""
    agent_name: str
    description: str
    tools: List[str]
    model: str
    cwd: str
    system_prompt: str
    resume_session: Any = False  # Can be bool or int (max exchanges)
    resource_dirs: Optional[List[str]] = None
    file_path: Optional[str] = None
    max_exchanges: int = field(init=False)
    
    def __post_init__(self):
        """Calculate max_exchanges from resume_session value."""
        if isinstance(self.resume_session, bool):
            self.max_exchanges = 5 if self.resume_session else 0
        elif isinstance(self.resume_session, int):
            self.max_exchanges = self.resume_session
            self.resume_session = True  # Enable if number provided
        else:
            self.max_exchanges = 0
            self.resume_session = False


class AgentManager:
    """Manages AI agents and their execution."""
    
    def __init__(self, config_dir: str = "./task-agents"):
        """Initialize the agent manager.
        
        Args:
            config_dir: Directory containing agent configuration files
        """
        self.config_dir = config_dir
        self.agents: Dict[str, AgentConfig] = {}
        self.session_store = SessionStore()
        
    def load_agents(self) -> None:
        """Load all agent configurations from the config directory."""
        if not os.path.exists(self.config_dir):
            logger.warning(f"Agent config directory {self.config_dir} does not exist")
            return
        
        # Clear existing agents to ensure fresh reload
        self.agents = {}
            
        for filename in os.listdir(self.config_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(self.config_dir, filename)
                try:
                    config = self._load_agent_config(filepath)
                    if config:
                        # Use filename without extension as agent key
                        agent_key = filename[:-3]  # Remove .md extension
                        self.agents[agent_key] = config
                        logger.info(f"Loaded agent: {agent_key}")
                except Exception as e:
                    logger.error(f"Failed to load agent from {filepath}: {e}")
    
    def _load_agent_config(self, filepath: str) -> Optional[AgentConfig]:
        """Load an agent configuration from a Markdown file.
        
        Args:
            filepath: Path to the agent configuration file
            
        Returns:
            AgentConfig object or None if loading fails
        """
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Extract YAML frontmatter
            match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
            if not match:
                logger.warning(f"No YAML frontmatter found in {filepath}")
                return None
            
            yaml_content = match.group(1)
            markdown_content = match.group(2)
            
            # Parse YAML
            config_data = yaml.safe_load(yaml_content)
            
            # Extract system prompt (everything after "System-prompt:")
            system_prompt_match = re.search(r'^System-prompt:\s*\n(.*)$', 
                                           markdown_content, re.MULTILINE | re.DOTALL)
            system_prompt = system_prompt_match.group(1).strip() if system_prompt_match else ""
            
            # Parse tools (comma-separated string to list)
            tools = [tool.strip() for tool in config_data.get('tools', '').split(',')]
            
            # Handle optional fields
            optional_config = config_data.get('optional', {})
            
            # Parse resume-session field (can be: false, true, "true 5", or just a number)
            resume_session_value = optional_config.get('resume-session', False)
            if isinstance(resume_session_value, str):
                parts = resume_session_value.split()
                if parts[0].lower() == 'true':
                    if len(parts) > 1:
                        resume_session = int(parts[1])
                    else:
                        resume_session = True
                elif parts[0].lower() == 'false':
                    resume_session = False
                else:
                    # Try to parse as number
                    try:
                        resume_session = int(parts[0])
                    except ValueError:
                        resume_session = False
            elif isinstance(resume_session_value, bool):
                resume_session = resume_session_value
            elif isinstance(resume_session_value, int):
                resume_session = resume_session_value
            else:
                resume_session = False
            
            # Parse resource_dirs (comma-separated string to list)
            resource_dirs = None
            if 'resource_dirs' in optional_config:
                resource_dirs = [
                    dir.strip() 
                    for dir in optional_config['resource_dirs'].split(',')
                ]
            
            return AgentConfig(
                agent_name=config_data.get('agent-name', 'Unnamed Agent'),
                description=config_data.get('description', ''),
                tools=tools,
                model=config_data.get('model', 'haiku'),
                cwd=config_data.get('cwd', '.'),
                system_prompt=system_prompt,
                resume_session=resume_session,
                resource_dirs=resource_dirs,
                file_path=filepath
            )
            
        except Exception as e:
            logger.error(f"Error loading agent config from {filepath}: {e}")
            return None
    
    def get_agent(self, agent_name: str) -> Optional[AgentConfig]:
        """Get an agent configuration by name.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            AgentConfig object or None if not found
        """
        return self.agents.get(agent_name)
    
    async def execute_agent_async(
        self,
        agent_config: AgentConfig,
        prompt: str,
        session_id: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Execute an agent asynchronously with streaming output.
        
        Args:
            agent_config: The agent configuration
            prompt: The task/prompt to execute
            session_id: Optional session ID for resumption
            
        Yields:
            Streaming output from the agent
        """
        # Get claude executable path
        import shutil
        claude_path = os.environ.get('CLAUDE_EXECUTABLE_PATH') or shutil.which('claude')
        
        if not claude_path:
            yield json.dumps({
                "type": "error",
                "content": {"text": "Claude CLI not found. Please install Claude Code CLI."}
            })
            return
        
        # Build command
        cmd = [claude_path]
        
        # Add model flag
        if agent_config.model:
            cmd.extend(['-m', agent_config.model])
        
        # Add tools if specified
        if agent_config.tools:
            for tool in agent_config.tools:
                cmd.extend(['-A', tool])
        
        # Add working directory
        if agent_config.cwd and agent_config.cwd != '.':
            cmd.extend(['--cwd', agent_config.cwd])
        
        # Add session resumption if provided
        if session_id:
            cmd.extend(['-r', session_id])
        
        # Add stream-json flag for structured output
        cmd.append('--stream-json')
        
        # Prepare the input (system prompt + user prompt)
        full_prompt = f"{agent_config.system_prompt}\n\nUser: {prompt}" if agent_config.system_prompt else prompt
        
        try:
            # Create subprocess
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Send prompt to stdin
            process.stdin.write(full_prompt.encode('utf-8'))
            await process.stdin.drain()
            process.stdin.close()
            
            # Stream output
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                    
                output = line.decode('utf-8').strip()
                if output:
                    yield output
            
            # Wait for process to complete
            await process.wait()
            
            # Check for errors
            if process.returncode != 0:
                stderr = await process.stderr.read()
                error_msg = stderr.decode('utf-8').strip()
                if error_msg:
                    yield json.dumps({
                        "type": "error",
                        "content": {"text": f"Agent error: {error_msg}"}
                    })
                    
        except Exception as e:
            logger.error(f"Error executing agent: {e}")
            yield json.dumps({
                "type": "error",
                "content": {"text": f"Execution error: {str(e)}"}
            })
    
    async def execute_agent(
        self,
        agent_config: AgentConfig,
        task_description: str,
        session_reset: bool = False,
        progress_callback: Optional[callable] = None
    ) -> str:
        """Execute an agent with a given task.
        
        Args:
            agent_config: The agent configuration to execute
            task_description: The task/query for the agent
            session_reset: Whether to reset the session chain
            progress_callback: Optional async callback for progress updates
            
        Returns:
            The agent's response as a string
        """
        # Check if SDK executor is available (it's not in our case)
        # Fallback to CLI execution
        
        # Handle session reset if requested
        if session_reset and agent_config.resume_session:
            logger.info(f"Resetting session for agent: {agent_config.agent_name}")
            self.session_store.clear_chain(agent_config.agent_name)
            if progress_callback:
                await progress_callback(f"🔄 Session reset for {agent_config.agent_name}")
        
        # Determine if we should resume a session
        resume_session_id = None
        was_resume = False
        if agent_config.resume_session and not session_reset:
            # Calculate max exchanges
            if agent_config.resume_session is True:
                max_exchanges = 5  # Default when just "true"
            else:
                max_exchanges = agent_config.resume_session
            
            # Get session to resume
            resume_session_id = self.session_store.get_resume_session(
                agent_config.agent_name,
                max_exchanges
            )
            was_resume = resume_session_id is not None
        
        # Get claude executable path from environment or try to find it
        claude_path = os.environ.get('CLAUDE_EXECUTABLE_PATH')
        
        if not claude_path:
            # Try to find claude in PATH
            import shutil
            claude_path = shutil.which('claude')
            
            if not claude_path:
                # Check common installation locations
                common_paths = [
                    os.path.expanduser('~/.claude/local/claude'),
                    '/usr/local/bin/claude',
                    '/opt/homebrew/bin/claude'
                ]
                for path in common_paths:
                    if os.path.exists(path) and os.access(path, os.X_OK):
                        claude_path = path
                        break
                        
            if not claude_path:
                return "Error: Claude Code CLI not found. Please install Claude Code CLI from https://claude.ai/download or set CLAUDE_EXECUTABLE_PATH environment variable."
        
        # Build the command
        cmd = [claude_path]
        
        # Add model flag
        if agent_config.model:
            cmd.extend(['-m', agent_config.model])
        
        # Add tools if specified
        if agent_config.tools:
            for tool in agent_config.tools:
                cmd.extend(['-A', tool])
        
        # Add working directory
        if agent_config.cwd and agent_config.cwd != '.':
            cmd.extend(['--cwd', agent_config.cwd])
        
        # Add session resumption if we have a session to resume
        if resume_session_id:
            cmd.extend(['-r', resume_session_id])
            
            # Get session info for exchange count
            session_info = self.session_store.get_session_info(agent_config.agent_name)
            exchange_count = session_info.get('exchange_count', 0) if session_info else 0
            max_exchanges = agent_config.max_exchanges or 5
            
            if progress_callback:
                await progress_callback(f"📊 Resuming session (Exchange {exchange_count + 1}/{max_exchanges})")
            
            logger.info(f"Resuming session {resume_session_id} for {agent_config.agent_name} (exchange {exchange_count + 1}/{max_exchanges})")
        else:
            if progress_callback:
                await progress_callback("🚀 Starting new session")
        
        # Prepare the full prompt
        full_prompt = agent_config.system_prompt + "\n\n" + task_description
        
        if progress_callback:
            await progress_callback(f"🤖 Executing {agent_config.agent_name} with {agent_config.model} model")
        
        try:
            # Execute the command with the prompt piped to stdin
            # Set timeout to 2 minutes (120 seconds)
            result = subprocess.run(
                cmd,
                input=full_prompt,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                error_msg = f"Error executing agent: {result.stderr}"
                logger.error(error_msg)
                return error_msg
            
            response = result.stdout
            
            # Extract session ID from response if available
            # Look for pattern like "Session: <session-id>"
            import re
            session_match = re.search(r'Session:\s+([a-zA-Z0-9-]+)', response)
            if session_match:
                new_session_id = session_match.group(1)
                
                # Update session store if this is a resumable agent
                if agent_config.resume_session:
                    if was_resume:
                        # Continue the chain
                        self.session_store.add_to_chain(agent_config.agent_name, new_session_id)
                    else:
                        # Start a new chain
                        self.session_store.start_chain(agent_config.agent_name, new_session_id)
                    
                    # Get updated session info
                    session_info = self.session_store.get_session_info(agent_config.agent_name)
                    exchange_count = session_info.get('exchange_count', 0) if session_info else 0
                    max_exchanges = agent_config.max_exchanges or 5
                    
                    if progress_callback:
                        await progress_callback(f"✅ Session saved ({exchange_count}/{max_exchanges} exchanges used)")
                    
                    logger.info(f"Session {new_session_id} saved for {agent_config.agent_name}")
            
            if progress_callback:
                await progress_callback("✨ Task completed successfully")
            
            return response
            
        except subprocess.TimeoutExpired:
            error_msg = "Error: Agent execution timed out after 2 minutes"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error executing agent: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def list_agents(self) -> List[str]:
        """List all available agent names.
        
        Returns:
            List of agent names
        """
        return list(self.agents.keys())