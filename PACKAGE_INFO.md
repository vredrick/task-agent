# Package Information for Multi-Tool Fork

## PyPI Package Details

### Original Package
- **Name**: task-agents-mcp
- **Version**: 1.0.11
- **PyPI**: https://pypi.org/project/task-agents-mcp/

### This Fork (If Published)
- **Name**: task-agents-multi-tool
- **Version**: 0.1.0
- **Status**: Not published yet (exploration phase)

## Key Changes Made

1. **Package Name**: `task-agents-mcp` → `task-agents-multi-tool`
2. **Version**: Reset to `0.1.0` for new architecture
3. **Script Entry**: `task-agents-multi-tool` command
4. **Description**: Updated to indicate multi-tool architecture

## Publishing Instructions (If Needed)

If you decide to publish this as a separate package:

1. **PyPI API Token**
   - Token saved in `.pypirc_token`
   - Load with: `export PYPI_API_TOKEN=$(grep PYPI_API_TOKEN .pypirc_token | cut -d= -f2)`

2. **Build Package**
   ```bash
   ./scripts/build_pypi.sh
   ```

3. **Test Locally First**
   ```bash
   pip install -e .
   task-agents-multi-tool
   ```

4. **Publish to PyPI**
   ```bash
   python scripts/publish_pypi.py --bump patch
   ```

## Installation Commands (After Publishing)

```bash
# Install from PyPI (when published)
pip install task-agents-multi-tool

# Install with uvx (when published)
uvx task-agents-multi-tool

# Install from source (current)
pip install -e .
```

## Claude Desktop Configuration

```bash
# Add to Claude Desktop (when ready)
claude mcp add task-agents-multi -s project -- uvx task-agents-multi-tool
```

## Important Notes

1. **Don't publish yet** - This is still exploration phase
2. **Keep version low** (0.x.x) until architecture is finalized
3. **Different package name** prevents conflicts with original
4. **Same module name** (`task_agents_mcp`) for now - may need to change

## Next Steps for Package

1. Implement multi-tool server first
2. Test thoroughly with Claude Desktop
3. If approach is successful:
   - Update module name to `task_agents_multi_tool`
   - Update all imports
   - Prepare for PyPI publication
4. If approach is not chosen:
   - Archive this fork
   - Document learnings in main project