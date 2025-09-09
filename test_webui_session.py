#!/usr/bin/env python3
"""Test the Web UI backend session resumption through the agent executor."""

import asyncio
import json
import sys
sys.path.insert(0, '/home/vredrick/task-agent/src')

from sdk_integration.agent_executor import AgentExecutor

async def test_webui_session():
    """Test session resumption through the agent executor (as used by Web UI)."""
    
    # Initialize the agent executor
    executor = AgentExecutor(agents_path="/home/vredrick/task-agent/task-agents", use_sdk=True)
    
    # List available agents
    agents = executor.list_agents()
    print("Available agents:", list(agents.keys()))
    
    # Use the example-agent for testing
    agent_name = "example-agent"
    
    print("\n=== First Message - Setting Context ===")
    session_id = None
    conversation_id = None
    
    # First message
    async for chunk in executor.execute_agent(
        agent_name=agent_name,
        prompt="Remember that my favorite color is red. Please confirm.",
        session_id=None,  # No session yet
        session_reset=False
    ):
        try:
            data = json.loads(chunk)
            if data.get("type") == "text":
                print(data["content"]["text"], end='', flush=True)
            elif data.get("type") == "metadata":
                # Extract session ID from metadata
                metadata = data.get("data", {})
                session_id = metadata.get("session_id")
                conversation_id = metadata.get("conversation_id")
                print(f"\n\n[Got session_id: {session_id}]")
                print(f"[Got conversation_id: {conversation_id}]")
        except json.JSONDecodeError:
            print(chunk, end='', flush=True)
    
    print("\n\n=== Second Message - Testing Resume ===")
    
    # Second message with session resumption
    response_text = ""
    async for chunk in executor.execute_agent(
        agent_name=agent_name,
        prompt="What is my favorite color?",
        session_id=session_id,  # Pass the session ID to resume
        session_reset=False
    ):
        try:
            data = json.loads(chunk)
            if data.get("type") == "text":
                text = data["content"]["text"]
                response_text += text
                print(text, end='', flush=True)
            elif data.get("type") == "metadata":
                print(f"\n\n[Session resumed with ID: {session_id}]")
        except json.JSONDecodeError:
            response_text += chunk
            print(chunk, end='', flush=True)
    
    # Check if the response mentions red
    if "red" in response_text.lower():
        print("\n✅ SUCCESS: Web UI session resumption works! The assistant remembered the favorite color.")
    else:
        print("\n❌ FAILURE: Web UI session resumption did not work. The assistant forgot the context.")
        print(f"Response was: {response_text}")

if __name__ == "__main__":
    asyncio.run(test_webui_session())