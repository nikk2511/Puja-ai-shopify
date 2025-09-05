/**
 * Puja AI Chatbot - Embeddable Widget
 * 
 * This is a standalone JavaScript widget that can be embedded in any website,
 * including Shopify stores, to provide AI-powered puja guidance.
 * 
 * Usage:
 * <script src="https://your-domain.com/embed.js"></script>
 * <div id="puja-ai-widget"></div>
 * 
 * Configuration (optional):
 * <script>
 *   window.pujaAIConfig = {
 *     apiUrl: 'https://your-backend.com',
 *     theme: 'light', // 'light' or 'dark'
 *     position: 'bottom-right', // 'bottom-right', 'bottom-left', etc.
 *     autoOpen: false,
 *     language: 'en'
 *   };
 * </script>
 */

(function() {
  'use strict';

  // Configuration
  const DEFAULT_CONFIG = {
    apiUrl: 'http://localhost:8000',
    theme: 'light',
    position: 'bottom-right',
    autoOpen: false,
    language: 'en',
    containerId: 'puja-ai-widget'
  };

  // Merge user config with defaults
  const config = Object.assign({}, DEFAULT_CONFIG, window.pujaAIConfig || {});

  // Global state
  let isOpen = false;
  let isLoading = false;
  let currentResponse = null;
  let presets = [];

  // Utility functions
  function createElement(tag, className, innerHTML) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (innerHTML) element.innerHTML = innerHTML;
    return element;
  }

  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  // API functions
  async function fetchPresets() {
    try {
      const response = await fetch(`${config.apiUrl}/api/presets`);
      if (response.ok) {
        const data = await response.json();
        presets = data.presets || [];
      }
    } catch (error) {
      console.warn('Failed to fetch presets:', error);
      // Fallback presets
      presets = [
        { id: 'ganesh', name: 'Ganesh Puja', description: 'Lord Ganesha worship guidance' },
        { id: 'durga', name: 'Durga Puja', description: 'Goddess Durga worship guidance' },
        { id: 'lakshmi', name: 'Lakshmi Puja', description: 'Goddess Lakshmi worship guidance' },
        { id: 'diwali', name: 'Diwali Puja', description: 'Diwali celebration guidance' }
      ];
    }
  }

  async function askQuestion(question, pujaId = null) {
    isLoading = true;
    updateLoadingState();

    try {
      const requestBody = {
        question: question,
        ...(pujaId && { puja_id: pujaId })
      };

      const response = await fetch(`${config.apiUrl}/api/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      if (!data.ok) {
        throw new Error(data.error || 'Unknown error occurred');
      }

      currentResponse = data.response;
      renderResponse();

    } catch (error) {
      renderError(error.message);
    } finally {
      isLoading = false;
      updateLoadingState();
    }
  }

  // UI rendering functions
  function createStyles() {
    const styles = `
      .puja-ai-widget {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        position: fixed;
        ${config.position.includes('bottom') ? 'bottom: 20px;' : 'top: 20px;'}
        ${config.position.includes('right') ? 'right: 20px;' : 'left: 20px;'}
        width: 380px;
        max-width: calc(100vw - 40px);
        max-height: calc(100vh - 40px);
        background: white;
        border-radius: 12px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        z-index: 10000;
        display: none;
        flex-direction: column;
        overflow: hidden;
      }

      .puja-ai-widget.open {
        display: flex;
      }

      .puja-ai-header {
        background: linear-gradient(135deg, #FF6B35 0%, #D73027 100%);
        color: white;
        padding: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      .puja-ai-title {
        font-size: 16px;
        font-weight: 600;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .puja-ai-close {
        background: none;
        border: none;
        color: white;
        font-size: 20px;
        cursor: pointer;
        padding: 4px;
        border-radius: 4px;
        opacity: 0.8;
        transition: opacity 0.2s;
      }

      .puja-ai-close:hover {
        opacity: 1;
      }

      .puja-ai-content {
        flex: 1;
        overflow-y: auto;
        padding: 16px;
        max-height: 500px;
      }

      .puja-ai-preset-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-bottom: 16px;
      }

      .puja-ai-preset-btn {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 12px;
        text-align: left;
        cursor: pointer;
        transition: all 0.2s;
        font-size: 13px;
      }

      .puja-ai-preset-btn:hover {
        border-color: #FF6B35;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      }

      .puja-ai-preset-name {
        font-weight: 600;
        color: #374151;
        margin-bottom: 4px;
      }

      .puja-ai-preset-desc {
        color: #6b7280;
        font-size: 11px;
      }

      .puja-ai-input-section {
        border-top: 1px solid #e5e7eb;
        padding-top: 16px;
        margin-top: 16px;
      }

      .puja-ai-textarea {
        width: 100%;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 12px;
        font-size: 14px;
        resize: none;
        outline: none;
        transition: border-color 0.2s;
        box-sizing: border-box;
      }

      .puja-ai-textarea:focus {
        border-color: #FF6B35;
      }

      .puja-ai-submit {
        background: linear-gradient(135deg, #FF6B35 0%, #D73027 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 16px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        margin-top: 8px;
        transition: opacity 0.2s;
        width: 100%;
      }

      .puja-ai-submit:hover:not(:disabled) {
        opacity: 0.9;
      }

      .puja-ai-submit:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }

      .puja-ai-loading {
        text-align: center;
        padding: 20px;
        color: #6b7280;
      }

      .puja-ai-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 2px solid #e5e7eb;
        border-radius: 50%;
        border-top-color: #FF6B35;
        animation: spin 1s ease-in-out infinite;
        margin-right: 8px;
      }

      @keyframes spin {
        to { transform: rotate(360deg); }
      }

      .puja-ai-response {
        animation: slideUp 0.3s ease-out;
      }

      @keyframes slideUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }

      .puja-ai-summary {
        background: linear-gradient(135deg, #FF6B35 0%, #D73027 100%);
        color: white;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 16px;
      }

      .puja-ai-section {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
      }

      .puja-ai-section-title {
        font-weight: 600;
        color: #374151;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .puja-ai-step {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        margin-bottom: 12px;
        padding: 12px;
        background: white;
        border-radius: 6px;
        border: 1px solid #e5e7eb;
      }

      .puja-ai-step-number {
        background: linear-gradient(135deg, #FF6B35 0%, #D73027 100%);
        color: white;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: 600;
        flex-shrink: 0;
      }

      .puja-ai-step-content h4 {
        font-weight: 600;
        color: #374151;
        margin: 0 0 4px 0;
        font-size: 14px;
      }

      .puja-ai-step-content p {
        color: #6b7280;
        margin: 0;
        font-size: 13px;
        line-height: 1.4;
      }

      .puja-ai-material {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 12px;
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        margin-bottom: 8px;
      }

      .puja-ai-material-info h4 {
        font-weight: 600;
        color: #374151;
        margin: 0 0 2px 0;
        font-size: 13px;
      }

      .puja-ai-material-info p {
        color: #6b7280;
        margin: 0;
        font-size: 11px;
      }

      .puja-ai-buy-link {
        background: #FF6B35;
        color: white;
        text-decoration: none;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 500;
        transition: background 0.2s;
      }

      .puja-ai-buy-link:hover {
        background: #D73027;
      }

      .puja-ai-error {
        background: #fef2f2;
        border: 1px solid #fecaca;
        color: #dc2626;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 16px;
        font-size: 14px;
      }

      .puja-ai-toggle {
        position: fixed;
        ${config.position.includes('bottom') ? 'bottom: 20px;' : 'top: 20px;'}
        ${config.position.includes('right') ? 'right: 20px;' : 'left: 20px;'}
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #FF6B35 0%, #D73027 100%);
        color: white;
        border: none;
        border-radius: 50%;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        transition: transform 0.2s;
      }

      .puja-ai-toggle:hover {
        transform: scale(1.05);
      }

      @media (max-width: 480px) {
        .puja-ai-widget {
          width: calc(100vw - 20px);
          left: 10px !important;
          right: 10px !important;
        }
        
        .puja-ai-preset-grid {
          grid-template-columns: 1fr;
        }
      }
    `;

    const styleSheet = document.createElement('style');
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);
  }

  function createToggleButton() {
    const button = createElement('button', 'puja-ai-toggle', '🕉️');
    button.onclick = toggleWidget;
    button.setAttribute('aria-label', 'Open Puja AI Assistant');
    document.body.appendChild(button);
    return button;
  }

  function createWidget() {
    const widget = createElement('div', 'puja-ai-widget');
    widget.innerHTML = `
      <div class="puja-ai-header">
        <h3 class="puja-ai-title">
          <span>🕉️</span>
          Puja AI Assistant
        </h3>
        <button class="puja-ai-close" onclick="PujaAI.close()" aria-label="Close">×</button>
      </div>
      <div class="puja-ai-content" id="puja-ai-content">
        <!-- Content will be rendered here -->
      </div>
    `;

    document.body.appendChild(widget);
    return widget;
  }

  function renderPresets() {
    const content = document.getElementById('puja-ai-content');
    
    const presetsHTML = presets.slice(0, 8).map(preset => `
      <button class="puja-ai-preset-btn" onclick="PujaAI.selectPreset('${preset.id}', '${preset.name}')">
        <div class="puja-ai-preset-name">${preset.name}</div>
        <div class="puja-ai-preset-desc">${preset.description}</div>
      </button>
    `).join('');

    content.innerHTML = `
      <div class="puja-ai-preset-grid">
        ${presetsHTML}
      </div>
      <div class="puja-ai-input-section">
        <textarea 
          class="puja-ai-textarea" 
          placeholder="Ask about any puja or ritual..."
          rows="3"
          id="puja-ai-input"
        ></textarea>
        <button class="puja-ai-submit" onclick="PujaAI.submitQuestion()">
          Ask Question
        </button>
      </div>
    `;

    // Add enter key listener
    const textarea = document.getElementById('puja-ai-input');
    textarea.addEventListener('keypress', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        window.PujaAI.submitQuestion();
      }
    });
  }

  function renderLoading() {
    const content = document.getElementById('puja-ai-content');
    content.innerHTML = `
      <div class="puja-ai-loading">
        <div class="puja-ai-spinner"></div>
        Searching sacred texts...
      </div>
    `;
  }

  function renderResponse() {
    if (!currentResponse) return;

    const content = document.getElementById('puja-ai-content');
    let html = '<div class="puja-ai-response">';

    // Summary
    if (currentResponse.summary) {
      html += `
        <div class="puja-ai-summary">
          <strong>Summary:</strong> ${currentResponse.summary}
        </div>
      `;
    }

    // Steps
    if (currentResponse.steps && currentResponse.steps.length > 0) {
      html += `
        <div class="puja-ai-section">
          <div class="puja-ai-section-title">📋 Step-by-Step Procedure</div>
          ${currentResponse.steps.map(step => `
            <div class="puja-ai-step">
              <div class="puja-ai-step-number">${step.step_no || 1}</div>
              <div class="puja-ai-step-content">
                <h4>${step.title || 'Step'}</h4>
                <p>${step.instruction}</p>
              </div>
            </div>
          `).join('')}
        </div>
      `;
    }

    // Materials
    if (currentResponse.materials && currentResponse.materials.length > 0) {
      html += `
        <div class="puja-ai-section">
          <div class="puja-ai-section-title">🛍️ Required Materials</div>
          ${currentResponse.materials.map(material => `
            <div class="puja-ai-material">
              <div class="puja-ai-material-info">
                <h4>${material.name}</h4>
                ${material.description ? `<p>${material.description}</p>` : ''}
                ${material.quantity ? `<p>Quantity: ${material.quantity}</p>` : ''}
              </div>
              ${material.product_match ? `
                <a href="${material.product_match}" target="_blank" class="puja-ai-buy-link">
                  🛒 Buy
                </a>
              ` : ''}
            </div>
          `).join('')}
        </div>
      `;
    }

    // Timings
    if (currentResponse.timings && currentResponse.timings.length > 0) {
      html += `
        <div class="puja-ai-section">
          <div class="puja-ai-section-title">⏰ Auspicious Timings</div>
          ${currentResponse.timings.map(timing => `
            <div style="background: #fef3c7; padding: 8px 12px; border-radius: 6px; margin-bottom: 8px; font-size: 13px;">
              ${timing}
            </div>
          `).join('')}
        </div>
      `;
    }

    // Mantras
    if (currentResponse.mantras && currentResponse.mantras.length > 0) {
      html += `
        <div class="puja-ai-section">
          <div class="puja-ai-section-title">🕉️ Mantras & Chants</div>
          ${currentResponse.mantras.map(mantra => `
            <div style="background: #fed7aa; padding: 12px; border-radius: 6px; margin-bottom: 8px; font-size: 14px; font-weight: 500;">
              ${mantra}
            </div>
          `).join('')}
        </div>
      `;
    }

    html += `
      <button class="puja-ai-submit" onclick="PujaAI.reset()" style="margin-top: 16px;">
        Ask Another Question
      </button>
    `;

    html += '</div>';
    content.innerHTML = html;
  }

  function renderError(message) {
    const content = document.getElementById('puja-ai-content');
    content.innerHTML = `
      <div class="puja-ai-error">
        <strong>Error:</strong> ${message}
      </div>
      <button class="puja-ai-submit" onclick="PujaAI.reset()">
        Try Again
      </button>
    `;
  }

  function updateLoadingState() {
    if (isLoading) {
      renderLoading();
    }
  }

  function toggleWidget() {
    isOpen = !isOpen;
    const widget = document.querySelector('.puja-ai-widget');
    const toggle = document.querySelector('.puja-ai-toggle');
    
    if (isOpen) {
      widget.classList.add('open');
      toggle.style.display = 'none';
      if (!currentResponse && presets.length === 0) {
        fetchPresets().then(renderPresets);
      } else if (!currentResponse) {
        renderPresets();
      }
    } else {
      widget.classList.remove('open');
      toggle.style.display = 'flex';
    }
  }

  // Public API
  window.PujaAI = {
    open: function() {
      if (!isOpen) toggleWidget();
    },
    close: function() {
      if (isOpen) toggleWidget();
    },
    reset: function() {
      currentResponse = null;
      renderPresets();
    },
    selectPreset: function(presetId, presetName) {
      askQuestion(`Guidance for ${presetName}`, presetId);
    },
    submitQuestion: function() {
      const input = document.getElementById('puja-ai-input');
      const question = input.value.trim();
      if (question) {
        askQuestion(question);
        input.value = '';
      }
    }
  };

  // Initialize when DOM is ready
  function init() {
    createStyles();
    
    // Check if there's a specific container
    const container = document.getElementById(config.containerId);
    
    if (container) {
      // Render inline widget
      container.innerHTML = `
        <div class="puja-ai-widget open" style="position: relative; width: 100%; max-width: 600px;">
          <div class="puja-ai-header">
            <h3 class="puja-ai-title">
              <span>🕉️</span>
              Puja AI Assistant
            </h3>
          </div>
          <div class="puja-ai-content" id="puja-ai-content">
            <!-- Content will be rendered here -->
          </div>
        </div>
      `;
      
      fetchPresets().then(renderPresets);
    } else {
      // Create floating widget
      createToggleButton();
      createWidget();
      
      if (config.autoOpen) {
        setTimeout(() => {
          window.PujaAI.open();
        }, 1000);
      }
    }
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
