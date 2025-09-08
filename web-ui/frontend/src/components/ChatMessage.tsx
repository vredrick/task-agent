import { cn } from '@/lib/utils'
import { User, Bot, Wrench } from 'lucide-react'

interface ChatMessageProps {
  role: 'user' | 'assistant'
  content: string
  toolUse?: {
    name: string
    input?: any
  }
}

export default function ChatMessage({ role, content, toolUse }: ChatMessageProps) {
  return (
    <div className={cn(
      "flex gap-3 p-4",
      role === 'user' ? "bg-white" : "bg-gray-50"
    )}>
      <div className={cn(
        "w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0",
        role === 'user' ? "bg-blue-100" : "bg-purple-100"
      )}>
        {role === 'user' ? (
          <User className="w-5 h-5 text-blue-600" />
        ) : (
          <Bot className="w-5 h-5 text-purple-600" />
        )}
      </div>
      
      <div className="flex-1 min-w-0">
        {toolUse && (
          <div className="mb-2 flex items-center gap-2 text-sm text-gray-600">
            <Wrench className="w-4 h-4" />
            <span>Using tool: {toolUse.name}</span>
          </div>
        )}
        
        <div className="prose prose-sm max-w-none">
          <pre className="whitespace-pre-wrap font-sans">{content}</pre>
        </div>
      </div>
    </div>
  )
}