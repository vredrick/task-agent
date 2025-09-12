/**
 * Agent Manager for TypeScript SDK
 * Loads and manages AI agent configurations from Markdown files
 */

import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';
import { AgentConfig, AgentConfigRaw } from './types/agent';

export { AgentConfig } from './types/agent';

export class AgentManager {
  private agents: Map<string, AgentConfig> = new Map();
  private configDir: string;

  constructor(configDir: string = './task-agents') {
    this.configDir = configDir;
  }

  /**
   * Load all agent configurations from the config directory
   */
  async loadAgents(): Promise<void> {
    // Clear existing agents
    this.agents.clear();

    // Check if directory exists
    if (!fs.existsSync(this.configDir)) {
      console.warn(`Agent config directory ${this.configDir} does not exist`);
      return;
    }

    // Read all .md files in the directory
    const files = fs.readdirSync(this.configDir);
    
    for (const filename of files) {
      if (filename.endsWith('.md')) {
        const filepath = path.join(this.configDir, filename);
        try {
          const config = await this.loadAgentConfig(filepath);
          if (config) {
            // Use filename without extension as agent key
            const agentKey = filename.slice(0, -3); // Remove .md extension
            this.agents.set(agentKey, config);
            console.log(`Loaded agent: ${agentKey}`);
          }
        } catch (error) {
          console.error(`Failed to load agent from ${filepath}:`, error);
        }
      }
    }
  }

  /**
   * Load a single agent configuration from a Markdown file
   */
  private async loadAgentConfig(filepath: string): Promise<AgentConfig | null> {
    try {
      // Read file content
      const content = fs.readFileSync(filepath, 'utf-8');
      
      // Parse frontmatter and content
      const { data, content: markdownContent } = matter(content);
      const configData = data as AgentConfigRaw;
      
      if (!configData['agent-name']) {
        console.warn(`No agent-name found in ${filepath}`);
        return null;
      }

      // Extract system prompt (everything after "System-prompt:")
      const systemPromptMatch = markdownContent.match(/^System-prompt:\s*\n(.*)$/ms);
      const systemPrompt = systemPromptMatch ? systemPromptMatch[1].trim() : '';

      // Parse tools (comma-separated string to array)
      const tools = configData.tools 
        ? configData.tools.split(',').map(t => t.trim())
        : [];

      // Handle optional fields
      const optional = configData.optional || {};
      
      // Parse resume-session field
      let resumeSession: boolean | number = false;
      let maxExchanges = 0;
      
      const resumeValue = optional['resume-session'];
      if (typeof resumeValue === 'string') {
        const parts = resumeValue.split(' ');
        if (parts[0].toLowerCase() === 'true') {
          if (parts.length > 1) {
            resumeSession = parseInt(parts[1], 10);
            maxExchanges = resumeSession as number;
          } else {
            resumeSession = true;
            maxExchanges = 5; // Default
          }
        } else if (parts[0].toLowerCase() === 'false') {
          resumeSession = false;
          maxExchanges = 0;
        } else {
          // Try to parse as number
          const num = parseInt(parts[0], 10);
          if (!isNaN(num)) {
            resumeSession = num;
            maxExchanges = num;
          }
        }
      } else if (typeof resumeValue === 'boolean') {
        resumeSession = resumeValue;
        maxExchanges = resumeValue ? 5 : 0;
      } else if (typeof resumeValue === 'number') {
        resumeSession = resumeValue;
        maxExchanges = resumeValue;
      }

      // Parse resource_dirs
      const resourceDirs = optional.resource_dirs
        ? optional.resource_dirs.split(',').map(d => d.trim())
        : undefined;

      return {
        agentName: configData['agent-name'],
        description: configData.description || '',
        tools,
        model: configData.model || 'haiku',
        cwd: configData.cwd || '.',
        systemPrompt,
        resumeSession,
        resourceDirs,
        filePath: filepath,
        maxExchanges
      };
    } catch (error) {
      console.error(`Error loading agent config from ${filepath}:`, error);
      return null;
    }
  }

  /**
   * Get an agent configuration by name
   */
  getAgent(agentName: string): AgentConfig | undefined {
    return this.agents.get(agentName);
  }

  /**
   * List all available agents
   */
  listAgents(): string[] {
    return Array.from(this.agents.keys());
  }

  /**
   * Get all agent configurations
   */
  getAllAgents(): Map<string, AgentConfig> {
    return this.agents;
  }

  /**
   * Get agent metadata for API responses
   */
  getAgentMetadata(agentName: string) {
    const agent = this.agents.get(agentName);
    if (!agent) return null;

    return {
      name: agent.agentName,
      description: agent.description,
      tools: agent.tools,
      model: agent.model,
      resumeSession: typeof agent.resumeSession === 'boolean' ? agent.resumeSession : true,
      maxExchanges: agent.maxExchanges
    };
  }

  /**
   * Get all agents metadata for API listing
   */
  getAllAgentsMetadata() {
    return this.listAgents().map(name => this.getAgentMetadata(name)).filter(Boolean);
  }
}