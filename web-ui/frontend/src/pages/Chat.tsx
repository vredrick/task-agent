import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api, type Agent } from '@/lib/api'
import { ChatWebSocket, type ChatMessage as WSMessage } from '@/lib/websocket'
import { Conversation, ConversationContent, ConversationScrollButton } from '@/components/ai-elements/conversation'
import { Message, MessageContent, MessageAvatar } from '@/components/ai-elements/message'
import { Tool, ToolHeader, ToolContent, ToolInput } from '@/components/ai-elements/tool'
import { CodeBlock, CodeBlockCopyButton } from '@/components/ai-elements/code-block'
import { Response } from '@/components/ai-elements/response'
import AuthStatus from '@/components/AuthStatus'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { ArrowLeft, Send, RotateCcw, Loader2, User, Bot, Paperclip, ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  toolUse?: {
    name: string
    input?: any
    state?: 'input-streaming' | 'input-available' | 'output-available' | 'output-error'
  }
  isStreaming?: boolean
  metadata?: {
    cost: number
    duration: number
    tokens: number
    session_id: string
  }
}

export default function Chat() {
  const { agentName } = useParams<{ agentName: string }>()
  const navigate = useNavigate()
  const [agent, setAgent] = useState<Agent | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [connecting, setConnecting] = useState(false)
  const [currentResponse, setCurrentResponse] = useState('')
  const [currentMessageId, setCurrentMessageId] = useState<string | null>(null)
  const [pendingResponse, setPendingResponse] = useState('')
  const [sessionId] = useState(() => crypto.randomUUID())
  const wsRef = useRef<ChatWebSocket | null>(null)

  // AI Elements handles scrolling automatically

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
            console.log('WebSocket message received:', message)
            if (message.type === 'text' && message.content?.text) {
              console.log('Adding text to currentResponse:', message.content.text)
              setCurrentResponse(prev => {
                // Concatenate text chunks directly - backend handles formatting
                const newResponse = prev + message.content.text
                console.log('Updated currentResponse:', newResponse)
                setPendingResponse(newResponse) // Store the full response for metadata handling
                return newResponse
              })
            } else if (message.type === 'text') {
              console.log('Text message but no content.text:', message)
            } else if (message.type === 'tool_use') {
              // Tool use received - finalize any current text and create tool message
              console.log('Tool use received:', message)
              
              // If there's current text, finalize it as a message first
              setCurrentResponse(currentText => {
                if (currentText) {
                  const textMessageId = currentMessageId || crypto.randomUUID()
                  setMessages(prev => [...prev, {
                    id: textMessageId,
                    role: 'assistant',
                    content: currentText
                  }])
                  setPendingResponse('') // Clear pending response
                }
                return '' // Clear current response
              })
              
              // Reset message ID for next text chunk
              setCurrentMessageId(null)
              
              // Add tool use as a separate message
              const toolUseData = {
                name: message.name || 'Unknown',
                input: message.input,
                state: 'input-available' as const
              }
              
              setMessages(prev => [...prev, {
                id: crypto.randomUUID(),
                role: 'assistant',
                content: '',
                toolUse: toolUseData
              }])
            } else if (message.type === 'metadata') {
              // Handle SDK metadata
              const metadata = message.data
              console.log('Metadata received:', metadata)
              
              // Finalize any remaining text as a message if exists
              setCurrentResponse(currentResp => {
                if (currentResp) {
                  // There's text that hasn't been finalized yet
                  const textMessageId = currentMessageId || crypto.randomUUID()
                  setMessages(prev => [...prev, {
                    id: textMessageId,
                    role: 'assistant',
                    content: currentResp
                  }])
                }
                return '' // Clear current response
              })
              
              // Add metadata as a separate message (just metadata, no content)
              // The metadata will be displayed on the last assistant message
              setMessages(prev => {
                // Find the last assistant message and add metadata to it
                if (prev.length > 0) {
                  const lastMessageIndex = prev.length - 1
                  const lastMessage = prev[lastMessageIndex]
                  
                  // Only add metadata to assistant messages
                  if (lastMessage.role === 'assistant') {
                    const updatedMessage = {
                      ...lastMessage,
                      metadata: {
                        cost: metadata.cost || 0,
                        duration: metadata.duration || 0,
                        tokens: (metadata.usage?.input_tokens || 0) + (metadata.usage?.output_tokens || 0),
                        session_id: metadata.session_id || ''
                      }
                    }
                    
                    const updated = [
                      ...prev.slice(0, lastMessageIndex),
                      updatedMessage
                    ]
                    console.log('Added metadata to last message:', updatedMessage)
                    return updated
                  }
                }
                return prev
              })
              
              // Clear streaming state
              setCurrentMessageId(null)
              setPendingResponse('')
              setLoading(false)
            } else if (message.type === 'error') {
              console.error('Error from agent:', message.content)
              setCurrentResponse(prev => prev + '\n[Error: ' + message.content + ']')
              setLoading(false)
            } else if (message.session_id || message.conversation_id) {
              console.log('Session established:', message.session_id || message.conversation_id)
              setTimeout(() => setLoading(false), 100)
            } else if (message.type === 'complete') {
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
    console.log('handleSend called with:', { input, agentName, loading, wsConnected: !!wsRef.current })
    
    if (!input.trim() || !wsRef.current || !agentName || loading) {
      console.log('handleSend early return:', {
        hasInput: !!input.trim(),
        hasWs: !!wsRef.current,
        hasAgent: !!agentName,
        loading
      })
      return
    }

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input
    }

    const assistantMessageId = crypto.randomUUID()
    
    console.log('Adding user message to chat:', userMessage)
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)
    setCurrentResponse('')
    setPendingResponse('') // Clear any previous pending response
    setCurrentMessageId(assistantMessageId)
    
    // Reset textarea and container height after sending
    const textarea = document.querySelector('textarea')
    if (textarea) {
      textarea.style.height = '38px'
      const container = textarea.closest('.relative')
      if (container instanceof HTMLElement) {
        container.style.minHeight = '76px'
      }
    }

    try {
      console.log('Sending WebSocket message:', { agentName, input })
      wsRef.current.sendMessage(agentName, input)
    } catch (error) {
      console.error('Failed to send message:', error)
      setLoading(false)
    }
  }

  // Stream current response as a temporary message
  const streamingMessage: ChatMessage | null = currentResponse ? {
    id: currentMessageId || 'streaming',
    role: 'assistant',
    content: currentResponse,
    isStreaming: true
  } : null

  // Debug logging for streamingMessage and messages
  console.log('Streaming message state:', { currentResponse, streamingMessage })
  console.log('Messages array:', messages)
  console.log('Combined messages for rendering:', [...messages, ...(streamingMessage ? [streamingMessage] : [])])

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
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      {/* Compact Header */}
      <header className="bg-card border-b border-border px-4 py-3">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/')}
              className="flex items-center gap-2 h-8 px-2"
            >
              <ArrowLeft className="w-4 h-4" />
              <span className="hidden sm:inline">Back</span>
            </Button>
            
            {agent && (
              <div className="flex flex-col">
                <h1 className="text-base font-medium leading-tight">{agent.name}</h1>
                <p className="text-xs text-muted-foreground leading-tight">{agent.description}</p>
              </div>
            )}
          </div>
          
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleReset}
              className="flex items-center gap-1 h-7 px-2 text-xs"
            >
              <RotateCcw className="w-3 h-3" />
              <span className="hidden sm:inline">Reset</span>
            </Button>
            {/* Compact Authentication Status */}
            <div className="text-xs px-2 py-1 bg-primary/10 rounded-md text-primary">
              Claude authenticated
            </div>
          </div>
        </div>
      </header>

      {/* Chat Area */}
      <div className="flex-1 overflow-hidden flex flex-col relative">
        <Conversation className="flex-1 max-w-3xl mx-auto w-full px-4 pb-32 min-w-0">
          <ConversationContent>
            {messages.length === 0 && !streamingMessage && (
              <div className="flex items-center justify-center h-full text-muted-foreground p-8">
                <p>Start a conversation with {agent?.name || 'the agent'}</p>
              </div>
            )}
            
            {[...messages, ...(streamingMessage ? [streamingMessage] : [])].map(message => (
              <Message key={message.id} from={message.role}>
                {/* User messages: avatar inside the bubble on the left */}
                {message.role === 'user' ? (
                  <div className="flex items-center gap-3 bg-secondary text-secondary-foreground rounded-xl px-4 py-2 max-w-[75%]">
                    <MessageAvatar
                      src="/user-avatar.png"
                      name="User"
                      className="size-8"
                    />
                    <div className="text-sm leading-relaxed flex-1">
                      {message.content}
                    </div>
                  </div>
                ) : (
                  /* AI messages: no avatar, plain text */
                  <MessageContent role={message.role}>
                    {/* Use Response component for proper markdown rendering */}
                    <Response 
                      className="prose prose-sm dark:prose-invert max-w-none overflow-hidden"
                      components={{
                        pre: ({ children, ...props }) => {
                          // Extract code content and language from the pre/code elements
                          const codeElement = children as any
                          const className = codeElement?.props?.className || ''
                          const language = className.replace(/language-/, '') || 'plaintext'
                          const code = codeElement?.props?.children || ''
                          
                          return (
                            <div className="my-3">
                              <CodeBlock 
                                code={code}
                                language={language}
                                showLineNumbers={code.split('\n').length > 5}
                                className="border-blue-900/30 dark:border-blue-400/30"
                              >
                                <CodeBlockCopyButton className="hover:bg-blue-900/10 dark:hover:bg-blue-400/10" />
                              </CodeBlock>
                            </div>
                          )
                        }
                      }}
                    >
                      {message.content}
                    </Response>
                    
                    {/* Tool usage with ai-elements styling */}
                    {message.toolUse && (
                      <Tool className="mt-3 border border-blue-900/30 dark:border-blue-400/30 rounded-lg">
                        <ToolHeader
                          type={message.toolUse.name}
                          state={message.toolUse.state || 'input-available'}
                        />
                        <ToolContent>
                          {message.toolUse.input && (
                            <ToolInput input={message.toolUse.input} />
                          )}
                        </ToolContent>
                      </Tool>
                    )}
                    
                    {/* Compact metadata display - only show at end of conversation */}
                    {message.metadata && message.id === messages[messages.length - 1]?.id && (
                      <div className="mt-3 pt-3 border-t border-border/20">
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <span>${message.metadata.cost.toFixed(4)}</span>
                          <span>{message.metadata.duration}ms</span>
                          <span>{message.metadata.tokens} tokens</span>
                          <span className="font-mono">#{message.metadata.session_id.slice(0, 6)}</span>
                        </div>
                      </div>
                    )}
                    
                    {/* Streaming indicator */}
                    {message.isStreaming && (
                      <div className="flex items-center gap-2 mt-2 text-sm text-muted-foreground">
                        <Loader2 className="w-3 h-3 animate-spin" />
                        <span>Streaming...</span>
                      </div>
                    )}
                  </MessageContent>
                )}
              </Message>
            ))}
            
            {loading && !streamingMessage && (
              <Message from="assistant">
                <MessageContent role="assistant">
                  <div className="flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Agent is thinking...</span>
                  </div>
                </MessageContent>
              </Message>
            )}
          </ConversationContent>
          
          <ConversationScrollButton />
        </Conversation>

        {/* Claude Desktop Style Input Area - Fixed Position */}
        <div className="fixed bottom-0 left-0 right-0 p-2 z-50 bg-gradient-to-t from-background via-background/95 to-transparent">
          <div className="max-w-2xl mx-auto">
            {/* Single input container with Claude styling - expands with content */}
            <div className="relative bg-background border border-input rounded-2xl p-4 min-h-[76px] transition-all duration-200">
              {/* Main Input Field - Full width on top */}
              <div className="flex flex-col h-full">
                <Textarea
                  value={input}
                  onChange={(e) => {
                    setInput(e.target.value)
                    // Auto-resize textarea and container
                    const target = e.target
                    target.style.height = 'auto'
                    const newHeight = Math.min(target.scrollHeight, 192) // max 8 lines
                    target.style.height = newHeight + 'px'
                    
                    // Expand container based on textarea height
                    const container = target.closest('.relative') as HTMLElement
                    if (container) {
                      // Base height is 76px, expand as textarea grows
                      const baseHeight = 76
                      const textareaBaseHeight = 38
                      const expansion = Math.max(0, newHeight - textareaBaseHeight)
                      container.style.minHeight = (baseHeight + expansion) + 'px'
                    }
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      handleSend()
                    }
                  }}
                  placeholder={`Reply to ${agent?.name || 'Agent'}...`}
                  disabled={loading || connecting || !wsRef.current}
                  className={cn(
                    "flex-1 min-h-[38px] max-h-[192px] resize-none border-0 bg-transparent p-0",
                    "focus-visible:ring-0 focus-visible:ring-offset-0",
                    "disabled:opacity-50 disabled:cursor-not-allowed",
                    "text-sm leading-relaxed placeholder:text-muted-foreground",
                    "overflow-y-auto"
                  )}
                  style={{ height: '38px' }}
                  rows={1}
                />
                
                {/* Bottom Controls Row */}
                <div className="flex items-center justify-between pt-2 mt-2">
                  {/* Upload Button - Bottom Left */}
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="h-8 w-8 p-0" 
                    disabled
                  >
                    <Paperclip className="w-4 h-4" />
                  </Button>
                  
                  {/* Right Controls - Model Selection and Send */}
                  <div className="flex items-center gap-2">
                    {/* Model Selection */}
                    <Select disabled>
                      <SelectTrigger className="w-24 h-7 text-xs border-0 bg-transparent">
                        <SelectValue placeholder="3.5" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="claude-3.5">3.5</SelectItem>
                        <SelectItem value="claude-3" disabled>3.0</SelectItem>
                      </SelectContent>
                    </Select>
                    
                    {/* Send Button */}
                    <Button
                      onClick={handleSend}
                      disabled={loading || connecting || !wsRef.current || !input.trim()}
                      size="sm"
                      className="h-8 w-8 p-0 bg-primary hover:bg-primary/90"
                    >
                      {loading ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Send className="w-4 h-4" />
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}