const WebSocket = require('ws');
const crypto = require('crypto');

const connectionId = crypto.randomUUID();
const ws = new WebSocket(`ws://localhost:8001/ws/chat/${connectionId}`);

console.log('Testing SDK streaming output...\n');
console.log('Connection ID:', connectionId);
console.log('-----------------------------------\n');

let startTime;
let deltaCount = 0;
let fullText = '';
let deltas = [];

ws.on('open', () => {
  console.log('Connected to WebSocket\n');
  
  // Send a message that will generate a multi-sentence response
  ws.send(JSON.stringify({
    type: 'chat',
    agentName: 'code-reviewer',
    prompt: 'Write a haiku about streaming data. Make it exactly 3 lines following the 5-7-5 syllable pattern.',
    sessionReset: true
  }));
  
  startTime = Date.now();
  console.log('Message sent at:', new Date().toISOString());
  console.log('Waiting for response...\n');
});

ws.on('message', (data) => {
  const msg = JSON.parse(data.toString());
  const elapsed = Date.now() - startTime;
  
  if (msg.type === 'text_delta') {
    deltaCount++;
    const deltaText = msg.content.text;
    fullText += deltaText;
    
    // Record delta details
    deltas.push({
      num: deltaCount,
      time: elapsed,
      text: deltaText,
      length: deltaText.length
    });
    
    // Show each delta as it arrives
    console.log(`Delta #${deltaCount} [${elapsed}ms]: "${deltaText.replace(/\n/g, '\\n')}"`);
    
  } else if (msg.type === 'metadata' && msg.content?.event === 'stream_complete') {
    console.log('\n-----------------------------------');
    console.log('STREAM COMPLETE\n');
    
    // Summary
    console.log('Summary:');
    console.log(`- Total deltas: ${deltaCount}`);
    console.log(`- Total time: ${elapsed}ms`);
    console.log(`- Total characters: ${fullText.length}`);
    console.log(`- Average time between deltas: ${deltaCount > 1 ? Math.round(elapsed / (deltaCount - 1)) : 0}ms`);
    
    // Show delta timing
    console.log('\nDelta Timing Analysis:');
    let prevTime = 0;
    deltas.forEach(d => {
      const gap = d.time - prevTime;
      console.log(`  Delta ${d.num}: +${gap}ms (${d.length} chars)`);
      prevTime = d.time;
    });
    
    console.log('\nFull text received:');
    console.log('---');
    console.log(fullText);
    console.log('---');
    
    ws.close();
    
  } else if (msg.type === 'error') {
    console.error('\nError:', msg.content.text);
    ws.close();
  } else if (msg.type === 'metadata') {
    // Other metadata events
    console.log(`\nMetadata [${elapsed}ms]:`, msg.content?.event || 'unknown');
  }
});

ws.on('close', () => {
  console.log('\nConnection closed');
  process.exit(0);
});

ws.on('error', (err) => {
  console.error('WebSocket error:', err);
  process.exit(1);
});

// Timeout after 30 seconds
setTimeout(() => {
  console.log('\nTimeout - closing connection');
  ws.close();
  process.exit(0);
}, 30000);