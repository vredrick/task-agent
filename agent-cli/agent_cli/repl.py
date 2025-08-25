#!/usr/bin/env python3
"""
REPL Interface for Task Agents

Provides an interactive terminal interface for conversing with task agents.
Uses prompt-toolkit for a Claude Code-like interface with persistent input field.
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
import tempfile
import os
import shutil

try:
    from prompt_toolkit import prompt
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.shortcuts import print_formatted_text, clear
    from prompt_toolkit.styles import Style
    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False
    # Try to install it automatically
    try:
        import subprocess
        print("Installing prompt-toolkit...")
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'prompt-toolkit'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            from prompt_toolkit import prompt
            from prompt_toolkit.formatted_text import HTML
            from prompt_toolkit.history import InMemoryHistory
            from prompt_toolkit.shortcuts import print_formatted_text, clear
            from prompt_toolkit.styles import Style
            PROMPT_TOOLKIT_AVAILABLE = True
            print("✅ prompt-toolkit installed successfully!")
        else:
            print(f"❌ Failed to install prompt-toolkit: {result.stderr}")
            print("Please install manually: pip install prompt-toolkit")
    except Exception as e:
        print(f"❌ Error installing prompt-toolkit: {e}")
        print("Please install manually: pip install prompt-toolkit")


# Import the proper session management from main package
import sys
from pathlib import Path

# Add the main package to path to import SessionChainStore
main_package_path = Path(__file__).parent.parent.parent / 'src'
if main_package_path.exists():
    sys.path.insert(0, str(main_package_path))

# Fallback session management functions (always available)
def load_session_data():
    """Load session data from file."""
    session_file = Path("/tmp/task_agents_sessions.json")
    if session_file.exists():
        try:
            with open(session_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_session_data(data):
    """Save session data to file."""
    session_file = Path("/tmp/task_agents_sessions.json")
    try:
        with open(session_file, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

# Try to import proper session store
try:
    from task_agents_mcp.session_store import SessionChainStore
    SESSION_STORE = SessionChainStore(Path("/tmp/task_agents_sessions.json"))
    HAS_SESSION_STORE = True
except ImportError:
    # Main package not available
    HAS_SESSION_STORE = False
    SESSION_STORE = None


class AgentREPL:
    """Interactive REPL for task agents with Claude Code-like interface."""
    
    def __init__(self, agent_name: str, config: Dict[str, Any]):
        self.agent_name = agent_name
        self.config = config
        self.conversation_history = []
        self.current_session_id = None
        
        # Initialize prompt-toolkit components
        if PROMPT_TOOLKIT_AVAILABLE:
            self.history = InMemoryHistory()
            self.style = Style.from_dict({
                'user': '#00aa00',         # Green for user messages
                'agent': '#0088ff',        # Blue for agent responses
                'error': '#ff0000',        # Red for errors
                'info': '#888888',         # Gray for info messages
                'prompt': '#ffffff bold',  # White bold for prompt
                'header': '#ffaa00 bold',  # Orange for header
            })
        
        # Chat history will be loaded when we know the session ID
        
    def _load_session_conversation(self, session_id: str):
        """Load conversation history for a specific session."""
        try:
            session_data = load_session_data()
            session_key = f"session_{session_id}"
            if session_key in session_data:
                self.conversation_history = session_data[session_key].get('messages', [])
            else:
                self.conversation_history = []  # New session, no history
        except Exception:
            self.conversation_history = []  # Default to empty on error
    
    def _save_session_conversation(self, session_id: str):
        """Save conversation history for a specific session."""
        try:
            session_data = load_session_data()
            session_key = f"session_{session_id}"
            session_data[session_key] = {
                'messages': self.conversation_history,
                'agent_name': self.agent_name,
                'last_updated': str(Path(__file__).stat().st_mtime)
            }
            save_session_data(session_data)
        except Exception:
            pass  # Ignore session saving errors
    
    def _load_agent_config_from_file(self):
        """Load the actual agent configuration from the .md file dynamically (same as alias script)."""
        try:
            import yaml
            
            # Try to find the agent file - check common locations
            agent_filename = self.agent_name.lower().replace(' ', '-') + '.md'
            possible_paths = [
                Path(f'./task-agents/{agent_filename}'),
                Path(f'../task-agents/{agent_filename}'),
                Path(f'../../task-agents/{agent_filename}'),
                Path(f'/Volumes/vredrick2/Claude-Code-Projects/task-agent/task-agents/{agent_filename}')
            ]
            
            agent_file_path = None
            for path in possible_paths:
                if path.exists():
                    agent_file_path = path
                    break
            
            if not agent_file_path:
                # Return None if file not found - will fallback to passed config
                return None
            
            # Parse the agent file (same logic as alias script)
            with open(agent_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '---' not in content:
                return None
            
            parts = content.split('---', 2)
            if len(parts) < 3:
                return None
            
            # Parse metadata and system prompt
            metadata = yaml.safe_load(parts[1])
            system_prompt_section = parts[2].strip()
            
            # Extract system prompt after System-prompt: marker
            system_prompt = ""
            if system_prompt_section.startswith("System-prompt:"):
                system_prompt = system_prompt_section[len("System-prompt:"):].strip()
            else:
                system_prompt = system_prompt_section
            
            # Get optional fields with proper parsing
            optional = metadata.get('optional', {})
            resume_session = optional.get('resume-session', False)
            
            # Parse resume-session setting properly
            if isinstance(resume_session, str):
                if resume_session.lower() == 'true':
                    resume_session = True
                elif resume_session.isdigit():
                    resume_session = int(resume_session)  # Max exchanges
                else:
                    resume_session = False
            
            # Return the fresh agent config
            return {
                'agent_name': metadata.get('agent-name', self.agent_name),
                'description': metadata.get('description', 'No description'),
                'model': metadata.get('model', 'haiku'),
                'tools': metadata.get('tools', 'Read,Write').replace(',', ' ').split(),
                'cwd': metadata.get('cwd', '.'),
                'resume_session': resume_session,
                'system_prompt': system_prompt
            }
            
        except Exception as e:
            # Return None if parsing fails - will fallback to passed config
            return None
        
    def _print_header(self):
        """Print the REPL header."""
        if not PROMPT_TOOLKIT_AVAILABLE:
            print(f"\n=== {self.agent_name} REPL ===")
            return
        
        # Load current agent config for display
        config = self._load_agent_config_from_file() or self.config
        
        header_text = HTML(f"""
