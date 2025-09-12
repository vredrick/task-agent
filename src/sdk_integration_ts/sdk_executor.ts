import { query } from '@anthropic-ai/claude-code';
import type { AgentConfig } from './agent_manager';
import { SessionStore } from './session_store';
import * as path from 'path';
import * as os from 'os';

// Message types matching the SDK documentation
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
  text?: string;
  tool_name?: string;
  tool_params?: any;
  is_error?: boolean;
  model?: string;
  delta?: any;
  error?: string;
  [key: string]: any; // Allow additional properties
}

export interface ExecutionOptions {
  sessionId?: string;
  sessionReset?: boolean;
  maxTurns?: number;
  includePartialMessages?: boolean;
  abortController?: AbortController;
  onMessage?: (message: SDKMessage) => void;
}

export class SDKExecutor {
  private sessionStore: SessionStore;
  private credentialsPath: string;

  constructor() {
    this.sessionStore = new SessionStore();
    this.credentialsPath = path.join(os.homedir(), '.claude', '.credentials.json');
  }

  /**
   * Execute an agent with the given prompt
   */
  async executeAgent(
    agent: AgentConfig,
    prompt: string,
    options: ExecutionOptions = {}
  ): Promise<AsyncGenerator<SDKMessage>> {
    const {
      sessionId,
      sessionReset = false,
      maxTurns,
      includePartialMessages = true,
      abortController = new AbortController(),
      onMessage
    } = options;

    // Handle session management
    let useSessionId = sessionId;
    if (sessionReset && sessionId) {
      // Reset session if requested
      this.sessionStore.deleteSession(sessionId);
      useSessionId = undefined;
    }

    // Prepare SDK options
    const sdkOptions: any = {
      appendSystemPrompt: agent.systemPrompt,
      allowedTools: agent.tools || [],
      maxTurns: maxTurns || agent.maxTurns || 5,
      abortController,
      includePartialMessages, // Control partial message streaming
      cwd: agent.cwd || process.cwd(),
    };

    // Handle session continuation
    if (useSessionId && !sessionReset) {
      const session = this.sessionStore.getSession(useSessionId);
      if (session) {
        sdkOptions.resume = useSessionId;
      }
    }

    // Add model if specified
    if (agent.model) {
      sdkOptions.model = agent.model;
    }

    // Create async generator to stream messages
    return this.streamMessages(prompt, sdkOptions, useSessionId, onMessage);
  }

  /**
   * Stream messages from the SDK
   */
  private async *streamMessages(
    prompt: string,
    sdkOptions: any,
    sessionId?: string,
    onMessage?: (message: SDKMessage) => void
  ): AsyncGenerator<SDKMessage> {
    try {
      let currentSessionId = sessionId;
      let hasInitMessage = false;

      // Call the SDK query function
      for await (const message of query({ prompt, options: sdkOptions })) {
        // Extract session ID from init message
        if (message.type === 'system' && message.subtype === 'init') {
          currentSessionId = message.session_id;
          hasInitMessage = true;
          
          // Save session for future use
          if (currentSessionId) {
            this.sessionStore.createSession(currentSessionId, {
              id: currentSessionId,
              agentName: sdkOptions.appendSystemPrompt ? 'custom' : 'default',
              createdAt: Date.now(),
              lastUsed: Date.now(),
              turnCount: 0
            });
          }
        }

        // Update turn count for result messages
        if (message.type === 'result' && currentSessionId) {
          const session = this.sessionStore.getSession(currentSessionId);
          if (session) {
            session.turnCount = message.num_turns || session.turnCount + 1;
            session.lastUsed = Date.now();
            this.sessionStore.updateSession(currentSessionId, session);
          }
        }

        // Call the optional message handler
        if (onMessage) {
          onMessage(message);
        }

        // Yield the message to the caller
        yield message;
      }
    } catch (error: any) {
      // Yield error as a message
      yield {
        type: 'error',
        subtype: 'sdk_error',
        session_id: sessionId,
        result: error.message || 'Unknown SDK error',
        message: {
          error: error.message,
          stack: error.stack
        }
      };
    }
  }

  /**
   * Get available sessions
   */
  getAvailableSessions(): any[] {
    return this.sessionStore.getAllSessions();
  }

  /**
   * Clear a specific session
   */
  clearSession(sessionId: string): boolean {
    return this.sessionStore.deleteSession(sessionId);
  }

  /**
   * Clear all sessions
   */
  clearAllSessions(): void {
    this.sessionStore.clearAll();
  }
}