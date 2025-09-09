#!/usr/bin/env python3
import asyncio
import websockets
import json
import time

async def test_streaming():
    uri = "ws://localhost:8000/ws/chat/test-session-123"
    
    async with websockets.connect(uri) as websocket:
        # Send a message requesting multiple tasks including tool use
        message = {
            "agent_name": "example-agent",
            "message": "Please do three things: 1) Read the README.md file and tell me what this project is about, 2) List the files in the task-agents directory, 3) Write a short joke about coding"
        }
        
        print(f"Sending: {message}")
        await websocket.send(json.dumps(message))
        
        # Receive and print all messages with timing
        start_time = time.time()
        chunk_count = 0
        
        while True:
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10)
                elapsed = time.time() - start_time
                chunk_count += 1
                
                data = json.loads(response)
                print(f"\n[{elapsed:.2f}s] Chunk #{chunk_count}:")
                print(f"Type: {data.get('type')}")
                
                if data.get('type') == 'text':
                    text = data.get('content', {}).get('text', '')
                    print(f"Text length: {len(text)} chars")
                    print(f"Text preview: {text[:100]}..." if len(text) > 100 else f"Text: {text}")
                elif data.get('type') == 'metadata':
                    print(f"Metadata: {data.get('data')}")
                    break  # Metadata usually signals end
                elif data.get('type') == 'complete':
                    print("Response complete")
                    break
                    
            except asyncio.TimeoutError:
                print("\nTimeout - no more messages")
                break
            except Exception as e:
                print(f"\nError: {e}")
                break
        
        print(f"\nTotal chunks received: {chunk_count}")
        print(f"Total time: {time.time() - start_time:.2f}s")

if __name__ == "__main__":
    asyncio.run(test_streaming())