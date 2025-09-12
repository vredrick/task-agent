/**
 * OAuth authentication module
 * Reads Claude OAuth credentials from ~/.claude/.credentials.json
 * Uses Claude subscription authentication (no API keys)
 * Matches Python backend authentication behavior
 */
export interface ClaudeOAuthCredentials {
    claudeAiOauth?: {
        accessToken: string;
        refreshToken: string;
        expiresAt: string;
        subscriptionType?: string;
        [key: string]: any;
    };
}
export interface AuthStatus {
    authenticated: boolean;
    subscription_type?: string;
    message: string;
}
export declare class OAuthManager {
    private credentialsPath;
    private alternativePath;
    private credentials;
    constructor();
    /**
     * Read OAuth credentials from filesystem
     */
    private readCredentials;
    /**
     * Load and cache credentials
     */
    loadCredentials(): Promise<boolean>;
    /**
     * Get authentication status
     */
    getAuthStatus(): Promise<AuthStatus>;
    /**
     * Get OAuth credentials for SDK initialization
     */
    getCredentials(): ClaudeOAuthCredentials | null;
    /**
     * Get access token for SDK
     */
    getAccessToken(): string | null;
    /**
     * Get refresh token for SDK
     */
    getRefreshToken(): string | null;
}
export declare const oauthManager: OAuthManager;
//# sourceMappingURL=oauth_handler.d.ts.map