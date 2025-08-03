#!/usr/bin/env python3
"""
Entry point for running task-agents-mcp as a module.
"""
from .server import mcp

if __name__ == "__main__":
    mcp.run()