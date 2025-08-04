# Changelog

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