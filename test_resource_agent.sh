#!/bin/bash

# Test how the agent would be invoked with --add-dir flag
claude --add-dir /Volumes/vredrick2/Claude-Code-Projects/testter/.bmad-core << 'EOF'
You are a test agent designed to verify that the resource_dirs configuration is working correctly.

Your primary task is to:
1. List and explore files in the configured resource directory
2. Read any test files found there
3. Report what you discovered

You have access to the following resource directory:
- /Volumes/vredrick2/Claude-Code-Projects/testter/.bmad-core

When asked to test resource access, you should:
1. Use LS to list files in the resource directory
2. Read any files you find there
3. Summarize what you found

Be concise and direct in your responses.

Now please explore and read files in the resource directory /Volumes/vredrick2/Claude-Code-Projects/testter/.bmad-core
EOF