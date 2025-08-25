#!/usr/bin/env python3
"""
CLI interface for task-agents-mcp

Supports both MCP server mode and alias generation.
"""

import sys
import argparse
import logging
import os
from pathlib import Path

def list_agents_command(agents_dir=None, verbose=False):
    """List all available agents."""
    try:
        # Avoid importing server modules to prevent logging
        import yaml
        
        # Determine agents directory
        agents_dir = agents_dir or os.environ.get('TASK_AGENTS_PATH') or './task-agents'
        agents_path = Path(agents_dir)
        
        if not agents_path.exists():
            print(f"❌ Agents directory not found: {agents_path}")
            return False
        
        # Find agent files without full AgentManager initialization
        agent_files = list(agents_path.glob("*.md"))
        if not agent_files:
            print(f"📭 No agents found in {agents_path}")
            print("Create agent configuration files (.md) in your agents directory.")
            return False
        
        # Parse agent configs manually to avoid server logging
        agents = {}
        for agent_file in agent_files:
            try:
                with open(agent_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if '---' not in content:
                    continue
                    
                parts = content.split('---', 2)
                if len(parts) < 3:
                    continue
                
                metadata = yaml.safe_load(parts[1])
                if not metadata:
                    continue
                
                agent_name = metadata.get('agent-name', 'Unknown Agent')
                description = metadata.get('description', 'No description')
                model = metadata.get('model', 'sonnet')
                tools = metadata.get('tools', 'Read,Write').replace(',', ' ').split()
                cwd = metadata.get('cwd', '.')
                optional = metadata.get('optional', {})
                resume_session = optional.get('resume-session', False)
                
                agents[agent_name] = {
                    'agent_name': agent_name,
                    'description': description,
                    'model': model,
                    'tools': tools,
                    'cwd': cwd,
                    'resume_session': resume_session
                }
            except Exception as e:
                print(f"⚠️  Warning: Could not parse {agent_file.name}: {e}")
                continue
        
        if not agents:
            print(f"📭 No valid agents found in {agents_path}")
            print("Create agent configuration files (.md) in your agents directory.")
            return False
        
        print(f"📋 Available agents ({len(agents)}):")
        print()
        
        for agent_name, agent_config in agents.items():
            alias_name = agent_name.lower().replace(' ', '-')
            
            if verbose:
                print(f"🤖 {agent_config['agent_name']}")
                print(f"   Description: {agent_config['description']}")
                print(f"   Model: {agent_config['model']}")
                print(f"   Tools: {', '.join(agent_config['tools'])}")
                print(f"   Working Dir: {agent_config['cwd']}")
                if agent_config['resume_session']:
                    print(f"   Session Support: ✅ Resumable sessions")
                else:
                    print(f"   Session Support: ❌ Single-turn only")
                print(f"   Usage: {alias_name} \"your query here\"")
                if agent_config['resume_session']:
                    print(f"          {alias_name} --reset \"start fresh session\"")
                print()
            else:
                print(f"  {alias_name}")
                print(f"    📝 {agent_config['description']}")
                print(f"    💻 Usage: {alias_name} \"your query here\"")
                print()
        
        if not verbose:
            print("💡 Use --verbose (-v) for detailed information")
            print("💡 Generate terminal aliases: task-agent generate-aliases")
            print("💡 Example: example-agent \"explain how this works\"")
        
        return True
        
    except Exception as e:
        print(f"❌ Error listing agents: {e}")
        return False

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Task Agents MCP Server - Multi-tool architecture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  task-agent                           # Start MCP server (default)
  task-agent list                      # List all available agents  
  task-agent list --verbose            # Show detailed agent info
  task-agent generate-aliases          # Generate alias scripts
  task-agent generate-aliases --output-dir ~/bin
  task-agent watch                     # Watch for changes (future)
  task-agent install my-agent          # Install single agent (future)
"""
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Default behavior (no subcommand) is to start the server
    parser.set_defaults(command='server')
    
    # Server subcommand (optional, for explicit usage)
    server_parser = subparsers.add_parser('server', help='Start the MCP server (default)')
    
    # Generate aliases subcommand
    aliases_parser = subparsers.add_parser('generate-aliases', help='Generate executable alias scripts for agents')
    aliases_parser.add_argument(
        '--output-dir', 
        help='Directory to output alias scripts (default: ~/task-agents-alias)'
    )
    aliases_parser.add_argument(
        '--agents-dir', 
        help='Directory containing agent configurations (default: ./task-agents or TASK_AGENTS_PATH)'
    )
    
    # List agents subcommand
    list_parser = subparsers.add_parser('list', help='List all available agents')
    list_parser.add_argument(
        '--agents-dir',
        help='Directory containing agent configurations (default: ./task-agents or TASK_AGENTS_PATH)'
    )
    list_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed agent information'
    )
    
    # Watch subcommand (future)
    watch_parser = subparsers.add_parser('watch', help='Watch for agent changes and auto-regenerate aliases')
    watch_parser.add_argument(
        '--agents-dir',
        help='Directory to watch for agent changes (default: ./task-agents or TASK_AGENTS_PATH)'
    )
    
    # Install specific agent subcommand (future)  
    install_parser = subparsers.add_parser('install', help='Install alias for a specific agent')
    install_parser.add_argument('agent_name', help='Name of agent to install')
    install_parser.add_argument(
        '--agents-dir',
        help='Directory containing agent configurations (default: ./task-agents or TASK_AGENTS_PATH)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle commands
    if args.command == 'generate-aliases':
        print("🔄 Using agent-cli module for alias generation...")
        try:
            # Try to use the new agent-cli module
            import os
            current_dir = Path(__file__).parent.parent.parent
            sys.path.insert(0, str(current_dir))
            
            from agent_cli.alias_generator import AliasGenerator
            from .agent_manager import AgentManager
            import subprocess
            
            # Determine agents directory
            agents_dir = args.agents_dir or os.environ.get('TASK_AGENTS_PATH') or './task-agents'
            agents_path = Path(agents_dir)
            
            if not agents_path.exists():
                print(f"❌ Agents directory not found: {agents_path}")
                sys.exit(1)
            
            # Load agents
            agent_manager = AgentManager(str(agents_path))
            agent_manager.load_agents()
            
            if not agent_manager.agents:
                print(f"❌ No agents found in {agents_path}")
                sys.exit(1)
            
            # Generate aliases
            alias_generator = AliasGenerator(agent_manager)
            output_dir = Path(args.output_dir or "~/task-agents-alias").expanduser()
            
            scripts = alias_generator.generate_all_aliases(output_dir)
            
            if scripts:
                print(f"✅ Generated {len(scripts)} alias scripts in {output_dir}")
                installer_script = alias_generator.generate_installer_script(output_dir, scripts)
                
                # Auto-install
                print("\n🚀 Auto-installing aliases...")
                result = subprocess.run(['bash', installer_script], capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ Aliases successfully installed!")
                    first_script = list(scripts.keys())[0]
                    first_script_name = Path(scripts[first_script]).name
                    print(f"\nExample usage: {first_script_name} \"your query here\"")
                    sys.exit(0)
                else:
                    print(f"❌ Installation failed. Run manually: bash {installer_script}")
                    sys.exit(1)
            else:
                print("❌ No alias scripts were generated")
                sys.exit(1)
                
        except ImportError:
            print("⚠️  Agent-cli module not found, using legacy implementation...")
            from .alias_generator import generate_aliases_command
            success = generate_aliases_command(args.output_dir, args.agents_dir)
            sys.exit(0 if success else 1)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    elif args.command == 'list':
        # List all available agents
        success = list_agents_command(args.agents_dir, args.verbose)
        sys.exit(0 if success else 1)
    
    elif args.command == 'watch':
        # Watch for agent changes and auto-regenerate
        print("🔍 Watch mode - auto-regenerating aliases on agent changes")
        print("(This feature will be implemented in a future version)")
        print("For now, manually run: task-agent generate-aliases")
        sys.exit(0)
    
    elif args.command == 'install':
        # Install specific agent alias
        print(f"🔧 Installing alias for agent: {args.agent_name}")
        print("(This feature will be implemented in a future version)")
        print("For now, use: task-agent generate-aliases")
        sys.exit(0)
    
    else:
        # Default: start the server
        from .server import main as server_main
        server_main()


if __name__ == "__main__":
    main()