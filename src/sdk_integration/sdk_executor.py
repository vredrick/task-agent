"""SDK Executor module for Claude Code SDK integration.

This module provides a drop-in replacement for CLI subprocess execution,
using the Claude Code SDK (with claude-max for subscription support).
"""

# Option A: Using claude-max package (recommended for subscriptions)
try:
    from claude_max import ClaudeMaxClient
    HAS_CLAUDE_MAX = True
except ImportError:
    HAS_CLAUDE_MAX = False
    try:
        from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions, query
    except ImportError:
        # Fallback if SDK not available
        ClaudeSDKClient = None
        ClaudeCodeOptions = None
        query = None

import asyncio
import json
import os
import logging
from typing import AsyncGenerator, Optional, Dict, Any
from pathlib import Path

from .oauth_handler import prepare_oauth_environment
from .message_parser import SDKMessageParser

logger = logging.getLogger(__name__)


class SDKExecutor:
    """Drop-in replacement for CLI subprocess execution using Claude Code SDK."""
    
    def __init__(self):
        """Initialize the SDK executor."""
        self.has_claude_max = HAS_CLAUDE_MAX
        self.has_sdk = ClaudeSDKClient is not None or HAS_CLAUDE_MAX
        self._current_client = None  # Track active client for interrupt support
        self._current_task = None    # Track current task info
        
        if not self.has_sdk:
            logger.warning("Neither claude-max nor claude-code-sdk is available. SDK execution disabled.")
    
    async def execute_task(
        self, 
        agent_config, 
        task_description: str,
        session_id: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> AsyncGenerator[str, None]:
        """Execute agent task using SDK instead of CLI subprocess.
        
        NOTE: Session resumption in SDK works differently than CLI:
        - CLI uses -r flag with session IDs from SessionChainStore
        - SDK uses 'resume' parameter with conversation IDs
        - These are separate systems and should not be mixed
        
        Args:
            agent_config: Agent configuration object with system_prompt, tools, model, etc.
            task_description: The task/query to execute
            session_id: Optional SDK conversation ID (NOT CLI session ID)
            progress_callback: Optional callback for progress updates
            
        Yields:
            str: JSON-formatted response strings (same format as CLI stream-json)
        """
        if not self.has_sdk:
            raise RuntimeError("Claude Code SDK is not installed. Please install claude-code-sdk or claude-max.")
        
        # Handle OAuth authentication (separated for safety)
        prepare_oauth_environment()
        
        # Get working directory from agent configuration
        working_dir = agent_config.cwd if hasattr(agent_config, 'cwd') else "."
        
        # Handle working directory resolution
        if working_dir == ".":
            # Default: resolve to project root (parent of task-agents directory)
            # This maintains consistency with the original design
            working_dir = str(Path(__file__).parent.parent.parent.resolve())
            logger.info(f"Using default project root directory: {working_dir}")
        elif working_dir and not os.path.isabs(working_dir):
            # If it's a relative path, resolve it relative to project root
            project_root = Path(__file__).parent.parent.parent.resolve()
            working_dir = str(project_root / working_dir)
            logger.info(f"Resolved relative path to: {working_dir}")
        else:
            # Absolute path - use as-is
            logger.info(f"Using absolute path from config: {working_dir}")
        
        try:
            if self.has_claude_max:
                logger.info("Using claude-max for subscription support")
                # TODO: Implement claude-max specific logic
                # For now, we'll fall back to standard SDK behavior
                raise NotImplementedError("claude-max integration not yet fully implemented")
            else:
                logger.info(f"Using standard Claude Code SDK (session_id={session_id})")
                # Create SDK options matching documentation patterns
                # NOTE: SDK session management is separate from CLI sessions
                # - session_id here should be an SDK conversation_id from a previous SDK call
                # - This is NOT compatible with CLI session IDs from SessionChainStore
                # - If integrating SDK sessions, create a separate SDKSessionStore
                options = ClaudeCodeOptions(
                    system_prompt=agent_config.system_prompt if hasattr(agent_config, 'system_prompt') else None,
                    allowed_tools=agent_config.tools if hasattr(agent_config, 'tools') else [],
                    model=agent_config.model if hasattr(agent_config, 'model') else 'claude-3-5-sonnet-20241022',
                    cwd=working_dir,
                    resume=session_id,  # SDK conversation ID (not CLI session ID)
                    max_turns=getattr(agent_config, 'max_exchanges', 5) if hasattr(agent_config, 'max_exchanges') else 5
                )
                
                # Initialize message parser
                parser = SDKMessageParser()
                
                # Use exact pattern from documentation
                async with ClaudeSDKClient(options=options) as client:
                    # Store client reference for interrupt support
                    self._current_client = client
                    self._current_task = task_description
                    
                    try:
                        await client.query(task_description)

                        messages = []
                        result_data = None

                        async for message in client.receive_messages():
                            messages.append(message)
                            message_type = type(message).__name__
                            
                            # Parse message using the new parser
                            parsed_message = parser.parse_message(message)
                            
                            if parsed_message:
                                # Handle different message types
                                if parsed_message.get("type") == "assistant_message":
                                    # Stream assistant message blocks
                                    for block in parsed_message.get("blocks", []):
                                        if block["type"] == "text":
                                            # Stream text content
                                            yield parser.create_text_event(block["content"])
                                        elif block["type"] == "tool_use":
                                            # Stream tool use
                                            yield parser.create_tool_use_event(
                                                name=block["name"],
                                                input_data=block["input"],
                                                tool_id=block.get("id")
                                            )
                                
                                elif parsed_message.get("type") == "user_message":
                                    # UserMessage contains tool results!
                                    logger.debug(f"Processing user message with {len(parsed_message.get('blocks', []))} blocks")
                                    for block in parsed_message.get("blocks", []):
                                        if block["type"] == "tool_result":
                                            logger.info(f"Sending tool_result event from UserMessage for tool_use_id: {block['tool_use_id'][:10]}...")
                                            yield parser.create_tool_result_event(
                                                tool_use_id=block["tool_use_id"],
                                                output=block["output"],
                                                is_error=block["is_error"]
                                            )
                                
                                elif parsed_message.get("type") == "system_message":
                                    # Stream system message blocks (for other system notifications)
                                    logger.debug(f"Processing system message with {len(parsed_message.get('blocks', []))} blocks")
                                    for block in parsed_message.get("blocks", []):
                                        logger.debug(f"Processing block type: {block.get('type')}")
                                        if block["type"] == "tool_result":
                                            logger.info(f"Sending tool_result event for tool_use_id: {block['tool_use_id'][:10]}...")
                                            yield parser.create_tool_result_event(
                                                tool_use_id=block["tool_use_id"],
                                                output=block["output"],
                                                is_error=block["is_error"]
                                            )
                                        elif block["type"] == "text":
                                            # System text (notifications)
                                            yield parser.create_text_event(block["content"])
                                
                                elif parsed_message.get("type") == "result":
                                    # Result message with metadata
                                    result_data = parsed_message
                                    
                                    # Send metadata event
                                    yield parser.create_metadata_event(result_data)
                                    
                                    logger.info(f"SDK completed with metadata: {result_data}")
                                    break
                            
                            # Fallback to original streaming for compatibility
                            # This ensures we don't break anything if parsing fails
                            elif hasattr(message, 'content') and not parsed_message:
                                logger.warning(f"Falling back to original streaming for message type: {message_type}")
                                for block in message.content:
                                    if hasattr(block, 'text'):
                                        json_event = {
                                            "type": "text",
                                            "content": {
                                                "text": block.text
                                            }
                                        }
                                        yield json.dumps(json_event)
                    finally:
                        # Clear client reference when done
                        self._current_client = None
                        self._current_task = None
                        logger.debug("Cleared client reference after task completion")
                    
        except Exception as e:
            logger.error(f"SDK execution failed: {e}")
            # Return error in same JSON format as CLI would
            error_response = {
                "type": "error",
                "error": str(e)
            }
            yield json.dumps(error_response)
    
    def is_available(self) -> bool:
        """Check if SDK execution is available.
        
        Returns:
            bool: True if either claude-max or claude-code-sdk is installed
        """
        return self.has_sdk
    
    async def interrupt(self) -> bool:
        """Interrupt the currently executing task.
        
        Returns:
            bool: True if interrupt was sent, False if no active task
        """
        if self._current_client:
            try:
                logger.info(f"Interrupting current task: {self._current_task[:50]}...")
                await self._current_client.interrupt()
                logger.info("Interrupt signal sent successfully")
                return True
            except Exception as e:
                logger.error(f"Failed to interrupt task: {e}")
                return False
        else:
            logger.debug("No active client to interrupt")
            return False


# Singleton instance
_executor = None

def get_sdk_executor() -> SDKExecutor:
    """Get or create the singleton SDK executor instance.
    
    Returns:
        SDKExecutor: The SDK executor instance
    """
    global _executor
    if _executor is None:
        _executor = SDKExecutor()
    return _executor