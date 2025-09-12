"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.SDKExecutor = void 0;
const claude_code_1 = require("@anthropic-ai/claude-code");
const session_store_1 = require("./session_store");
const path = __importStar(require("path"));
const os = __importStar(require("os"));
class SDKExecutor {
    sessionStore;
    credentialsPath;
    constructor() {
        this.sessionStore = new session_store_1.SessionStore();
        this.credentialsPath = path.join(os.homedir(), '.claude', '.credentials.json');
    }
    /**
     * Execute an agent with the given prompt
     */
    async executeAgent(agent, prompt, options = {}) {
        const { sessionId, sessionReset = false, maxTurns, includePartialMessages = true, abortController = new AbortController(), onMessage } = options;
        // Handle session management
        let useSessionId = sessionId;
        if (sessionReset && sessionId) {
            // Reset session if requested
            this.sessionStore.deleteSession(sessionId);
            useSessionId = undefined;
        }
        // Prepare SDK options
        const sdkOptions = {
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
    async *streamMessages(prompt, sdkOptions, sessionId, onMessage) {
        try {
            let currentSessionId = sessionId;
            let hasInitMessage = false;
            // Call the SDK query function
            for await (const message of (0, claude_code_1.query)({ prompt, options: sdkOptions })) {
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
        }
        catch (error) {
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
    getAvailableSessions() {
        return this.sessionStore.getAllSessions();
    }
    /**
     * Clear a specific session
     */
    clearSession(sessionId) {
        return this.sessionStore.deleteSession(sessionId);
    }
    /**
     * Clear all sessions
     */
    clearAllSessions() {
        this.sessionStore.clearAll();
    }
}
exports.SDKExecutor = SDKExecutor;
//# sourceMappingURL=sdk_executor.js.map