/**
 * SDK Integration Layer for TypeScript
 * Provides direct agent execution using Claude Code SDK
 * Shared by Web UI, MCP server, and other consumers
 */

// Export authentication components (matches Python oauth_handler.py)
export { oauthManager, OAuthManager, AuthStatus, ClaudeOAuthCredentials } from './oauth_handler';

// Export agent management components (matches Python agent_manager.py)
export { AgentManager } from './agent_manager';
export * from './types/agent';

// Export SDK executor components (matches Python sdk_executor.py)
export { SDKExecutor } from './sdk_executor';
export type { SDKMessage, ExecutionOptions } from './sdk_executor';

// Export session store (matches Python session handling)
export { SessionStore } from './session_store';
export type { Session } from './session_store';