<header>╔══════════════════════════════════════════════════════════════╗
║                    {self.agent_name} REPL                     ║
╚══════════════════════════════════════════════════════════════╝</header>

<info>🎯 Agent: {self.agent_name}
📝 Model: {config.get('model', 'haiku')}
🛠️  Tools: {', '.join(config.get('tools', []))}
📁 CWD: {config.get('cwd', '.')}
🔄 Resume Session: {config.get('resume_session', False)}</info>

<info>Commands: Type your query and press Enter | Ctrl+C to exit</info>
""")
        print_formatted_text(header_text, style=self.style)
        
    def _print_conversation_history(self):
        """Print existing conversation history for current session."""
        if not self.conversation_history:
            if self.current_session_id:
                if PROMPT_TOOLKIT_AVAILABLE:
                    print_formatted_text(HTML(f"<info>🆕 New session: {self.current_session_id[:8]}...</info>"), style=self.style)
                else:
                    print(f"🆕 New session: {self.current_session_id[:8]}...")
            return
            
        if PROMPT_TOOLKIT_AVAILABLE:
            session_display = f"{self.current_session_id[:8]}..." if self.current_session_id else "unknown"
            print_formatted_text(HTML(f"<info>📚 Session history ({session_display}):</info>"), style=self.style)
        else:
            session_display = f"{self.current_session_id[:8]}..." if self.current_session_id else "unknown"
            print(f"📚 Session history ({session_display}):")
            
        for msg in self.conversation_history[-10:]:  # Show last 10 messages
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            
            if PROMPT_TOOLKIT_AVAILABLE:
                if role == 'user':
                    print_formatted_text(HTML(f"<user>> {content}</user>"), style=self.style)
                elif role == 'assistant':
                    print_formatted_text(HTML(f"<agent>{self.agent_name}: {content}</agent>"), style=self.style)
            else:
                if role == 'user':
                    print(f"> {content}")
                elif role == 'assistant':
                    print(f"{self.agent_name}: {content}")
                    
        if PROMPT_TOOLKIT_AVAILABLE:
            print_formatted_text(HTML("<info>───────────────────────────────────────────────────────────────</info>"), style=self.style)
        else:
            print("───────────────────────────────────────────────────────────────")
    
    def _execute_agent_query(self, user_input: str) -> str:
        """Execute a query using the same Claude CLI command structure as the alias script."""
        try:
            # Find Claude CLI executable
            claude_executable = os.environ.get('CLAUDE_EXECUTABLE_PATH')
            if not claude_executable:
                claude_executable = shutil.which('claude')
            
            if not claude_executable:
                # Check common installation locations
                common_paths = [
                    os.path.expanduser('~/.claude/local/claude'),
                    '/usr/local/bin/claude', 
                    '/opt/homebrew/bin/claude'
                ]
                for path in common_paths:
                    if os.path.exists(path) and os.access(path, os.X_OK):
                        claude_executable = path
                        break
                        
            if not claude_executable:
                return "❌ Error: Claude Code CLI not found. Please install Claude Code CLI from https://claude.ai/download"
            
            # Load fresh agent config from .md file on each query (like alias script)
            config = self._load_agent_config_from_file() or self.config
            
            # Get system prompt from the actual agent file
            system_prompt_content = config.get('system_prompt', f"""You are {self.agent_name}, a specialized AI assistant.

