#!/usr/bin/env python3
"""Test SDK integration with example agent using Read and Glob tools."""

import asyncio
import json
from src.sdk_integration.agent_executor import AgentExecutor

async def test_example_agent():
    """Test the example agent with Read and Glob tools."""
    
    # Initialize the agent executor
    executor = AgentExecutor(agents_path="./task-agents")
    
    # Test 1: Using Read tool
    print("=" * 60)
    print("TEST 1: Read tool with example agent")
    print("=" * 60)
    
    read_prompt = """
    Use the Read tool to read the file /home/vredrick/task-agent/pyproject.toml
    and show me just the first 10 lines.
    """
    
    print(f"Prompt: {read_prompt.strip()}")
    print("\nOutput stream:")
    print("-" * 40)
    
    async for chunk_str in executor.execute_agent("example_agent", read_prompt):
        try:
            chunk = json.loads(chunk_str)
            if chunk["type"] == "text":
                print(f"[TEXT]: {chunk.get('content', {}).get('text', '')}")
            elif chunk["type"] == "tool_use":
                print(f"[TOOL_USE]: {chunk.get('name')} with input: {json.dumps(chunk.get('input', {}), indent=2)}")
            elif chunk["type"] == "tool_result":
                content = chunk.get('content', '')
                if isinstance(content, str):
                    # Truncate long results for display
                    if len(content) > 300:
                        content = content[:300] + "... [truncated]"
                    print(f"[TOOL_RESULT]: {content}")
                else:
                    print(f"[TOOL_RESULT]: {json.dumps(content, indent=2)}")
            elif chunk["type"] == "error":
                print(f"[ERROR]: {chunk.get('content', {}).get('text', '')}")
            else:
                print(f"[{chunk.get('type', 'UNKNOWN')}]: {json.dumps(chunk, indent=2)}")
        except json.JSONDecodeError:
            print(f"[RAW]: {chunk_str}")
    
    print("\n" + "=" * 60)
    print("TEST 2: Glob tool with example agent")
    print("=" * 60)
    
    glob_prompt = """
    Use the Glob tool to find Python files with pattern: src/**/*.py
    Show me the first 3 files you find.
    """
    
    print(f"Prompt: {glob_prompt.strip()}")
    print("\nOutput stream:")
    print("-" * 40)
    
    async for chunk_str in executor.execute_agent("example_agent", glob_prompt):
        try:
            chunk = json.loads(chunk_str)
            if chunk["type"] == "text":
                print(f"[TEXT]: {chunk.get('content', {}).get('text', '')}")
            elif chunk["type"] == "tool_use":
                print(f"[TOOL_USE]: {chunk.get('name')} with input: {json.dumps(chunk.get('input', {}), indent=2)}")
            elif chunk["type"] == "tool_result":
                content = chunk.get('content', '')
                if isinstance(content, str):
                    # Truncate long results for display
                    if len(content) > 300:
                        content = content[:300] + "... [truncated]"
                    print(f"[TOOL_RESULT]: {content}")
                else:
                    print(f"[TOOL_RESULT]: {json.dumps(content, indent=2)}")
            elif chunk["type"] == "error":
                print(f"[ERROR]: {chunk.get('content', {}).get('text', '')}")
            else:
                print(f"[{chunk.get('type', 'UNKNOWN')}]: {json.dumps(chunk, indent=2)}")
        except json.JSONDecodeError:
            print(f"[RAW]: {chunk_str}")

if __name__ == "__main__":
    asyncio.run(test_example_agent())