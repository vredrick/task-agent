#!/usr/bin/env python3
"""Test script to see the exact output format from SDK executor."""

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
        self.system_prompt = "You are a helpful assistant. When asked to read a file, use the Read tool. When asked to list files, use the Bash tool with 'ls -la' command."
        self.tools = ["Read", "Bash"]
        self.model = "claude-3-5-sonnet-20241022"
        self.cwd = "."
        self.max_exchanges = 5

async def test_sdk_output():
    """Test the SDK executor and print all output."""
    executor = SDKExecutor()
    
    # Create a test agent config
    agent_config = TestAgentConfig()
    
    print("=" * 60)
    print("Testing SDK Executor Output Format")
    print("=" * 60)
    print("\nSending message: 'Please list the files in the current directory'\n")
    print("-" * 60)
    print("SDK Output (each line is a separate message):")
    print("-" * 60)
    
    message_count = 0
    try:
        async for chunk in executor.execute_task(
            agent_config,
            "Please list the files in the current directory",
            session_id=None
        ):
            message_count += 1
            print(f"\n[Message {message_count}]:")
            
            # Parse and pretty print the JSON
            try:
                data = json.loads(chunk)
                print(json.dumps(data, indent=2))
            except json.JSONDecodeError:
                print(f"Raw (not JSON): {chunk}")
    
    except Exception as e:
        print(f"\nError occurred: {e}")
    
    print("\n" + "=" * 60)
    print(f"Total messages received: {message_count}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_sdk_output())