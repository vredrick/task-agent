#!/bin/bash

# Build script for PyPI package

echo "Building task-agents-mcp for PyPI..."

# Clean previous builds
rm -rf build/ dist/ *.egg-info src/*.egg-info

# Update the README for PyPI if needed
cp README.pypi.md README_PYPI.md

# Build the package
python3 -m pip install --upgrade build
python3 -m build

echo "Build complete! To upload to PyPI:"
echo "  python3 -m pip install --upgrade twine"
echo "  python3 -m twine upload dist/*"
echo ""
echo "To test locally:"
echo "  pip install dist/task_agents_mcp-*.whl"
echo "  python3 -m task_agents_mcp"