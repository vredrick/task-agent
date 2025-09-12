"use strict";
/**
 * OAuth authentication module
 * Reads Claude OAuth credentials from ~/.claude/.credentials.json
 * Uses Claude subscription authentication (no API keys)
 * Matches Python backend authentication behavior
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.oauthManager = exports.OAuthManager = void 0;
const fs_1 = require("fs");
const path_1 = __importDefault(require("path"));
const os_1 = __importDefault(require("os"));
class OAuthManager {
    credentialsPath;
    alternativePath;
    credentials = null;
    constructor() {
        // Primary path: user home directory
        this.credentialsPath = path_1.default.join(os_1.default.homedir(), '.claude', '.credentials.json');
        // Alternative path: task-agent user (matches Python backend)
        this.alternativePath = '/home/task-agent/.claude/.credentials.json';
    }
    /**
     * Read OAuth credentials from filesystem
     */
    async readCredentials() {
        try {
            // Try primary path first
            let credPath = this.credentialsPath;
            try {
                await fs_1.promises.access(credPath);
            }
            catch {
                // Try alternative path
                credPath = this.alternativePath;
                await fs_1.promises.access(credPath);
            }
            const content = await fs_1.promises.readFile(credPath, 'utf-8');
            return JSON.parse(content);
        }
        catch (error) {
            console.error('Failed to read OAuth credentials:', error);
            return null;
        }
    }
    /**
     * Load and cache credentials
     */
    async loadCredentials() {
        this.credentials = await this.readCredentials();
        return this.credentials !== null && this.credentials.claudeAiOauth !== undefined;
    }
    /**
     * Get authentication status
     */
    async getAuthStatus() {
        try {
            const hasCredentials = await this.loadCredentials();
            if (hasCredentials && this.credentials?.claudeAiOauth) {
                const oauth = this.credentials.claudeAiOauth;
                // Check if token is expired
                const expiresAt = new Date(oauth.expiresAt);
                const isExpired = expiresAt < new Date();
                if (isExpired) {
                    return {
                        authenticated: false,
                        subscription_type: undefined,
                        message: 'OAuth token expired'
                    };
                }
                return {
                    authenticated: true,
                    subscription_type: oauth.subscriptionType || 'unknown',
                    message: 'Claude authenticated'
                };
            }
            return {
                authenticated: false,
                subscription_type: undefined,
                message: 'No OAuth credentials found'
            };
        }
        catch (error) {
            console.error('Error checking auth status:', error);
            return {
                authenticated: false,
                subscription_type: undefined,
                message: `Error checking authentication: ${error instanceof Error ? error.message : String(error)}`
            };
        }
    }
    /**
     * Get OAuth credentials for SDK initialization
     */
    getCredentials() {
        return this.credentials;
    }
    /**
     * Get access token for SDK
     */
    getAccessToken() {
        return this.credentials?.claudeAiOauth?.accessToken || null;
    }
    /**
     * Get refresh token for SDK
     */
    getRefreshToken() {
        return this.credentials?.claudeAiOauth?.refreshToken || null;
    }
}
exports.OAuthManager = OAuthManager;
// Export singleton instance
exports.oauthManager = new OAuthManager();
//# sourceMappingURL=oauth_handler.js.map