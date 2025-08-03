#!/usr/bin/env python3
"""
Automated PyPI publishing script for task-agents-mcp.

This script handles:
1. Version bumping
2. Building the package
3. Publishing to PyPI
4. Git tagging

Usage:
    python scripts/publish_pypi.py [patch|minor|major]
"""

import subprocess
import sys
import re
import os
from pathlib import Path

def run_command(cmd, capture_output=False):
    """Run a shell command and handle errors."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=capture_output, text=True)
    if result.returncode != 0:
        if capture_output:
            print(f"Error: {result.stderr}")
        sys.exit(1)
    return result

def get_current_version():
    """Extract current version from pyproject.toml."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    with open(pyproject_path, 'r') as f:
        content = f.read()
    match = re.search(r'version = "(\d+\.\d+\.\d+)"', content)
    if match:
        return match.group(1)
    raise ValueError("Could not find version in pyproject.toml")

def bump_version(current_version, bump_type):
    """Bump version based on type (patch, minor, major)."""
    major, minor, patch = map(int, current_version.split('.'))
    
    if bump_type == 'patch':
        patch += 1
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")
    
    return f"{major}.{minor}.{patch}"

def update_version(new_version):
    """Update version in pyproject.toml."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    with open(pyproject_path, 'r') as f:
        content = f.read()
    
    content = re.sub(
        r'version = "\d+\.\d+\.\d+"',
        f'version = "{new_version}"',
        content
    )
    
    with open(pyproject_path, 'w') as f:
        f.write(content)

def clean_build():
    """Clean previous build artifacts."""
    dirs_to_clean = ['dist', 'build', 'src/task_agents_mcp.egg-info']
    for dir_name in dirs_to_clean:
        run_command(['rm', '-rf', dir_name])

def build_package():
    """Build the package using build tool."""
    run_command([sys.executable, '-m', 'pip', 'install', '--upgrade', 'build'])
    run_command([sys.executable, '-m', 'build'])

def check_pypi_token():
    """Check if PyPI token is available."""
    # Check environment variable first
    if os.environ.get('PYPI_TOKEN'):
        return 'env'
    
    # Check .pypirc file
    pypirc_path = Path.home() / '.pypirc'
    if pypirc_path.exists():
        return 'pypirc'
    
    # Check local .pypirc (in project root, git-ignored)
    local_pypirc = Path(__file__).parent.parent / '.pypirc'
    if local_pypirc.exists():
        return 'local'
    
    return None

def publish_to_pypi(token_source):
    """Publish to PyPI using appropriate authentication method."""
    run_command([sys.executable, '-m', 'pip', 'install', '--upgrade', 'twine'])
    
    if token_source == 'env':
        # Use token from environment variable
        env = os.environ.copy()
        env['TWINE_USERNAME'] = '__token__'
        env['TWINE_PASSWORD'] = os.environ['PYPI_TOKEN']
        subprocess.run([sys.executable, '-m', 'twine', 'upload', 'dist/*'], env=env)
    elif token_source == 'local':
        # Use local .pypirc file
        local_pypirc = Path(__file__).parent.parent / '.pypirc'
        run_command([sys.executable, '-m', 'twine', 'upload', '--config-file', str(local_pypirc), 'dist/*'])
    else:
        # Use default .pypirc location
        run_command([sys.executable, '-m', 'twine', 'upload', 'dist/*'])

def create_git_tag(version):
    """Create and push git tag."""
    # Check if there are uncommitted changes
    result = run_command(['git', 'status', '--porcelain'], capture_output=True)
    if result.stdout.strip():
        print("Warning: There are uncommitted changes. Commit them first.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Create tag
    run_command(['git', 'tag', f'v{version}', '-m', f'Release v{version}'])
    
    # Push tag
    print("Push tag to remote? (y/N): ", end='')
    if input().lower() == 'y':
        run_command(['git', 'push', 'origin', f'v{version}'])

def main():
    # Parse arguments
    if len(sys.argv) < 2:
        bump_type = 'patch'
    else:
        bump_type = sys.argv[1]
        if bump_type not in ['patch', 'minor', 'major']:
            print("Usage: python scripts/publish_pypi.py [patch|minor|major]")
            sys.exit(1)
    
    # Check for PyPI token
    token_source = check_pypi_token()
    if not token_source:
        print("Error: No PyPI token found!")
        print("\nTo set up authentication, choose one of these options:")
        print("\n1. Environment variable (temporary):")
        print("   export PYPI_TOKEN='your-token-here'")
        print("\n2. Local .pypirc file (git-ignored):")
        print("   Create .pypirc in project root")
        print("\n3. Global .pypirc file:")
        print("   Create ~/.pypirc")
        print("\nExample .pypirc content:")
        print("""
[pypi]
  username = __token__
  password = pypi-your-token-here
""")
        sys.exit(1)
    
    # Get current version
    current_version = get_current_version()
    print(f"Current version: {current_version}")
    
    # Bump version
    new_version = bump_version(current_version, bump_type)
    print(f"New version: {new_version}")
    
    # Confirm
    print(f"\nThis will publish version {new_version} to PyPI.")
    print("Continue? (y/N): ", end='')
    if input().lower() != 'y':
        print("Aborted.")
        sys.exit(0)
    
    # Update version
    print("\nUpdating version...")
    update_version(new_version)
    
    # Clean and build
    print("\nCleaning previous builds...")
    clean_build()
    
    print("\nBuilding package...")
    build_package()
    
    # Publish
    print("\nPublishing to PyPI...")
    publish_to_pypi(token_source)
    
    # Git tag
    print("\nCreating git tag...")
    create_git_tag(new_version)
    
    print(f"\n✅ Successfully published version {new_version}!")
    print("\nDon't forget to:")
    print("1. Commit the version change: git commit -am 'Release v{}'".format(new_version))
    print("2. Push to remote: git push origin main")

if __name__ == "__main__":
    main()