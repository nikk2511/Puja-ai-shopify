'use client'

import { useState } from 'react'

export default function AnswerDisplay({ 
  response, 
  sources = [], 
  rawText = '', 
  costEstimate = null, 
  cacheHit = false,
  compact = false 
}) {
  const [showSources, setShowSources] = useState(false)
  const [showRawText, setShowRawText] = useState(false)
  const [showCostInfo, setShowCostInfo] = useState(false)

  if (!response) {
    return (
      <div className="text-center p-8 text-gray-500">
        <p>No response to display</p>
      </div>
    )
  }

  // Extract data from response
  const {
    summary = '',
    steps = [],
    materials = [],
    timings = [],
    mantras = [],
    sources: responseSources = [],
    notes = ''
  } = response

  if (compact) {
    return (
      <div className="space-y-3">
        {/* Summary */}
        {summary && (
          <div>
            <h3 className="font-semibold text-gray-900 text-sm mb-1">{summary}</h3>
          </div>
        )}

        {/* Steps - compact */}
        {steps && steps.length > 0 && (
          <div>
            <h4 className="font-medium text-gray-800 text-xs mb-2 flex items-center">
              <span className="mr-1">📋</span> Steps
            </h4>
            <div className="space-y-2">
              {steps.slice(0, 3).map((step, index) => (
                <div key={index} className="text-sm">
                  <span className="font-medium text-gray-700">
                    {index + 1}. {step.title || `Step ${index + 1}`}
                  </span>
                  <p className="text-gray-600 text-xs mt-1">
                    {step.instruction.length > 100 
                      ? `${step.instruction.substring(0, 100)}...` 
                      : step.instruction
                    }
                  </p>
                </div>
              ))}
              {steps.length > 3 && (
                <p className="text-xs text-gray-500">
                  + {steps.length - 3} more steps...
                </p>
              )}
            </div>
          </div>
        )}

        {/* Materials - compact */}
        {materials && materials.length > 0 && (
          <div>
            <h4 className="font-medium text-gray-800 text-xs mb-2 flex items-center">
              <span className="mr-1">🛍️</span> Materials
            </h4>
            <div className="flex flex-wrap gap-1">
              {materials.slice(0, 5).map((material, index) => (
                <span key={index} className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
                  {material.name}
                </span>
              ))}
              {materials.length > 5 && (
                <span className="text-xs text-gray-500">
                  +{materials.length - 5} more
                </span>
              )}
            </div>
          </div>
        )}

        {/* Mantras - compact */}
        {mantras && mantras.length > 0 && (
          <div>
            <h4 className="font-medium text-gray-800 text-xs mb-2 flex items-center">
              <span className="mr-1">🕉️</span> Mantras
            </h4>
            <div className="bg-orange-50 rounded px-2 py-1">
              <p className="text-orange-800 text-xs">
                {mantras[0].length > 80 
                  ? `${mantras[0].substring(0, 80)}...` 
                  : mantras[0]
                }
              </p>
              {mantras.length > 1 && (
                <p className="text-xs text-orange-600 mt-1">
                  +{mantras.length - 1} more mantras
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Cache Hit Indicator */}
      {cacheHit && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-sm text-green-700">
          <span className="font-medium">⚡ Cached Result</span> - This response was served from cache for faster delivery.
        </div>
      )}

      {/* Summary */}
      {summary && (
        <div className="bg-gradient-to-r from-puja-orange to-puja-red text-white rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-2">Summary</h2>
          <p className="text-orange-100 leading-relaxed">{summary}</p>
        </div>
      )}

      {/* Steps */}
      {steps && steps.length > 0 && (
        <div className="puja-card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <span className="text-xl mr-2">📋</span>
            Step-by-Step Procedure
          </h3>
          <div className="space-y-4">
            {steps.map((step, index) => (
              <div key={index} className="step-item">
                <div className="step-number">
                  {step.step_no || index + 1}
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900 mb-1">
                    {step.title || `Step ${step.step_no || index + 1}`}
                  </h4>
                  <p className="text-gray-700 leading-relaxed">
                    {step.instruction}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Materials */}
      {materials && materials.length > 0 && (
        <div className="puja-card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <span className="text-xl mr-2">🛍️</span>
            Required Materials
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {materials.map((material, index) => (
              <div key={index} className="material-item">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">
                    {material.name}
                  </h4>
                  {material.description && (
                    <p className="text-sm text-gray-600 mt-1">
                      {material.description}
                    </p>
                  )}
                  {material.quantity && (
                    <p className="text-sm text-gray-500 mt-1">
                      Quantity: {material.quantity}
                    </p>
                  )}
                </div>
                {material.product_match && (
                  <a
                    href={material.product_match}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="product-link flex items-center space-x-1 ml-3"
                    aria-label={`Buy ${material.name}`}
                  >
                    <span>🛒</span>
                    <span>Buy</span>
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Timings */}
      {timings && timings.length > 0 && (
        <div className="puja-card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <span className="text-xl mr-2">⏰</span>
            Auspicious Timings
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {timings.map((timing, index) => (
              <div key={index} className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                <p className="text-yellow-800 font-medium">{timing}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Mantras */}
      {mantras && mantras.length > 0 && (
        <div className="puja-card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <span className="text-xl mr-2">🕉️</span>
            Mantras & Chants
          </h3>
          <div className="space-y-3">
            {mantras.map((mantra, index) => (
              <div key={index} className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                <p className="text-orange-900 font-sanskrit text-lg leading-relaxed">
                  {mantra}
                </p>
                <button
                  onClick={() => {
                    // Copy to clipboard
                    navigator.clipboard.writeText(mantra)
                  }}
                  className="mt-2 text-xs text-orange-600 hover:text-orange-800 transition-colors duration-200"
                  title="Copy mantra to clipboard"
                >
                  📋 Copy
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Notes */}
      {notes && (
        <div className="puja-card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <span className="text-xl mr-2">📝</span>
            Additional Notes
          </h3>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-blue-900 leading-relaxed">{notes}</p>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-3 pt-4 border-t no-print">
        <button
          onClick={() => window.print()}
          className="puja-button-secondary flex items-center space-x-2"
        >
          <span>🖨️</span>
          <span>Print</span>
        </button>
        
        <button
          onClick={() => setShowSources(!showSources)}
          className="puja-button-secondary flex items-center space-x-2"
        >
          <span>📚</span>
          <span>{showSources ? 'Hide' : 'Show'} Sources</span>
        </button>

        {process.env.NODE_ENV === 'development' && (
          <>
            <button
              onClick={() => setShowRawText(!showRawText)}
              className="puja-button-secondary flex items-center space-x-2"
            >
              <span>🔍</span>
              <span>{showRawText ? 'Hide' : 'Show'} Raw</span>
            </button>
            
            {costEstimate && (
              <button
                onClick={() => setShowCostInfo(!showCostInfo)}
                className="puja-button-secondary flex items-center space-x-2"
              >
                <span>💰</span>
                <span>Cost Info</span>
              </button>
            )}
          </>
        )}
      </div>

      {/* Sources Panel */}
      {showSources && (sources.length > 0 || responseSources.length > 0) && (
        <div className="puja-card animate-slide-up">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            📖 Source References
          </h3>
          <div className="space-y-3">
            {(responseSources.length > 0 ? responseSources : sources).map((source, index) => (
              <div key={index} className="source-citation">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="font-medium text-gray-700 mb-1">
                      {source.book || 'Unknown Book'}
                      {source.page && ` - Page ${source.page}`}
                    </p>
                    {source.snippet && (
                      <p className="text-gray-600 text-sm italic">
                        "{source.snippet}"
                      </p>
                    )}
                  </div>
                  {source.distance !== undefined && (
                    <span className="text-xs text-gray-400 ml-2">
                      Score: {(1 - source.distance).toFixed(3)}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Raw Text Panel (Development) */}
      {showRawText && rawText && process.env.NODE_ENV === 'development' && (
        <div className="puja-card animate-slide-up">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            🤖 Raw LLM Response
          </h3>
          <pre className="bg-gray-100 p-4 rounded-lg text-xs overflow-auto max-h-60 whitespace-pre-wrap">
            {rawText}
          </pre>
        </div>
      )}

      {/* Cost Information Panel (Development) */}
      {showCostInfo && costEstimate && process.env.NODE_ENV === 'development' && (
        <div className="puja-card animate-slide-up">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            💰 Cost Estimate
          </h3>
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Input Cost:</p>
                <p className="font-mono">${costEstimate.input_cost?.toFixed(6) || '0.000000'}</p>
              </div>
              <div>
                <p className="text-gray-600">Output Cost:</p>
                <p className="font-mono">${costEstimate.output_cost?.toFixed(6) || '0.000000'}</p>
              </div>
              <div>
                <p className="text-gray-600">Total Cost:</p>
                <p className="font-mono font-bold">${costEstimate.total_cost?.toFixed(6) || '0.000000'}</p>
              </div>
              <div>
                <p className="text-gray-600">Tokens:</p>
                <p className="font-mono">{costEstimate.prompt_tokens || 0} + {costEstimate.completion_tokens || 0}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
