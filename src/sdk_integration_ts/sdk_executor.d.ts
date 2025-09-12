import type { AgentConfig } from './agent_manager';
export interface SDKMessage {
    type: string;
    subtype?: string;
    uuid?: string;
    session_id?: string;
    message?: any;
    result?: string;
    total_cost_usd?: number;
    duration_ms?: number;
    num_turns?: number;
    usage?: any;
    parent_tool_use_id?: string | null;
    event?: any;
}
export interface ExecutionOptions {
    sessionId?: string;
    sessionReset?: boolean;
    maxTurns?: number;
    includePartialMessages?: boolean;
    abortController?: AbortController;
    onMessage?: (message: SDKMessage) => void;
}
export declare class SDKExecutor {
    private sessionStore;
    private credentialsPath;
    constructor();
    /**
     * Execute an agent with the given prompt
     */
    executeAgent(agent: AgentConfig, prompt: string, options?: ExecutionOptions): Promise<AsyncGenerator<SDKMessage>>;
    /**
     * Stream messages from the SDK
     */
    private streamMessages;
    /**
     * Get available sessions
     */
    getAvailableSessions(): any[];
    /**
     * Clear a specific session
     */
    clearSession(sessionId: string): boolean;
    /**
     * Clear all sessions
     */
    clearAllSessions(): void;
}
//# sourceMappingURL=sdk_executor.d.ts.map