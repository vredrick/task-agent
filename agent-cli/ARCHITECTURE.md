# Agent CLI Architecture

## Overview

The Agent CLI system provides direct terminal access to task agents by generating executable shell scripts that wrap Claude CLI commands. This bypasses the MCP server while maintaining identical functionality.

## Directory Structure

```
agent-cli/
├── __init__.py           # Package initialization
├── cli.py               # Main CLI entry point (future expansion)
├── alias_generator.py   # Core alias generation logic
├── README.md           # User documentation
├── ARCHITECTURE.md     # This file
└── examples/           # Example configurations (future)
```

## Core Components

### 1. AliasGenerator (`alias_generator.py`)

**Purpose**: Generates executable shell scripts for each agent

**Key Methods**:
- `generate_alias_script()` - Creates individual agent script
- `generate_all_aliases()` - Processes all agents 
- `generate_installer_script()` - Creates installation script
- `_find_claude_path()` - Locates Claude CLI executable

**Template Structure**:
```bash
#!/bin/bash
# Static configuration (paths, agent file)
# Input validation
# Claude CLI path verification
# Dynamic config loading (Python embedded)
# Working directory resolution
# Claude command construction
# Session management (if enabled)
# Command execution with stream-json
# JSON parsing and output formatting
# Cleanup
```

### 2. CLI Interface (`cli.py`)

**Purpose**: Extensible command-line interface for agent management

**Current Commands**:
- `generate` - Generate aliases for all agents
- `list` - List available agents (placeholder)
- `install` - Install specific agent (placeholder)

**Design for Expansion**:
- Subcommand architecture using argparse
- Modular command handlers
- Consistent error handling and logging

## Data Flow

### Alias Generation Process

```
1. AgentManager loads .md files → Agent configurations
2. AliasGenerator processes each agent:
   a. Build shell script template
   b. Embed Python code for config parsing  
   c. Apply variable substitution
   d. Write executable script
3. Generate installer script
4. Auto-install to ~/.local/bin (optional)
```

### Runtime Execution Process

```
1. User runs: example-agent "query"
2. Shell script executes:
   a. Validate input arguments
   b. Find Claude CLI path
   c. Parse agent .md file (Python)
   d. Extract: name, tools, model, system prompt
   e. Resolve working directory
   f. Build Claude command array
   g. Handle session resumption (if enabled)
   h. Execute Claude CLI with stream-json
   i. Parse JSON output stream
   j. Format and display results
   k. Cleanup temp files
```

## Key Design Decisions

### 1. Dynamic Config Loading
- **Decision**: Parse .md files on each execution
- **Rationale**: Ensures aliases always use latest agent configuration
- **Trade-off**: Slight startup overhead vs. always-current config

### 2. Embedded Python Parser
- **Decision**: Embed Python YAML parser in shell script
- **Rationale**: Reuse existing parsing logic, handle complex frontmatter
- **Alternative**: Pure shell parsing (rejected due to complexity)

### 3. String Replacement vs Format()
- **Decision**: Use .replace() instead of .format()
- **Rationale**: Avoid conflicts with shell variable braces
- **Lesson**: Template engines must account for target language syntax

### 4. Session Management
- **Decision**: Store sessions in /tmp/task_agents_sessions.json
- **Rationale**: Match MCP server behavior exactly
- **Feature**: Support --reset flag for fresh sessions

## Extension Points

### New Commands
Add to `cli.py` subparsers:
```python
# Example: agent-cli watch
watch_parser = subparsers.add_parser("watch", help="Watch for agent changes")
```

### Custom Formatters
Extend output processing:
- JSON formatters
- Markdown renderers  
- Interactive displays

### Agent Discovery
Enhanced agent management:
- Recursive directory scanning
- Agent validation
- Dependency checking

### Configuration Management
Global and per-agent settings:
- Default models/tools
- Output preferences
- Custom working directories

## Technical Challenges Solved

### 1. Shell Variable Escaping
- **Problem**: Shell variables `${VAR}` conflicted with Python .format() placeholders
- **Solution**: Use .replace() and escape braces with double braces `${{VAR}}`

### 2. Python String Embedding
- **Problem**: Multi-line Python code in shell heredoc with quote escaping
- **Solution**: Use single quotes for heredoc, pass variables as arguments

### 3. Template Variable Substitution  
- **Problem**: .format() trying to interpret shell syntax as format placeholders
- **Solution**: Switch to string .replace() with explicit variable names

### 4. Working Directory Resolution
- **Problem**: Agent `cwd: "."` should resolve to project directory
- **Solution**: Resolve relative to grandparent of task-agents directory

## Future Architecture Considerations

### Plugin System
- Modular command plugins
- Third-party extensions
- Configuration-driven features

### Performance Optimization
- Agent config caching
- Parallel alias generation
- Lazy loading for large agent sets

### Cross-Platform Support
- Windows PowerShell scripts
- Fish/Zsh shell compatibility
- Package manager integration

### Integration Points
- IDE extensions
- CI/CD pipeline integration
- Monitoring and metrics collection