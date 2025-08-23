# CLAUDE.md - docs/

## Directory Purpose

This directory contains **technical documentation** for the task-agents MCP server, explaining features, implementation details, and usage patterns. Documentation here supplements the main README with deeper technical information.

## Current Documentation

### session-resumption.md
**Purpose**: Technical specification for the session resumption feature

**Key Topics**:
- How session chaining works
- Configuration options and syntax
- Session ID management and persistence
- Exchange counting and limits
- Integration with Claude CLI's `-r` flag
- Troubleshooting session issues

## Documentation Standards

### File Organization
- One feature/topic per file
- Clear, descriptive filenames
- Markdown format for consistency
- Technical depth appropriate for developers

### Content Structure
Each documentation file should include:
1. **Overview**: High-level feature description
2. **Configuration**: How to enable/configure
3. **How It Works**: Technical implementation details
4. **Examples**: Practical usage scenarios
5. **Troubleshooting**: Common issues and solutions

## Relationship to Other Documentation

### Hierarchy
```
README.md                 # User-facing, installation, basic usage
├── CLAUDE.md            # Project architecture, development guide
├── docs/                # Technical feature documentation
│   ├── CLAUDE.md       # This file - docs directory guide
│   └── *.md            # Individual feature docs
├── examples/            # Code examples and templates
└── src/.../CLAUDE.md    # Code-specific documentation
```

### Cross-References
- README links to docs/ for detailed feature info
- CLAUDE.md references docs/ for implementation specs
- Individual docs link back to relevant code sections

## Adding New Documentation

When adding new documentation:

1. **Choose the Right Location**:
   - Feature specifications → `docs/`
   - Usage examples → `examples/`
   - Code documentation → Source directory `CLAUDE.md`

2. **Follow Naming Convention**:
   - Lowercase with hyphens: `feature-name.md`
   - Descriptive but concise names
   - Version suffixes if needed: `session-v2.md`

3. **Include Standard Sections**:
   ```markdown
   # Feature Name
   
   ## Overview
   [High-level description]
   
   ## Configuration
   [How to enable/configure]
   
   ## How It Works
   [Technical details]
   
   ## Examples
   [Usage scenarios]
   
   ## API Reference
   [If applicable]
   
   ## Troubleshooting
   [Common issues]
   ```

## Documentation Topics to Cover

Potential future documentation:

### Agent Development
- Creating custom agents
- Agent configuration syntax
- System prompt best practices
- Tool selection guidelines

### MCP Integration
- Resource registration details
- Tool function implementation
- Context handling
- Error propagation

### Advanced Features
- Resource directory management
- Session persistence architecture
- Multi-agent workflows
- Performance optimization

### Deployment
- Production configuration
- Security considerations
- Monitoring and logging
- Scaling strategies

## Version-Specific Documentation

When features change significantly:
- Keep old docs with version suffix
- Add deprecation notices
- Link to migration guides
- Maintain compatibility notes

Example:
```
session-resumption.md      # Current version
session-resumption-v1.md   # Legacy (pre-2.5.0)
```

## Documentation Testing

Ensure documentation accuracy:
1. **Code Examples**: Test all code snippets
2. **Configuration**: Verify all settings work
3. **Commands**: Test CLI commands shown
4. **Links**: Check internal and external links
5. **Versions**: Update version numbers

## Contributing Documentation

When contributing:
1. Follow existing patterns
2. Include practical examples
3. Explain the "why" not just "what"
4. Add diagrams for complex flows
5. Update related documentation

## Documentation Maintenance

Regular maintenance tasks:
- Review for accuracy after releases
- Update version numbers
- Fix broken links
- Add newly discovered patterns
- Remove deprecated content

## Quick Reference

### Key Documentation Files
| File | Purpose |
|------|---------|
| `README.md` | User guide, installation |
| `CLAUDE.md` | Architecture, development |
| `docs/session-resumption.md` | Session feature spec |
| `examples/*.md` | Usage examples |

### Documentation Commands
```bash
# Generate documentation outline
grep -r "^#" docs/ --include="*.md"

# Find TODOs in docs
grep -r "TODO" docs/ --include="*.md"

# Check for broken links
# (would need a link checker tool)
```

## Future Documentation Plans

Planned documentation additions:
1. Agent development guide
2. MCP protocol details
3. Performance tuning guide
4. Security best practices
5. Migration guides for major versions

## Related Resources

### Internal
- `/examples/` - Practical examples
- `/src/task_agents_mcp/agents/` - Agent configurations
- Root `CLAUDE.md` - Main architecture doc

### External
- [MCP Documentation](https://modelcontextprotocol.io/)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [Claude CLI Docs](https://claude.ai/docs)

## Documentation Philosophy

Our documentation aims to:
- **Educate**: Teach concepts, not just syntax
- **Enable**: Help users accomplish tasks
- **Explain**: Provide context and reasoning
- **Evolve**: Stay current with the codebase