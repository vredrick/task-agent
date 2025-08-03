"""
Setup script for Task-Agents MCP Server
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="task-agents-mcp",
    version="2.0.0",
    author="vredrick",
    description="Multi-tool MCP server for specialized AI agents - each agent as its own tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vredrick/task-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastmcp>=0.1.0",
        "pyyaml>=6.0",
        "aiofiles>=23.0.0",
    ],
    entry_points={
        "console_scripts": [
            "task-agents=server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["configs/*.md"],
    },
)