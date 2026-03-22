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
    disallowed_tools: List[str] = None  # Optional tools to deny via --disallowed-tools
    mcp_config: Optional[str] = None  # Optional path to MCP config JSON via --mcp-config
    plugin_dir: Optional[str] = None  # Path to plugin directory (for registry-based agents)
    prompt_type: str = "override"  # "override" or "append" (how PROMPT.md is applied)
    is_plugin_agent: bool = False  # True if loaded from plugin registry
    prompt_file: Optional[str] = None  # Path to PROMPT.md file
    

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

        # Resolve symlinks to detect plugin directories
        real_path = os.path.realpath(str(config_path))
        plugin_dir = None
        is_plugin = False
        prompt_file = None
        prompt_type = "override"

        parent_dir = Path(real_path).parent
        if (parent_dir / ".claude-plugin").is_dir():
            plugin_dir = str(parent_dir)
            is_plugin = True
            prompt_file = real_path
            logger.info(f"Auto-detected plugin agent: {config_path.name} -> {plugin_dir}")

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
            disallowed_tools = None
            mcp_config = None
            
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

                # Parse disallowed-tools
                disallowed_tools_val = optional.get('disallowed-tools') or optional.get('disallowed_tools')
                if disallowed_tools_val:
                    if isinstance(disallowed_tools_val, str):
                        disallowed_tools = [t.strip() for t in disallowed_tools_val.split(',')]
                    elif isinstance(disallowed_tools_val, list):
                        disallowed_tools = disallowed_tools_val

                # Parse mcp-config
                mcp_config_val = optional.get('mcp-config') or optional.get('mcp_config')
                if mcp_config_val and isinstance(mcp_config_val, str):
                    mcp_config = mcp_config_val.strip()

                # Parse prompt-type (for plugin agents)
                prompt_type_val = optional.get('prompt-type', optional.get('prompt_type'))
                if prompt_type_val:
                    prompt_type = prompt_type_val

            # Auto-detect mcp.json for plugin agents
            if is_plugin and not mcp_config:
                mcp_json = os.path.join(plugin_dir, "mcp.json")
                if os.path.exists(mcp_json):
                    mcp_config = mcp_json
                    logger.info(f"Auto-detected mcp.json at {mcp_json}")

            return AgentConfig(
                name=config_path.stem,
                agent_name=frontmatter['agent-name'],
                description=frontmatter['description'],
                tools=tools,
                model=frontmatter['model'],
                cwd=cwd,
                system_prompt=system_prompt,
                resume_session=resume_session,
                resource_dirs=resource_dirs,
                disallowed_tools=disallowed_tools,
                mcp_config=mcp_config,
                plugin_dir=plugin_dir,
                prompt_type=prompt_type,
                is_plugin_agent=is_plugin,
                prompt_file=prompt_file
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

    def load_registry_agents(self, registry_path: str = None) -> None:
        """Load agents from the plugin registry (~/.claude/plugins/registry.json)."""
        if registry_path is None:
            registry_path = os.path.expanduser("~/.claude/plugins/registry.json")

        registry_file = Path(registry_path)
        if not registry_file.exists():
            logger.info(f"No plugin registry found at {registry_path}")
            return

        try:
            with open(registry_file) as f:
                registry = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to read plugin registry: {e}")
            return

        agents_dict = registry.get("agents", {})
        loaded_count = 0

        for agent_name, entry in agents_dict.items():
            # Skip if MCP tool not enabled
            if not entry.get("mcpToolEnabled", True):
                logger.info(f"Skipping {agent_name}: mcpToolEnabled is false")
                continue

            # Skip if setup not complete
            if not entry.get("setupComplete", True):
                logger.info(f"Skipping {agent_name}: setup not complete")
                continue

            # Skip if already loaded from .md files (md takes precedence)
            if agent_name in self.agents:
                logger.info(f"Skipping registry agent {agent_name}: already loaded from .md")
                continue

            try:
                config = self._parse_registry_agent(agent_name, entry)
                if config:
                    self.agents[config.name] = config
                    loaded_count += 1
                    logger.info(f"Loaded plugin agent: {config.name} ({config.agent_name})")
            except Exception as e:
                logger.error(f"Error loading registry agent {agent_name}: {e}")

        if loaded_count > 0:
            logger.info(f"Loaded {loaded_count} agents from plugin registry")

    def _parse_registry_agent(self, name: str, entry: dict) -> Optional[AgentConfig]:
        """Parse a single agent from a registry entry + its plugin directory."""
        plugin_dir_raw = entry.get("pluginDir", "")
        plugin_dir = os.path.expanduser(plugin_dir_raw)

        if not os.path.isdir(plugin_dir):
            logger.error(f"Plugin directory not found: {plugin_dir}")
            return None

        # Read plugin.json for tool config
        plugin_json_path = os.path.join(plugin_dir, ".claude-plugin", "plugin.json")
        if not os.path.exists(plugin_json_path):
            logger.error(f"No plugin.json at {plugin_json_path}")
            return None

        try:
            with open(plugin_json_path) as f:
                plugin_meta = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to read plugin.json for {name}: {e}")
            return None

        # Read PROMPT.md for system prompt
        prompt_file = os.path.join(plugin_dir, "PROMPT.md")
        system_prompt = ""
        if os.path.exists(prompt_file):
            with open(prompt_file) as f:
                system_prompt = f.read()
        else:
            logger.warning(f"No PROMPT.md found for {name}")

        # Determine tools (from plugin.json, with defaults)
        tools = plugin_meta.get("tools", ["Read", "Write", "Edit", "Bash", "Glob", "Grep"])
        if isinstance(tools, str):
            tools = [t.strip() for t in tools.split(",")]

        # Determine disallowed tools
        disallowed_tools = plugin_meta.get("disallowedTools", [])
        if isinstance(disallowed_tools, str):
            disallowed_tools = [t.strip() for t in disallowed_tools.split(",")]
        disallowed_tools = disallowed_tools if disallowed_tools else None

        # Determine resume session
        resume_session = plugin_meta.get("resumeSession", False)

        # Resolve working directory
        cwd = entry.get("workingDir") or "."

        # MCP config path
        mcp_config_path = os.path.join(plugin_dir, "mcp.json")
        mcp_config = mcp_config_path if os.path.exists(mcp_config_path) else None

        # Display name from registry or derive from name
        display_name = entry.get("displayName", name.replace("-", " ").title())

        return AgentConfig(
            name=name,
            agent_name=display_name,
            description=plugin_meta.get("description", entry.get("domain", "")),
            tools=tools,
            model=entry.get("model", "sonnet"),
            cwd=cwd,
            system_prompt=system_prompt,
            resume_session=resume_session,
            disallowed_tools=disallowed_tools,
            mcp_config=mcp_config,
            plugin_dir=plugin_dir,
            prompt_type=entry.get("promptType", "override"),
            is_plugin_agent=True,
            prompt_file=prompt_file if os.path.exists(prompt_file) else None
        )

    async def execute_task(self, selected_agent: Dict[str, Any], task_description: str, 
                          session_reset: bool = False,
                          progress_callback: Optional[Callable[[str], Awaitable[None]]] = None) -> str:
        """Execute a task using the selected agent via Claude Code CLI.
        
        Args:
            selected_agent: The agent configuration to use
            task_description: The task to execute
            session_reset: Whether to reset the session before executing (default: False)
            progress_callback: Optional async callback for progress updates
        
        Returns:
            The final response from the agent
        """
        agent_config = selected_agent['config']
        
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
        
        # Start building the command
        cmd = [
            claude_path,
            '-p', task_description,
            '--output-format', 'stream-json',
            '--verbose',  # Required for stream-json output
            '--include-partial-messages',
            '--tools', ','.join(agent_config.tools),
            '--model', agent_config.model
        ]
        
        # Add session display name
        session_name = agent_config.agent_name.lower().replace(' ', '_').replace('-', '_')
        cmd.extend(['--name', session_name])

        # Add disallowed tools if configured
        if agent_config.disallowed_tools:
            cmd.extend(['--disallowed-tools', ','.join(agent_config.disallowed_tools)])

        # Add resume flag if we have a session to resume
        if resume_session_id:
            cmd.extend(['-r', resume_session_id])
            logger.info(f"Resuming session {resume_session_id} for {agent_config.agent_name}")
        
        try:
            # Resolve the working directory from agent config
            cwd = agent_config.cwd
            
            
            # If cwd is '.', resolve based on agent type
            if cwd == '.':
                if agent_config.is_plugin_agent:
                    # Plugin agent: use current working directory
                    cwd = os.getcwd()
                    logger.info(f"Plugin agent cwd was '.', resolved to cwd: {cwd}")
                else:
                    # .md agent: use the parent directory of the task-agents folder
                    task_agents_dir = Path(self.configs_dir).resolve()
                    cwd = str(task_agents_dir.parent)
                    logger.info(f"Agent cwd was '.', resolved to: {cwd}")
            
            # Expand environment variables and make absolute
            working_dir = os.path.abspath(os.path.expandvars(cwd))
            
            # Add any resource directories specified in agent config
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
            
            # Add MCP config if specified
            if agent_config.mcp_config:
                mcp_config_path = agent_config.mcp_config
                if not os.path.isabs(mcp_config_path):
                    mcp_config_path = os.path.abspath(os.path.join(working_dir, mcp_config_path))
                if os.path.exists(mcp_config_path):
                    cmd.extend(['--mcp-config', mcp_config_path, '--strict-mcp-config'])
                    logger.info(f"Added MCP config: {mcp_config_path}")
                else:
                    logger.warning(f"MCP config file not found: {mcp_config_path}")

            # Branch: plugin-based agents vs .md-based agents
            if agent_config.is_plugin_agent and agent_config.plugin_dir:
                # Plugin agent: use --plugin-dir + --system-prompt-file
                cmd.extend(['--plugin-dir', agent_config.plugin_dir])

                if agent_config.prompt_file:
                    if agent_config.prompt_type == "append":
                        cmd.extend(['--append-system-prompt-file', agent_config.prompt_file])
                    else:
                        cmd.extend(['--system-prompt-file', agent_config.prompt_file])
                        # Only add working dir context for override agents
                        # (append agents retain default prompt which handles cwd)
                        cmd.extend(['--append-system-prompt',
                                    f"WORKING DIRECTORY CONTEXT: You are currently operating from the directory: {working_dir}"])
            else:
                # .md-based agent: inline system prompt (existing behavior)
                # Build dynamic resource directory instruction
                resource_info = []
                if accessible_resource_dirs:
                    resource_info.append(f"ACCESSIBLE RESOURCES: {', '.join(accessible_resource_dirs)}")
                if missing_resource_dirs:
                    missing_list = [f"{orig} (looked at: {resolved})" for orig, resolved in missing_resource_dirs]
                    resource_info.append(f"MISSING RESOURCES: {', '.join(missing_list)}")

                # Replace [resource_dir] placeholders in system prompt with actual paths
                system_prompt_with_replacements = agent_config.system_prompt
                if accessible_resource_dirs:
                    if len(accessible_resource_dirs) == 1:
                        system_prompt_with_replacements = system_prompt_with_replacements.replace('[resource_dir]', accessible_resource_dirs[0])
                    else:
                        resource_dirs_str = ', '.join(accessible_resource_dirs)
                        system_prompt_with_replacements = system_prompt_with_replacements.replace('[resource_dir]', resource_dirs_str)

                # Add the system prompt with replacements
                cmd.extend(['--system-prompt', system_prompt_with_replacements])

                # Build append-system-prompt instruction for working directory and resources
                append_prompt_parts = []
                append_prompt_parts.append(f"WORKING DIRECTORY CONTEXT: You are currently operating from the directory: {working_dir}")
                if resource_info:
                    append_prompt_parts.extend(resource_info)

                # Add append-system-prompt flag
                append_prompt = '\n'.join(append_prompt_parts)
                cmd.extend(['--append-system-prompt', append_prompt])
            
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
            
            # Send initial progress update
            if progress_callback:
                await progress_callback(f"🚀 Starting {agent_config.agent_name} agent...")
            
            # Stream output line by line for real-time progress
            output_lines = []
            stderr_lines = []
            
            # Extract the final assistant message from the stream
            assistant_messages = []  # Collect all text segments
            
            # Track progress events and usage
            tool_count = 0
            tools_used = []
            token_usage = {}
            total_cost = None
            session_id = None
            
            # Read stdout line by line for real-time streaming
            async def read_stream():
                while True:
                    line = await process.stdout.readline()
                    if not line:
                        break
                    
                    line_str = line.decode('utf-8').strip()
                    if line_str:
                        output_lines.append(line_str)
                        
                        # Process each line as it arrives for real-time progress
                        try:
                            event = json.loads(line_str)
                            await process_event(event)
                        except json.JSONDecodeError:
                            logger.debug(f"Non-JSON line: {line_str[:100]}")
                        except Exception as e:
                            logger.debug(f"Error processing line: {e}")
            
            # Process events as they arrive
            async def process_event(event):
                nonlocal tool_count, session_id
                event_type = event.get('type')
                
                # Capture session ID from system init
                if event_type == 'system' and event.get('subtype') == 'init':
                    session_id = event.get('session_id')
                    logger.info(f"Session ID: {session_id}")

                # Handle partial message streaming events
                elif event_type == 'stream_event':
                    stream_data = event.get('event', {})
                    if stream_data.get('type') == 'content_block_delta':
                        delta = stream_data.get('delta', {})
                        if delta.get('type') == 'text_delta' and delta.get('text'):
                            if progress_callback:
                                await progress_callback(f"partial:{delta['text']}")

                # Look for tool use events for progress
                elif event_type == 'assistant' and 'message' in event:
                    message = event['message']
                    if message.get('content'):
                        for content_item in message['content']:
                            if content_item.get('type') == 'tool_use':
                                tool_name = content_item.get('name', 'unknown')
                                tool_count += 1
                                tools_used.append(tool_name)
                                if progress_callback:
                                    await progress_callback(f"🔧 Using tool: {tool_name} (#{tool_count})")
                            elif content_item.get('type') == 'text' and content_item.get('text'):
                                assistant_messages.append(content_item['text'])
                
                # Check for completion
                elif event_type == 'result':
                    if event.get('result'):
                        result_text = event['result']
                        if result_text and isinstance(result_text, str):
                            assistant_messages.clear()
                            assistant_messages.append(result_text)
                    
                    # Extract token usage
                    if 'usage' in event:
                        nonlocal token_usage, total_cost
                        token_usage = event['usage']
                    if 'total_cost_usd' in event:
                        total_cost = event['total_cost_usd']
                    
                    if progress_callback:
                        await progress_callback("✅ Task completed!")
            
            # Start reading the stream
            await read_stream()
            
            # Also collect any stderr
            stderr_task = asyncio.create_task(process.stderr.read())
            
            # Wait for process to complete
            await process.wait()
            
            # Get stderr if any
            try:
                stderr_data = await asyncio.wait_for(stderr_task, timeout=1.0)
                if stderr_data:
                    stderr_lines = stderr_data.decode('utf-8').split('\n')
            except asyncio.TimeoutError:
                pass
            
            # Check return code
            if process.returncode != 0:
                error_msg = '\n'.join(stderr_lines) if stderr_lines else "Unknown error"
                logger.error(f"Claude CLI error (return code {process.returncode}): {error_msg}")
                return f"Error executing Claude CLI (return code {process.returncode}): {error_msg}"
            
            # Check if we got any output
            if not output_lines:
                logger.warning("Claude CLI returned empty output")
                return "Claude CLI returned empty output. The command may have completed without generating a response."
            
            logger.debug(f"Total output lines: {len(output_lines)}")
            
            # Note: All processing already happened in real-time during streaming
            # No need to re-process the lines here
            
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