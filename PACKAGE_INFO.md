# Package Information

## PyPI Package Details

### Package Name
- **Name**: task-agents-mcp
- **Version**: 2.0.0
- **Command**: `task-agent`
- **PyPI**: https://pypi.org/project/task-agents-mcp/

## Installation

### From PyPI
```bash
# Install with pip
pip install task-agents-mcp

# Install with uvx
uvx task-agents-mcp
```

### From Source (current)
```bash
# Clone the repository
git clone https://github.com/vredrick/task-agent.git
cd task-agent

# Install in development mode
pip install -e .

# Or build and install
python -m build
pip install dist/task_agents_mcp-2.0.0-py3-none-any.whl
```

## Usage

### With Claude Desktop
```json
{
  "mcpServers": {
    "task-agent": {
      "command": "task-agent"
    }
  }
}
```

### With Claude Code CLI
```bash
claude mcp add task-agent -s project -- task-agent
```

## Built Packages

The following packages are available in the `dist/` directory:
- `task_agents_mcp-2.0.0-py3-none-any.whl` - Wheel distribution
- `task_agents_mcp-2.0.0.tar.gz` - Source distribution

## Publishing to PyPI

### Prerequisites
1. PyPI account with API token
2. Token saved in `.pypirc_token` or environment variable

### Publish Command
```bash
python -m twine upload dist/*
```

### Automated Publishing
```bash
python scripts/publish_pypi.py --bump patch
```

## Package Contents

- **Entry Point**: `task-agent` command
- **Main Module**: `task_agents_mcp`
- **Server**: Multi-tool MCP server
- **Agents**: 6 pre-configured agents
- **Tools**: Each agent exposed as individual tool

## Dependencies

- `fastmcp>=2.0.0`
- `pyyaml>=6.0.0`
- Python 3.9+

## Architecture

This package implements the multi-tool architecture where each AI agent is exposed as its own MCP tool:
- `code_reviewer`
- `debugger`
- `default_assistant`
- `documentation_writer`
- `performance_optimizer`
- `test_runner`

## Repository

- **GitHub**: https://github.com/vredrick/task-agent (Private)
- **Issues**: https://github.com/vredrick/task-agent/issues