"""OAuth Authentication Handler for Claude SDK.

IMPORTANT: This module handles OAuth authentication for the Claude SDK.
DO NOT MODIFY this file unless you specifically need to change OAuth behavior.
This separation ensures authentication logic remains stable and protected.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class OAuthHandler:
    """Handles OAuth authentication for Claude SDK.
    
    This class manages the OAuth authentication process, ensuring proper
    credential handling for subscription-based Claude access.
    """
    
    @staticmethod
    def prepare_oauth_environment() -> None:
        """Prepare environment for OAuth authentication.
        
        CRITICAL: This removes ANTHROPIC_API_KEY to force OAuth subscription
        authentication. The SDK will automatically use ~/.claude/.credentials.json
        for authentication when API key is not present.
        
        DO NOT MODIFY this behavior without understanding the implications.
        """
        if 'ANTHROPIC_API_KEY' in os.environ:
            logger.info("Removing ANTHROPIC_API_KEY to force OAuth subscription authentication")
            del os.environ['ANTHROPIC_API_KEY']  # Force OAuth fallback
    
    @staticmethod
    def get_credentials_path() -> str:
        """Get the path to OAuth credentials file.
        
        Returns:
            str: Path to the credentials file (~/.claude/.credentials.json)
        """
        return os.path.expanduser("~/.claude/.credentials.json")
    
    @staticmethod
    def check_credentials_exist() -> bool:
        """Check if OAuth credentials file exists.
        
        Returns:
            bool: True if credentials file exists, False otherwise
        """
        creds_path = OAuthHandler.get_credentials_path()
        exists = os.path.exists(creds_path)
        if exists:
            logger.debug(f"OAuth credentials found at: {creds_path}")
        else:
            logger.warning(f"OAuth credentials not found at: {creds_path}")
        return exists
    
    @staticmethod
    def ensure_oauth_ready() -> None:
        """Ensure OAuth environment is ready for SDK usage.
        
        This is the main entry point for OAuth preparation.
        Call this before any SDK operations.
        
        Raises:
            RuntimeError: If credentials are not available
        """
        # First, prepare the environment
        OAuthHandler.prepare_oauth_environment()
        
        # Then check if credentials exist
        if not OAuthHandler.check_credentials_exist():
            raise RuntimeError(
                "OAuth credentials not found. Please ensure ~/.claude/.credentials.json exists. "
                "Run 'claude login' to authenticate if needed."
            )
        
        logger.info("OAuth environment prepared successfully")


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