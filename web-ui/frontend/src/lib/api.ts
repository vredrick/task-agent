// API client for Task Agent Web UI

export interface Agent {
  name: string
  description: string
  model: string
  tools: string[]
  resume_session: boolean
  max_exchanges: number
}

export interface AuthStatus {
  authenticated: boolean
  subscription_type?: string
  message: string
}

class APIClient {
  private baseURL = ''  // Same origin (served from backend)

  async getAuthStatus(): Promise<AuthStatus> {
    const response = await fetch(`${this.baseURL}/api/auth/status`)
    if (!response.ok) throw new Error('Failed to get auth status')
    return response.json()
  }

  async listAgents(): Promise<Record<string, Agent>> {
    const response = await fetch(`${this.baseURL}/api/agents`)
    if (!response.ok) throw new Error('Failed to list agents')
    const data = await response.json()
    return data.agents
  }

  async getAgent(name: string): Promise<Agent> {
    const response = await fetch(`${this.baseURL}/api/agents/${name}`)
    if (!response.ok) throw new Error(`Failed to get agent ${name}`)
    return response.json()
  }
}

export const api = new APIClient()