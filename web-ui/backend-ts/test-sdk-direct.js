// Test the SDK directly to see what it outputs
const { query } = require('@anthropic-ai/claude-code');

async function testSDKStreaming() {
  console.log('Testing SDK directly with includePartialMessages...\n');
  
  const options = {
    prompt: 'Count from 1 to 10, one number per line.',
    options: {
      appendSystemPrompt: 'You are a helpful assistant.',
      allowedTools: [],
      maxTurns: 1,
      includePartialMessages: true,  // This should enable streaming
      model: 'sonnet'
    }
  };
  
  let messageCount = 0;
  let startTime = Date.now();
  let lastTime = startTime;
  
  console.log('Calling SDK with includePartialMessages: true\n');
  console.log('Messages received:');
  console.log('-----------------------------------');
  
  try {
    for await (const message of query(options)) {
      messageCount++;
      const now = Date.now();
      const elapsed = now - startTime;
      const gap = now - lastTime;
      lastTime = now;
      
      // Log message type and timing
      console.log(`#${messageCount} [${elapsed}ms, +${gap}ms]: type="${message.type}", subtype="${message.subtype || 'none'}"`);
      
      // Show content for specific message types
      if (message.type === 'stream_event' && message.event?.type === 'content_block_delta') {
        const delta = message.event.delta;
        if (delta?.type === 'text_delta') {
          console.log(`  → Text delta: "${delta.text.replace(/\n/g, '\\n')}"`);
        }
      } else if (message.type === 'text') {
        console.log(`  → Text: "${(message.text || '').substring(0, 50).replace(/\n/g, '\\n')}..."`);
      } else if (message.type === 'assistant') {
        console.log(`  → Assistant response (full message)`);
      }
    }
  } catch (error) {
    console.error('Error:', error.message);
  }
  
  console.log('-----------------------------------');
  console.log(`\nTotal messages: ${messageCount}`);
  console.log(`Total time: ${Date.now() - startTime}ms`);
}

testSDKStreaming();