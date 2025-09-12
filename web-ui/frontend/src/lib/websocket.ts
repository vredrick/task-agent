// WebSocket client for streaming chat responses

export interface ChatMessage {
  type: 'text' | 'text_delta' | 'tool_use' | 'tool_result' | 'error' | 'session_info' | 'usage' | 'complete' | 'cancelled' | 'metadata'
  content?: any
  name?: string
  input?: any
  conversation_id?: string
  session_id?: string
  usage?: {
    input_tokens: number
    output_tokens: number
    total_cost_usd?: number
  }
}

export class ChatWebSocket {
  private ws: WebSocket | null = null
  private url: string
  private onMessage: (message: ChatMessage) => void
  private onError?: (error: any) => void
  private onClose?: () => void

  constructor(
    connectionId: string,  // Just a connection identifier, not an SDK session
    onMessage: (message: ChatMessage) => void,
    onError?: (error: any) => void,
    onClose?: () => void,
    backendPort?: number
  ) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const hostname = window.location.hostname
    const port = backendPort || (import.meta.env.VITE_BACKEND_PORT || 8000)
    this.url = `${protocol}//${hostname}:${port}/ws/chat/${connectionId}`
    this.onMessage = onMessage
    this.onError = onError
    this.onClose = onClose
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        console.log('Attempting WebSocket connection to:', this.url)
        this.ws = new WebSocket(this.url)

        this.ws.onopen = () => {
          console.log('WebSocket connected')
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data)
            this.onMessage(message)
          } catch (e) {
            console.error('Failed to parse message:', e)
            if (this.onError) this.onError(e)
          }
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          if (this.onError) this.onError(error)
          reject(error)
        }

        this.ws.onclose = () => {
          console.log('WebSocket closed')
          if (this.onClose) this.onClose()
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  sendMessage(agentName: string, message: string, sessionReset = false) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'chat',
        agentName: agentName,    // Changed from agent_name to agentName
        prompt: message,          // Changed from message to prompt
        sessionReset: sessionReset,  // Changed from session_reset to sessionReset
        maxTurns: 5              // Adding optional parameter that backend accepts
      }))
    } else {
      throw new Error('WebSocket is not connected')
    }
  }

  cancelRequest() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'interrupt'
      }))
    }
  }

  close() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }
}