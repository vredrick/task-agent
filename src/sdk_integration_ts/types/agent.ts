/**
 * Agent configuration types for TypeScript SDK integration
 */

export interface AgentConfig {
  agentName: string;
  description: string;
  tools: string[];
  model: string;
  cwd: string;
  systemPrompt: string;
  resumeSession: boolean | number;
  resourceDirs?: string[];
  filePath?: string;
  maxExchanges: number;
  maxTurns?: number;
}

export interface AgentConfigRaw {
  'agent-name': string;
  description: string;
  tools: string;
  model: string;
  cwd: string;
  optional?: {
    'resume-session'?: boolean | string | number;
    resource_dirs?: string;
  };
}

export interface AgentMetadata {
  name: string;
  description: string;
  tools: string[];
  model: string;
  resumeSession: boolean;
  maxExchanges: number;
}

export interface AgentListResponse {
  agents: AgentMetadata[];
}

export interface AgentDetailResponse extends AgentConfig {
  available: boolean;
}