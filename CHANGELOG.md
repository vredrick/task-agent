# Changelog

All notable changes to the task-agents-mcp project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.11] - 2025-08-02

### Fixed
- Module import errors when installing from PyPI
- Version synchronization between `__init__.py` and `pyproject.toml`
- All internal imports now use relative imports (e.g., `from .module import`)
- Connection issues in Claude Code CLI when task-agents directory is missing

### Added
- Setup script (`scripts/setup_project.sh`) for easy project initialization
- Troubleshooting guide for "Failed to reconnect" error
- Import structure documentation in CLAUDE.md

### Changed
- Improved error messages for missing configurations
- Enhanced README with clearer troubleshooting steps

## [1.0.3] - 2025-08-02

### Added
- Enhanced output format with tool usage tracking
- Token count display (input, output, total) in agent responses
- Stream-json output format support for Claude Code CLI
- Automated PyPI publishing scripts
- GitHub Actions workflow for releases
- PyPI token configuration support (.pypirc)

### Changed
- Agent execution now uses `--output-format stream-json` with `--verbose` flag
- Improved agent response parsing to extract metadata from JSON events
- Updated agent manager to display tools used during execution

### Technical Details
- Parse tool_use events from assistant messages
- Extract token usage from result events
- Format output as: Tools list → Message → Token count

## [1.0.2] - 2025-07-15

### Added
- Python packaging support with PyPI distribution
- Default agents included in package
- Standard entry point: `task-agents-mcp`

### Fixed
- Working directory resolution for different installation methods
- Python module import structure

## [1.0.1] - 2025-07-01

### Added
- Support for multiple installation methods (uvx, pip, local)
- Comprehensive documentation
- Test suite

## [1.0.0] - 2025-06-15

### Added
- Initial release
- Core MCP server functionality
- Six default agents: Code Reviewer, Debugger, Default Assistant, Documentation Writer, Performance Optimizer, Test Runner
- FastMCP integration
- Agent configuration via markdown files with YAML frontmatter
- Support for Claude Desktop and Claude Code CLI