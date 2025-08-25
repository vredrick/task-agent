# CLAUDE.md - Agent CLI Module

## 🎯 Quick Context

You're working with the **agent-cli** module, a specialized component of the task-agent system that provides direct terminal access to agents through generated aliases and an interactive REPL interface.

### Key Architecture Points
- **Purpose**: Generate executable shell scripts for direct agent access
- **REPL Mode**: Interactive chat interface with session management
- **Direct Mode**: Single-query execution (like MCP server)
- **Integration**: Uses same SessionChainStore as MCP server
- **Dependencies**: Claude CLI, prompt-toolkit, PyYAML

## 📁 Module Structure

```
agent-cli/
├── CLAUDE.md               # This file - module documentation
├── README.md               # User-facing documentation  
├── ARCHITECTURE.md         # Technical deep-dive
└── agent_cli/              # Python package
    ├── __init__.py         # Package exports
    ├── alias_generator.py  # Core alias generation logic
    ├── repl.py            # Interactive REPL functionality
    └── cli.py             # CLI interface (expandable)
```

## 🔧 Key Technical Details

### Alias Generation Flow
```python
# alias_generator.py - Main workflow
for agent_config in agent_manager.agents.values():
    script_content, script_path = generate_alias_script(agent_config, output_dir)
    # Creates bash script with REPL + direct query support
```

### REPL Integration  
```python
# repl.py - REPL functionality
class AgentREPL:
    def __init__(self, agent_name, config):
        # Loads agent config and initializes prompt-toolkit interface
    
    def run(self):
        # Main REPL loop with colored output and session management
```

### Session Management
- **Shared storage**: `/tmp/task_agents_sessions.json`
- **SessionChainStore**: Same session logic as MCP server
- **Exchange counting**: Tracks conversation turns per session
- **Session isolation**: Each session has separate conversation history

## 📝 Common Development Tasks

### Adding REPL Features
The REPL module (`repl.py`) handles interactive functionality:
```python
# Key components to modify:
- AgentREPL.run(): Main interaction loop
- _execute_agent_query(): Query execution logic  
- _print_conversation_history(): History display
```

### Updating Alias Generation
The alias generator (`alias_generator.py`) creates bash scripts:
```python
# Key template sections:
- REPL mode (no arguments): Lines 99-190
- Direct mode (with arguments): Lines 192+
- String replacements: Lines 454-463
```

### Session Integration
Session logic integrates with MCP server:
```python
from task_agents_mcp.session_store import SessionChainStore
SESSION_STORE = SessionChainStore(Path("/tmp/task_agents_sessions.json"))
```

## 🐛 Common Issues & Fixes

### 1. "REPL module not found"
- **Cause**: Python path issues in generated aliases
- **Fix**: Check `{project_root}` replacement in alias template
- **Location**: `alias_generator.py:164`

### 2. Bash syntax errors in installer
- **Cause**: Double braces `{{` in bash template
- **Fix**: Use single braces `{SCRIPTS[@]}` 
- **Location**: `alias_generator.py:550`

### 3. JSON parsing issues in REPL
- **Cause**: Escaped quotes not handled properly
- **Fix**: Use `json.loads()` first, regex as fallback
- **Location**: `repl.py:398-431`

### 4. Session history showing wrong conversations
- **Cause**: Global vs session-specific storage
- **Fix**: Use session-based keys `session_{session_id}`
- **Location**: `repl.py:113-137`

## 🚀 Development Workflow

### Testing Changes
1. **Modify code** in `agent_cli/` directory
2. **Regenerate aliases**: `task-agent generate-aliases`
3. **Test REPL mode**: `code-reviewer` (no arguments)
4. **Test direct mode**: `code-reviewer "test query"`

### Debugging REPL Issues
```bash
# Manual REPL testing
python3 -c "
import sys
sys.path.insert(0, '/path/to/agent-cli')
from agent_cli.repl import start_repl
start_repl('Test Agent', {'agent_name': 'Test', 'model': 'haiku'})
"
```

### Adding New REPL Features
1. **Modify**: `repl.py` - Add feature logic
2. **Update**: `README.md` - Document new feature
3. **Test**: Regenerate aliases and test with actual agent
4. **Validate**: Ensure session management still works

## 💡 Implementation Details

### Generated Alias Structure
Each alias supports dual modes:

**Without arguments → REPL Mode:**
```bash
code-reviewer  # Starts interactive chat
```

**With arguments → Direct Mode:**  
```bash
code-reviewer "analyze this code"  # Single query
```

### REPL Features
- **Colored output**: prompt-toolkit styling
- **Session tracking**: Shows current session ID  
- **Conversation history**: Per-session storage
- **Dynamic config**: Reloads `.md` file each query
- **Token usage**: Shows input/output token counts

### Integration Points
- **MCP Server**: Shared session storage and logic
- **Claude CLI**: Direct command execution  
- **Main CLI**: Invoked via `task-agent generate-aliases`
- **Agent Configs**: Reads same `.md` files as MCP server

## 🎯 Key Patterns

### Error Handling
Always provide helpful error messages:
```python
except ImportError as e:
    print(f"❌ REPL module not found: {e}")
    print("Make sure prompt-toolkit is installed: pip install prompt-toolkit")
```

### Dynamic Config Loading
Always read fresh config on each query:
```python
def _execute_agent_query(self, user_input: str) -> str:
    # Load fresh agent config from .md file on each query
    config = self._load_agent_config_from_file() or self.config
```

### Session Consistency  
Use same session management as MCP server:
```python
if config.get('resume_session') and HAS_SESSION_STORE:
    resume_session_id = SESSION_STORE.get_resume_session(
        self.agent_name,
        max_exchanges
    )
```

## 🚨 Important Reminders

1. **Always regenerate aliases** after modifying templates
2. **Test both REPL and direct modes** when making changes
3. **Keep session logic consistent** with MCP server
4. **Handle bash escaping carefully** in templates  
5. **Provide clear error messages** for debugging

The agent-cli module is designed to be a seamless bridge between the MCP server's functionality and direct terminal access, with the added benefit of an interactive REPL interface.