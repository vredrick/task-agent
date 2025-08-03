#!/usr/bin/env python3
"""
Test suite for Task-Agents MCP Server
"""
import os
import sys
import unittest
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_manager import AgentManager


class TestAgentManager(unittest.TestCase):
    """Test the AgentManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent.parent / "task-agents"
        self.manager = AgentManager(str(self.test_dir))
    
    def test_load_agents(self):
        """Test that agents can be loaded from directory."""
        self.manager.load_agents()
        self.assertGreater(len(self.manager.agents), 0, "No agents were loaded")
        print(f"✓ Loaded {len(self.manager.agents)} agents")
    
    def test_agent_config_parsing(self):
        """Test that agent configurations are parsed correctly."""
        self.manager.load_agents()
        
        for name, agent in self.manager.agents.items():
            # Check required fields
            self.assertIsNotNone(agent.agent_name, f"Agent {name} missing agent_name")
            self.assertIsNotNone(agent.description, f"Agent {name} missing description")
            self.assertIsInstance(agent.tools, list, f"Agent {name} tools should be a list")
            self.assertIsNotNone(agent.model, f"Agent {name} missing model")
            self.assertIsNotNone(agent.cwd, f"Agent {name} missing cwd")
            self.assertIsNotNone(agent.system_prompt, f"Agent {name} missing system_prompt")
            print(f"✓ Agent '{agent.agent_name}' configuration valid")
    
    def test_get_agents_info(self):
        """Test getting agent information."""
        self.manager.load_agents()
        info = self.manager.get_agents_info()
        
        self.assertIsInstance(info, dict)
        self.assertEqual(len(info), len(self.manager.agents))
        
        for name, agent_info in info.items():
            self.assertIn('description', agent_info)
            self.assertIn('tools', agent_info)
            self.assertIn('model', agent_info)
        
        print("✓ Agent info retrieval working")


class TestServerStartup(unittest.TestCase):
    """Test server startup and configuration."""
    
    def test_imports(self):
        """Test that all required modules can be imported."""
        try:
            import fastmcp
            import yaml
            print("✓ All required modules can be imported")
        except ImportError as e:
            self.fail(f"Failed to import required module: {e}")
    
    def test_environment_setup(self):
        """Test environment variable handling."""
        # Test with TASK_AGENTS_PATH set
        test_path = "/tmp/test-agents"
        os.environ['TASK_AGENTS_PATH'] = test_path
        
        # Import server to trigger initialization
        from server import config_dir
        
        self.assertEqual(config_dir, test_path)
        print("✓ Environment variable handling works")
        
        # Clean up
        del os.environ['TASK_AGENTS_PATH']


if __name__ == "__main__":
    print("Running Task-Agents Server Tests...\n")
    unittest.main(verbosity=2)