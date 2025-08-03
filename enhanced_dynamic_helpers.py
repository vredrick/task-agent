#!/usr/bin/env python3
"""
Enhanced helper functions for dynamic prompt and resource generation
Phase 2: Improved resource implementation with richer data
"""
from typing import Dict, Any, Callable, List, Optional
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)


def categorize_agent(agent_name: str, agent_info: Dict[str, Any]) -> str:
    """
    Categorize an agent based on its name and description.
    
    Returns category like: 'review', 'debug', 'test', 'docs', 'performance', 'general'
    """
    name_lower = agent_name.lower()
    desc_lower = agent_info.get('description', '').lower()
    
    # Check for category keywords
    if 'review' in name_lower or 'review' in desc_lower:
        return 'review'
    elif 'debug' in name_lower or 'debug' in desc_lower or 'fix' in desc_lower:
        return 'debug'
    elif 'test' in name_lower or 'test' in desc_lower:
        return 'test'
    elif 'doc' in name_lower or 'doc' in desc_lower:
        return 'documentation'
    elif 'performance' in name_lower or 'optim' in desc_lower:
        return 'performance'
    else:
        return 'general'


def get_agent_capabilities(agent_info: Dict[str, Any]) -> List[str]:
    """
    Derive capabilities from agent tools and description.
    """
    capabilities = []
    tools = agent_info.get('tools', [])
    
    # Derive capabilities from tools
    if 'Read' in tools or 'Grep' in tools:
        capabilities.append('code_analysis')
    if 'Write' in tools or 'Edit' in tools or 'MultiEdit' in tools:
        capabilities.append('code_modification')
    if 'Bash' in tools:
        capabilities.append('command_execution')
    if 'WebSearch' in tools or 'WebFetch' in tools:
        capabilities.append('web_research')
    if 'NotebookRead' in tools or 'NotebookEdit' in tools:
        capabilities.append('jupyter_support')
    
    # Derive from description
    desc = agent_info.get('description', '').lower()
    if 'security' in desc:
        capabilities.append('security_analysis')
    if 'quality' in desc:
        capabilities.append('quality_assurance')
    
    return list(set(capabilities))  # Remove duplicates


def generate_usage_example(agent_name: str, agent_info: Dict[str, Any]) -> str:
    """
    Generate a contextual usage example for the agent.
    """
    category = categorize_agent(agent_name, agent_info)
    
    examples = {
        'review': f'Use the {agent_name} agent to review my authentication module for security issues',
        'debug': f'Use the {agent_name} agent to fix the TypeError in user_service.py',
        'test': f'Use the {agent_name} agent to run tests and improve coverage to 80%',
        'documentation': f'Use the {agent_name} agent to create API documentation for the new endpoints',
        'performance': f'Use the {agent_name} agent to optimize the database query performance',
        'general': f'Use the {agent_name} agent to help implement a new feature'
    }
    
    return examples.get(category, f'Use the {agent_name} agent for specialized tasks')


def create_enhanced_agents_list_resource(agent_manager) -> Callable:
    """
    Create an enhanced resource function with rich agent metadata.
    """
    async def get_agents_list() -> Dict[str, Any]:
        """Get comprehensive list of all available agents with rich metadata."""
        # Get basic info from agent manager
        agents_info = agent_manager.get_agents_info()
        
        # Build full agent data with tools from actual configs
        agents_full_data = {}
        for name, info in agents_info.items():
            # Get the actual agent config to access tools
            agent_config = agent_manager.get_agent_by_display_name(name)
            if agent_config:
                agents_full_data[name] = {
                    'description': info['description'],
                    'model': info['model'],
                    'tools': agent_config.tools,  # Get tools from config
                    'system_prompt': agent_config.system_prompt,
                    'cwd': agent_config.cwd,
                    'file': agent_config.name  # Original filename
                }
            else:
                # Fallback to basic info if config not found
                agents_full_data[name] = info
        
        # Format agent data with enhanced information
        agents_data = []
        categories_count = {}
        models_count = {}
        all_capabilities = set()
        
        for name, info in agents_full_data.items():
            # Determine category
            category = categorize_agent(name, info)
            categories_count[category] = categories_count.get(category, 0) + 1
            
            # Count models
            model = info.get("model", "unknown")
            models_count[model] = models_count.get(model, 0) + 1
            
            # Get capabilities
            capabilities = get_agent_capabilities(info)
            all_capabilities.update(capabilities)
            
            # Build comprehensive agent data
            agent_data = {
                "name": name,
                "description": info.get("description", ""),
                "category": category,
                "model": model,
                "tools": info.get("tools", []),
                "tool_count": len(info.get("tools", [])),
                "capabilities": capabilities,
                "prompt_name": f"{sanitize_function_name(name)}_task",
                "usage_example": generate_usage_example(name, info),
                "metadata": {
                    "file": info.get("file", ""),  # Original filename if available
                    "has_system_prompt": bool(info.get("system_prompt", "")),
                    "working_directory": info.get("cwd", ".")
                }
            }
            agents_data.append(agent_data)
        
        # Sort by category, then name
        agents_data.sort(key=lambda x: (x["category"], x["name"]))
        
        # Group by category for easier consumption
        agents_by_category = {}
        for agent in agents_data:
            cat = agent["category"]
            if cat not in agents_by_category:
                agents_by_category[cat] = []
            agents_by_category[cat].append(agent)
        
        return {
            "agents": agents_data,
            "agents_by_category": agents_by_category,
            "total_count": len(agents_data),
            "statistics": {
                "by_category": categories_count,
                "by_model": models_count,
                "total_capabilities": sorted(list(all_capabilities))
            },
            "server_info": {
                "dynamic_prompts_enabled": True,
                "prompt_suffix": "_task",
                "resource_version": "2.0",
                "features": [
                    "dynamic_prompts",
                    "categorization",
                    "capability_detection",
                    "usage_examples"
                ]
            },
            "generated_at": datetime.now().isoformat(),
            "usage_guide": {
                "tool_usage": "Use 'delegate' tool with agent name and prompt",
                "prompt_usage": "Use '{agent_name}_task' prompts for guided task creation",
                "resource_usage": "Query 'agents://list' for current agent information"
            }
        }
    
    return get_agents_list


def sanitize_function_name(name: str) -> str:
    """Convert agent display name to a valid Python function name."""
    clean = name.lower()
    clean = clean.replace(' ', '_')
    clean = clean.replace('-', '_')
    clean = ''.join(c if c.isalnum() or c == '_' else '' for c in clean)
    
    if clean and clean[0].isdigit():
        clean = f"agent_{clean}"
    if not clean:
        clean = "agent_unknown"
    
    return clean


# If running as main module, add current directory to path for imports
if __name__ == "__main__":
    import sys
    sys.path.append('.')

try:
    # Import other functions from original helpers if available
    from dynamic_helpers import (
        create_agent_prompt_function,
        generate_agent_tips,
        register_dynamic_prompts
    )
except ImportError:
    # Fallback - these functions might not be needed for resource-only usage
    pass