"""
Resource Manager for Task-Agents MCP Server

Provides MCP resources that help LLM clients understand and use each agent effectively.
Each agent has one resource using its agent-name as the URI.
"""

import logging
from typing import Dict, List, Optional, Any
from fastmcp import FastMCP

logger = logging.getLogger(__name__)


class AgentResourceManager:
    """Manages MCP resources for agents - one resource per agent."""
    
    def __init__(self, mcp_server: FastMCP, agent_manager):
        """
        Initialize the resource manager.
        
        Args:
            mcp_server: The FastMCP server instance
            agent_manager: The AgentManager instance for accessing agent configs
        """
        self.mcp = mcp_server
        self.agent_manager = agent_manager
        self.registered_resources = {}
        
        # Track BMad workflow positions if applicable
        self.bmad_workflow = [
            "analyst", "pm", "ux_expert", "architect", 
            "po", "sm", "dev", "qa"
        ]
        
    def register_all_resources(self):
        """Register resources for all agents."""
        logger.info("Registering MCP resources for agents...")
        
        # Register one resource per agent using agent-name
        for agent_name, agent_config in self.agent_manager.agents.items():
            self._register_agent_resource(agent_name, agent_config)
        
        logger.info(f"Registered {len(self.registered_resources)} agent resources")
        
    def _register_agent_resource(self, internal_name: str, agent_config):
        """Register a single resource for an agent using its agent-name."""
        
        # Use the agent name itself as the URI scheme (sanitized for URI format)
        # Replace spaces with hyphens and remove special characters for valid URI
        sanitized_name = agent_config.agent_name.replace(' ', '-').replace('_', '-')
        resource_uri = f"{sanitized_name}://"
        
        # Create a unique function name for this agent
        safe_name = internal_name.replace('-', '_')
        
        # Create a closure to capture the agent config with a unique function name
        async def agent_resource_func() -> Dict[str, Any]:
            """Get comprehensive information about this agent for LLM clients."""
            
            # Build the resource tailored for LLM consumption
            resource_data = {
                "name": agent_config.agent_name,
                "internal_name": internal_name,
                "description": agent_config.description,
                "capabilities": self._get_agent_capabilities(internal_name, agent_config),
                "when_to_use": self._get_when_to_use(internal_name),
                "how_to_call": {
                    "tool_name": internal_name.replace('-', '_'),
                    "parameters": {
                        "prompt": "Your specific task or request for this agent"
                    },
                    "example_calls": self._get_example_calls(internal_name, agent_config.agent_name)
                },
                "technical_details": {
                    "model": agent_config.model,
                    "available_tools": agent_config.tools,
                    "working_directory": agent_config.cwd,
                    "session_support": {
                        "enabled": bool(agent_config.resume_session),
                        "max_exchanges": (
                            agent_config.resume_session if isinstance(agent_config.resume_session, int) 
                            else 5 if agent_config.resume_session else 0
                        ),
                        "can_reset": bool(agent_config.resume_session)
                    }
                },
                "best_practices": self._get_best_practices(internal_name),
                "workflow_context": self._get_workflow_context(internal_name)
            }
            
            # Add resource directories if present
            if agent_config.resource_dirs:
                resource_data["technical_details"]["resource_directories"] = agent_config.resource_dirs
            
            return resource_data
        
        # Set the function name to be unique and descriptive
        agent_resource_func.__name__ = f"call_{safe_name}"
        
        # Register the resource with FastMCP
        self.mcp.resource(resource_uri)(agent_resource_func)
        self.registered_resources[resource_uri] = internal_name
        logger.info(f"Registered resource: {resource_uri} for agent: {internal_name}")
    
    def _get_agent_capabilities(self, agent_name: str, agent_config) -> List[str]:
        """Get a list of specific capabilities for an agent."""
        capabilities_map = {
            "analyst": [
                "Market research and competitive analysis",
                "Requirements gathering and documentation",
                "Brainstorming and ideation facilitation",
                "Project discovery for greenfield and brownfield projects",
                "Creating comprehensive project briefs",
                "Strategic research planning"
            ],
            "pm": [
                "Creating Product Requirements Documents (PRDs)",
                "Feature definition and prioritization",
                "Success metrics and KPI definition",
                "Product vision and roadmap planning",
                "Stakeholder alignment documentation",
                "Epic and feature breakdown"
            ],
            "ux_expert": [
                "UI/UX design specifications",
                "Wireframe and mockup creation",
                "Design system development",
                "User flow optimization",
                "Accessibility planning",
                "Generating prompts for AI UI tools (v0, Lovable)"
            ],
            "architect": [
                "System architecture design",
                "Technology stack selection",
                "API and database schema design",
                "Infrastructure planning",
                "Integration architecture",
                "Performance and security considerations"
            ],
            "po": [
                "PRD and architecture validation",
                "Document sharding into manageable epics",
                "Backlog prioritization",
                "Requirement quality assurance",
                "Sprint readiness assessment",
                "Stakeholder requirement validation"
            ],
            "sm": [
                "Converting epics to detailed user stories",
                "Task breakdown and estimation",
                "Acceptance criteria definition",
                "Sprint planning preparation",
                "Story implementation readiness",
                "Developer-ready documentation"
            ],
            "dev": [
                "Full-stack code implementation",
                "Feature development from stories",
                "API and backend development",
                "Frontend implementation",
                "Database operations",
                "Code debugging and testing"
            ],
            "qa": [
                "Code review and quality assurance",
                "Refactoring for better maintainability",
                "Test coverage improvement",
                "Security vulnerability identification",
                "Performance optimization",
                "Best practices enforcement"
            ]
        }
        
        return capabilities_map.get(agent_name, [
            "General task assistance",
            "Problem solving",
            "Code and documentation support"
        ])
    
    def _get_when_to_use(self, agent_name: str) -> Dict[str, Any]:
        """Get guidance on when to use this agent."""
        when_to_use_map = {
            "analyst": {
                "primary_use": "ALWAYS call FIRST when starting new projects or analyzing existing ones",
                "triggers": [
                    "Starting a new project",
                    "Need market or competitive research",
                    "Gathering requirements",
                    "Brainstorming features or solutions",
                    "Analyzing existing systems"
                ],
                "prerequisites": "None - this is typically the first agent to call"
            },
            "pm": {
                "primary_use": "Call AFTER analyst to transform research into product requirements",
                "triggers": [
                    "Need to create a PRD",
                    "Defining product features",
                    "Setting success metrics",
                    "Planning product roadmap"
                ],
                "prerequisites": "Analyst research should be complete"
            },
            "ux_expert": {
                "primary_use": "Call AFTER PM for UI-heavy projects, BEFORE architect",
                "triggers": [
                    "Need UI/UX specifications",
                    "Creating design systems",
                    "Planning user interfaces",
                    "Optimizing user experience"
                ],
                "prerequisites": "Product requirements should be defined"
            },
            "architect": {
                "primary_use": "Call AFTER PM/UX to create technical design",
                "triggers": [
                    "Need system architecture",
                    "Selecting technology stack",
                    "Designing APIs or databases",
                    "Planning infrastructure"
                ],
                "prerequisites": "Product requirements should be complete"
            },
            "po": {
                "primary_use": "Call AFTER architecture to validate and prepare for development",
                "triggers": [
                    "Validating requirements alignment",
                    "Breaking down large documents",
                    "Preparing backlog for development"
                ],
                "prerequisites": "Architecture should be complete"
            },
            "sm": {
                "primary_use": "Call AFTER PO to create developer-ready stories",
                "triggers": [
                    "Converting epics to stories",
                    "Need detailed task breakdown",
                    "Preparing sprint work"
                ],
                "prerequisites": "PO should have sharded documents into epics"
            },
            "dev": {
                "primary_use": "Call when ready to implement code from approved stories",
                "triggers": [
                    "Implementing features",
                    "Writing code from stories",
                    "Building APIs or UI",
                    "Fixing bugs"
                ],
                "prerequisites": "Stories should be approved and ready"
            },
            "qa": {
                "primary_use": "Call AFTER dev completes implementation",
                "triggers": [
                    "Code needs review",
                    "Improving code quality",
                    "Adding tests",
                    "Refactoring existing code"
                ],
                "prerequisites": "Development should be complete"
            }
        }
        
        return when_to_use_map.get(agent_name, {
            "primary_use": "Use for general assistance with tasks",
            "triggers": ["Need help with specific task"],
            "prerequisites": "None"
        })
    
    def _get_example_calls(self, agent_name: str, display_name: str) -> List[Dict[str, str]]:
        """Get example calls for this agent."""
        examples_map = {
            "analyst": [
                {
                    "scenario": "Starting a new e-commerce project",
                    "call": f"{agent_name.replace('-', '_')}(prompt='Research the current state of e-commerce platforms and identify key features for a new online marketplace')"
                },
                {
                    "scenario": "Analyzing existing system",
                    "call": f"{agent_name.replace('-', '_')}(prompt='Analyze our current authentication system and document improvement opportunities')"
                }
            ],
            "pm": [
                {
                    "scenario": "Creating product documentation",
                    "call": f"{agent_name.replace('-', '_')}(prompt='Create a PRD for a user notification system based on the analyst research')"
                }
            ],
            "dev": [
                {
                    "scenario": "Implementing a feature",
                    "call": f"{agent_name.replace('-', '_')}(prompt='Implement the user authentication API endpoint from story US-001')"
                }
            ],
            "qa": [
                {
                    "scenario": "Reviewing code",
                    "call": f"{agent_name.replace('-', '_')}(prompt='Review the authentication module implementation and suggest improvements')"
                }
            ]
        }
        
        default_example = [{
            "scenario": "General task",
            "call": f"{agent_name.replace('-', '_')}(prompt='[Your specific request]')"
        }]
        
        return examples_map.get(agent_name, default_example)
    
    def _get_best_practices(self, agent_name: str) -> List[str]:
        """Get best practices for using this agent."""
        practices_map = {
            "analyst": [
                "Provide context about your business domain",
                "Be specific about research scope",
                "Use interactive checkpoints to guide research",
                "Save analyst output for downstream agents"
            ],
            "pm": [
                "Include analyst research in your prompt",
                "Be clear about target users and goals",
                "Review PRD before passing to architect",
                "Specify any constraints or requirements"
            ],
            "dev": [
                "Reference specific story IDs when implementing",
                "Ensure stories are approved before starting",
                "Follow existing code patterns in the project",
                "Test your implementation before marking complete"
            ],
            "qa": [
                "Run after development is complete",
                "Be specific about areas of concern",
                "Apply suggested improvements systematically",
                "Verify fixes don't break existing functionality"
            ]
        }
        
        return practices_map.get(agent_name, [
            "Be specific and clear in your requests",
            "Provide relevant context",
            "Review output before proceeding"
        ])
    
    def _get_workflow_context(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get workflow context if this agent is part of BMad workflow."""
        if agent_name not in self.bmad_workflow:
            return None
        
        position = self.bmad_workflow.index(agent_name)
        return {
            "workflow": "BMad Development Methodology",
            "stage": position + 1,
            "total_stages": len(self.bmad_workflow),
            "previous_agent": self.bmad_workflow[position - 1] if position > 0 else None,
            "next_agent": self.bmad_workflow[position + 1] if position < len(self.bmad_workflow) - 1 else None,
            "role_in_workflow": self._get_workflow_role(agent_name)
        }
    
    def _get_workflow_role(self, agent_name: str) -> str:
        """Get the role description in the BMad workflow."""
        roles = {
            "analyst": "Discovery and Research Phase - Gathers requirements and context",
            "pm": "Product Definition Phase - Creates product requirements",
            "ux_expert": "Design Phase - Creates UI/UX specifications",
            "architect": "Technical Design Phase - Defines system architecture",
            "po": "Validation Phase - Ensures alignment and prepares backlog",
            "sm": "Story Creation Phase - Creates developer-ready stories",
            "dev": "Implementation Phase - Builds the solution",
            "qa": "Quality Assurance Phase - Reviews and improves code"
        }
        return roles.get(agent_name, "Supporting role in development")