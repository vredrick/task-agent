import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api, type Agent } from '@/lib/api'
import { ChatWebSocket, type ChatMessage as WSMessage } from '@/lib/websocket'
import { Conversation, ConversationContent, ConversationScrollButton } from '@/components/ai-elements/conversation'
import { Message, MessageContent, MessageAvatar } from '@/components/ai-elements/message'
import { Tool, ToolHeader, ToolContent, ToolInput } from '@/components/ai-elements/tool'
import { ToolOutputEnhanced } from '@/components/ai-elements/ToolOutputEnhanced'
import { CodeBlock, CodeBlockCopyButton } from '@/components/ai-elements/code-block'
import { Loader } from '@/components/ai-elements/loader'
import { StreamingMessage } from '@/components/StreamingMessage'
import AuthStatus from '@/components/AuthStatus'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { ArrowLeft, Send, RotateCcw, User, Bot, Paperclip, ChevronDown, Square } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  toolUse?: {
    name: string
    input?: any
    output?: any
    state?: 'input-streaming' | 'input-available' | 'output-available' | 'output-error'
    tool_id?: string
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
  const [pendingTools, setPendingTools] = useState<any[]>([]) // Queue for tools waiting for text to finish
  const [isTextStreaming, setIsTextStreaming] = useState(false) // Track if text is currently streaming
  const [displayedTextLength, setDisplayedTextLength] = useState(0) // Track how much text has been displayed
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const chatContainerRef = useRef<HTMLDivElement>(null)

  // Manual scroll to bottom
  const scrollToBottom = () => {
    // Try multiple methods to ensure scrolling works
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' })
    } else if (chatContainerRef.current) {
      const scrollElement = chatContainerRef.current.querySelector('[role="log"]')
      if (scrollElement) {
        scrollElement.scrollTop = scrollElement.scrollHeight
      }
    }
  }

  // Scroll when messages or streaming content changes
  useEffect(() => {
    // Use requestAnimationFrame to ensure DOM has painted
    requestAnimationFrame(() => {
      setTimeout(() => {
        scrollToBottom()
      }, 100)
    })
  }, [messages, currentResponse, loading])

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
              
              // If we have a current message ID, update that message directly
              if (currentMessageId) {
                setMessages(prev => {
                  const existingIndex = prev.findIndex(msg => msg.id === currentMessageId)
                  if (existingIndex >= 0) {
                    // Update existing message
                    const updated = [...prev]
                    updated[existingIndex] = {
                      ...updated[existingIndex],
                      content: updated[existingIndex].content + message.content.text,
                      isStreaming: true
                    }
                    return updated
                  } else {
                    // Create new message
                    return [...prev, {
                      id: currentMessageId,
                      role: 'assistant',
                      content: message.content.text,
                      isStreaming: true
                    }]
                  }
                })
              } else {
                // No message ID yet, accumulate in currentResponse
                setCurrentResponse(prev => prev + message.content.text)
              }
              
              setPendingResponse(prev => prev + message.content.text) // Store for metadata
            } else if (message.type === 'text') {
              console.log('Text message but no content.text:', message)
            } else if (message.type === 'tool_use') {
              // Tool use received - finalize any current text and queue tool
              console.log('Tool use received:', message)
              
              // Clear states since text has already been added to messages
              setCurrentResponse('')
              setPendingResponse('')
              setCurrentMessageId(null)
              setIsTextStreaming(true) // Mark that text is streaming
              
              // Create tool data
              const toolUseData = {
                name: message.name || 'Unknown',
                input: message.input,
                state: 'input-available' as const,
                tool_id: message.id || crypto.randomUUID()
              }
              
              // Queue the tool instead of adding it immediately
              setPendingTools(prev => [...prev, {
                id: crypto.randomUUID(),
                role: 'assistant',
                content: '',
                toolUse: toolUseData
              }])
            } else if (message.type === 'tool_result') {
              // Handle tool result - update the corresponding tool message
              console.log('Tool result received:', message)
              
              // First check if the tool is in pending tools
              setPendingTools(prev => {
                const pendingIndex = prev.findIndex(msg => 
                  msg.toolUse && msg.toolUse.tool_id === message.tool_use_id
                )
                
                if (pendingIndex >= 0) {
                  // Update the pending tool with the result
                  const updatedTool = {
                    ...prev[pendingIndex],
                    toolUse: {
                      ...prev[pendingIndex].toolUse!,
                      output: message.output,
                      state: message.is_error ? 'output-error' : 'output-available' as const
                    }
                  }
                  
                  return [
                    ...prev.slice(0, pendingIndex),
                    updatedTool,
                    ...prev.slice(pendingIndex + 1)
                  ]
                }
                
                return prev
              })
              
              // Also check if the tool is already in messages
              setMessages(prev => {
                const toolMessageIndex = prev.findIndex(msg => 
                  msg.toolUse && msg.toolUse.tool_id === message.tool_use_id
                )
                
                if (toolMessageIndex >= 0) {
                  const toolMessage = prev[toolMessageIndex]
                  const updatedToolMessage = {
                    ...toolMessage,
                    toolUse: {
                      ...toolMessage.toolUse!,
                      output: message.output,
                      state: message.is_error ? 'output-error' : 'output-available' as const
                    }
                  }
                  
                  return [
                    ...prev.slice(0, toolMessageIndex),
                    updatedToolMessage,
                    ...prev.slice(toolMessageIndex + 1)
                  ]
                }
                
                return prev
              })
            } else if (message.type === 'tool_start') {
              // Handle tool start - update state to running
              console.log('Tool start received:', message)
              
              setMessages(prev => {
                const toolMessageIndex = prev.findIndex(msg => 
                  msg.toolUse && msg.toolUse.tool_id === message.id
                )
                
                if (toolMessageIndex >= 0) {
                  const toolMessage = prev[toolMessageIndex]
                  const updatedToolMessage = {
                    ...toolMessage,
                    toolUse: {
                      ...toolMessage.toolUse!,
                      state: 'input-available' as const
                    }
                  }
                  
                  return [
                    ...prev.slice(0, toolMessageIndex),
                    updatedToolMessage,
                    ...prev.slice(toolMessageIndex + 1)
                  ]
                }
                
                return prev
              })
            } else if (message.type === 'tool_complete') {
              // Handle tool complete - finalize state
              console.log('Tool complete received:', message)
              
              setMessages(prev => {
                const toolMessageIndex = prev.findIndex(msg => 
                  msg.toolUse && msg.toolUse.tool_id === message.id
                )
                
                if (toolMessageIndex >= 0) {
                  const toolMessage = prev[toolMessageIndex]
                  const updatedToolMessage = {
                    ...toolMessage,
                    toolUse: {
                      ...toolMessage.toolUse!,
                      state: message.success ? 'output-available' : 'output-error'
                    }
                  }
                  
                  return [
                    ...prev.slice(0, toolMessageIndex),
                    updatedToolMessage,
                    ...prev.slice(toolMessageIndex + 1)
                  ]
                }
                
                return prev
              })
            } else if (message.type === 'interrupt_result') {
              // Handle interrupt result
              console.log('Interrupt result received:', message)
              
              // Mark any pending tools as interrupted
              setMessages(prev => prev.map(msg => {
                if (msg.toolUse && msg.toolUse.state === 'input-available' && !msg.toolUse.output) {
                  return {
                    ...msg,
                    toolUse: {
                      ...msg.toolUse,
                      state: 'output-error' as const,
                      output: 'Tool execution interrupted'
                    }
                  }
                }
                return msg
              }))
              
              // Clear pending tools that haven't been added to messages
              setPendingTools([])
              
              // Stop loading
              setLoading(false)
              setCurrentResponse('')
              setIsTextStreaming(false)
              
              // Log the interrupt result
              if (message.success) {
                console.log('Task interrupted successfully')
              } else {
                console.log('Failed to interrupt or no active task')
              }
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
                    content: currentResp,
                    isStreaming: true  // Mark as streaming for animation
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

  // Effect to add pending tools after text streaming completes
  useEffect(() => {
    if (!isTextStreaming && pendingTools.length > 0) {
      // Add a small delay to ensure text animation completes
      const timer = setTimeout(() => {
        // Add all pending tools to messages
        setMessages(prev => [...prev, ...pendingTools])
        setPendingTools([]) // Clear the queue
      }, 500) // 500ms delay to ensure text streaming visually completes
      
      return () => clearTimeout(timer)
    }
  }, [isTextStreaming, pendingTools])

  // Effect to mark text streaming as complete when messages finish animating
  useEffect(() => {
    // Find messages that are marked as streaming
    const streamingMessage = messages.find(msg => msg.isStreaming && msg.role === 'assistant')
    
    if (streamingMessage && isTextStreaming) {
      // Set a timer to mark streaming as complete
      // This should be slightly longer than the total animation time
      // With 25ms per word and average 5 chars per word, that's ~5ms per char
      const wordsInContent = streamingMessage.content.split(' ').length
      const animationTime = Math.max(1000, wordsInContent * 25) // 25ms per word
      const timer = setTimeout(() => {
        setIsTextStreaming(false)
        // Also mark the message as no longer streaming
        setMessages(prev => prev.map(msg => 
          msg.id === streamingMessage.id 
            ? { ...msg, isStreaming: false }
            : msg
        ))
      }, animationTime)
      
      return () => clearTimeout(timer)
    }
  }, [messages, isTextStreaming])

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
    
    // Reset textarea height after sending
    const textarea = document.querySelector('textarea')
    if (textarea) {
      textarea.style.height = '38px'
    }

    try {
      console.log('Sending WebSocket message:', { agentName, input })
      wsRef.current.sendMessage(agentName, input)
    } catch (error) {
      console.error('Failed to send message:', error)
      setLoading(false)
    }
  }

  // Stream current response as a temporary message only if we don't have a currentMessageId
  // (currentMessageId means we're updating an existing message directly)
  const streamingMessage: ChatMessage | null = (currentResponse && !currentMessageId) ? {
    id: 'streaming',
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
  
  const handleInterrupt = async () => {
    if (wsRef.current) {
      // Send interrupt signal via WebSocket
      wsRef.current.ws?.send(JSON.stringify({ type: 'interrupt' }))
      console.log('Interrupt signal sent')
      // Stop loading state
      setLoading(false)
      setCurrentResponse('')
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
      <div className="flex-1 flex flex-col relative overflow-hidden" ref={chatContainerRef}>
        <Conversation className="flex-1 max-w-3xl mx-auto w-full px-4" style={{ height: 'calc(100vh - 180px)' }}>
          <ConversationContent className="pb-24">
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
                    {/* Use StreamingMessage for smooth text animation */}
                    <StreamingMessage 
                      content={message.content}
                      isStreaming={message.isStreaming || false}
                      className="prose prose-sm dark:prose-invert max-w-none overflow-hidden"
                    />
                    
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
                          {message.toolUse.output && (
                            <ToolOutputEnhanced 
                              output={typeof message.toolUse.output === 'string' 
                                ? message.toolUse.output 
                                : JSON.stringify(message.toolUse.output, null, 2)}
                              errorText={message.toolUse.state === 'output-error' ? 'Tool execution failed' : undefined}
                            />
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
                  </MessageContent>
                )}
              </Message>
            ))}
            
            {loading && !streamingMessage && (
              <Message from="assistant">
                <MessageContent role="assistant">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Loader size={14} className="text-primary" />
                    <span className="text-sm">Thinking...</span>
                  </div>
                </MessageContent>
              </Message>
            )}
            
            {/* Scroll anchor */}
            <div ref={messagesEndRef} style={{ height: 1 }} />
          </ConversationContent>
          
          <ConversationScrollButton />
        </Conversation>

        {/* Claude Desktop Style Input Area - Fixed Position */}
        <div className="fixed bottom-0 left-0 right-0 p-2 z-50 bg-gradient-to-t from-background via-background/95 to-transparent pointer-events-none">
          <div className="max-w-2xl mx-auto pointer-events-auto">
            {/* Single input container with Claude styling - expands upward only */}
            <div 
              className="relative bg-background border border-input rounded-2xl transition-all duration-200"
              style={{ minHeight: '76px' }}
            >
              {/* Main Input Field - Expands upward */}
              <div className="flex flex-col">
                {/* Textarea container that expands */}
                <div className="p-4 pb-2">
                  <Textarea
                    value={input}
                    onChange={(e) => {
                      setInput(e.target.value)
                      // Auto-resize textarea only
                      const target = e.target
                      target.style.height = 'auto'
                      const newHeight = Math.min(target.scrollHeight, 192) // max 8 lines
                      target.style.height = newHeight + 'px'
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
                      "w-full min-h-[38px] max-h-[192px] resize-none border-0 bg-transparent p-0",
                      "focus-visible:ring-0 focus-visible:ring-offset-0",
                      "disabled:opacity-50 disabled:cursor-not-allowed",
                      "text-sm leading-relaxed placeholder:text-muted-foreground",
                      "overflow-y-auto"
                    )}
                    style={{ height: '38px' }}
                    rows={1}
                  />
                </div>
                
                {/* Bottom Controls Row - Fixed at bottom */}
                <div className="flex items-center justify-between px-4 pb-3">
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
                    
                    {/* Send/Stop Button - Same shape, different state */}
                    <Button
                      onClick={loading ? handleInterrupt : handleSend}
                      disabled={!loading && (connecting || !wsRef.current || !input.trim())}
                      size="icon"
                      variant={loading ? "destructive" : "default"}
                      className="h-8 w-8"
                    >
                      {loading ? (
                        <Square className="w-4 h-4" />
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