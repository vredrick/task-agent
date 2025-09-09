import { useState, useEffect, useRef } from 'react'

interface UseStreamingTextOptions {
  // Speed in milliseconds between words
  wordDelay?: number
  // Whether to stream character by character instead of word by word
  characterMode?: boolean
  // Callback when streaming completes
  onComplete?: () => void
}

export function useStreamingText(
  fullText: string,
  isStreaming: boolean,
  options: UseStreamingTextOptions = {}
) {
  const {
    wordDelay = 30, // 30ms between words for smooth reading
    characterMode = false,
    onComplete
  } = options

  const [displayedText, setDisplayedText] = useState('')
  const [isAnimating, setIsAnimating] = useState(false)
  const animationFrameRef = useRef<number>()
  const currentIndexRef = useRef(0)
  const lastUpdateTimeRef = useRef(0)
  const textQueueRef = useRef<string>('')

  useEffect(() => {
    // When new text comes in, add it to the queue
    if (fullText && fullText !== textQueueRef.current) {
      textQueueRef.current = fullText
      
      // If this is a fresh message (not continuation), reset
      if (!displayedText || fullText.length < displayedText.length) {
        setDisplayedText('')
        currentIndexRef.current = 0
      }
      
      // Start animation if not already running
      if (!isAnimating && isStreaming) {
        setIsAnimating(true)
        currentIndexRef.current = displayedText.length
      }
    }
  }, [fullText, isStreaming, displayedText.length, isAnimating])

  useEffect(() => {
    if (!isAnimating || !isStreaming) return

    const animate = (timestamp: number) => {
      // Control animation speed
      if (timestamp - lastUpdateTimeRef.current < wordDelay) {
        animationFrameRef.current = requestAnimationFrame(animate)
        return
      }

      const targetText = textQueueRef.current
      const currentLength = currentIndexRef.current

      if (currentLength < targetText.length) {
        let nextIndex = currentLength

        if (characterMode) {
          // Character by character
          nextIndex = currentLength + 1
        } else {
          // Word by word - find the next word boundary
          let foundSpace = false
          for (let i = currentLength + 1; i <= targetText.length; i++) {
            if (i === targetText.length || targetText[i] === ' ' || targetText[i] === '\n') {
              nextIndex = i
              foundSpace = true
              break
            }
          }
          // If no space found, just add one character (for long words)
          if (!foundSpace) {
            nextIndex = Math.min(currentLength + 1, targetText.length)
          }
        }

        currentIndexRef.current = nextIndex
        setDisplayedText(targetText.substring(0, nextIndex))
        lastUpdateTimeRef.current = timestamp
        animationFrameRef.current = requestAnimationFrame(animate)
      } else {
        // Animation complete
        setIsAnimating(false)
        if (onComplete) {
          onComplete()
        }
      }
    }

    animationFrameRef.current = requestAnimationFrame(animate)

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [isAnimating, isStreaming, characterMode, wordDelay, onComplete])

  // When streaming stops, immediately show all remaining text
  useEffect(() => {
    if (!isStreaming && textQueueRef.current) {
      setDisplayedText(textQueueRef.current)
      setIsAnimating(false)
      currentIndexRef.current = textQueueRef.current.length
    }
  }, [isStreaming])

  return {
    displayedText,
    isAnimating,
    // Allow skipping animation
    skipAnimation: () => {
      setDisplayedText(textQueueRef.current)
      setIsAnimating(false)
      currentIndexRef.current = textQueueRef.current.length
    }
  }
}