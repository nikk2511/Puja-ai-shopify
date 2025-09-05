'use client'

import { useState, useRef, useEffect } from 'react'

export default function ChatInput({ 
  onSubmit, 
  disabled = false, 
  placeholder = "Ask about any puja, ritual, or ceremony..." 
}) {
  const [question, setQuestion] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const textareaRef = useRef(null)

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [question])

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault()
    
    const trimmedQuestion = question.trim()
    if (!trimmedQuestion || disabled) return

    onSubmit(trimmedQuestion)
    setQuestion('')
    setIsTyping(false)
  }

  // Handle key press for submit on Enter (but not Shift+Enter)
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  // Handle input change
  const handleInputChange = (e) => {
    setQuestion(e.target.value)
    setIsTyping(e.target.value.length > 0)
  }

  // Sample questions for inspiration
  const sampleQuestions = [
    "How do I perform Ganesh Puja at home?",
    "What materials do I need for Lakshmi Puja?",
    "What are the steps for morning aarti?",
    "How to celebrate Diwali properly?",
    "What mantras should I chant during Shiva Puja?"
  ]

  const [showSamples, setShowSamples] = useState(false)

  return (
    <form onSubmit={handleSubmit} className="flex items-end space-x-3">
      <div className="flex-1 relative">
        <textarea
          ref={textareaRef}
          value={question}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
          disabled={disabled}
          className={`
            w-full px-4 py-3 border border-gray-300 rounded-lg resize-none
            focus:ring-2 focus:ring-orange-500 focus:border-orange-500
            ${disabled ? 'opacity-50 cursor-not-allowed bg-gray-100' : 'bg-white'}
            ${question.length > 0 ? 'border-orange-300' : ''}
          `}
          rows={1}
          style={{ minHeight: '48px', maxHeight: '120px' }}
          maxLength={500}
          aria-label="Type your message"
        />
        
        {/* Character counter */}
        {question.length > 400 && (
          <div className="absolute bottom-1 right-2 text-xs text-gray-400">
            {question.length}/500
          </div>
        )}
      </div>

      <button
        type="submit"
        disabled={disabled || !question.trim()}
        className={`
          bg-orange-500 hover:bg-orange-600 text-white rounded-lg p-3
          transition-colors duration-200 flex-shrink-0
          ${(!question.trim() || disabled) ? 'opacity-50 cursor-not-allowed' : ''}
        `}
        aria-label="Send message"
      >
        {disabled ? (
          <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
        ) : (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        )}
      </button>
    </form>
  )
}
