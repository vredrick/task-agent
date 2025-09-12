"use strict";
/**
 * SDK Integration Layer for TypeScript
 * Provides direct agent execution using Claude Code SDK
 * Shared by Web UI, MCP server, and other consumers
 */
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
var __exportStar = (this && this.__exportStar) || function(m, exports) {
    for (var p in m) if (p !== "default" && !Object.prototype.hasOwnProperty.call(exports, p)) __createBinding(exports, m, p);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.SessionStore = exports.SDKExecutor = exports.AgentManager = exports.OAuthManager = exports.oauthManager = void 0;
// Export authentication components (matches Python oauth_handler.py)
var oauth_handler_1 = require("./oauth_handler");
Object.defineProperty(exports, "oauthManager", { enumerable: true, get: function () { return oauth_handler_1.oauthManager; } });
Object.defineProperty(exports, "OAuthManager", { enumerable: true, get: function () { return oauth_handler_1.OAuthManager; } });
// Export agent management components (matches Python agent_manager.py)
var agent_manager_1 = require("./agent_manager");
Object.defineProperty(exports, "AgentManager", { enumerable: true, get: function () { return agent_manager_1.AgentManager; } });
__exportStar(require("./types/agent"), exports);
// Export SDK executor components (matches Python sdk_executor.py)
var sdk_executor_1 = require("./sdk_executor");
Object.defineProperty(exports, "SDKExecutor", { enumerable: true, get: function () { return sdk_executor_1.SDKExecutor; } });
// Export session store (matches Python session handling)
var session_store_1 = require("./session_store");
Object.defineProperty(exports, "SessionStore", { enumerable: true, get: function () { return session_store_1.SessionStore; } });
//# sourceMappingURL=index.js.map