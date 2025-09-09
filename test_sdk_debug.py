#!/usr/bin/env python3
"""Debug script to see the exact structure of SDK messages."""

import asyncio
import json
import sys
import os

# Add the src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sdk_integration.sdk_executor import SDKExecutor

class TestAgentConfig:
    """Mock agent config for testing."""
    def __init__(self):
        self.system_prompt = "You are a helpful assistant. Always use the Bash tool to execute commands when asked to list files or show directory contents."
        self.tools = ["Bash", "Read"]
        self.model = "claude-3-5-sonnet-20241022"
        self.cwd = "."
        self.max_exchanges = 5

async def test_sdk_debug():
    """Debug the SDK executor to see message structure."""
    executor = SDKExecutor()
    
    # Create a test agent config
    agent_config = TestAgentConfig()
    
    print("=" * 60)
    print("Debugging SDK Message Structure")
    print("=" * 60)
    print("\nSending message: 'List the files in the current directory using ls -la'\n")
    print("-" * 60)
    
    message_count = 0
    
    # First, let's capture raw messages before JSON encoding
    print("RAW MESSAGE INSPECTION:")
    print("-" * 60)
    
    # We'll need to modify the approach - let's directly use the SDK
    try:
        # Import the SDK directly to debug
        from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
        
        options = ClaudeCodeOptions(
            system_prompt=agent_config.system_prompt,
            allowed_tools=agent_config.tools,
            model=agent_config.model,
            cwd=".",
            max_turns=5
        )
        
        async with ClaudeSDKClient(options=options) as client:
            await client.query("List the files in the current directory using ls -la")
            
            async for message in client.receive_messages():
                message_count += 1
                print(f"\n[Message {message_count}]:")
                print(f"Type: {type(message).__name__}")
                print(f"Attributes: {dir(message)}")
                
                if hasattr(message, 'content'):
                    print(f"Content type: {type(message.content)}")
                    print(f"Content: {message.content}")
                    
                    # Inspect each block
                    for i, block in enumerate(message.content):
                        print(f"\n  Block {i}:")
                        print(f"  - Type: {type(block).__name__}")
                        print(f"  - Attributes: {[attr for attr in dir(block) if not attr.startswith('_')]}")
                        
                        # Check for specific attributes
                        if hasattr(block, 'type'):
                            print(f"  - block.type: {block.type}")
                        if hasattr(block, 'text'):
                            print(f"  - block.text: {block.text[:100]}..." if len(block.text) > 100 else f"  - block.text: {block.text}")
                        if hasattr(block, 'name'):
                            print(f"  - block.name: {block.name}")
                        if hasattr(block, 'input'):
                            print(f"  - block.input: {block.input}")
                
                # Check for ResultMessage
                if type(message).__name__ == "ResultMessage":
                    print("\nThis is a ResultMessage!")
                    if hasattr(message, 'result'):
                        print(f"Result: {message.result[:200]}..." if len(message.result) > 200 else f"Result: {message.result}")
                    if hasattr(message, 'total_cost_usd'):
                        print(f"Cost: ${message.total_cost_usd}")
                    if hasattr(message, 'duration_ms'):
                        print(f"Duration: {message.duration_ms}ms")
                    break
                    
    except ImportError as e:
        print(f"Cannot import SDK directly: {e}")
        print("\nFalling back to executor output:")
        
        # Fall back to testing through executor
        async for chunk in executor.execute_task(
            agent_config,
            "List the files in the current directory using ls -la",
            session_id=None
        ):
            message_count += 1
            print(f"\n[JSON Message {message_count}]:")
            try:
                data = json.loads(chunk)
                print(json.dumps(data, indent=2))
            except json.JSONDecodeError:
                print(f"Raw: {chunk}")
    
    print("\n" + "=" * 60)
    print(f"Total messages: {message_count}")

if __name__ == "__main__":
    asyncio.run(test_sdk_debug())