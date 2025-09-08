import { useNavigate } from 'react-router-dom'
import { type Agent } from '@/lib/api'
import { cn } from '@/lib/utils'
import { Code2, FileText } from 'lucide-react'

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
  const Icon = agent.name.toLowerCase().includes('code') ? Code2 : FileText

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start gap-4 mb-4">
        <div className="p-2 bg-gray-100 rounded-lg">
          <Icon className="w-6 h-6 text-gray-700" />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
          <p className="text-sm text-gray-600 mt-1">{agent.description}</p>
        </div>
      </div>

      <div className="space-y-3 mb-4">
        <div>
          <span className="text-sm font-medium text-gray-700">Model: </span>
          <span className="text-sm text-gray-600">{agent.model}</span>
        </div>
        
        <div>
          <span className="text-sm font-medium text-gray-700">Tools: </span>
          <span className="text-sm text-gray-600">
            {agent.tools.slice(0, 3).join(', ')}
            {agent.tools.length > 3 && ` +${agent.tools.length - 3} more`}
          </span>
        </div>

        {agent.resume_session && (
          <div>
            <span className="text-sm font-medium text-gray-700">Session: </span>
            <span className="text-sm text-gray-600">
              Up to {agent.max_exchanges} exchanges
            </span>
          </div>
        )}
      </div>

      <button
        onClick={handleSelect}
        className={cn(
          "w-full py-2 px-4 rounded-lg font-medium transition-colors",
          "bg-blue-600 text-white hover:bg-blue-700"
        )}
      >
        Select Agent
      </button>
    </div>
  )
}