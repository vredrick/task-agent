"""
Agent Manager for Task-Agents MCP Server

Handles agent discovery, selection, and task execution via Claude Code CLI.
"""

import os
import re
import yaml
import logging
import subprocess
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Awaitable, Union
from dataclasses import dataclass

from .session_store import SessionChainStore

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for a single agent."""
    name: str  # File name (for internal use)
    agent_name: str  # Display name for the agent
    description: str
    tools: List[str]
    model: str
    cwd: str
    system_prompt: str
    resume_session: Union[bool, int] = False  # False, True (5 default), or specific number
    resource_dirs: List[str] = None  # Optional additional directories to add via --add-dir
    

class AgentManager:
    """Manages agent configurations and task delegation."""
    
    def __init__(self, configs_dir: str = "configs"):
        self.configs_dir = Path(configs_dir)
        self.agents: Dict[str, AgentConfig] = {}
        
        # Initialize session store with persistent storage
        session_store_path = Path("/tmp/task_agents_sessions.json")
        self.session_store = SessionChainStore(session_store_path)
        
    def load_agents(self) -> None:
        """Load all agent configurations from the configs directory."""
        if not self.configs_dir.exists():
            logger.warning(f"Configs directory not found: {self.configs_dir}")
            return
            
        for config_file in self.configs_dir.glob("*.md"):
            try:
                agent = self._parse_agent_config(config_file)
                if agent:
                    self.agents[agent.name] = agent
                    logger.info(f"Loaded agent: {agent.name}")
            except Exception as e:
                logger.error(f"Error loading agent config {config_file}: {e}")
                
    def _parse_agent_config(self, config_path: Path) -> Optional[AgentConfig]:
        """Parse a single agent configuration file."""
        content = config_path.read_text()
        
        # Extract YAML frontmatter
        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
        if not frontmatter_match:
            logger.error(f"Invalid config format in {config_path}")
            return None
            
        try:
            # Parse YAML frontmatter
            frontmatter = yaml.safe_load(frontmatter_match.group(1))
            system_prompt_section = frontmatter_match.group(2)
            
            # Extract system prompt
            system_prompt_match = re.search(r'System-prompt:\s*\n(.*)$', system_prompt_section, re.DOTALL)
            system_prompt = system_prompt_match.group(1).strip() if system_prompt_match else ""
            
            # Validate required fields
            required_fields = ['agent-name', 'description', 'tools', 'model', 'cwd']
            for field in required_fields:
                if field not in frontmatter:
                    logger.error(f"Missing required field '{field}' in {config_path}")
                    return None
            
            # Parse tools list
            tools = frontmatter['tools']
            if isinstance(tools, str):
                tools = [t.strip() for t in tools.split(',')]
            
            # Expand environment variables in cwd
            cwd = os.path.expandvars(frontmatter.get('cwd', '.'))
            
            # Keep cwd as-is for now - it will be resolved during execution
            # This allows for different behaviors based on the execution context
            
            # Parse optional fields
            resume_session = False
            resource_dirs = None
            
            if 'optional' in frontmatter and isinstance(frontmatter['optional'], dict):
                optional = frontmatter['optional']
                
                # Parse resume-session
                resume_val = optional.get('resume-session', False)
                if isinstance(resume_val, bool):
                    resume_session = resume_val
                elif isinstance(resume_val, int) and resume_val > 0:
                    resume_session = resume_val
                elif isinstance(resume_val, str):
                    # Parse string format like "true", "false", "true 5", or just "5"
                    parts = resume_val.strip().split()
                    if parts[0].lower() == 'true':
                        # "true" or "true 5"
                        resume_session = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 5
                    elif parts[0].lower() == 'false':
                        resume_session = False
                    elif parts[0].isdigit():
                        # Just a number like "5"
                        resume_session = int(parts[0])
                
                # Parse resource_dirs (similar to tools parsing)
                resource_dirs_val = optional.get('resource_dirs')
                if resource_dirs_val:
                    if isinstance(resource_dirs_val, str):
                        # Parse comma-separated string like tools
                        resource_dirs = [d.strip() for d in resource_dirs_val.split(',')]
                    elif isinstance(resource_dirs_val, list):
                        # Already a list
                        resource_dirs = resource_dirs_val
            
            return AgentConfig(
                name=config_path.stem,
                agent_name=frontmatter['agent-name'],
                description=frontmatter['description'],
                tools=tools,
                model=frontmatter['model'],
                cwd=cwd,
                system_prompt=system_prompt,
                resume_session=resume_session,
                resource_dirs=resource_dirs
            )
            
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in {config_path}: {e}")
            return None
            
        
    def get_agent_by_display_name(self, display_name: str) -> Optional[AgentConfig]:
        """Get agent by its display name (agent-name field)."""
        for agent in self.agents.values():
            if agent.agent_name == display_name:
                return agent
        return None
        
    def get_agents_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available agents."""
        return {
            agent.agent_name: {
                'description': agent.description,
                'model': agent.model,
                'internal_name': name
            }
            for name, agent in self.agents.items()
        }
        
    async def execute_task(self, selected_agent: Dict[str, Any], task_description: str, 
                          progress_callback: Optional[Callable[[str], Awaitable[None]]] = None) -> str:
        """Execute a task using the selected agent via Claude Code CLI.
        
        Args:
            selected_agent: The agent configuration to use
            task_description: The task to execute
            progress_callback: Optional async callback for progress updates
        
        Returns:
            The final response from the agent
        """
        agent_config = selected_agent['config']
        
        # Determine if we should resume a session
        resume_session_id = None
        was_resume = False
        if agent_config.resume_session:
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
        
        # Start building the command
        cmd = [
            claude_path,
            '-p', task_description,
            '--system-prompt', agent_config.system_prompt,
            '--output-format', 'stream-json',
            '--verbose',  # Required for stream-json output
            '--allowedTools', *agent_config.tools,  # Unpack list for space-separated tools
            '--model', agent_config.model
        ]
        
        # Add resume flag if we have a session to resume
        if resume_session_id:
            cmd.extend(['-r', resume_session_id])
            logger.info(f"Resuming session {resume_session_id} for {agent_config.agent_name}")
        
        try:
            # Resolve the working directory from agent config
            cwd = agent_config.cwd
            
            
            # If cwd is '.', use the parent directory of the task-agents folder
            if cwd == '.':
                # The task-agents folder is always at configs_dir
                # We want to go to the parent directory of the task-agents folder
                task_agents_dir = Path(self.configs_dir).resolve()
                # Always go up one level from the task-agents directory
                cwd = str(task_agents_dir.parent)
                logger.info(f"Agent cwd was '.', resolved to: {cwd}")
            
            # Expand environment variables and make absolute
            working_dir = os.path.abspath(os.path.expandvars(cwd))
            
            # Add --add-dir flag to ensure Claude has access to the working directory
            cmd.extend(['--add-dir', working_dir])
            
            # Add any additional resource directories specified in agent config
            resolved_resource_dirs = []
            accessible_resource_dirs = []
            missing_resource_dirs = []
            
            if agent_config.resource_dirs:
                for resource_dir in agent_config.resource_dirs:
                    # Resolve resource_dir relative to the working directory
                    if not os.path.isabs(resource_dir):
                        # Relative path - resolve from working directory
                        resolved_dir = os.path.abspath(os.path.join(working_dir, resource_dir))
                    else:
                        # Absolute path - use as-is  
                        resolved_dir = os.path.abspath(os.path.expandvars(resource_dir))
                    
                    resolved_resource_dirs.append((resource_dir, resolved_dir))
                    
                    # Check if directory exists before adding
                    if os.path.exists(resolved_dir) and os.path.isdir(resolved_dir):
                        cmd.extend(['--add-dir', resolved_dir])
                        logger.info(f"Added resource directory: {resolved_dir}")
                        accessible_resource_dirs.append(resolved_dir)
                    else:
                        logger.warning(f"Resource directory not found or not a directory: {resolved_dir}")
                        missing_resource_dirs.append((resource_dir, resolved_dir))
            
            # Build dynamic resource directory instruction
            resource_info = []
            if accessible_resource_dirs:
                resource_info.append(f"ACCESSIBLE RESOURCES: {', '.join(accessible_resource_dirs)}")
            if missing_resource_dirs:
                missing_list = [f"{orig} (looked at: {resolved})" for orig, resolved in missing_resource_dirs]
                resource_info.append(f"MISSING RESOURCES: {', '.join(missing_list)}")
            
            # Append system prompt instruction to inform about the working directory and resources
            working_dir_instruction = f"\n\nWORKING DIRECTORY CONTEXT: You are currently operating from the directory: {working_dir}"
            if resource_info:
                working_dir_instruction += f"\n{chr(10).join(resource_info)}"
            
            # Combine the original system prompt with the working directory instruction
            combined_system_prompt = agent_config.system_prompt + working_dir_instruction
            
            # Update the command to use the combined system prompt
            # Find and replace the system prompt in the command
            for i, arg in enumerate(cmd):
                if arg == '--system-prompt' and i + 1 < len(cmd):
                    cmd[i + 1] = combined_system_prompt
                    break
            
            # Log the full command for debugging
            logger.info(f"Agent config cwd: {agent_config.cwd}")
            logger.info(f"Resolved cwd: {cwd}")
            logger.info(f"Final working directory: {working_dir}")
            logger.info(f"Appending working directory instruction to system prompt")
            logger.info(f"Executing command: {' '.join(cmd)}")
            logger.info(f"Using model: {agent_config.model}")
            
            # Verify the working directory exists
            if not os.path.exists(working_dir):
                logger.error(f"Working directory does not exist: {working_dir}")
                return f"Error: Working directory does not exist: {working_dir}"
            
            # Run the command asynchronously with a timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=working_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.DEVNULL  # Ensure no interactive input is expected
            )
            
            # Wait for the command to complete - no timeout
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                stdout_msg = stdout.decode('utf-8') if stdout else ""
                logger.error(f"Claude CLI error (return code {process.returncode}): {error_msg}")
                if stdout_msg:
                    logger.error(f"Claude CLI stdout: {stdout_msg}")
                return f"Error executing Claude CLI (return code {process.returncode}): {error_msg}"
                
            # Parse stream-json output
            output = stdout.decode('utf-8').strip()
            if not output:
                logger.warning("Claude CLI returned empty output")
                stderr_msg = stderr.decode('utf-8') if stderr else ""
                if stderr_msg:
                    logger.warning(f"Claude CLI stderr: {stderr_msg}")
                return "Claude CLI returned empty output. The command may have completed without generating a response."
            
            # Send initial progress update
            if progress_callback:
                await progress_callback(f"🚀 Starting {agent_config.agent_name} agent...")
            
            # Split output into lines for parsing
            output_lines = output.split('\n')
            
            # Extract the final assistant message from the stream
            assistant_messages = []  # Collect all text segments
            logger.debug(f"Total output lines: {len(output_lines)}")
            
            # Track progress events and usage
            tool_count = 0
            tools_used = []
            token_usage = {}
            total_cost = None
            session_id = None
            
            for line in output.split('\n'):
                if line.strip():
                    try:
                        event = json.loads(line)
                        event_type = event.get('type')
                        logger.debug(f"Event type: {event_type}")
                        
                        # Capture session ID from system init
                        if event_type == 'system' and event.get('subtype') == 'init':
                            session_id = event.get('session_id')
                            logger.info(f"Session ID: {session_id}")
                        
                        # Look for assistant messages
                        elif event_type == 'assistant' and 'message' in event:
                            message = event['message']
                            if message.get('content'):
                                content_list = message['content']
                                # Process content items
                                for content_item in content_list:
                                    item_type = content_item.get('type')
                                    
                                    if item_type == 'text' and content_item.get('text'):
                                        # Text content - accumulate all segments
                                        text_content = content_item['text']
                                        assistant_messages.append(text_content)
                                        logger.debug(f"Found assistant text: {text_content[:100]}")
                                    
                                    elif item_type == 'tool_use':
                                        # Tool use content
                                        tool_name = content_item.get('name', 'unknown')
                                        tool_count += 1
                                        tools_used.append(tool_name)
                                        if progress_callback:
                                            await progress_callback(f"🔧 Using tool: {tool_name} (#{tool_count})")
                        
                        # Also check the result for the final output
                        elif event_type == 'result':
                            if event.get('result'):
                                # The result field might contain the final output
                                result_text = event['result']
                                if result_text and isinstance(result_text, str):
                                    # Override accumulated messages with final result
                                    assistant_messages = [result_text]
                                    logger.debug(f"Found result text: {result_text[:100]}")
                            
                            # Extract token usage and cost
                            if 'usage' in event:
                                token_usage = event['usage']
                            if 'total_cost_usd' in event:
                                total_cost = event['total_cost_usd']
                            
                            if progress_callback:
                                await progress_callback("✅ Task completed!")
                                
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse JSON line: {line[:100]}... Error: {e}")
                        # Check if it's a partial line that might be concatenated
                        if line.startswith('{') and not line.endswith('}'):
                            logger.debug("Detected potential partial JSON line, skipping...")
                        continue
                    except Exception as e:
                        logger.error(f"Unexpected error parsing line: {e}")
                        continue
            
            # Log parsing summary
            logger.info(f"Parsing complete - Messages: {len(assistant_messages)}, Tools: {len(tools_used)}, Session: {session_id}")
            
            # Combine all assistant messages
            final_message = '\n'.join(assistant_messages) if assistant_messages else ""
            
            if not final_message:
                logger.warning("No assistant message found in stream-json output")
                if progress_callback:
                    await progress_callback("⚠️ Task completed but no response was generated")
                return "Task completed but no response message was generated."
            
            # Update session store with the NEW session ID
            if session_id and agent_config.resume_session:
                self.session_store.update_chain(
                    agent_config.agent_name,
                    session_id,
                    was_resume=was_resume
                )
            
            # Format the response with tool usage first
            formatted_response = ""
            
            # Add session ID and chain info if available
            if session_id:
                formatted_response += f"Session: {session_id}\n"
                
                # Add session chain info if resume is enabled
                if agent_config.resume_session:
                    chain_info = self.session_store.get_chain_info(agent_config.agent_name)
                    if chain_info:
                        formatted_response += f"Exchange: {chain_info['exchange_count']}"
                        if agent_config.resume_session is True:
                            formatted_response += "/5"
                        else:
                            formatted_response += f"/{agent_config.resume_session}"
                        formatted_response += "\n"
            
            # Add tool usage summary if any tools were used
            if tools_used:
                formatted_response += f"Tools used: {', '.join(tools_used)}\n\n"
            
            # Add the actual message
            formatted_response += final_message
            
            # Add token usage if available
            if token_usage:
                input_tokens = token_usage.get('input_tokens', 0)
                output_tokens = token_usage.get('output_tokens', 0)
                total_tokens = input_tokens + output_tokens
                
                formatted_response += f"\n\nTokens: {total_tokens:,} ({input_tokens:,} in, {output_tokens:,} out)"
            
            return formatted_response
            
        except FileNotFoundError:
            return "Error: Claude CLI not found. Please ensure 'claude' is installed and in PATH."
        except Exception as e:
            logger.error(f"Error executing task: {str(e)}")
            return f"Error executing task: {str(e)}"