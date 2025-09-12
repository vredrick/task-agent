import * as fs from 'fs';
import * as path from 'path';

export interface Session {
  id: string;
  agentName: string;
  createdAt: number;
  lastUsed: number;
  turnCount: number;
}

export class SessionStore {
  private sessions: Map<string, Session>;
  private storePath: string;

  constructor() {
    this.sessions = new Map();
    this.storePath = '/tmp/task_agents_sessions_ts.json';
    this.loadSessions();
  }

  /**
   * Load sessions from disk
   */
  private loadSessions(): void {
    try {
      if (fs.existsSync(this.storePath)) {
        const data = fs.readFileSync(this.storePath, 'utf-8');
        const sessionData = JSON.parse(data);
        
        // Convert to Map
        Object.entries(sessionData).forEach(([id, session]) => {
          this.sessions.set(id, session as Session);
        });
      }
    } catch (error) {
      console.error('Error loading sessions:', error);
      this.sessions = new Map();
    }
  }

  /**
   * Save sessions to disk
   */
  private saveSessions(): void {
    try {
      const sessionData: Record<string, Session> = {};
      this.sessions.forEach((session, id) => {
        sessionData[id] = session;
      });
      
      fs.writeFileSync(this.storePath, JSON.stringify(sessionData, null, 2));
    } catch (error) {
      console.error('Error saving sessions:', error);
    }
  }

  /**
   * Create a new session
   */
  createSession(id: string, session: Session): void {
    this.sessions.set(id, session);
    this.saveSessions();
  }

  /**
   * Get a session by ID
   */
  getSession(id: string): Session | undefined {
    return this.sessions.get(id);
  }

  /**
   * Update a session
   */
  updateSession(id: string, session: Session): void {
    this.sessions.set(id, session);
    this.saveSessions();
  }

  /**
   * Delete a session
   */
  deleteSession(id: string): boolean {
    const deleted = this.sessions.delete(id);
    if (deleted) {
      this.saveSessions();
    }
    return deleted;
  }

  /**
   * Get all sessions
   */
  getAllSessions(): Session[] {
    return Array.from(this.sessions.values());
  }

  /**
   * Clear all sessions
   */
  clearAll(): void {
    this.sessions.clear();
    this.saveSessions();
  }

  /**
   * Clean up old sessions (older than 24 hours)
   */
  cleanupOldSessions(): void {
    const now = Date.now();
    const maxAge = 24 * 60 * 60 * 1000; // 24 hours
    
    let cleaned = false;
    this.sessions.forEach((session, id) => {
      if (now - session.lastUsed > maxAge) {
        this.sessions.delete(id);
        cleaned = true;
      }
    });
    
    if (cleaned) {
      this.saveSessions();
    }
  }
}