export interface Session {
    id: string;
    agentName: string;
    createdAt: number;
    lastUsed: number;
    turnCount: number;
}
export declare class SessionStore {
    private sessions;
    private storePath;
    constructor();
    /**
     * Load sessions from disk
     */
    private loadSessions;
    /**
     * Save sessions to disk
     */
    private saveSessions;
    /**
     * Create a new session
     */
    createSession(id: string, session: Session): void;
    /**
     * Get a session by ID
     */
    getSession(id: string): Session | undefined;
    /**
     * Update a session
     */
    updateSession(id: string, session: Session): void;
    /**
     * Delete a session
     */
    deleteSession(id: string): boolean;
    /**
     * Get all sessions
     */
    getAllSessions(): Session[];
    /**
     * Clear all sessions
     */
    clearAll(): void;
    /**
     * Clean up old sessions (older than 24 hours)
     */
    cleanupOldSessions(): void;
}
//# sourceMappingURL=session_store.d.ts.map