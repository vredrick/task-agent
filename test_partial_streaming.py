#!/usr/bin/env python3
"""Test script for partial message streaming support."""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from src.sdk_integration.sdk_executor import get_sdk_executor

# Configure logging to see debug output
logging.basicConfig(
    level=logging.INFO,  # Changed to INFO to reduce noise
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set specific loggers to DEBUG for targeted debugging
logging.getLogger("src.sdk_integration.sdk_executor").setLevel(logging.DEBUG)
logging.getLogger("src.sdk_integration.message_parser").setLevel(logging.DEBUG)


class SimpleAgentConfig:
    """Simple agent config for testing."""
    def __init__(self):
        self.agent_name = "test_agent"
        self.system_prompt = "You are a helpful assistant. Be concise."
        self.tools = ["Read", "Bash"]
        self.model = "claude-3-5-sonnet-20241022"
        self.cwd = "."
        self.max_exchanges = 3


async def test_streaming():
    """Test the streaming functionality."""
    executor = get_sdk_executor()
    
    if not executor.is_available():
        print("SDK is not available!")
        return
    
    agent_config = SimpleAgentConfig()
    
    # Simple test prompt
    test_prompt = "Count from 1 to 5 slowly, with each number on a new line."
    
    print(f"\n{'='*60}")
    print("Testing SDK Streaming")
    print(f"{'='*60}")
    print(f"Prompt: {test_prompt}")
    print(f"{'='*60}\n")
    
    chunk_count = 0
    text_chunks = []
    
    try:
        async for chunk in executor.execute_task(
            agent_config=agent_config,
            task_description=test_prompt,
            session_id=None
        ):
            chunk_count += 1
            
            # Parse the JSON chunk
            try:
                data = json.loads(chunk)
                
                # Log chunk details
                logger.info(f"Chunk {chunk_count}: type={data.get('type')}")
                
                if data.get("type") == "text":
                    text = data.get("content", {}).get("text", "")
                    text_chunks.append(text)
                    print(f"[TEXT CHUNK {chunk_count}]: {repr(text[:100])}")
                elif data.get("type") == "tool_use":
                    print(f"[TOOL USE]: {data.get('name')}")
                elif data.get("type") == "tool_result":
                    print(f"[TOOL RESULT]: {data.get('tool_use_id')[:10]}...")
                elif data.get("type") == "metadata":
                    print(f"[METADATA]: session_id={data.get('data', {}).get('session_id')}")
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse chunk: {e}")
                print(f"[RAW CHUNK {chunk_count}]: {chunk[:100]}")
    
    except Exception as e:
        logger.error(f"Error during streaming: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'='*60}")
    print(f"Total chunks received: {chunk_count}")
    print(f"Text chunks: {len(text_chunks)}")
    if text_chunks:
        full_text = "".join(text_chunks)
        print(f"Full response ({len(full_text)} chars):")
        print(full_text)
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(test_streaming())