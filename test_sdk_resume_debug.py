#!/usr/bin/env python3
"""Debug why SDK resume isn't working."""

import asyncio
from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions

async def test_resume():
    session_id = None
    
    # First query
    print("=== First Query ===")
    async with ClaudeSDKClient(
        options=ClaudeCodeOptions(
            system_prompt="Remember user facts",
            allowed_tools=["Read"],
            model="claude-3-5-sonnet-20241022"
        )
    ) as client:
        await client.query("My favorite color is red. Reply with 'understood'.")
        
        async for message in client.receive_messages():
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        print(block.text, end='', flush=True)
            
            if type(message).__name__ == "ResultMessage":
                session_id = getattr(message, 'session_id', None)
                print(f"\n[Session ID: {session_id}]")
                break
    
    # Second query with resume
    print("\n\n=== Second Query (with resume={}) ===".format(session_id))
    async with ClaudeSDKClient(
        options=ClaudeCodeOptions(
            system_prompt="Remember user facts",
            allowed_tools=["Read"],
            model="claude-3-5-sonnet-20241022",
            resume=session_id  # Pass the session ID here
        )
    ) as client:
        await client.query("What is my favorite color?")
        
        async for message in client.receive_messages():
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        print(block.text, end='', flush=True)
            
            if type(message).__name__ == "ResultMessage":
                new_session_id = getattr(message, 'session_id', None)
                print(f"\n[New Session ID: {new_session_id}]")
                
                if new_session_id == session_id:
                    print("✅ Same session ID - resume worked!")
                else:
                    print("❌ Different session ID - resume didn't work!")
                break

asyncio.run(test_resume())