/**
 * OAuth authentication module
 * Reads Claude OAuth credentials from ~/.claude/.credentials.json
 * Uses Claude subscription authentication (no API keys)
 * Matches Python backend authentication behavior
 */

import { promises as fs } from 'fs';
import path from 'path';
import os from 'os';

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
  subscription_type?: string;  // Match Python backend naming
  message: string;
}

export class OAuthManager {
  private credentialsPath: string;
  private alternativePath: string;
  private credentials: ClaudeOAuthCredentials | null = null;

  constructor() {
    // Primary path: user home directory
    this.credentialsPath = path.join(os.homedir(), '.claude', '.credentials.json');
    // Alternative path: task-agent user (matches Python backend)
    this.alternativePath = '/home/task-agent/.claude/.credentials.json';
  }

  /**
   * Read OAuth credentials from filesystem
   */
  private async readCredentials(): Promise<ClaudeOAuthCredentials | null> {
    try {
      // Try primary path first
      let credPath = this.credentialsPath;
      
      try {
        await fs.access(credPath);
      } catch {
        // Try alternative path
        credPath = this.alternativePath;
        await fs.access(credPath);
      }

      const content = await fs.readFile(credPath, 'utf-8');
      return JSON.parse(content) as ClaudeOAuthCredentials;
    } catch (error) {
      console.error('Failed to read OAuth credentials:', error);
      return null;
    }
  }

  /**
   * Load and cache credentials
   */
  async loadCredentials(): Promise<boolean> {
    this.credentials = await this.readCredentials();
    return this.credentials !== null && this.credentials.claudeAiOauth !== undefined;
  }

  /**
   * Get authentication status
   */
  async getAuthStatus(): Promise<AuthStatus> {
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
    } catch (error) {
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
  getCredentials(): ClaudeOAuthCredentials | null {
    return this.credentials;
  }

  /**
   * Get access token for SDK
   */
  getAccessToken(): string | null {
    return this.credentials?.claudeAiOauth?.accessToken || null;
  }

  /**
   * Get refresh token for SDK
   */
  getRefreshToken(): string | null {
    return this.credentials?.claudeAiOauth?.refreshToken || null;
  }
}

// Export singleton instance
export const oauthManager = new OAuthManager();