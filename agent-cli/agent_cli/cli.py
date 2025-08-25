#!/usr/bin/env python3
"""
Agent CLI - Command line interface for agent alias management.

This module provides the CLI entry point for managing agent aliases,
separated from the main MCP server functionality.
"""

import sys
import argparse
import logging
from pathlib import Path

# Import the alias generator from this directory
from .alias_generator import AliasGenerator

def main():
    """Main CLI entry point for agent-cli commands."""
    parser = argparse.ArgumentParser(
        prog="agent-cli",
        description="Direct terminal access to task agents"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate aliases command
    generate_parser = subparsers.add_parser(
        "generate", 
        help="Generate shell script aliases for all agents"
    )
    generate_parser.add_argument(
        "--output-dir",
        type=str,
        default="~/task-agents-alias",
        help="Directory to save generated aliases (default: ~/task-agents-alias)"
    )
    generate_parser.add_argument(
        "--no-install",
        action="store_true",
        help="Don't auto-install aliases to ~/.local/bin"
    )
    
    # List agents command (future expansion)
    list_parser = subparsers.add_parser(
        "list",
        help="List all available agents"
    )
    
    # Install command (future expansion)
    install_parser = subparsers.add_parser(
        "install", 
        help="Install specific agent alias"
    )
    install_parser.add_argument("agent_name", help="Name of agent to install")
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == "generate":
        return generate_aliases(args)
    elif args.command == "list":
        return list_agents(args)
    elif args.command == "install":
        return install_agent(args)
    else:
        parser.print_help()
        return 1

def generate_aliases(args):
    """Generate aliases for all agents."""
    try:
        # Find the main project directory
        current_dir = Path(__file__).parent.parent
        agents_dir = current_dir / "task-agents"
        
        if not agents_dir.exists():
            print(f"❌ Agents directory not found: {agents_dir}")
            return 1
        
        # Load agents - import here to avoid path issues
        import sys
        sys.path.insert(0, str(current_dir / "src"))
        from task_agents_mcp.agent_manager import AgentManager
        
        agent_manager = AgentManager(str(agents_dir))
        agent_manager.load_agents()
        
        if not agent_manager.agents:
            print(f"❌ No agents found in {agents_dir}")
            return 1
        
        # Generate aliases
        alias_generator = AliasGenerator(agent_manager)
        output_path = Path(args.output_dir).expanduser()
        
        scripts = alias_generator.generate_all_aliases(output_path)
        
        if not scripts:
            print("❌ No alias scripts were generated.")
            return 1
        
        print(f"✅ Generated {len(scripts)} alias scripts in {output_path}")
        print("\nGenerated aliases:")
        for script_name, agent_name in [(Path(path).name, name) for name, path in scripts.items()]:
            print(f"  {script_name} - {agent_name}")
        
        # Auto-install unless disabled
        if not args.no_install:
            installer_script = alias_generator.generate_installer_script(output_path, scripts)
            try:
                import subprocess
                result = subprocess.run(['bash', installer_script], capture_output=True, text=True)
                if result.returncode == 0:
                    print("\n🚀 Auto-installing aliases...")
                    print("✅ Aliases successfully installed!")
                    print(f"\nYou can now use your agents directly from the terminal:")
                    first_script = list(scripts.keys())[0]
                    first_script_name = Path(scripts[first_script]).name
                    print(f"  {first_script_name} \"your query here\"")
                    print(f"\nExample:")
                    print(f"  {first_script_name} \"explain how this agent system works\"")
                else:
                    print(f"   bash {installer_script}")
                    if result.stderr:
                        print(f"Error: {result.stderr}")
            except Exception as e:
                print(f"   bash {installer_script}")
                print(f"Error: {e}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating aliases: {e}")
        return 1

def list_agents(args):
    """List all available agents."""
    print("📋 Available agents:")
    print("(This feature will be implemented in future versions)")
    return 0

def install_agent(args):
    """Install a specific agent alias."""
    print(f"🔧 Installing agent: {args.agent_name}")
    print("(This feature will be implemented in future versions)")
    return 0

if __name__ == "__main__":
    sys.exit(main())