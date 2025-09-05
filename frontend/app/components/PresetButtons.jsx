'use client'

import { useState, useEffect } from 'react'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Fallback preset data in case API is unavailable
const FALLBACK_PRESETS = [
  { id: 'ganesh', name: 'Ganesh Puja', description: 'Lord Ganesha worship guidance' },
  { id: 'durga', name: 'Durga Puja', description: 'Goddess Durga worship guidance' },
  { id: 'lakshmi', name: 'Lakshmi Puja', description: 'Goddess Lakshmi worship guidance' },
  { id: 'saraswati', name: 'Saraswati Puja', description: 'Goddess Saraswati worship guidance' },
  { id: 'shiva', name: 'Shiva Puja', description: 'Lord Shiva worship guidance' },
  { id: 'vishnu', name: 'Vishnu Puja', description: 'Lord Vishnu worship guidance' },
  { id: 'krishna', name: 'Krishna Puja', description: 'Lord Krishna worship guidance' },
  { id: 'hanuman', name: 'Hanuman Puja', description: 'Lord Hanuman worship guidance' },
  { id: 'kali', name: 'Kali Puja', description: 'Goddess Kali worship guidance' },
  { id: 'ram', name: 'Ram Puja', description: 'Lord Ram worship guidance' },
  { id: 'ganesha_chaturthi', name: 'Ganesha Chaturthi', description: 'Ganesha Chaturthi celebration' },
  { id: 'diwali', name: 'Diwali Puja', description: 'Diwali celebration and worship' },
  { id: 'navratri', name: 'Navratri', description: 'Navratri celebration guidance' },
  { id: 'holi', name: 'Holi', description: 'Holi celebration rituals' },
  { id: 'janmashtami', name: 'Janmashtami', description: 'Krishna Janmashtami celebration' },
  { id: 'general_home_puja', name: 'Daily Home Puja', description: 'General daily home worship' },
  { id: 'morning_prayers', name: 'Morning Prayers', description: 'Morning prayer guidance' },
  { id: 'evening_aarti', name: 'Evening Aarti', description: 'Evening aarti guidance' },
  { id: 'satyanarayan', name: 'Satyanarayan Puja', description: 'Satyanarayan puja guidance' },
  { id: 'griha_pravesh', name: 'Griha Pravesh', description: 'Housewarming ceremony guidance' }
]

// Icons for different preset categories
const PRESET_ICONS = {
  'ganesh': '🐘',
  'durga': '🗡️',
  'lakshmi': '🪙',
  'saraswati': '📚',
  'shiva': '🔱',
  'vishnu': '🪷',
  'krishna': '🪈',
  'hanuman': '💪',
  'kali': '⚡',
  'ram': '🏹',
  'ganesha_chaturthi': '🎊',
  'diwali': '🪔',
  'navratri': '💃',
  'holi': '🌈',
  'janmashtami': '🎂',
  'general_home_puja': '🏠',
  'morning_prayers': '🌅',
  'evening_aarti': '🌆',
  'satyanarayan': '🙏',
  'griha_pravesh': '🔑'
}

export default function PresetButtons({ onPresetSelect, selectedPreset, disabled = false, compact = false }) {
  const [presets, setPresets] = useState(FALLBACK_PRESETS)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showAll, setShowAll] = useState(false)

  // Fetch presets from API
  useEffect(() => {
    const fetchPresets = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/presets`)
        
        if (response.ok) {
          const data = await response.json()
          setPresets(data.presets || FALLBACK_PRESETS)
        } else {
          console.warn('Failed to fetch presets, using fallback')
          setPresets(FALLBACK_PRESETS)
        }
      } catch (err) {
        console.warn('Error fetching presets:', err)
        setError('Could not load presets from server')
        setPresets(FALLBACK_PRESETS)
      } finally {
        setLoading(false)
      }
    }

    fetchPresets()
  }, [])

  // Handle preset selection
  const handlePresetClick = (preset) => {
    if (disabled) return
    onPresetSelect(preset)
  }

  // Display loading state
  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {[...Array(6)].map((_, index) => (
          <div key={index} className="preset-button opacity-50 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-100 rounded w-full"></div>
          </div>
        ))}
      </div>
    )
  }

  // Show error state
  if (error) {
    return (
      <div className="text-center p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-yellow-700 text-sm">{error}</p>
        <p className="text-yellow-600 text-xs mt-1">Using default presets</p>
      </div>
    )
  }

  // Determine how many presets to show initially
  const initialShowCount = compact ? 6 : 12
  const presetsToShow = showAll ? presets : presets.slice(0, initialShowCount)
  const hasMore = presets.length > initialShowCount

  if (compact) {
    return (
      <div className="flex flex-wrap gap-2">
        {presets.slice(0, 8).map((preset) => {
          const icon = PRESET_ICONS[preset.id] || '🕉️'
          
          return (
            <button
              key={preset.id}
              onClick={() => handlePresetClick(preset)}
              disabled={disabled}
              className="bg-orange-100 hover:bg-orange-200 text-orange-700 px-3 py-2 rounded-lg text-xs transition-colors flex items-center space-x-1"
              aria-label={`Get guidance for ${preset.name}`}
            >
              <span className="text-sm">{icon}</span>
              <span>{preset.name}</span>
            </button>
          )
        })}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Preset Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {presetsToShow.map((preset) => {
          const isSelected = selectedPreset === preset.id
          const icon = PRESET_ICONS[preset.id] || '🕉️'
          
          return (
            <button
              key={preset.id}
              onClick={() => handlePresetClick(preset)}
              disabled={disabled}
              className={`
                preset-button text-left transition-all duration-200
                ${isSelected ? 'active' : ''}
                ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105'}
              `}
              aria-label={`Get guidance for ${preset.name}`}
            >
              <div className="flex items-start space-x-3">
                <span className="text-2xl flex-shrink-0 mt-1">
                  {icon}
                </span>
                <div className="min-w-0 flex-1">
                  <h4 className="font-medium text-gray-900 group-hover:text-puja-orange transition-colors duration-200">
                    {preset.name}
                  </h4>
                  <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                    {preset.description}
                  </p>
                </div>
              </div>
              
              {/* Selection indicator */}
              {isSelected && (
                <div className="absolute top-2 right-2 w-3 h-3 bg-puja-orange rounded-full"></div>
              )}
            </button>
          )
        })}
      </div>

      {/* Show More/Less Button */}
      {hasMore && (
        <div className="text-center">
          <button
            onClick={() => setShowAll(!showAll)}
            className="puja-button-secondary text-sm"
            disabled={disabled}
          >
            {showAll ? 'Show Less' : `Show ${presets.length - initialShowCount} More`}
          </button>
        </div>
      )}

      {/* Category Legend (optional) */}
      {showAll && (
        <div className="text-center text-xs text-gray-500 mt-4">
          <p>Choose any puja or festival for step-by-step guidance</p>
        </div>
      )}
    </div>
  )
}
