"""SDK Integration module for direct agent execution.

This module provides direct SDK-based execution of agents without going through
the MCP server, primarily for web UI integration.
"""

from .sdk_executor import SDKExecutor, get_sdk_executor

__all__ = ['SDKExecutor', 'get_sdk_executor']