'use client'

import { useState, useEffect } from 'react'
import PujaWidget from './components/PujaWidget'

export default function Home() {
  const [isShopifyEmbedded, setIsShopifyEmbedded] = useState(false)

  useEffect(() => {
    // Check if running in Shopify admin or embedded context
    const checkShopifyContext = () => {
      try {
        // Check for Shopify App Bridge context
        if (window.parent !== window || window.top !== window) {
          setIsShopifyEmbedded(true)
        }
        
        // Check URL parameters for Shopify context
        const urlParams = new URLSearchParams(window.location.search)
        if (urlParams.get('embedded') === '1' || urlParams.get('shop')) {
          setIsShopifyEmbedded(true)
        }
      } catch (error) {
        console.log('Error checking Shopify context:', error)
      }
    }

    checkShopifyContext()
  }, [])

  return (
    <main className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200 flex-shrink-0">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-red-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">🕉</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                Puja AI Assistant
              </h1>
              <p className="text-gray-500 text-sm">
                Your guide to Hindu puja and ritual practices
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Container */}
      <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full">
        <PujaWidget isEmbedded={isShopifyEmbedded} />
      </div>
    </main>
  )
}
