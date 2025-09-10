#!/usr/bin/env python3
"""Test interrupt functionality with Claude SDK."""

import asyncio
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import Claude SDK
try:
    from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
    HAS_SDK = True
except ImportError:
    logger.error("Claude SDK not available")
    HAS_SDK = False
    exit(1)


async def test_interrupt_basic():
    """Test basic interrupt functionality."""
    logger.info("Testing basic interrupt...")
    
    # Create options
    options = ClaudeCodeOptions(
        model="claude-3-5-sonnet-20241022",
        allowed_tools=["Read", "Bash", "Write"]
    )
    
    client = ClaudeSDKClient(options=options)
    
    try:
        # Connect with empty stream for interactive use
        await client.connect()
        logger.info("Connected to Claude")
        
        # Start a long-running task
        await client.query("Count from 1 to 100 slowly, showing each number")
        logger.info("Sent long-running task")
        
        # Collect some messages
        message_count = 0
        async def receive_with_timeout():
            nonlocal message_count
            try:
                async for message in client.receive_messages():
                    message_count += 1
                    logger.info(f"Received message {message_count}: {type(message).__name__}")
                    
                    # After 3 messages, interrupt
                    if message_count >= 3:
                        logger.info("Interrupting after 3 messages...")
                        return
            except Exception as e:
                logger.error(f"Error receiving messages: {e}")
        
        # Start receiving in background
        receive_task = asyncio.create_task(receive_with_timeout())
        
        # Wait for a few messages
        await asyncio.sleep(2)
        
        # Send interrupt
        logger.info("Sending interrupt signal...")
        await client.interrupt()
        logger.info("Interrupt sent")
        
        # Wait a bit
        await asyncio.sleep(1)
        
        # Send new query
        logger.info("Sending new query after interrupt...")
        await client.query("Just say 'Interrupted successfully!' and nothing else")
        
        # Receive the response
        async for message in client.receive_messages():
            logger.info(f"Post-interrupt message: {type(message).__name__}")
            message_content = str(message)
            if "Interrupted successfully" in message_content:
                logger.info("SUCCESS: Interrupt worked!")
                break
            if "ResultMessage" in type(message).__name__:
                break
        
    finally:
        await client.disconnect()
        logger.info("Disconnected")


async def test_interrupt_with_context_manager():
    """Test interrupt using context manager pattern."""
    logger.info("\nTesting interrupt with context manager...")
    
    options = ClaudeCodeOptions(
        model="claude-3-5-sonnet-20241022",
        allowed_tools=["Read", "Bash"]
    )
    
    async with ClaudeSDKClient(options=options) as client:
        # Store client reference for interrupt
        client_ref = client
        
        # Start long task
        await client.query("List all files in the current directory with detailed explanations for each one")
        
        # Create interrupt task
        async def interrupt_after_delay():
            await asyncio.sleep(1.5)
            logger.info("Interrupting from background task...")
            await client_ref.interrupt()
        
        # Start interrupt task
        interrupt_task = asyncio.create_task(interrupt_after_delay())
        
        # Receive messages until interrupted
        message_count = 0
        try:
            async for message in client.receive_response():
                message_count += 1
                logger.info(f"Message {message_count}: {type(message).__name__}")
                
                # Check for result message (end of response)
                if "ResultMessage" in type(message).__name__:
                    logger.info("Received ResultMessage")
                    break
        except Exception as e:
            logger.info(f"Response interrupted: {e}")
        
        # Wait for interrupt task to complete
        await interrupt_task
        
        # Send new query after interrupt
        await client.query("Say 'Context manager interrupt test successful!'")
        
        async for message in client.receive_response():
            message_content = str(message)
            if "successful" in message_content.lower():
                logger.info("SUCCESS: Context manager interrupt worked!")
                break


async def test_interrupt_tracking():
    """Test how we can track client for interrupt in our implementation."""
    logger.info("\nTesting client tracking for interrupt...")
    
    class InterruptableExecutor:
        def __init__(self):
            self._current_client = None
            self._current_task = None
        
        async def execute_with_interrupt(self, task: str):
            """Execute a task with interrupt capability."""
            options = ClaudeCodeOptions(
                model="claude-3-5-sonnet-20241022",
                allowed_tools=["Read", "Bash"]
            )
            
            async with ClaudeSDKClient(options=options) as client:
                # Store client reference
                self._current_client = client
                
                try:
                    await client.query(task)
                    
                    async for message in client.receive_messages():
                        yield message
                        
                        if "ResultMessage" in type(message).__name__:
                            break
                finally:
                    # Clear client reference
                    self._current_client = None
        
        async def interrupt(self):
            """Interrupt the current task."""
            if self._current_client:
                logger.info("Interrupting current client...")
                await self._current_client.interrupt()
                return True
            else:
                logger.info("No active client to interrupt")
                return False
    
    # Test the interruptable executor
    executor = InterruptableExecutor()
    
    # Start task in background
    async def run_task():
        async for message in executor.execute_with_interrupt("Count from 1 to 50"):
            logger.info(f"Task message: {type(message).__name__}")
    
    task = asyncio.create_task(run_task())
    
    # Wait a bit then interrupt
    await asyncio.sleep(2)
    success = await executor.interrupt()
    logger.info(f"Interrupt result: {success}")
    
    # Wait for task to complete
    try:
        await asyncio.wait_for(task, timeout=3)
    except asyncio.TimeoutError:
        logger.info("Task timed out after interrupt")
    
    logger.info("Interrupt tracking test complete")


async def main():
    """Run all interrupt tests."""
    if not HAS_SDK:
        logger.error("Claude SDK not available, cannot run tests")
        return
    
    try:
        # Test 1: Basic interrupt
        await test_interrupt_basic()
        
        # Test 2: Context manager interrupt
        await test_interrupt_with_context_manager()
        
        # Test 3: Client tracking for our implementation
        await test_interrupt_tracking()
        
        logger.info("\n=== All interrupt tests completed ===")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())