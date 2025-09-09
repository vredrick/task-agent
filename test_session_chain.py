#!/usr/bin/env python3
"""Test that session chaining works correctly."""

import asyncio
from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions

async def test_chain():
    session_id = None
    
    messages = [
        "My favorite color is red. Reply with 'Noted.'",
        "My favorite food is pizza. Reply with 'Got it.'",
        "What is my favorite color and food?"
    ]
    
    for i, msg in enumerate(messages, 1):
        print(f"\n=== Message {i} (resume={session_id}) ===")
        
        async with ClaudeSDKClient(
            options=ClaudeCodeOptions(
                system_prompt="Remember user facts",
                allowed_tools=["Read"],
                model="claude-3-5-sonnet-20241022",
                resume=session_id  # Use previous session_id
            )
        ) as client:
            await client.query(msg)
            
            response = ""
            async for message in client.receive_messages():
                if hasattr(message, 'content'):
                    for block in message.content:
                        if hasattr(block, 'text'):
                            response += block.text
                            print(block.text, end='', flush=True)
                
                if type(message).__name__ == "ResultMessage":
                    # Get the NEW session_id for next message
                    session_id = getattr(message, 'session_id', None)
                    print(f"\n[New session_id for next message: {session_id}]")
                    break
            
            # Check if context is maintained
            if i == 3:
                if "red" in response.lower() and "pizza" in response.lower():
                    print("\n✅ SUCCESS: Session chaining works! Context maintained across all messages.")
                else:
                    print("\n❌ FAILURE: Context not maintained.")

asyncio.run(test_chain())