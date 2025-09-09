#!/usr/bin/env python3
"""Test what message types the SDK actually sends."""

import asyncio
import os
from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
from claude_code_sdk import UserMessage, AssistantMessage, SystemMessage, ResultMessage

async def test_tool_messages():
    """Test what messages are sent when tools are used."""
    
    # Simple options with tools
    options = ClaudeCodeOptions(
        allowed_tools=["Read", "Bash"],
        cwd="/home/vredrick/task-agent"
    )
    
    async with ClaudeSDKClient(options=options) as client:
        # Query that will use a tool
        await client.query("Read the first 5 lines of the README.md file")
        
        print("=== Receiving messages ===")
        message_types = []
        
        async for message in client.receive_messages():
            msg_type = type(message).__name__
            message_types.append(msg_type)
            print(f"\n{msg_type}:")
            
            if isinstance(message, UserMessage):
                print("  [User message - skipping content]")
                
            elif isinstance(message, AssistantMessage):
                print(f"  Role: {message.role if hasattr(message, 'role') else 'N/A'}")
                if hasattr(message, 'content'):
                    for i, block in enumerate(message.content):
                        block_type = type(block).__name__
                        print(f"  Block {i}: {block_type}")
                        if hasattr(block, 'text'):
                            print(f"    Text: {block.text[:100]}...")
                        elif hasattr(block, 'name'):
                            print(f"    Tool: {block.name}")
                            if hasattr(block, 'id'):
                                print(f"    Tool ID: {block.id}")
                        elif hasattr(block, 'tool_use_id'):
                            print(f"    Tool Result for: {block.tool_use_id}")
                            if hasattr(block, 'output'):
                                print(f"    Output: {block.output[:100]}...")
                                
            elif isinstance(message, SystemMessage):
                print(f"  === SYSTEM MESSAGE FOUND ===")
                print(f"  Role: {message.role if hasattr(message, 'role') else 'N/A'}")
                if hasattr(message, 'content'):
                    for i, block in enumerate(message.content):
                        block_type = type(block).__name__
                        print(f"  Block {i}: {block_type}")
                        if hasattr(block, 'tool_use_id'):
                            print(f"    Tool Result ID: {block.tool_use_id}")
                            if hasattr(block, 'output'):
                                print(f"    Output preview: {block.output[:200] if block.output else 'None'}...")
                        elif hasattr(block, 'text'):
                            print(f"    Text: {block.text[:100]}...")
                            
            elif isinstance(message, ResultMessage):
                print(f"  Session ID: {message.session_id if hasattr(message, 'session_id') else 'N/A'}")
                print(f"  Cost: ${message.total_cost_usd if hasattr(message, 'total_cost_usd') else 0}")
                break
        
        print(f"\n=== Summary ===")
        print(f"Message types received: {message_types}")
        print(f"SystemMessage count: {message_types.count('SystemMessage')}")

if __name__ == "__main__":
    asyncio.run(test_tool_messages())