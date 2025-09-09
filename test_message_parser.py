#!/usr/bin/env python3
"""Test script for Phase 1: Enhanced Message Parsing implementation."""

import asyncio
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.sdk_integration.message_parser import SDKMessageParser, TextBlock, ToolUseBlock, ToolResultBlock


def test_text_block():
    """Test text block creation and serialization."""
    print("Testing TextBlock...")
    block = TextBlock(content="Hello, world!")
    assert block.to_dict() == {"type": "text", "content": "Hello, world!"}
    print("✓ TextBlock works correctly")


def test_tool_use_block():
    """Test tool use block creation and serialization."""
    print("Testing ToolUseBlock...")
    block = ToolUseBlock(
        id="tool_123",
        name="Read",
        input={"file_path": "/tmp/test.txt"}
    )
    result = block.to_dict()
    assert result["type"] == "tool_use"
    assert result["name"] == "Read"
    assert result["input"]["file_path"] == "/tmp/test.txt"
    print("✓ ToolUseBlock works correctly")


def test_tool_result_block():
    """Test tool result block creation and serialization."""
    print("Testing ToolResultBlock...")
    block = ToolResultBlock(
        tool_use_id="tool_123",
        output="File contents here",
        is_error=False
    )
    result = block.to_dict()
    assert result["type"] == "tool_result"
    assert result["tool_use_id"] == "tool_123"
    assert result["output"] == "File contents here"
    assert result["is_error"] == False
    print("✓ ToolResultBlock works correctly")


def test_parser_events():
    """Test parser event creation methods."""
    print("Testing SDKMessageParser event creation...")
    parser = SDKMessageParser()
    
    # Test text event
    text_event = parser.create_text_event("Hello")
    data = json.loads(text_event)
    assert data["type"] == "text"
    assert data["data"]["content"] == "Hello"
    
    # Test tool use event
    tool_event = parser.create_tool_use_event(
        name="Bash",
        input_data={"command": "ls -la"},
        tool_id="bash_123"
    )
    data = json.loads(tool_event)
    assert data["type"] == "tool_use"
    assert data["data"]["name"] == "Bash"
    assert data["data"]["input"]["command"] == "ls -la"
    
    # Test tool result event
    result_event = parser.create_tool_result_event(
        tool_use_id="bash_123",
        output="total 24\ndrwxr-xr-x  ...",
        is_error=False
    )
    data = json.loads(result_event)
    assert data["type"] == "tool_result"
    assert data["data"]["tool_use_id"] == "bash_123"
    
    # Test metadata event
    metadata_event = parser.create_metadata_event({
        "session_id": "sess_123",
        "num_turns": 3,
        "duration_ms": 1500
    })
    data = json.loads(metadata_event)
    assert data["type"] == "metadata"
    assert data["data"]["session_id"] == "sess_123"
    
    print("✓ SDKMessageParser event creation works correctly")


def test_message_parsing_simulation():
    """Simulate parsing different message types."""
    print("\nTesting message parsing simulation...")
    parser = SDKMessageParser()
    
    # Simulate an assistant message with text and tool use
    class MockAssistantMessage:
        def __init__(self):
            self.role = "assistant"
            self.content = [
                type('TextBlock', (), {'text': 'Let me help you with that.'}),
                type('ToolUseBlock', (), {
                    'id': 'tool_001',
                    'name': 'Read',
                    'input': {'file_path': '/tmp/test.txt'}
                })
            ]
    
    msg = MockAssistantMessage()
    parsed = parser.parse_assistant_message(msg)
    assert parsed["type"] == "assistant_message"
    assert len(parsed["blocks"]) == 2
    assert parsed["blocks"][0]["type"] == "text"
    assert parsed["blocks"][1]["type"] == "tool_use"
    print("✓ Assistant message parsing works")
    
    # Simulate a system message with tool result
    class MockSystemMessage:
        def __init__(self):
            self.role = "system"
            self.content = [
                type('ToolResultBlock', (), {
                    'tool_use_id': 'tool_001',
                    'output': 'File contents here',
                    'is_error': False
                })
            ]
    
    msg = MockSystemMessage()
    parsed = parser.parse_system_message(msg)
    assert parsed["type"] == "system_message"
    assert len(parsed["blocks"]) == 1
    assert parsed["blocks"][0]["type"] == "tool_result"
    print("✓ System message parsing works")
    
    # Simulate a result message with metadata
    class MockResultMessage:
        def __init__(self):
            self.session_id = "sess_abc123"
            self.num_turns = 5
            self.duration_ms = 2500
            self.total_cost_usd = 0.025
            self.result = "Task completed successfully"
            self.usage = type('Usage', (), {
                'input_tokens': 150,
                'output_tokens': 200
            })
    
    msg = MockResultMessage()
    parsed = parser.parse_result_message(msg)
    assert parsed["type"] == "result"
    assert parsed["session_id"] == "sess_abc123"
    assert parsed["num_turns"] == 5
    assert parsed["usage"]["total_tokens"] == 350
    print("✓ Result message parsing works")


def main():
    """Run all tests."""
    print("=" * 50)
    print("Phase 1: Message Parser Tests")
    print("=" * 50)
    
    try:
        test_text_block()
        test_tool_use_block()
        test_tool_result_block()
        test_parser_events()
        test_message_parsing_simulation()
        
        print("\n" + "=" * 50)
        print("✅ All Phase 1 tests passed!")
        print("=" * 50)
        print("\nPhase 1 Implementation Summary:")
        print("- Created message_parser.py with structured block types")
        print("- Updated sdk_executor.py to use the parser")
        print("- Maintains backward compatibility with fallback")
        print("- Provides structured events for frontend consumption")
        print("\nNext: Phase 2 - Tool Result Capture & Streaming")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()