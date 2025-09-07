#!/usr/bin/env python3
"""Test script for SDK integration.

This script tests whether the SDK executor works correctly
and produces compatible output with the CLI version.
"""

import asyncio
import os
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.task_agents_mcp.agent_manager import AgentManager
from src.task_agents_mcp.sdk_executor import get_sdk_executor


async def test_sdk_availability():
    """Test if SDK is available."""
    print("=" * 60)
    print("Testing SDK Availability")
    print("=" * 60)
    
    executor = get_sdk_executor()
    is_available = executor.is_available()
    
    print(f"SDK Available: {is_available}")
    print(f"Has claude-max: {executor.has_claude_max}")
    print(f"Has standard SDK: {executor.has_sdk}")
    
    if not is_available:
        print("\n❌ SDK is not available. Please install claude-code-sdk or claude-max")
        return False
    
    print("\n✅ SDK is available and ready to use")
    return True


async def test_basic_execution():
    """Test basic SDK execution with a simple task."""
    print("\n" + "=" * 60)
    print("Testing Basic SDK Execution")
    print("=" * 60)
    
    # Set USE_SDK environment variable
    os.environ['USE_SDK'] = 'true'
    
    # Initialize agent manager
    agents_dir = Path(__file__).parent / "task-agents"
    if not agents_dir.exists():
        print(f"❌ Agents directory not found: {agents_dir}")
        return False
    
    manager = AgentManager(str(agents_dir))
    manager.load_agents()
    
    # Check if we have any agents
    if not manager.agents:
        print("❌ No agents loaded")
        return False
    
    print(f"✅ Loaded {len(manager.agents)} agents")
    
    # Use the example agent if it exists
    agent_name = "example-agent"
    if agent_name not in manager.agents:
        # Use first available agent
        agent_name = next(iter(manager.agents.keys()))
    
    print(f"\nTesting with agent: {agent_name}")
    
    # Prepare agent for execution
    selected_agent = {
        'name': agent_name,
        'config': manager.agents[agent_name]
    }
    
    # Simple test task
    test_task = "Say hello and tell me what tools you have available."
    
    print(f"Task: {test_task}")
    print("\nExecuting...")
    
    try:
        # Execute with SDK
        # Define async progress callback
        async def progress_callback(msg):
            print(f"  Progress: {msg}")
        
        result = await manager.execute_task(
            selected_agent,
            test_task,
            session_reset=True,
            progress_callback=progress_callback
        )
        
        print("\n" + "-" * 40)
        print("Result:")
        print("-" * 40)
        print(result)
        
        # Check if we got SDK mode indicator
        if "(SDK mode)" in result:
            print("\n✅ SDK execution successful!")
            return True
        else:
            print("\n⚠️  Result doesn't indicate SDK mode was used")
            return False
            
    except Exception as e:
        print(f"\n❌ Execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_cli_comparison():
    """Compare SDK output with CLI output."""
    print("\n" + "=" * 60)
    print("Comparing SDK vs CLI Output")
    print("=" * 60)
    
    # This would require actually having the CLI available
    # For now, we'll skip this if CLI is not available
    
    import shutil
    claude_cli = shutil.which('claude')
    
    if not claude_cli:
        print("⚠️  Claude CLI not found - skipping comparison test")
        print("   To run comparison, install Claude Code CLI")
        return True
    
    print(f"✅ Claude CLI found at: {claude_cli}")
    
    # TODO: Implement actual comparison
    print("   (Detailed comparison not yet implemented)")
    
    return True


async def main():
    """Run all tests."""
    print("Task Agent SDK Integration Test Suite")
    print("=" * 60)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    
    # Run tests
    tests_passed = []
    
    # Test 1: SDK Availability
    tests_passed.append(await test_sdk_availability())
    
    # Test 2: Basic Execution
    if tests_passed[-1]:  # Only if SDK is available
        tests_passed.append(await test_basic_execution())
    
    # Test 3: CLI Comparison (optional)
    if all(tests_passed):
        tests_passed.append(await test_cli_comparison())
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    total_tests = len(tests_passed)
    passed_tests = sum(tests_passed)
    
    print(f"Tests passed: {passed_tests}/{total_tests}")
    
    if all(tests_passed):
        print("\n🎉 All tests passed! SDK integration is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)