/**
 * Parse and clean tool output for better display
 */

export function parseToolOutput(rawOutput: string): {
  type: 'text' | 'code' | 'file' | 'error';
  content: string;
  language?: string;
  fileName?: string;
  lineNumbers?: boolean;
} {
  // Check if it's an error
  if (rawOutput.includes('Error:') || rawOutput.includes('error:')) {
    return {
      type: 'error',
      content: rawOutput
    };
  }

  // Check if it's file content with line numbers (like from Read tool)
  const lineNumberPattern = /^\s*\d+→/m;
  if (lineNumberPattern.test(rawOutput)) {
    // Extract clean content without line numbers
    const lines = rawOutput.split('\n');
    const cleanedLines = lines.map(line => {
      // Remove line number prefix (e.g., "     1→" or "   123→")
      const match = line.match(/^\s*\d+→(.*)$/);
      return match ? match[1] : line;
    });
    
    // Try to detect language from content or file extension
    const firstLine = cleanedLines[0] || '';
    let language = 'text';
    
    // Common shebang patterns
    if (firstLine.startsWith('#!/usr/bin/env python') || firstLine.startsWith('#!/usr/bin/python')) {
      language = 'python';
    } else if (firstLine.startsWith('#!/usr/bin/env node') || firstLine.startsWith('#!/usr/bin/node')) {
      language = 'javascript';
    } else if (firstLine.startsWith('#!/bin/bash') || firstLine.startsWith('#!/bin/sh')) {
      language = 'bash';
    }
    // Check for common patterns in content
    else if (rawOutput.includes('import ') || rawOutput.includes('from ') || rawOutput.includes('def ')) {
      language = 'python';
    } else if (rawOutput.includes('const ') || rawOutput.includes('function ') || rawOutput.includes('import {')) {
      language = 'javascript';
    } else if (rawOutput.includes('interface ') || rawOutput.includes('type ') || rawOutput.includes(': React.FC')) {
      language = 'typescript';
    } else if (rawOutput.includes('<!DOCTYPE') || rawOutput.includes('<html')) {
      language = 'html';
    } else if (rawOutput.includes('{') && rawOutput.includes('}') && rawOutput.includes(':')) {
      // Might be JSON
      try {
        JSON.parse(cleanedLines.join('\n'));
        language = 'json';
      } catch {
        // Not valid JSON
      }
    } else if (rawOutput.includes('# ') && (rawOutput.includes('## ') || rawOutput.includes('### '))) {
      language = 'markdown';
    }

    return {
      type: 'code',
      content: cleanedLines.join('\n'),
      language,
      lineNumbers: true
    };
  }

  // Check if it's JSON output
  try {
    const parsed = JSON.parse(rawOutput);
    return {
      type: 'code',
      content: JSON.stringify(parsed, null, 2),
      language: 'json'
    };
  } catch {
    // Not JSON
  }

  // Check if it's structured command output (like ls, git status, etc.)
  if (rawOutput.includes('\t') || rawOutput.match(/^\s{2,}/m)) {
    return {
      type: 'code',
      content: rawOutput,
      language: 'text'
    };
  }

  // Default to plain text
  return {
    type: 'text',
    content: rawOutput
  };
}

/**
 * Truncate long output with a "show more" option
 */
export function truncateOutput(content: string, maxLines: number = 20): {
  content: string;
  isTruncated: boolean;
  fullContent: string;
} {
  const lines = content.split('\n');
  if (lines.length <= maxLines) {
    return {
      content,
      isTruncated: false,
      fullContent: content
    };
  }

  return {
    content: lines.slice(0, maxLines).join('\n'),
    isTruncated: true,
    fullContent: content
  };
}