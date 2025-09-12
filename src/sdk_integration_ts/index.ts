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

// Future exports will include:
// - agent_executor.ts (matches Python agent_executor.py)
// - sdk_executor.ts (matches Python sdk_executor.py)
// - message_parser.ts (matches Python message_parser.py)