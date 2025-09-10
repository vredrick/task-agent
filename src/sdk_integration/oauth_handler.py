"""OAuth Authentication Handler for Claude SDK.

This module centralizes how we force OAuth (Claude cloud subscription)
authentication when using the SDK. It deliberately avoids API-key-based
auth by masking relevant environment variables when requested.

Behavior highlights:
- Prefer OAuth credentials from `~/.claude/.credentials.json` (or an override)
- Provide a context manager to temporarily suppress API key vars
- Offer helpers to validate credentials availability before SDK use
"""

import os
import logging
from typing import Optional, List
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class OAuthHandler:
    """Handles OAuth authentication for Claude SDK.
    
    This class manages the OAuth authentication process, ensuring proper
    credential handling for subscription-based Claude access.
    """
    
    @staticmethod
    def prepare_oauth_environment() -> None:
        """Prepare process env to favor OAuth over API keys.

        Masks common Anthropic API key environment variables so the SDK/CLI
        will fall back to OAuth credentials stored by Claude Code.
        """
        removed: List[str] = []
        for var in ("ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY_FILE", "ANTHROPIC_API_KEY_PATH"):
            if var in os.environ:
                removed.append(var)
                del os.environ[var]
        if removed:
            logger.info(
                "Masked API key env to force OAuth: %s",
                ", ".join(removed),
            )
    
    @staticmethod
    def get_credentials_path() -> str:
        """Primary OAuth credentials path.

        If `CLAUDE_CREDENTIALS_PATH` is set, return that; otherwise use the
        default `~/.claude/.credentials.json`.
        """
        override = os.environ.get("CLAUDE_CREDENTIALS_PATH")
        if override:
            return override
        return os.path.expanduser("~/.claude/.credentials.json")

    @staticmethod
    def get_candidate_credentials_paths() -> List[str]:
        """All candidate locations for OAuth credentials, in priority order."""
        candidates: List[str] = []
        # Highest priority: explicit override
        if os.environ.get("CLAUDE_CREDENTIALS_PATH"):
            candidates.append(os.environ["CLAUDE_CREDENTIALS_PATH"])
        # User default
        candidates.append(os.path.expanduser("~/.claude/.credentials.json"))
        # Common alternate (documented in codebase docs)
        candidates.append("/home/task-agent/.claude/.credentials.json")
        return candidates
    
    @staticmethod
    def check_credentials_exist() -> bool:
        """Check if any candidate OAuth credentials file exists."""
        for path in OAuthHandler.get_candidate_credentials_paths():
            if os.path.exists(path):
                logger.debug(f"OAuth credentials found at: {path}")
                return True
        logger.warning(
            "OAuth credentials not found. Searched: %s",
            ", ".join(OAuthHandler.get_candidate_credentials_paths()),
        )
        return False
    
    @staticmethod
    def ensure_oauth_ready() -> None:
        """Ensure OAuth environment is ready for SDK usage.
        
        This is the main entry point for OAuth preparation.
        Call this before any SDK operations.
        
        Raises:
            RuntimeError: If credentials are not available
        """
        # First, prepare the environment (mask API key vars)
        OAuthHandler.prepare_oauth_environment()
        
        # Then check if credentials exist
        if not OAuthHandler.check_credentials_exist():
            raise RuntimeError(
                "OAuth credentials not found. Ensure a credentials file exists at one of: "
                f"{OAuthHandler.get_candidate_credentials_paths()}. "
                "Run 'claude login' to authenticate with Claude Code."
            )
        
        logger.info("OAuth environment prepared successfully")

    @staticmethod
    @contextmanager
    def oauth_only_env():
        """Temporarily force OAuth by masking API key env during a block.

        Restores original values after use to avoid side effects.
        Example:
            with OAuthHandler.oauth_only_env():
                ...  # call SDK/CLI that should use OAuth
        """
        saved = {}
        key_vars = ("ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY_FILE", "ANTHROPIC_API_KEY_PATH")
        try:
            for var in key_vars:
                if var in os.environ:
                    saved[var] = os.environ[var]
                    del os.environ[var]
            if saved:
                logger.debug("Temporarily masked API key env: %s", ", ".join(saved.keys()))
            yield
        finally:
            # Restore any previous values
            for var, val in saved.items():
                os.environ[var] = val
            if saved:
                logger.debug("Restored API key env after OAuth-only block")


# Singleton instance for convenience
_oauth_handler = OAuthHandler()

def ensure_oauth_ready() -> None:
    """Convenience function to ensure OAuth is ready.
    
    This is a module-level function that uses the singleton instance.
    """
    _oauth_handler.ensure_oauth_ready()

def prepare_oauth_environment() -> None:
    """Convenience function to prepare OAuth environment.
    
    This is a module-level function that uses the singleton instance.
    """
    _oauth_handler.prepare_oauth_environment()

@contextmanager
def oauth_only_env():
    """Module-level context manager to temporarily force OAuth-only auth."""
    with _oauth_handler.oauth_only_env():
        yield