Configuration:
- Model: {config.get('model', 'haiku')}
- Tools: {', '.join(config.get('tools', []))}
- Working Directory: {config.get('cwd', '.')}

Description: {config.get('description', 'A helpful AI assistant')}

Please respond to the user's query as this specialized agent.""")
            
            # Create temporary system prompt file (same as alias script)
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.prompt', delete=False) as f:
                f.write(system_prompt_content)
                temp_system_prompt = f.name
            
            # Determine working directory (same logic as alias script)
            working_dir = config.get('cwd', '.')
            if working_dir == '.':
                # For REPL, assume we're already in the right directory or use current dir
                working_dir = os.getcwd()
            else:
                working_dir = os.path.abspath(working_dir)
            
            # Build Claude CLI command (same structure as alias script)
            cmd = [
                claude_executable,
                '-p', user_input,
                '--output-format', 'stream-json',
                '--verbose',
                '--allowedTools'] + config.get('tools', ['Read', 'Write'])
            
            cmd.extend([
                '--model', config.get('model', 'haiku'),
                '--system-prompt-file', temp_system_prompt,
                '--append-system-prompt', f'WORKING DIRECTORY CONTEXT: You are currently operating from the directory: {working_dir}'
            ])
            
            # Add session resumption using proper MCP server logic
            resume_session_id = None
            was_resume = False
            
            if config.get('resume_session') and HAS_SESSION_STORE:
                # Calculate max exchanges (same logic as MCP server)
                resume_setting = config.get('resume_session')
                if resume_setting is True:
                    max_exchanges = 5  # Default when just "true"
                else:
                    max_exchanges = resume_setting if isinstance(resume_setting, int) else 5
                
                # Get session to resume using the proper session store
                resume_session_id = SESSION_STORE.get_resume_session(
                    self.agent_name,
                    max_exchanges
                )
                was_resume = resume_session_id is not None
                
                # Add resume flag if we have a session to resume
                if resume_session_id:
                    cmd.extend(['-r', resume_session_id])
            elif config.get('resume_session'):
                # Fallback to simple session logic if session store not available
                try:
                    session_data = load_session_data()
                    agent_key = self.agent_name
                    if agent_key in session_data and 'session_id' in session_data[agent_key]:
                        last_session = session_data[agent_key]['session_id']
                        cmd.extend(['-r', last_session])
                        was_resume = True
                except Exception:
                    pass  # Ignore session errors
            
            # Execute the command and parse stream-json output (same as alias script)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=working_dir)
            
            # Clean up temp file
            os.unlink(temp_system_prompt)
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                return f"❌ Claude CLI Error: {error_msg}"
            
            # Parse the stream-json output (same logic as alias script)
            output_lines = result.stdout.strip().split('\n')
            session_id = ""
            assistant_messages = []
            tools_used = []
            final_result = ""
            token_usage = ""
            
            for line in output_lines:
                if line.strip():
                    try:
                        import json
                        import re
                        
                        # Try to parse as JSON first for more robust extraction
                        try:
                            json_data = json.loads(line)
                            
                            # Extract session ID from system init events
                            if json_data.get("type") == "system" and json_data.get("subtype") == "init":
                                session_id = json_data.get("session_id", "")
                            
                            # Extract assistant messages
                            elif json_data.get("type") == "assistant":
                                if json_data.get("content", {}).get("type") == "text":
                                    text_content = json_data.get("content", {}).get("text", "")
                                    if text_content:
                                        assistant_messages.append(text_content)
                                
                                # Track tool usage
                                elif json_data.get("content", {}).get("type") == "tool_use":
                                    tool_name = json_data.get("content", {}).get("name", "")
                                    if tool_name:
                                        tools_used.append(tool_name)
                            
                            # Extract final result
                            elif json_data.get("type") == "result":
                                final_result = json_data.get("result", "")
                                
                                # Extract token usage
                                usage = json_data.get("usage", {})
                                input_tokens = usage.get("input_tokens", 0)
                                output_tokens = usage.get("output_tokens", 0)
                                if input_tokens or output_tokens:
                                    total_tokens = input_tokens + output_tokens
                                    token_usage = f"Tokens: {total_tokens} ({input_tokens} in, {output_tokens} out)"
                        
                        except json.JSONDecodeError:
                            # Fallback to regex if JSON parsing fails
                            # Extract session ID
                            if '"type":"system"' in line and '"subtype":"init"' in line:
                                session_match = re.search(r'"session_id":"([^"]*)"', line)
                                if session_match:
                                    session_id = session_match.group(1)
                            
                            # Extract assistant messages with better handling of escaped content
                            if '"type":"assistant"' in line:
                                if '"type":"text"' in line:
                                    # More robust text extraction that handles escaped quotes
                                    text_match = re.search(r'"text":"((?:[^"\\]|\\.)*)\"', line)
                                    if text_match:
                                        # Unescape the extracted text
                                        text_content = text_match.group(1)
                                        text_content = text_content.replace('\\"', '"').replace('\\\\', '\\').replace('\\n', '\n').replace('\\t', '\t')
                                        assistant_messages.append(text_content)
                                
                                # Track tool usage
                                if '"type":"tool_use"' in line:
                                    tool_match = re.search(r'"name":"([^"]*)"', line)
                                    if tool_match:
                                        tools_used.append(tool_match.group(1))
                            
                            # Extract final result with better escaping
                            if '"type":"result"' in line:
                                result_match = re.search(r'"result":"((?:[^"\\]|\\.)*)"', line)
                                if result_match:
                                    result_text = result_match.group(1)
                                    result_text = result_text.replace('\\"', '"').replace('\\\\', '\\').replace('\\n', '\n').replace('\\t', '\t')
                                    final_result = result_text
                                
                                # Extract token usage
                                input_match = re.search(r'"input_tokens":([0-9]*)', line)
                                output_match = re.search(r'"output_tokens":([0-9]*)', line)
                                if input_match and output_match:
                                    input_tokens = int(input_match.group(1))
                                    output_tokens = int(output_match.group(1))
                                    total_tokens = input_tokens + output_tokens
                                    token_usage = f"Tokens: {total_tokens} ({input_tokens} in, {output_tokens} out)"
                                
                    except Exception:
                        continue  # Skip malformed lines
            
            # Handle session changes and conversation history
            if session_id:
                # Check if this is a new session
                if self.current_session_id != session_id:
                    # Session changed - load conversation for this session
                    self.current_session_id = session_id
                    self._load_session_conversation(session_id)
                
                # Update session chain after execution (same as MCP server)  
                if config.get('resume_session') and HAS_SESSION_STORE:
                    SESSION_STORE.update_chain(self.agent_name, session_id, was_resume)
                elif config.get('resume_session'):
                    # Fallback session tracking
                    try:
                        session_data = load_session_data()
                        session_data[self.agent_name] = {'session_id': session_id}
                        save_session_data(session_data)
                    except Exception:
                        pass
            
            # Format response (same as alias script)
            response_parts = []
            
            if session_id:
                response_parts.append(f"Session: {session_id}")
            
            if tools_used:
                response_parts.append(f"Tools used: {', '.join(tools_used)}")
                response_parts.append("")  # Empty line
            
            # Use final result if available, otherwise use assistant messages
            if final_result:
                response_parts.append(final_result)
            elif assistant_messages:
                response_parts.extend(assistant_messages)
            else:
                response_parts.append("Task completed but no response was generated.")
            
            if token_usage:
                response_parts.append("")
                response_parts.append(token_usage)
            
            return '\n'.join(response_parts)
            
        except subprocess.TimeoutExpired:
            return "⏰ Error: Query timed out (5 minutes)"
        except Exception as e:
            return f"❌ Error executing Claude CLI: {str(e)}"
    
    def _save_conversation(self):
        """Save conversation to session-specific data."""
        if self.current_session_id:
            self._save_session_conversation(self.current_session_id)
        # If no session ID yet, don't save (will save after first query)
    
    def _determine_current_session(self):
        """Determine what session we would resume with."""
        try:
            # Load agent config to check if session resumption is enabled
            config = self._load_agent_config_from_file() or self.config
            
            if config.get('resume_session') and HAS_SESSION_STORE:
                # Calculate max exchanges (same logic as MCP server)
                resume_setting = config.get('resume_session')
                if resume_setting is True:
                    max_exchanges = 5  # Default when just "true"
                else:
                    max_exchanges = resume_setting if isinstance(resume_setting, int) else 5
                
                # Get session we would resume with
                resume_session_id = SESSION_STORE.get_resume_session(
                    self.agent_name,
                    max_exchanges
                )
                
                if resume_session_id:
                    # We have a session to resume - load its conversation
                    self.current_session_id = resume_session_id
                    self._load_session_conversation(resume_session_id)
                # If no session to resume, current_session_id stays None until first query
                
        except Exception:
            pass  # Ignore errors, will be handled in first query
    
    def run(self):
        """Run the interactive REPL."""
        if not PROMPT_TOOLKIT_AVAILABLE:
            print("❌ Error: prompt-toolkit not available. Please install it: pip install prompt-toolkit")
            return
        
        try:
            # Clear screen and show header
            clear()
            self._print_header()
            
            # Load current session to show correct conversation history
            self._determine_current_session()
            self._print_conversation_history()
            
            # Main REPL loop
            while True:
                try:
                    # Get user input with styled prompt
                    user_input = prompt(
                        HTML('<prompt>> </prompt>'),
                        style=self.style,
                        history=self.history,
                        multiline=False
                    ).strip()
                    
                    if not user_input:
                        continue
                        
                    # Add user message to history
                    self.conversation_history.append({
                        'role': 'user',
                        'content': user_input
                    })
                    
                    # Don't show user message again - already shown in prompt
                    
                    # Execute agent query
                    if PROMPT_TOOLKIT_AVAILABLE:
                        print_formatted_text(HTML("<info>Thinking...</info>"), style=self.style)
                    
                    response = self._execute_agent_query(user_input)
                    
                    # Add agent response to history
                    self.conversation_history.append({
                        'role': 'assistant', 
                        'content': response
                    })
                    
                    # Show agent response with styling
                    if response.startswith('❌'):
                        print_formatted_text(HTML(f"<error>{response}</error>"), style=self.style)
                    else:
                        print_formatted_text(HTML(f"<agent>{self.agent_name}: {response}</agent>"), style=self.style)
                    
                    print()  # Add spacing
                    
                    # Save conversation
                    self._save_conversation()
                    
                except KeyboardInterrupt:
                    # Graceful exit on Ctrl+C
                    print_formatted_text(HTML("\n<info>👋 Goodbye!</info>"), style=self.style)
                    break
                except EOFError:
                    # Handle Ctrl+D
                    print_formatted_text(HTML("\n<info>👋 Goodbye!</info>"), style=self.style)
                    break
                    
        except Exception as e:
            if PROMPT_TOOLKIT_AVAILABLE:
                print_formatted_text(HTML(f"<error>❌ REPL Error: {str(e)}</error>"), style=self.style)
            else:
                print(f"❌ REPL Error: {str(e)}")


def start_repl(agent_name: str, config: Dict[str, Any]):
    """Start REPL with given agent name and configuration."""
    repl = AgentREPL(agent_name, config)
    repl.run()


def main():
    """Main entry point for the REPL."""
    if len(sys.argv) < 2:
        print("Usage: python repl.py <agent_name> [config_file]")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    
    # Load config if provided
    config = {}
    if len(sys.argv) > 2:
        config_file = Path(sys.argv[2])
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
            except Exception as e:
                print(f"❌ Error loading config: {e}")
                sys.exit(1)
    
    # Start REPL
    start_repl(agent_name, config)


if __name__ == "__main__":
    main()