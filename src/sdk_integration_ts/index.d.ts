/**
 * SDK Integration Layer for TypeScript
 * Provides direct agent execution using Claude Code SDK
 * Shared by Web UI, MCP server, and other consumers
 */
export { oauthManager, OAuthManager, AuthStatus, ClaudeOAuthCredentials } from './oauth_handler';
export { AgentManager } from './agent_manager';
export * from './types/agent';
export { SDKExecutor } from './sdk_executor';
export type { SDKMessage, ExecutionOptions } from './sdk_executor';
export { SessionStore } from './session_store';
export type { Session } from './session_store';
//# sourceMappingURL=index.d.ts.map