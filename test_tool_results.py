#!/usr/bin/env python3
"""Test tool result streaming."""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from src.sdk_integration.message_parser import SDKMessageParser, ToolUseBlock, ToolResultBlock

async def test_tool_result_streaming():
    """Test that tool results are properly generated."""
    parser = SDKMessageParser()
    
    print("Testing tool result event generation...")
    
    # Test tool use event
    tool_use_event = parser.create_tool_use_event(
        name="Bash",
        input_data={"command": "ls -la"},
        tool_id="tool_123"
    )
    print(f"Tool use event: {tool_use_event}")
    tool_use_json = json.loads(tool_use_event)
    assert tool_use_json["type"] == "tool_use"
    assert tool_use_json["name"] == "Bash"
    assert tool_use_json["id"] == "tool_123"
    
    # Test tool start event
    tool_start_event = parser.create_tool_start_event(
        name="Bash",
        tool_id="tool_123"
    )
    print(f"Tool start event: {tool_start_event}")
    tool_start_json = json.loads(tool_start_event)
    assert tool_start_json["type"] == "tool_start"
    assert tool_start_json["id"] == "tool_123"
    
    # Test tool result event
    tool_result_event = parser.create_tool_result_event(
        tool_use_id="tool_123",
        output="total 24\ndrwxr-xr-x  5 user user 4096 Dec 27 10:00 .",
        is_error=False
    )
    print(f"Tool result event: {tool_result_event}")
    tool_result_json = json.loads(tool_result_event)
    assert tool_result_json["type"] == "tool_result"
    assert tool_result_json["tool_use_id"] == "tool_123"
    assert "total 24" in tool_result_json["output"]
    assert tool_result_json["is_error"] == False
    
    # Test tool complete event
    tool_complete_event = parser.create_tool_complete_event(
        tool_id="tool_123",
        success=True
    )
    print(f"Tool complete event: {tool_complete_event}")
    tool_complete_json = json.loads(tool_complete_event)
    assert tool_complete_json["type"] == "tool_complete"
    assert tool_complete_json["id"] == "tool_123"
    assert tool_complete_json["success"] == True
    
    # Test error case
    tool_error_result = parser.create_tool_result_event(
        tool_use_id="tool_456",
        output="Command not found: foobar",
        is_error=True
    )
    print(f"Tool error result: {tool_error_result}")
    tool_error_json = json.loads(tool_error_result)
    assert tool_error_json["is_error"] == True
    
    print("\n✅ All tool result tests passed!")
    
    # Test parsing tool result blocks
    print("\nTesting tool result block parsing...")
    
    # Create a mock tool result block
    class MockToolResultBlock:
        def __init__(self):
            self.tool_use_id = "tool_789"
            self.output = "File created successfully"
            self.is_error = False
    
    mock_block = MockToolResultBlock()
    result_block = ToolResultBlock(
        tool_use_id=mock_block.tool_use_id,
        output=mock_block.output,
        is_error=mock_block.is_error
    )
    
    result_dict = result_block.to_dict()
    print(f"Parsed tool result block: {json.dumps(result_dict, indent=2)}")
    
    assert result_dict["type"] == "tool_result"
    assert result_dict["tool_use_id"] == "tool_789"
    assert result_dict["output"] == "File created successfully"
    assert result_dict["is_error"] == False
    
    print("✅ Tool result block parsing works!")

if __name__ == "__main__":
    asyncio.run(test_tool_result_streaming())