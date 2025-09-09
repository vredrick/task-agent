#!/usr/bin/env python3
"""Test script to verify SDK session resumption works correctly."""

import asyncio
import json
from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions

async def test_session_resume():
    """Test that session resumption works with the SDK."""
    
    session_id = None
    
    # First message - establish context
    print("=== First Query - Setting Context ===")
    async with ClaudeSDKClient(
        options=ClaudeCodeOptions(
            system_prompt="You are a helpful assistant. Remember facts the user tells you.",
            allowed_tools=["Read", "Write"],
            model="claude-3-5-sonnet-20241022",
            cwd="/home/vredrick/task-agent"
        )
    ) as client:
        await client.query("Remember, my favorite color is red. Please confirm you understand.")
        
        async for message in client.receive_messages():
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        print(block.text, end='', flush=True)
            
            # Capture session ID from ResultMessage
            if type(message).__name__ == "ResultMessage":
                session_id = getattr(message, 'session_id', None)
                print(f"\n\n[Got session_id: {session_id}]")
                break
    
    print("\n\n=== Second Query - Testing Resume ===")
    
    # Second message - test if context is remembered
    async with ClaudeSDKClient(
        options=ClaudeCodeOptions(
            system_prompt="You are a helpful assistant. Remember facts the user tells you.",
            allowed_tools=["Read", "Write"],
            model="claude-3-5-sonnet-20241022",
            cwd="/home/vredrick/task-agent",
            resume=session_id  # Resume the previous session
        )
    ) as client:
        await client.query("What is my favorite color?")
        
        response_text = ""
        async for message in client.receive_messages():
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        response_text += block.text
                        print(block.text, end='', flush=True)
            
            if type(message).__name__ == "ResultMessage":
                print(f"\n\n[Session resumed successfully: {session_id}]")
                break
        
        # Check if the response mentions red
        if "red" in response_text.lower():
            print("\n✅ SUCCESS: Session resumption works! The assistant remembered the favorite color.")
        else:
            print("\n❌ FAILURE: Session resumption did not work. The assistant forgot the context.")
            print(f"Response was: {response_text}")

if __name__ == "__main__":
    asyncio.run(test_session_resume())