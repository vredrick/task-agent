import React from 'react'
import { Response } from '@/components/ai-elements/response'
import { CodeBlock, CodeBlockCopyButton } from '@/components/ai-elements/code-block'
import { useStreamingText } from '@/hooks/useStreamingText'

interface StreamingMessageProps {
  content: string
  isStreaming?: boolean
  className?: string
}

export function StreamingMessage({ content, isStreaming = false, className }: StreamingMessageProps) {
  // Use the streaming hook to animate text
  const { displayedText, isAnimating } = useStreamingText(
    content,
    isStreaming,
    {
      wordDelay: 40, // Slower for more noticeable streaming effect
      characterMode: false // Word by word looks more natural
    }
  )

  return (
    <>
      <Response 
        className={className}
        parseIncompleteMarkdown={true}
        components={{
          pre: ({ children, ...props }) => {
            // Extract code content and language from the pre/code elements
            const codeElement = children as any
            const className = codeElement?.props?.className || ''
            const language = className.replace(/language-/, '') || 'plaintext'
            const code = codeElement?.props?.children || ''
            
            // Don't render empty code blocks during streaming
            if (!code || code.trim() === '') {
              return null
            }
            
            return (
              <div className="my-3">
                <CodeBlock 
                  code={code}
                  language={language}
                  showLineNumbers={code.split('\n').length > 5}
                  className="border-blue-900/30 dark:border-blue-400/30"
                >
                  <CodeBlockCopyButton className="hover:bg-blue-900/10 dark:hover:bg-blue-400/10" />
                </CodeBlock>
              </div>
            )
          }
        }}
      >
        {displayedText}
      </Response>
    </>
  )
}