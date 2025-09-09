"""SDK Message Parser for structured message formatting.

This module provides parsing for different SDK message types to create
structured output for the frontend, enabling better streaming and
type differentiation.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class TextBlock:
    """Represents a text content block."""
    type: str = "text"
    content: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type, "content": self.content}


@dataclass
class ToolUseBlock:
    """Represents a tool invocation block."""
    type: str = "tool_use"
    id: str = ""
    name: str = ""
    input: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.input is None:
            self.input = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "id": self.id,
            "name": self.name,
            "input": self.input
        }


@dataclass
class ToolResultBlock:
    """Represents a tool execution result block."""
    type: str = "tool_result"
    tool_use_id: str = ""
    output: str = ""
    is_error: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "tool_use_id": self.tool_use_id,
            "output": self.output,
            "is_error": self.is_error
        }


class SDKMessageParser:
    """Parse SDK messages into structured format for frontend consumption."""
    
    def __init__(self):
        """Initialize the message parser."""
        self.current_blocks: List[Union[TextBlock, ToolUseBlock, ToolResultBlock]] = []
        self.metadata: Dict[str, Any] = {}
    
    def parse_assistant_message(self, message) -> Dict[str, Any]:
        """Parse an assistant message into structured blocks.
        
        Args:
            message: The SDK assistant message object
            
        Returns:
            Structured message dict with type and blocks
        """
        blocks = []
        
        # Extract content blocks if available
        if hasattr(message, 'content'):
            for block in message.content:
                block_type = type(block).__name__
                
                # Handle text blocks
                if hasattr(block, 'text'):
                    text_block = TextBlock(content=block.text)
                    blocks.append(text_block.to_dict())
                    logger.debug(f"Parsed text block: {len(block.text)} chars")
                
                # Handle tool use blocks
                elif block_type == 'ToolUseBlock' or hasattr(block, 'name'):
                    tool_block = ToolUseBlock(
                        id=getattr(block, 'id', ''),
                        name=getattr(block, 'name', 'unknown'),
                        input=getattr(block, 'input', {})
                    )
                    blocks.append(tool_block.to_dict())
                    logger.debug(f"Parsed tool use block: {tool_block.name}")
        
        return {
            "type": "assistant_message",
            "blocks": blocks,
            "role": "assistant"
        }
    
    def parse_user_message(self, message) -> Dict[str, Any]:
        """Parse a user message which may contain tool results.
        
        Args:
            message: The SDK user message object
            
        Returns:
            Structured message dict or None if just user text
        """
        blocks = []
        has_tool_results = False
        
        logger.info(f"Parsing UserMessage with content: {hasattr(message, 'content')}, content type: {type(getattr(message, 'content', None))}")
        
        # Check for content blocks (tool results come as blocks)
        if hasattr(message, 'content'):
            content = message.content
            # Ensure content is iterable
            if not isinstance(content, list):
                logger.debug(f"UserMessage content is not a list: {type(content)}")
                if isinstance(content, str):
                    # Just text content, no tool results
                    return None
                # Try to make it a list
                content = [content] if content else []
            
            for block in content:
                block_type = type(block).__name__
                logger.info(f"UserMessage block type: {block_type}")
                
                # Handle tool result blocks in UserMessage
                if block_type == 'ToolResultBlock' or hasattr(block, 'tool_use_id'):
                    has_tool_results = True
                    result_block = ToolResultBlock(
                        tool_use_id=getattr(block, 'tool_use_id', ''),
                        output=getattr(block, 'content', getattr(block, 'output', '')),
                        is_error=getattr(block, 'is_error', False)
                    )
                    blocks.append(result_block.to_dict())
                    logger.info(f"Found tool result in UserMessage: {result_block.tool_use_id}")
                
                # Handle text blocks
                elif hasattr(block, 'text'):
                    text_block = TextBlock(content=block.text)
                    blocks.append(text_block.to_dict())
        
        # Only return if we found tool results, otherwise skip
        if has_tool_results:
            return {
                "type": "user_message",
                "blocks": blocks,
                "role": "user"
            }
        else:
            # Just a regular user echo, skip it
            logger.debug("UserMessage contains no tool results, skipping")
            return None
    
    def parse_system_message(self, message) -> Dict[str, Any]:
        """Parse a system message (tool results, notifications).
        
        Args:
            message: The SDK system message object
            
        Returns:
            Structured message dict
        """
        blocks = []
        
        logger.info(f"Parsing system message with content: {hasattr(message, 'content')}")
        
        # Check for tool result content
        if hasattr(message, 'content'):
            for block in message.content:
                block_type = type(block).__name__
                logger.info(f"System message block type: {block_type}")
                
                # Handle tool result blocks
                if block_type == 'ToolResultBlock' or hasattr(block, 'tool_use_id'):
                    result_block = ToolResultBlock(
                        tool_use_id=getattr(block, 'tool_use_id', ''),
                        output=getattr(block, 'output', ''),
                        is_error=getattr(block, 'is_error', False)
                    )
                    blocks.append(result_block.to_dict())
                    logger.info(f"Parsed tool result block: {result_block.tool_use_id}")
                
                # Handle text in system messages
                elif hasattr(block, 'text'):
                    text_block = TextBlock(content=block.text)
                    blocks.append(text_block.to_dict())
        
        return {
            "type": "system_message",
            "blocks": blocks,
            "role": "system"
        }
    
    def parse_result_message(self, message) -> Dict[str, Any]:
        """Parse a result message containing metadata.
        
        Args:
            message: The SDK result message object
            
        Returns:
            Structured metadata dict
        """
        metadata = {
            "type": "result",
            "session_id": getattr(message, 'session_id', None),
            "conversation_id": getattr(message, 'session_id', None),  # For compatibility
            "num_turns": getattr(message, 'num_turns', 1),
            "duration_ms": getattr(message, 'duration_ms', 0),
            "total_cost_usd": getattr(message, 'total_cost_usd', 0.0)
        }
        
        # Include usage information if available
        if hasattr(message, 'usage'):
            usage = message.usage
            metadata["usage"] = {
                "input_tokens": getattr(usage, 'input_tokens', 0),
                "output_tokens": getattr(usage, 'output_tokens', 0),
                "total_tokens": (
                    getattr(usage, 'input_tokens', 0) + 
                    getattr(usage, 'output_tokens', 0)
                )
            }
        
        # Include result text if available
        if hasattr(message, 'result'):
            metadata["result"] = message.result
        
        logger.debug(f"Parsed result message with session_id: {metadata.get('session_id')}")
        return metadata
    
    def parse_message(self, message) -> Optional[Dict[str, Any]]:
        """Parse any SDK message type.
        
        Args:
            message: The SDK message object
            
        Returns:
            Structured message dict or None if unknown type
        """
        message_type = type(message).__name__
        logger.debug(f"Parsing message type: {message_type}, has role: {hasattr(message, 'role')}, role value: {getattr(message, 'role', 'N/A')}")
        
        try:
            if message_type == "AssistantMessage" or hasattr(message, 'role') and getattr(message, 'role') == 'assistant':
                return self.parse_assistant_message(message)
            elif message_type == "SystemMessage" or hasattr(message, 'role') and getattr(message, 'role') == 'system':
                logger.info(f"Detected SystemMessage, parsing tool results...")
                return self.parse_system_message(message)
            elif message_type == "ResultMessage" or hasattr(message, 'session_id'):
                return self.parse_result_message(message)
            elif message_type == "UserMessage" or hasattr(message, 'role') and getattr(message, 'role') == 'user':
                # UserMessage can contain tool results!
                logger.debug(f"Processing UserMessage - checking for tool results")
                return self.parse_user_message(message)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                return None
        except Exception as e:
            logger.error(f"Error parsing message of type {message_type}: {e}")
            return None
    
    def create_streaming_event(self, event_type: str, data: Any) -> str:
        """Create a JSON streaming event for the frontend.
        
        Args:
            event_type: Type of event (text, tool_use, tool_result, metadata, etc.)
            data: Event data
            
        Returns:
            JSON-formatted event string
        """
        event = {
            "type": event_type,
            "data": data
        }
        return json.dumps(event)
    
    def create_text_event(self, text: str) -> str:
        """Create a text streaming event.
        
        Args:
            text: Text content to stream
            
        Returns:
            JSON-formatted text event
        """
        # Match current frontend expectations
        return json.dumps({
            "type": "text",
            "content": {"text": text}
        })
    
    def create_tool_use_event(self, name: str, input_data: Dict[str, Any], tool_id: Optional[str] = None) -> str:
        """Create a tool use event.
        
        Args:
            name: Tool name
            input_data: Tool input parameters
            tool_id: Optional tool invocation ID
            
        Returns:
            JSON-formatted tool use event
        """
        # Match current frontend expectations - tool data at top level
        event = {
            "type": "tool_use",
            "name": name,
            "input": input_data
        }
        if tool_id:
            event["id"] = tool_id
        return json.dumps(event)
    
    def create_tool_result_event(self, tool_use_id: str, output: str, is_error: bool = False) -> str:
        """Create a tool result event.
        
        Args:
            tool_use_id: ID of the tool invocation
            output: Tool execution output
            is_error: Whether the tool execution failed
            
        Returns:
            JSON-formatted tool result event
        """
        # Match current frontend expectations
        return json.dumps({
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "output": output,
            "is_error": is_error
        })
    
    def create_tool_start_event(self, name: str, tool_id: str) -> str:
        """Create a tool start event to indicate tool execution beginning.
        
        Args:
            name: Tool name
            tool_id: Tool invocation ID
            
        Returns:
            JSON-formatted tool start event
        """
        return json.dumps({
            "type": "tool_start",
            "name": name,
            "id": tool_id
        })
    
    def create_tool_complete_event(self, tool_id: str, success: bool = True) -> str:
        """Create a tool complete event to indicate tool execution finished.
        
        Args:
            tool_id: Tool invocation ID
            success: Whether the tool completed successfully
            
        Returns:
            JSON-formatted tool complete event
        """
        return json.dumps({
            "type": "tool_complete",
            "id": tool_id,
            "success": success
        })
    
    def create_metadata_event(self, metadata: Dict[str, Any]) -> str:
        """Create a metadata event.
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            JSON-formatted metadata event
        """
        # Match current frontend expectations - metadata goes in "data" field
        return json.dumps({
            "type": "metadata",
            "data": metadata
        })