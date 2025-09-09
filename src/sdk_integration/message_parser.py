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
    
    def parse_system_message(self, message) -> Dict[str, Any]:
        """Parse a system message (tool results, notifications).
        
        Args:
            message: The SDK system message object
            
        Returns:
            Structured message dict
        """
        blocks = []
        
        # Check for tool result content
        if hasattr(message, 'content'):
            for block in message.content:
                block_type = type(block).__name__
                
                # Handle tool result blocks
                if block_type == 'ToolResultBlock' or hasattr(block, 'tool_use_id'):
                    result_block = ToolResultBlock(
                        tool_use_id=getattr(block, 'tool_use_id', ''),
                        output=getattr(block, 'output', ''),
                        is_error=getattr(block, 'is_error', False)
                    )
                    blocks.append(result_block.to_dict())
                    logger.debug(f"Parsed tool result block: {result_block.tool_use_id}")
                
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
        
        try:
            if message_type == "AssistantMessage" or hasattr(message, 'role') and getattr(message, 'role') == 'assistant':
                return self.parse_assistant_message(message)
            elif message_type == "SystemMessage" or hasattr(message, 'role') and getattr(message, 'role') == 'system':
                return self.parse_system_message(message)
            elif message_type == "ResultMessage" or hasattr(message, 'session_id'):
                return self.parse_result_message(message)
            elif message_type == "UserMessage" or hasattr(message, 'role') and getattr(message, 'role') == 'user':
                # UserMessage is typically just echoing user input - we can skip it
                logger.debug(f"Skipping UserMessage (echo of user input)")
                return None
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