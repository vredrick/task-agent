import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { CodeBlock } from './code-block';
import { parseToolOutput } from '@/utils/parseToolOutput';
import { Copy, Check } from 'lucide-react';

interface ToolOutputEnhancedProps {
  output: string;
  errorText?: string;
  className?: string;
}

export const ToolOutputEnhanced: React.FC<ToolOutputEnhancedProps> = ({
  output,
  errorText,
  className
}) => {
  const [copied, setCopied] = useState(false);

  if (!output && !errorText) {
    return null;
  }

  // Parse the output to determine type and clean content
  const parsed = parseToolOutput(errorText || output);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(parsed.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <div className={cn('space-y-2 px-3 pb-3 overflow-hidden', className)}>
      <h4 className="font-medium text-muted-foreground text-xs uppercase tracking-wide">
        {errorText ? 'Error' : 'Response'}
      </h4>
      
      <div className={cn(
        'rounded-md overflow-hidden relative',
        errorText ? 'bg-destructive/10' : 'bg-muted/20'
      )}>
        <button
          onClick={handleCopy}
          className="absolute top-2 right-2 z-10 p-1.5 rounded bg-background/80 hover:bg-background transition-colors"
          title="Copy output"
        >
          {copied ? (
            <Check className="w-3.5 h-3.5 text-green-500" />
          ) : (
            <Copy className="w-3.5 h-3.5 text-muted-foreground hover:text-foreground" />
          )}
        </button>
        
        {parsed.type === 'code' ? (
          <div className="max-h-64 overflow-auto">
            <CodeBlock 
              code={parsed.content} 
              language={parsed.language || 'text'}
              showLineNumbers={parsed.lineNumbers}
            />
          </div>
        ) : parsed.type === 'error' ? (
          <div className="p-3 text-sm text-destructive break-words font-mono max-h-64 overflow-auto">
            {parsed.content}
          </div>
        ) : (
          <div className="p-3 text-sm text-foreground break-words max-h-64 overflow-auto">
            {parsed.content}
          </div>
        )}
      </div>
    </div>
  );
};