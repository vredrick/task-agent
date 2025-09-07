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
        from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
        from claude_code_sdk.types import (
            AssistantMessage, 
            UserMessage, 
            SystemMessage, 
            ResultMessage,
            TextBlock,
            ToolUseBlock
        )
    except ImportError:
        # Fallback if SDK not available
        ClaudeSDKClient = None
        ClaudeCodeOptions = None

import asyncio
import json
import os
import logging
from typing import AsyncGenerator, Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class SDKExecutor:
    """Drop-in replacement for CLI subprocess execution using Claude Code SDK."""
    
    def __init__(self):
        """Initialize the SDK executor."""
        self.has_claude_max = HAS_CLAUDE_MAX
        self.has_sdk = ClaudeSDKClient is not None or HAS_CLAUDE_MAX
        
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
        
        Args:
            agent_config: Agent configuration object with system_prompt, tools, model, etc.
            task_description: The task/query to execute
            session_id: Optional session ID for conversation continuity
            progress_callback: Optional callback for progress updates
            
        Yields:
            str: JSON-formatted response strings (same format as CLI stream-json)
        """
        if not self.has_sdk:
            raise RuntimeError("Claude Code SDK is not installed. Please install claude-code-sdk or claude-max.")
        
        # IMPORTANT: Don't set ANTHROPIC_API_KEY to use subscription OAuth
        # SDK will automatically use ~/.claude/credentials.json
        if 'ANTHROPIC_API_KEY' in os.environ and self.has_claude_max:
            logger.info("Removing ANTHROPIC_API_KEY to force OAuth subscription authentication")
            del os.environ['ANTHROPIC_API_KEY']  # Force OAuth fallback
        
        # Get working directory
        working_dir = agent_config.cwd if hasattr(agent_config, 'cwd') else None
        if working_dir == ".":
            # Resolve relative to project root (parent of task-agents directory)
            working_dir = str(Path(__file__).parent.parent.parent.resolve())
        
        try:
            if self.has_claude_max:
                logger.info("Using claude-max for subscription support")
                # TODO: Implement claude-max specific logic
                # For now, we'll fall back to standard SDK behavior
                raise NotImplementedError("claude-max integration not yet fully implemented")
            else:
                logger.info("Using standard Claude Code SDK")
                # Create SDK options
                options = ClaudeCodeOptions(
                    system_prompt=agent_config.system_prompt if hasattr(agent_config, 'system_prompt') else None,
                    allowed_tools=agent_config.tools if hasattr(agent_config, 'tools') else [],
                    model=agent_config.model if hasattr(agent_config, 'model') else 'haiku',
                    cwd=working_dir,
                    resume=session_id,  # Use 'resume' for session continuation
                )
                
                # Create client
                client = ClaudeSDKClient(options=options)
                
                # Connect to Claude
                await client.connect()
                
                try:
                    # Send the query
                    await client.query(task_description)
                    
                    # Receive and convert responses to JSON format
                    conversation_id = None
                    total_cost = 0.0
                    input_tokens = 0
                    output_tokens = 0
                    
                    async for msg in client.receive_response():
                        if isinstance(msg, AssistantMessage):
                            # Process assistant message content
                            for block in msg.content:
                                if isinstance(block, TextBlock):
                                    # Convert to stream-json format
                                    json_event = {
                                        "type": "text",
                                        "content": {
                                            "text": block.text
                                        }
                                    }
                                    yield json.dumps(json_event)
                                    
                                elif hasattr(block, '__class__') and 'ToolUse' in block.__class__.__name__:
                                    # Tool use block
                                    json_event = {
                                        "type": "tool_use",
                                        "name": getattr(block, 'name', 'unknown'),
                                        "input": getattr(block, 'input', {})
                                    }
                                    yield json.dumps(json_event)
                        
                        elif isinstance(msg, ResultMessage):
                            # Extract session info and usage
                            conversation_id = getattr(msg, 'conversation_id', None)
                            total_cost = getattr(msg, 'total_cost_usd', 0.0)
                            
                            # Try to get token usage
                            if hasattr(msg, 'usage'):
                                usage = msg.usage
                                input_tokens = getattr(usage, 'input_tokens', 0)
                                output_tokens = getattr(usage, 'output_tokens', 0)
                            
                            # Send session info event
                            if conversation_id:
                                json_event = {
                                    "claude_version": "SDK",
                                    "conversation_id": conversation_id
                                }
                                yield json.dumps(json_event)
                            
                            # Send usage event
                            if input_tokens or output_tokens:
                                json_event = {
                                    "type": "usage",
                                    "usage": {
                                        "input_tokens": input_tokens,
                                        "output_tokens": output_tokens,
                                        "total_cost_usd": total_cost
                                    }
                                }
                                yield json.dumps(json_event)
                            
                            # Result message indicates completion
                            break
                        
                        elif isinstance(msg, UserMessage):
                            # User message (shouldn't happen in response)
                            logger.debug(f"Unexpected UserMessage in response: {msg}")
                        
                        elif isinstance(msg, SystemMessage):
                            # System message
                            logger.debug(f"System message: {msg}")
                            
                finally:
                    # Disconnect from Claude
                    await client.disconnect()
                    
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