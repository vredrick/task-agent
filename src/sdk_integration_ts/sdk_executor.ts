import { spawn, type ChildProcess } from 'child_process';
import { createInterface } from 'readline';
import { randomUUID } from 'crypto';
import type { AgentConfig } from './agent_manager';
import { SessionStore } from './session_store';

// Message types matching the CLI stream-json output
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
  private activeProcesses: Map<string, ChildProcess> = new Map();

  constructor() {
    this.sessionStore = new SessionStore();
  }

  /**
   * Execute an agent with the given prompt via the claude CLI
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
      this.sessionStore.deleteSession(sessionId);
      useSessionId = undefined;
    }

    // Prepare CLI options (same shape as before for streamMessages compatibility)
    const cliOptions: any = {
      appendSystemPrompt: agent.systemPrompt,
      allowedTools: agent.tools || [],
      maxTurns: maxTurns || agent.maxTurns || 5,
      abortController,
      includePartialMessages,
      cwd: agent.cwd || process.cwd(),
    };

    // Handle session continuation
    if (useSessionId && !sessionReset) {
      const session = this.sessionStore.getSession(useSessionId);
      if (session) {
        cliOptions.resume = useSessionId;
      }
    }

    // Add model if specified
    if (agent.model) {
      cliOptions.model = agent.model;
    }

    return this.streamMessages(prompt, cliOptions, useSessionId, onMessage);
  }

  /**
   * Stream messages from the claude CLI subprocess
   */
  private async *streamMessages(
    prompt: string,
    cliOptions: any,
    sessionId?: string,
    onMessage?: (message: SDKMessage) => void
  ): AsyncGenerator<SDKMessage> {
    let currentSessionId = sessionId;

    // Build CLI arguments
    const args: string[] = [
      '-p', prompt,
      '--output-format', 'stream-json',
      '--include-partial-messages',
      '--permission-mode', 'default',
    ];

    if (cliOptions.appendSystemPrompt) {
      args.push('--append-system-prompt', cliOptions.appendSystemPrompt);
    }

    if (cliOptions.allowedTools && cliOptions.allowedTools.length > 0) {
      args.push('--allowed-tools', ...cliOptions.allowedTools);
    }

    if (cliOptions.model) {
      args.push('--model', cliOptions.model);
    }

    if (cliOptions.resume) {
      args.push('-r', cliOptions.resume);
    }

    // Spawn the claude CLI process
    const processId = randomUUID();
    const child = spawn('claude', args, {
      cwd: cliOptions.cwd || process.cwd(),
      stdio: ['pipe', 'pipe', 'pipe'],
      env: { ...process.env },
    });

    this.activeProcesses.set(processId, child);

    // Wire up abort support
    let abortHandler: (() => void) | null = null;
    if (cliOptions.abortController) {
      abortHandler = () => {
        child.kill('SIGTERM');
        setTimeout(() => {
          if (!child.killed) child.kill('SIGKILL');
        }, 2000);
      };
      cliOptions.abortController.signal.addEventListener('abort', abortHandler, { once: true });
    }

    try {
      // Parse newline-delimited JSON from stdout
      const rl = createInterface({ input: child.stdout! });

      // Collect stderr for error reporting
      let stderrData = '';
      child.stderr?.on('data', (chunk: Buffer) => {
        stderrData += chunk.toString();
      });

      for await (const line of rl) {
        if (!line.trim()) continue;

        let message: SDKMessage;
        try {
          message = JSON.parse(line);
        } catch {
          // Skip non-JSON lines (debug output, etc.)
          continue;
        }

        // Extract session ID from init message
        if (message.type === 'system' && message.subtype === 'init') {
          currentSessionId = message.session_id;

          if (currentSessionId) {
            this.sessionStore.createSession(currentSessionId, {
              id: currentSessionId,
              agentName: cliOptions.appendSystemPrompt ? 'custom' : 'default',
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

        if (onMessage) {
          onMessage(message);
        }

        yield message;
      }

      // Wait for process to fully exit
      await new Promise<void>((resolve) => {
        if (child.exitCode !== null) {
          resolve();
          return;
        }
        child.on('close', (code) => {
          if (code !== 0 && !cliOptions.abortController?.signal.aborted && stderrData.trim()) {
            console.error(`Claude CLI exited with code ${code}: ${stderrData.slice(0, 500)}`);
          }
          resolve();
        });
      });

    } catch (error: any) {
      const isAbortError =
        cliOptions.abortController?.signal.aborted ||
        error.message?.includes('abort') ||
        error.message?.includes('cancelled') ||
        error.message?.includes('interrupted');

      if (isAbortError) {
        yield {
          type: 'interrupt_result',
          subtype: 'user_interrupted',
          session_id: sessionId || currentSessionId,
          result: 'Operation interrupted by user',
          message: {
            reason: 'User requested interruption',
            timestamp: Date.now()
          }
        };
      } else {
        yield {
          type: 'error',
          subtype: 'cli_error',
          session_id: sessionId,
          result: error.message || 'Unknown CLI error',
          message: {
            error: error.message,
            stack: error.stack
          }
        };
      }
    } finally {
      this.activeProcesses.delete(processId);
      // Clean up abort listener
      if (abortHandler && cliOptions.abortController) {
        cliOptions.abortController.signal.removeEventListener('abort', abortHandler);
      }
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
