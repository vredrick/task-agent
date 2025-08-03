# FastMCP Framework Overview

> **Source**: https://github.com/jlowin/fastmcp  
> **Fetched**: August 1, 2025  
> **Description**: A Python framework for building Model Context Protocol (MCP) servers and clients

## Introduction

FastMCP is a Python framework designed to be "fast, simple, and Pythonic" for building Model Context Protocol (MCP) servers and clients. It provides a high-level interface for creating servers that expose tools, resources, and prompts to AI applications.

## Installation

```bash
uv pip install fastmcp
```

## Core Concepts

### 1. Server Creation

Create a server using the `FastMCP` class:

```python
from fastmcp import FastMCP

mcp = FastMCP("My Assistant Server")
```

### 2. Basic Server Example

```python
from fastmcp import FastMCP

mcp = FastMCP("Demo 🚀")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

if __name__ == "__main__":
    mcp.run()
```

## Key Components

### Tools
Server-side functions that LLMs can call:
- Use `@mcp.tool` decorator
- Support automatic schema generation from type hints and docstrings
- Enable direct function execution by AI models

```python
@mcp.tool
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers."""
    return a * b
```

### Resources
Expose read-only data sources:
- Use `@mcp.resource()` decorator
- Support dynamic URI templates
- Provide structured data access

```python
@mcp.resource("users://{user_id}/profile")
def get_profile(user_id: int):
    return {"name": f"User {user_id}", "status": "active"}
```

### Prompts
Define reusable message templates:
- Use `@mcp.prompt` decorator
- Create structured LLM interaction patterns
- Enable consistent prompt management

```python
@mcp.prompt
def summarize_request(text: str) -> str:
    return f"Please summarize the following text:\n\n{text}"
```

### Context
Access session capabilities within tools and resources:
- Provides logging methods
- Enables LLM sampling
- Supports HTTP requests
- Manages resource reading

```python
@mcp.tool
async def process_data(uri: str, ctx: Context):
    await ctx.info(f"Processing {uri}...")
    data = await ctx.read_resource(uri)
    summary = await ctx.sample(f"Summarize: {data.content[:500]}")
    return summary.text
```

## Transport Protocols

FastMCP supports multiple transport protocols:

### STDIO (Default)
- Standard input/output communication
- Ideal for command-line integration
- Default transport method

### HTTP
- RESTful API endpoints
- Web-based integrations
- Network-accessible servers

### Server-Sent Events (SSE)
- Real-time streaming communication
- Event-driven architectures
- Live data updates

## Advanced Features

### Server Composition
- Combine multiple servers
- Modular architecture support
- Scalable server design

### Authentication Support
- Secure server access
- User authentication patterns
- Permission management

### Proxy Servers
- Load balancing capabilities
- Request routing
- Distributed architectures

### OpenAPI/FastAPI Generation
- Automatic API documentation
- REST API compatibility
- Standard web service patterns

## Running Servers

### Basic Execution
```python
if __name__ == "__main__":
    mcp.run()
```

### Transport Configuration
```python
# STDIO (default)
mcp.run()

# HTTP
mcp.run(transport="http", port=8000)

# SSE
mcp.run(transport="sse", port=8001)
```

## Schema Generation

FastMCP automatically generates schemas from:
- Function type hints
- Docstring descriptions
- Parameter annotations
- Return type specifications

This enables AI models to understand:
- Available function parameters
- Expected input types
- Function purposes and usage
- Return value structures

## Best Practices

### Tool Design
- Use clear, descriptive function names
- Provide comprehensive docstrings
- Include proper type hints
- Handle errors gracefully

### Resource Management
- Design logical URI patterns
- Implement efficient data access
- Cache frequently accessed data
- Handle resource not found cases

### Server Architecture
- Organize tools by functionality
- Implement proper logging
- Design for scalability
- Consider security implications

## Error Handling

FastMCP provides built-in error handling for:
- Invalid function parameters
- Resource access failures
- Transport communication errors
- Schema validation issues

## Integration Patterns

FastMCP is ideal for:
- AI-powered applications
- Standardized server interfaces
- Secure tool exposure
- Structured AI interactions
- Development workflow automation

## Next Steps

- Review [FastMCP Server Implementation](./fastmcp-server-implementation.md) for detailed patterns
- Explore [FastMCP Tools and Resources](./fastmcp-tools-resources.md) for advanced usage
- See [Building Claude Code MCP Wrapper](./claude-code-mcp-wrapper.md) for practical examples