"""
Session Chain Store for Task-Agents MCP Server

Manages session ID chaining for resume functionality.
Each resume creates a new session ID that must be tracked.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass, field, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class SessionChain:
    """Represents a chain of session IDs for an agent."""
    current_session_id: str
    exchange_count: int = 1
    previous_sessions: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


class SessionChainStore:
    """Manages session chains for agents with resume support."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize the session store.
        
        Args:
            storage_path: Optional path to persist session data. 
                         If None, uses in-memory storage only.
        """
        self.storage_path = storage_path
        self.chains: Dict[str, SessionChain] = {}
        
        # Load existing chains if storage path exists
        if self.storage_path and self.storage_path.exists():
            self._load_chains()
    
    def get_resume_session(self, agent_name: str, max_exchanges: int) -> Optional[str]:
        """Get the session ID to resume for an agent.
        
        Args:
            agent_name: Name of the agent
            max_exchanges: Maximum exchanges before starting fresh
            
        Returns:
            Session ID to resume with -r flag, or None to start fresh
        """
        if agent_name not in self.chains:
            logger.info(f"No existing session chain for {agent_name}")
            return None
            
        chain = self.chains[agent_name]
        
        # Check if we've exceeded max exchanges
        if chain.exchange_count >= max_exchanges:
            logger.info(f"Session chain for {agent_name} exceeded max exchanges ({chain.exchange_count} >= {max_exchanges})")
            # Archive the old chain
            chain.previous_sessions.append(chain.current_session_id)
            del self.chains[agent_name]
            self._save_chains()
            return None
            
        # Return the current session ID to resume
        logger.info(f"Resuming session for {agent_name}: {chain.current_session_id} (exchange {chain.exchange_count + 1}/{max_exchanges})")
        return chain.current_session_id
    
    def update_chain(self, agent_name: str, new_session_id: str, was_resume: bool = False):
        """Update the session chain with a new session ID.
        
        Args:
            agent_name: Name of the agent
            new_session_id: The NEW session ID from this execution
            was_resume: Whether this was a resumed session
        """
        if was_resume and agent_name in self.chains:
            # This was a resume, update the chain
            chain = self.chains[agent_name]
            # Move current to previous
            chain.previous_sessions.append(chain.current_session_id)
            # Update to new session
            chain.current_session_id = new_session_id
            chain.exchange_count += 1
            chain.last_updated = datetime.now().isoformat()
            logger.info(f"Updated session chain for {agent_name}: {new_session_id} (exchange {chain.exchange_count})")
        else:
            # New chain or fresh start
            self.chains[agent_name] = SessionChain(
                current_session_id=new_session_id,
                exchange_count=1
            )
            logger.info(f"Created new session chain for {agent_name}: {new_session_id}")
        
        # Persist changes
        self._save_chains()
    
    def clear_chain(self, agent_name: str):
        """Clear the session chain for an agent."""
        if agent_name in self.chains:
            del self.chains[agent_name]
            self._save_chains()
            logger.info(f"Cleared session chain for {agent_name}")
    
    def get_chain_info(self, agent_name: str) -> Optional[Dict]:
        """Get information about an agent's session chain."""
        if agent_name not in self.chains:
            return None
            
        chain = self.chains[agent_name]
        return {
            "current_session": chain.current_session_id,
            "exchange_count": chain.exchange_count,
            "previous_sessions": len(chain.previous_sessions),
            "created_at": chain.created_at,
            "last_updated": chain.last_updated
        }
    
    def _load_chains(self):
        """Load session chains from storage."""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                for agent_name, chain_data in data.items():
                    self.chains[agent_name] = SessionChain(**chain_data)
            logger.info(f"Loaded {len(self.chains)} session chains from {self.storage_path}")
        except Exception as e:
            logger.error(f"Failed to load session chains: {e}")
    
    def _save_chains(self):
        """Save session chains to storage."""
        if not self.storage_path:
            return
            
        try:
            # Ensure directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert chains to dict
            data = {
                agent_name: asdict(chain)
                for agent_name, chain in self.chains.items()
            }
            
            # Write to file
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.debug(f"Saved {len(self.chains)} session chains to {self.storage_path}")
        except Exception as e:
            logger.error(f"Failed to save session chains: {e}")