#!/bin/bash
# Quick publish script for task-agents-mcp
# Usage: ./scripts/quick_publish.sh

set -e

echo "🚀 Quick PyPI Publish for task-agents-mcp"
echo "========================================="

# Check if PYPI_TOKEN is set
if [ -z "$PYPI_TOKEN" ]; then
    echo "❌ Error: PYPI_TOKEN environment variable not set!"
    echo ""
    echo "Set it with: export PYPI_TOKEN='your-token-here'"
    echo "Get your token from: https://pypi.org/manage/account/token/"
    exit 1
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ src/task_agents_mcp.egg-info/

# Build the package
echo "📦 Building package..."
python3 -m pip install --upgrade build
python3 -m build

# Upload to PyPI
echo "📤 Uploading to PyPI..."
python3 -m pip install --upgrade twine
TWINE_USERNAME=__token__ TWINE_PASSWORD=$PYPI_TOKEN python3 -m twine upload dist/*

echo ""
echo "✅ Published successfully!"
echo ""
echo "Test with: pip install --upgrade task-agents-mcp"