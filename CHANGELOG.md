# Changelog

## [4.1.0] - 2026-03-22

### Changed
- Replaced `--allowedTools` with `--tools` (comma-separated, explicit tool control)

### Added
- `--name` flag auto-generated from agent name for session identification in `/resume`
- `--include-partial-messages` for real-time token-by-token streaming via progress notifications
- `disallowed-tools` optional agent config field with `--disallowed-tools` CLI flag
- `mcp-config` optional agent config field with `--mcp-config` + `--strict-mcp-config` CLI flags
- `stream_event` handler in process_event for partial message deltas
- Partial text forwarding through progress_callback to MCP client via `ctx.info()`

## [4.0.0] - 2026-03-21

### Changed
- Simplified architecture: removed all built-in agents, user-defined only
- Single agents directory (no more dual-directory loading)
- Standardized on Python 3.11+

### Removed
- Built-in BMad methodology agents directory (`src/task_agents_mcp/agents/`)
- Dual-directory agent loading logic

### Added
- Example agent template in `task-agents/example-agent.md`

## [3.0.0] - 2025

### Added
- Real-time progress streaming via MCP context
- Resource manager for MCP resource registration per agent
- Dynamic resource directory handling with `--add-dir`
- Enhanced resource directory path resolution

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