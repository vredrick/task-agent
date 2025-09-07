#!/usr/bin/env python3
"""Test SDK OAuth authentication with Claude subscription."""

import asyncio
import os
from pathlib import Path
from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
from claude_code_sdk.types import AssistantMessage, ResultMessage, TextBlock

async def test_oauth_authentication():
    """Test if SDK can authenticate using OAuth credentials."""
    
    print("Testing Claude Code SDK OAuth Authentication")
    print("=" * 60)
    
    # Check for OAuth credentials (try both possible names)
    creds_path1 = Path.home() / ".claude" / "credentials.json"
    creds_path2 = Path.home() / ".claude" / ".credentials.json"
    
    creds_path = None
    if creds_path1.exists():
        creds_path = creds_path1
        print(f"✅ Found credentials at: {creds_path}")
    elif creds_path2.exists():
        creds_path = creds_path2
        print(f"✅ Found credentials at: {creds_path}")
    else:
        print(f"❌ No credentials found at: {creds_path1} or {creds_path2}")
        print("   Please login with: claude login")
        return False
    
    # Make sure we're NOT using API key (to force OAuth)
    if 'ANTHROPIC_API_KEY' in os.environ:
        print("⚠️  ANTHROPIC_API_KEY is set, removing to test OAuth...")
        del os.environ['ANTHROPIC_API_KEY']
    
    print("\nAttempting SDK connection with OAuth...")
    
    try:
        # Create minimal options
        options = ClaudeCodeOptions(
            allowed_tools=["Read", "Write"],
            model="haiku"
        )
        
        # Create client
        client = ClaudeSDKClient(options=options)
        
        # Connect
        print("Connecting to Claude...")
        await client.connect()
        
        print("✅ Connected successfully!")
        
        # Send a simple query
        print("\nSending test query...")
        await client.query("Say 'OAuth authentication successful!' and nothing else.")
        
        # Get response
        response_text = ""
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        response_text += block.text
            elif isinstance(msg, ResultMessage):
                print(f"\n✅ Got result message")
                if hasattr(msg, 'conversation_id'):
                    print(f"   Session ID: {msg.conversation_id}")
                if hasattr(msg, 'total_cost_usd'):
                    print(f"   Cost: ${msg.total_cost_usd:.6f}")
                break
        
        print(f"\nResponse: {response_text}")
        
        # Disconnect
        await client.disconnect()
        print("\n✅ Disconnected successfully")
        
        if "OAuth authentication successful" in response_text:
            print("\n🎉 OAuth authentication is working!")
            return True
        else:
            print("\n⚠️  Got unexpected response")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        # Check if it's an auth error
        error_str = str(e).lower()
        if 'auth' in error_str or 'credential' in error_str or 'token' in error_str:
            print("\n⚠️  This appears to be an authentication issue.")
            print("Suggestions:")
            print("1. Run: claude login")
            print("2. Check ~/.claude/credentials.json exists")
            print("3. Ensure you have an active Claude subscription")
        
        return False

async def main():
    success = await test_oauth_authentication()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)