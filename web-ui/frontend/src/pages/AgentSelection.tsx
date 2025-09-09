import { useState, useEffect } from 'react'
import { api, type Agent } from '@/lib/api'
import AgentCard from '@/components/AgentCard'
import AuthStatus from '@/components/AuthStatus'

export default function AgentSelection() {
  const [agents, setAgents] = useState<Record<string, Agent>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const agentList = await api.listAgents()
        setAgents(agentList)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load agents')
      } finally {
        setLoading(false)
      }
    }

    fetchAgents()
  }, [])

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Compact Header */}
      <header className="bg-card border-b border-border px-4 py-3">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <div className="flex flex-col">
            <h1 className="text-base font-medium leading-tight">Task Agent Web UI</h1>
            <p className="text-xs text-muted-foreground leading-tight">Select an agent to start a conversation</p>
          </div>
          <div className="scale-75 origin-right">
            <AuthStatus />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-6">

        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="bg-card rounded-lg border border-border p-4">
                <div className="animate-pulse">
                  <div className="h-4 bg-muted rounded w-3/4 mb-2"></div>
                  <div className="h-3 bg-muted rounded w-full mb-4"></div>
                  <div className="h-8 bg-muted rounded"></div>
                </div>
              </div>
            ))}
          </div>
        )}

        {error && (
          <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4">
            <p className="text-destructive text-sm">{error}</p>
          </div>
        )}

        {!loading && !error && Object.keys(agents).length === 0 && (
          <div className="bg-muted/30 border border-border rounded-lg p-4">
            <p className="text-muted-foreground text-sm">No agents available. Please add agent configurations to the task-agents directory.</p>
          </div>
        )}

        {!loading && !error && Object.keys(agents).length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(agents).map(([key, agent]) => (
              <AgentCard key={key} agent={agent} agentKey={key} />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}