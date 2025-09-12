const WebSocket = require('ws');

// Generate a connection ID
const connectionId = require('crypto').randomUUID();

// Connect to WebSocket
const ws = new WebSocket(`ws://localhost:8001/ws/chat/${connectionId}`);

ws.on('open', () => {
  console.log('Connected to WebSocket');
  
  // Send a chat message
  ws.send(JSON.stringify({
    type: 'chat',
    agentName: 'example_agent',
    prompt: 'Write a short poem about streaming text animations.',
    sessionReset: true
  }));
  
  console.log('Sent chat message');
});

ws.on('message', (data) => {
  const message = JSON.parse(data.toString());
  
  if (message.type === 'text_delta') {
    process.stdout.write(message.content.text);
  } else if (message.type === 'metadata' && message.content?.event === 'stream_complete') {
    console.log('\n\n[Stream Complete]');
    ws.close();
  } else if (message.type === 'error') {
    console.error('\nError:', message.content.text);
    ws.close();
  }
});

ws.on('error', (err) => {
  console.error('WebSocket error:', err);
});

ws.on('close', () => {
  console.log('Connection closed');
  process.exit(0);
});

setTimeout(() => {
  console.log('\nTimeout - closing connection');
  ws.close();
  process.exit(0);
}, 30000);
