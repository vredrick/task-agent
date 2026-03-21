import { useNavigate } from 'react-router-dom'
import { type Agent } from '@/lib/api'
// cn available if needed
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Bot } from 'lucide-react'

interface AgentCardProps {
  agent: Agent
  agentKey: string
}

export default function AgentCard({ agent, agentKey }: AgentCardProps) {
  const navigate = useNavigate()

  const handleSelect = () => {
    navigate(`/chat/${agentKey}`)
  }

  // Choose icon based on agent name
  return (
    <div className="bg-card rounded-lg border border-border p-4 hover:bg-card/80 transition-colors cursor-pointer group"
         onClick={handleSelect}>
      <div className="flex items-start gap-3 mb-3">
        <div className="p-2 bg-primary/10 rounded-lg">
          <Bot className="w-4 h-4 text-primary" />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-medium text-foreground truncate">{agent.name}</h3>
          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{agent.description}</p>
        </div>
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="text-xs px-2 py-0.5">
            {agent.model}
          </Badge>
          {agent.resume_session && (
            <Badge variant="outline" className="text-xs px-2 py-0.5">
              Session: {agent.max_exchanges}
            </Badge>
          )}
        </div>
        
        <div className="flex flex-wrap gap-1">
          {agent.tools.slice(0, 3).map((tool, index) => (
            <Badge key={index} variant="outline" className="text-xs px-1.5 py-0.5">
              {tool}
            </Badge>
          ))}
          {agent.tools.length > 3 && (
            <Badge variant="outline" className="text-xs px-1.5 py-0.5">
              +{agent.tools.length - 3}
            </Badge>
          )}
        </div>
      </div>

      <Button
        size="sm"
        className="w-full h-8 text-xs bg-primary hover:bg-primary/90 group-hover:bg-primary/80"
      >
        Start Chat
      </Button>
    </div>
  )
}