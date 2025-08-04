# Changelog

## [2.5.0] - 2025-08-04

### Added
- **Session Resumption Feature**: Agents can now maintain context across multiple exchanges
  - Supports `resume-session` field in agent configurations
  - Automatic session chaining with Claude CLI's `-r` flag
  - Configurable exchange limits before starting fresh
  - Session persistence in `/tmp/task_agents_sessions.json`
- SessionChainStore class for managing session ID chains
- Session info in agent responses (Session ID, Exchange count)
- Documentation for session resumption feature

### Updated
- AgentConfig to support `resume-session` field with boolean or numeric values
- AgentManager to integrate session chain tracking and resume functionality
- Default agents (Debugger, Default Assistant) now include session resumption
- README with session resumption documentation and examples

### Added Agent
- Session Tester agent for testing session functionality

## [2.4.4] - 2025-08-04

### Added
- Claude Code slash command `/task-agents` to easily create task-agents directory with default configurations
- Example slash command file in `examples/task-agents-command.md`

### Updated
- README documentation to mention the slash command for quick setup

## [2.4.3] - 2025-08-04

### Fixed
- Removed dependency on missing enhanced features modules (enhanced_dynamic_helpers, enhanced_prompt_helpers)
- Fixed import errors that prevented MCP server from starting

### Enhanced
- Improved JSON parsing to capture session IDs from Claude CLI
- Enhanced response accumulation to handle multiple text segments properly
- Added better error handling and recovery for malformed JSON lines
- Improved debug logging for troubleshooting

### Removed
- Removed enhanced resources and prompts features (not supported by most MCP clients)

## [2.4.2] - Previous Version
- Initial multi-tool MCP server implementation