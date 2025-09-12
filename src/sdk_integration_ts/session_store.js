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
exports.SessionStore = void 0;
const fs = __importStar(require("fs"));
class SessionStore {
    sessions;
    storePath;
    constructor() {
        this.sessions = new Map();
        this.storePath = '/tmp/task_agents_sessions_ts.json';
        this.loadSessions();
    }
    /**
     * Load sessions from disk
     */
    loadSessions() {
        try {
            if (fs.existsSync(this.storePath)) {
                const data = fs.readFileSync(this.storePath, 'utf-8');
                const sessionData = JSON.parse(data);
                // Convert to Map
                Object.entries(sessionData).forEach(([id, session]) => {
                    this.sessions.set(id, session);
                });
            }
        }
        catch (error) {
            console.error('Error loading sessions:', error);
            this.sessions = new Map();
        }
    }
    /**
     * Save sessions to disk
     */
    saveSessions() {
        try {
            const sessionData = {};
            this.sessions.forEach((session, id) => {
                sessionData[id] = session;
            });
            fs.writeFileSync(this.storePath, JSON.stringify(sessionData, null, 2));
        }
        catch (error) {
            console.error('Error saving sessions:', error);
        }
    }
    /**
     * Create a new session
     */
    createSession(id, session) {
        this.sessions.set(id, session);
        this.saveSessions();
    }
    /**
     * Get a session by ID
     */
    getSession(id) {
        return this.sessions.get(id);
    }
    /**
     * Update a session
     */
    updateSession(id, session) {
        this.sessions.set(id, session);
        this.saveSessions();
    }
    /**
     * Delete a session
     */
    deleteSession(id) {
        const deleted = this.sessions.delete(id);
        if (deleted) {
            this.saveSessions();
        }
        return deleted;
    }
    /**
     * Get all sessions
     */
    getAllSessions() {
        return Array.from(this.sessions.values());
    }
    /**
     * Clear all sessions
     */
    clearAll() {
        this.sessions.clear();
        this.saveSessions();
    }
    /**
     * Clean up old sessions (older than 24 hours)
     */
    cleanupOldSessions() {
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
exports.SessionStore = SessionStore;
//# sourceMappingURL=session_store.js.map