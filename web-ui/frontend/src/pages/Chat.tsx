import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api, type Agent } from '@/lib/api'
import { ChatWebSocket, type ChatMessage as WSMessage } from '@/lib/websocket'
import ChatMessage from '@/components/ChatMessage'
import AuthStatus from '@/components/AuthStatus'
import { ArrowLeft, Send, RotateCcw, Loader2 } from 'lucide-react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  toolUse?: {
    name: string
    input?: any
  }
}

export default function Chat() {
  const { agentName } = useParams<{ agentName: string }>()
  const navigate = useNavigate()
  const [agent, setAgent] = useState<Agent | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [connecting, setConnecting] = useState(false)
  const [currentResponse, setCurrentResponse] = useState('')
  const [sessionId] = useState(() => crypto.randomUUID())
  const wsRef = useRef<ChatWebSocket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, currentResponse])

  // Load agent info
  useEffect(() => {
    if (!agentName) return

    const loadAgent = async () => {
      try {
        const agentInfo = await api.getAgent(agentName)
        setAgent(agentInfo)
      } catch (error) {
        console.error('Failed to load agent:', error)
        navigate('/')
      }
    }

    loadAgent()
  }, [agentName, navigate])

  // Setup WebSocket
  useEffect(() => {
    if (!agentName) return

    const setupWebSocket = async () => {
      setConnecting(true)
      try {
        const ws = new ChatWebSocket(
          sessionId,
          (message: WSMessage) => {
            if (message.type === 'text' && message.content?.text) {
              setCurrentResponse(prev => prev + message.content.text)
            } else if (message.type === 'tool_use') {
              // Handle tool use display
              const toolMessage: Message = {
                id: crypto.randomUUID(),
                role: 'assistant',
                content: '',
                toolUse: {
                  name: message.name || 'Unknown',
                  input: message.input
                }
              }
              setMessages(prev => [...prev, toolMessage])
            } else if (message.type === 'error') {
              console.error('Error from agent:', message.content)
              setCurrentResponse(prev => prev + '\n[Error: ' + message.content + ']')
              setLoading(false)  // Stop loading on error
            } else if (message.session_id || message.conversation_id) {
              // Session info usually comes at the end of the response
              console.log('Session established:', message.session_id || message.conversation_id)
              // Delay slightly to ensure all text is processed
              setTimeout(() => {
                setLoading(false)
              }, 100)
            } else if (message.type === 'usage') {
              // Usage info indicates completion
              console.log('Usage:', message.usage)
              setLoading(false)
            } else if (message.type === 'complete') {
              // Explicit completion signal
              console.log('Response complete')
              setLoading(false)
            }
          },
          (error) => {
            console.error('WebSocket error:', error)
            setLoading(false)
          },
          () => {
            console.log('WebSocket closed')
            setLoading(false)
          }
        )

        await ws.connect()
        wsRef.current = ws
      } catch (error) {
        console.error('Failed to connect WebSocket:', error)
      } finally {
        setConnecting(false)
      }
    }

    setupWebSocket()

    return () => {
      wsRef.current?.close()
    }
  }, [agentName, sessionId])

  const handleSend = async () => {
    if (!input.trim() || !wsRef.current || !agentName || loading) return

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)
    setCurrentResponse('')

    try {
      wsRef.current.sendMessage(agentName, input)
      // The response will be handled by the WebSocket message handler
      // We'll detect completion when we stop receiving messages
    } catch (error) {
      console.error('Failed to send message:', error)
      setLoading(false)
    }
  }

  // Monitor currentResponse and add to messages when complete
  useEffect(() => {
    if (!loading && currentResponse) {
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: currentResponse
      }
      setMessages(prev => [...prev, assistantMessage])
      setCurrentResponse('')
    }
  }, [loading, currentResponse])

  const handleReset = () => {
    setMessages([])
    setCurrentResponse('')
    if (wsRef.current && agentName) {
      wsRef.current.sendMessage(agentName, 'Reset session', true)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="w-5 h-5" />
              Back to Agents
            </button>
            
            {agent && (
              <div>
                <h1 className="text-xl font-semibold text-gray-900">{agent.name}</h1>
                <p className="text-sm text-gray-600">{agent.description}</p>
              </div>
            )}
          </div>
          
          <div className="flex items-center gap-4">
            <button
              onClick={handleReset}
              className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-900"
            >
              <RotateCcw className="w-4 h-4" />
              Reset
            </button>
            <AuthStatus />
          </div>
        </div>
      </header>

      {/* Chat Area */}
      <div className="flex-1 overflow-hidden flex flex-col max-w-4xl mx-auto w-full">
        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 && !currentResponse && (
            <div className="flex items-center justify-center h-full text-gray-500 p-8">
              <p>Start a conversation with {agent?.name || 'the agent'}</p>
            </div>
          )}
          
          {messages.map(message => (
            <ChatMessage
              key={message.id}
              role={message.role}
              content={message.content}
              toolUse={message.toolUse}
            />
          ))}
          
          {currentResponse && (
            <ChatMessage
              role="assistant"
              content={currentResponse}
            />
          )}
          
          {loading && !currentResponse && (
            <div className="flex items-center gap-2 p-4 text-gray-600">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Agent is thinking...</span>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 bg-white p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={`Message ${agent?.name || 'Agent'}...`}
              disabled={loading || connecting || !wsRef.current}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            />
            <button
              onClick={handleSend}
              disabled={loading || connecting || !wsRef.current || !input.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}