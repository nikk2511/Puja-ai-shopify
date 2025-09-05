'use client'

import { useState, useEffect, useRef } from 'react'
import PresetButtons from './PresetButtons'
import ChatInput from './ChatInput'
import AnswerDisplay from './AnswerDisplay'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function PujaWidget({ isEmbedded = false }) {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const messagesEndRef = useRef(null)
  const [showPresets, setShowPresets] = useState(true)

  // Auto scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isLoading])

  // Add initial welcome message
  useEffect(() => {
    if (messages.length === 0) {
      const welcomeMessage = {
        id: 'welcome',
        type: 'ai',
        content: {
          summary: "Welcome to Puja AI Assistant! 🕉️",
          text: "I'm here to help you with Hindu puja and ritual guidance. You can ask me about any puja, festival celebration, or spiritual practice. I'll provide step-by-step instructions, required materials, mantras, and auspicious timings based on traditional texts and authentic sources."
        },
        timestamp: new Date().toISOString(),
        isWelcome: true
      }
      setMessages([welcomeMessage])
    }
  }, [])

  // Handle API requests
  const makeApiRequest = async (question, pujaId = null) => {
    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user', 
      content: question,
      timestamp: new Date().toISOString(),
      pujaId: pujaId
    }
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    setError(null)
    setShowPresets(false)

    try {
      const requestBody = {
        question: question,
        ...(pujaId && { puja_id: pujaId })
      }

      const response = await fetch(`${API_BASE_URL}/api/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()

      if (!data.ok) {
        throw new Error(data.error || 'Unknown error occurred')
      }

      // Add AI response message
      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: data.response,
        timestamp: new Date().toISOString(),
        sources: data.sources,
        cacheHit: data.cache_hit,
        costEstimate: data.cost_estimate
      }

      setMessages(prev => [...prev, aiMessage])

    } catch (err) {
      console.error('API Error:', err)
      
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: err.message,
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  // Handle preset button click
  const handlePresetSelect = (preset) => {
    makeApiRequest(`Guidance for ${preset.name}`, preset.id)
  }

  // Handle custom question
  const handleCustomQuestion = (question) => {
    makeApiRequest(question)
  }

  // Clear chat
  const handleClearChat = () => {
    setMessages([])
    setError(null)
    setShowPresets(true)
    setIsLoading(false)
  }

  // Message component
  const MessageBubble = ({ message }) => {
    if (message.type === 'user') {
      return (
        <div className="flex justify-end mb-4">
          <div className="max-w-xs lg:max-w-md xl:max-w-lg bg-orange-500 text-white rounded-lg px-4 py-2 shadow">
            <p className="text-sm">{message.content}</p>
            <p className="text-xs opacity-75 mt-1">
              {new Date(message.timestamp).toLocaleTimeString()}
            </p>
          </div>
        </div>
      )
    }

    if (message.type === 'error') {
      return (
        <div className="flex justify-start mb-4">
          <div className="max-w-xs lg:max-w-md xl:max-w-lg bg-red-100 border border-red-200 rounded-lg px-4 py-2 shadow">
            <div className="flex items-center space-x-2">
              <span className="text-red-500">⚠️</span>
              <p className="text-red-700 text-sm font-medium">Error occurred</p>
            </div>
            <p className="text-red-600 text-sm mt-1">{message.content}</p>
          </div>
        </div>
      )
    }

    // AI message
    return (
      <div className="flex justify-start mb-4">
        <div className="flex space-x-3 max-w-full">
          <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-red-500 rounded-full flex items-center justify-center flex-shrink-0">
            <span className="text-white text-sm">🕉</span>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg px-4 py-3 shadow-sm max-w-xs lg:max-w-md xl:max-w-2xl">
            {message.isWelcome ? (
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">{message.content.summary}</h3>
                <p className="text-sm text-gray-700">{message.content.text}</p>
              </div>
            ) : (
              <AnswerDisplay 
                response={message.content}
                sources={message.sources}
                cacheHit={message.cacheHit}
                costEstimate={message.costEstimate}
                compact={true}
              />
            )}
            <p className="text-xs text-gray-400 mt-2">
              {new Date(message.timestamp).toLocaleTimeString()}
              {message.cacheHit && <span className="ml-2 text-green-600">• Cached</span>}
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Chat Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-1">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        
        {/* Loading indicator */}
        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="flex space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-red-500 rounded-full flex items-center justify-center">
                <span className="text-white text-sm">🕉</span>
              </div>
              <div className="bg-gray-100 rounded-lg px-4 py-3 shadow-sm">
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  </div>
                  <span className="text-sm text-gray-600">Thinking...</span>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Empty state */}
        {messages.length === 1 && messages[0].isWelcome && (
          <div className="text-center py-8">
            <div className="text-4xl mb-4">🕉️</div>
            <p className="text-gray-500 text-sm mb-6">
              Ask me anything about Hindu puja, rituals, or ceremonies
            </p>
            
            {/* Quick action buttons */}
            <div className="flex flex-wrap justify-center gap-2 mb-6">
              <button 
                onClick={() => handleCustomQuestion("How to perform Ganesh Puja?")}
                className="bg-orange-100 hover:bg-orange-200 text-orange-700 px-3 py-1 rounded-full text-sm transition-colors"
              >
                Ganesh Puja
              </button>
              <button 
                onClick={() => handleCustomQuestion("Lakshmi Puja steps")}
                className="bg-orange-100 hover:bg-orange-200 text-orange-700 px-3 py-1 rounded-full text-sm transition-colors"
              >
                Lakshmi Puja
              </button>
              <button 
                onClick={() => handleCustomQuestion("Diwali celebration guide")}
                className="bg-orange-100 hover:bg-orange-200 text-orange-700 px-3 py-1 rounded-full text-sm transition-colors"
              >
                Diwali Guide
              </button>
              <button 
                onClick={() => handleCustomQuestion("Morning aarti procedure")}
                className="bg-orange-100 hover:bg-orange-200 text-orange-700 px-3 py-1 rounded-full text-sm transition-colors"
              >
                Morning Aarti
              </button>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Preset buttons (show initially or when no messages) */}
      {showPresets && messages.length <= 1 && (
        <div className="border-t border-gray-200 px-4 py-4">
          <div className="mb-3">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Quick Puja Guide</h3>
            <PresetButtons 
              onPresetSelect={handlePresetSelect}
              disabled={isLoading}
              compact={true}
            />
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="border-t border-gray-200 px-4 py-4 bg-white">
        <div className="flex items-center space-x-3">
          <div className="flex-1">
            <ChatInput 
              onSubmit={handleCustomQuestion}
              disabled={isLoading}
              placeholder="Ask about any puja, ritual, or ceremony..."
            />
          </div>
          {messages.length > 1 && (
            <button
              onClick={handleClearChat}
              className="bg-gray-100 hover:bg-gray-200 text-gray-600 px-3 py-2 rounded-lg text-sm transition-colors"
              title="Clear chat"
            >
              🗑️
            </button>
          )}
        </div>
        
        {/* Disclaimer */}
        <p className="text-xs text-gray-400 mt-2 text-center">
          AI guidance based on traditional texts. Consult qualified priests for important ceremonies.
        </p>
      </div>
    </div>
  )
}
