/**
 * Agent Manager for TypeScript SDK
 * Loads and manages AI agent configurations from Markdown files
 */
import { AgentConfig } from './types/agent';
export declare class AgentManager {
    private agents;
    private configDir;
    constructor(configDir?: string);
    /**
     * Load all agent configurations from the config directory
     */
    loadAgents(): Promise<void>;
    /**
     * Load a single agent configuration from a Markdown file
     */
    private loadAgentConfig;
    /**
     * Get an agent configuration by name
     */
    getAgent(agentName: string): AgentConfig | undefined;
    /**
     * List all available agents
     */
    listAgents(): string[];
    /**
     * Get all agent configurations
     */
    getAllAgents(): Map<string, AgentConfig>;
    /**
     * Get agent metadata for API responses
     */
    getAgentMetadata(agentName: string): {
        name: string;
        description: string;
        tools: string[];
        model: string;
        resumeSession: boolean;
        maxExchanges: number;
    } | null;
    /**
     * Get all agents metadata for API listing
     */
    getAllAgentsMetadata(): ({
        name: string;
        description: string;
        tools: string[];
        model: string;
        resumeSession: boolean;
        maxExchanges: number;
    } | null)[];
}
//# sourceMappingURL=agent_manager.d.ts.map