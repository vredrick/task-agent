"""
Example client for Task-Agents MCP Server

Demonstrates how to connect and use the task_delicator tool.
"""

import asyncio
from fastmcp import FastMCPClient


async def main():
    """Example usage of the task-agents MCP server."""
    
    # Note: This example assumes the server is running
    # Start the server first with: python server.py
    
    print("Task-Agents MCP Client Example")
    print("==============================\n")
    
    # Example tasks to demonstrate agent selection
    example_tasks = [
        {
            "task": "Review the authentication module for security vulnerabilities",
            "expected_agent": "code-reviewer"
        },
        {
            "task": "Fix the TypeError in the payment processing function", 
            "expected_agent": "debugger"
        },
        {
            "task": "Run the test suite and fix failing unit tests",
            "expected_agent": "test-runner"
        },
        {
            "task": "Create API documentation for the new endpoints",
            "expected_agent": "documentation-writer"
        },
        {
            "task": "The dashboard is loading slowly, analyze and optimize",
            "expected_agent": "performance-optimizer"
        }
    ]
    
    print("Example task delegations:")
    print("------------------------\n")
    
    for example in example_tasks:
        print(f"Task: {example['task']}")
        print(f"Expected agent: {example['expected_agent']}")
        print()
        
        # In a real scenario, you would:
        # 1. Connect to the MCP server
        # 2. Call the task_delicator tool
        # 3. Get the response
        
        # Example (pseudo-code):
        # async with FastMCPClient("http://localhost:8000") as client:
        #     result = await client.call_tool("task_delicator", {
        #         "task_description": example['task']
        #     })
        #     print(f"Result: {result}")
    
    print("\nTo use this with a real MCP client:")
    print("1. Install an MCP client library")
    print("2. Start the server: python server.py")
    print("3. Connect to the server")
    print("4. Call the 'task_delicator' tool with your task description")


if __name__ == "__main__":
    asyncio.run(main())