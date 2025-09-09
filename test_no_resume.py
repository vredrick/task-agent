#!/usr/bin/env python3
"""Test that session resumption is properly disabled when resume-session is false."""

import asyncio
import json
import sys
sys.path.insert(0, '/home/vredrick/task-agent/src')

from sdk_integration.agent_executor import AgentExecutor

async def test_no_resume():
    """Test that session doesn't resume when resume-session is false."""
    
    # Initialize the agent executor
    executor = AgentExecutor(agents_path="/home/vredrick/task-agent/task-agents", use_sdk=True)
    
    print("=== Testing with resume-session: false ===\n")
    
    # First message
    print("First message: Setting context...")
    session_id = None
    
    async for chunk in executor.execute_agent(
        agent_name="example-agent",
        prompt="Remember that my favorite color is blue. Please confirm.",
        session_id=None,
        session_reset=False
    ):
        try:
            data = json.loads(chunk)
            if data.get("type") == "text":
                print(data["content"]["text"], end='', flush=True)
            elif data.get("type") == "metadata":
                metadata = data.get("data", {})
                session_id = metadata.get("session_id")
                print(f"\n[Got session_id: {session_id}]")
        except json.JSONDecodeError:
            print(chunk, end='', flush=True)
    
    print("\n\nSecond message: Testing if context is remembered...")
    print(f"Passing session_id: {session_id}")
    
    # Second message - should NOT remember context
    response_text = ""
    async for chunk in executor.execute_agent(
        agent_name="example-agent",
        prompt="What is my favorite color?",
        session_id=session_id,  # Pass session ID (should be ignored)
        session_reset=False
    ):
        try:
            data = json.loads(chunk)
            if data.get("type") == "text":
                text = data["content"]["text"]
                response_text += text
                print(text, end='', flush=True)
        except json.JSONDecodeError:
            response_text += chunk
            print(chunk, end='', flush=True)
    
    # Check results
    if "blue" in response_text.lower():
        print("\n\n❌ FAILURE: Agent remembered context when it shouldn't have!")
        print("resume-session is false, so it should NOT remember.")
    else:
        print("\n\n✅ SUCCESS: Agent correctly did NOT remember context.")
        print("resume-session is false, working as expected.")

if __name__ == "__main__":
    asyncio.run(test_no_resume())