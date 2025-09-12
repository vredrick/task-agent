"use strict";
/**
 * Agent Manager for TypeScript SDK
 * Loads and manages AI agent configurations from Markdown files
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.AgentManager = void 0;
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const gray_matter_1 = __importDefault(require("gray-matter"));
class AgentManager {
    agents = new Map();
    configDir;
    constructor(configDir = './task-agents') {
        this.configDir = configDir;
    }
    /**
     * Load all agent configurations from the config directory
     */
    async loadAgents() {
        // Clear existing agents
        this.agents.clear();
        // Check if directory exists
        if (!fs_1.default.existsSync(this.configDir)) {
            console.warn(`Agent config directory ${this.configDir} does not exist`);
            return;
        }
        // Read all .md files in the directory
        const files = fs_1.default.readdirSync(this.configDir);
        for (const filename of files) {
            if (filename.endsWith('.md')) {
                const filepath = path_1.default.join(this.configDir, filename);
                try {
                    const config = await this.loadAgentConfig(filepath);
                    if (config) {
                        // Use filename without extension as agent key
                        const agentKey = filename.slice(0, -3); // Remove .md extension
                        this.agents.set(agentKey, config);
                        console.log(`Loaded agent: ${agentKey}`);
                    }
                }
                catch (error) {
                    console.error(`Failed to load agent from ${filepath}:`, error);
                }
            }
        }
    }
    /**
     * Load a single agent configuration from a Markdown file
     */
    async loadAgentConfig(filepath) {
        try {
            // Read file content
            const content = fs_1.default.readFileSync(filepath, 'utf-8');
            // Parse frontmatter and content
            const { data, content: markdownContent } = (0, gray_matter_1.default)(content);
            const configData = data;
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
            let resumeSession = false;
            let maxExchanges = 0;
            const resumeValue = optional['resume-session'];
            if (typeof resumeValue === 'string') {
                const parts = resumeValue.split(' ');
                if (parts[0].toLowerCase() === 'true') {
                    if (parts.length > 1) {
                        resumeSession = parseInt(parts[1], 10);
                        maxExchanges = resumeSession;
                    }
                    else {
                        resumeSession = true;
                        maxExchanges = 5; // Default
                    }
                }
                else if (parts[0].toLowerCase() === 'false') {
                    resumeSession = false;
                    maxExchanges = 0;
                }
                else {
                    // Try to parse as number
                    const num = parseInt(parts[0], 10);
                    if (!isNaN(num)) {
                        resumeSession = num;
                        maxExchanges = num;
                    }
                }
            }
            else if (typeof resumeValue === 'boolean') {
                resumeSession = resumeValue;
                maxExchanges = resumeValue ? 5 : 0;
            }
            else if (typeof resumeValue === 'number') {
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
        }
        catch (error) {
            console.error(`Error loading agent config from ${filepath}:`, error);
            return null;
        }
    }
    /**
     * Get an agent configuration by name
     */
    getAgent(agentName) {
        return this.agents.get(agentName);
    }
    /**
     * List all available agents
     */
    listAgents() {
        return Array.from(this.agents.keys());
    }
    /**
     * Get all agent configurations
     */
    getAllAgents() {
        return this.agents;
    }
    /**
     * Get agent metadata for API responses
     */
    getAgentMetadata(agentName) {
        const agent = this.agents.get(agentName);
        if (!agent)
            return null;
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
exports.AgentManager = AgentManager;
//# sourceMappingURL=agent_manager.js.map