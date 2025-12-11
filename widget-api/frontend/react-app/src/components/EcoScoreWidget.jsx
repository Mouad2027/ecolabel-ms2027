import { useState, useEffect } from 'react'
import axios from 'axios'
import './EcoScoreWidget.css'

const API_BASE = import.meta.env.VITE_API_URL || '/public'

function EcoScoreWidget({ productId, demoMode = false, demoData = null }) {
  const [product, setProduct] = useState(demoMode ? demoData : null)
  const [loading, setLoading] = useState(!demoMode)
  const [error, setError] = useState(null)
  const [expanded, setExpanded] = useState(false)

  useEffect(() => {
    if (demoMode) return

    const fetchProduct = async () => {
      try {
        setLoading(true)
        setError(null)
        const response = await axios.get(`${API_BASE}/product/${productId}`)
        setProduct(response.data)
      } catch (err) {
        setError('Failed to load product data')
        console.error('Error fetching product:', err)
      } finally {
        setLoading(false)
      }
    }

    if (productId) {
      fetchProduct()
    }
  }, [productId, demoMode])

  if (loading) {
    return (
      <div className="eco-widget eco-widget-loading">
        <div className="loading-spinner"></div>
        <p>Loading eco-score...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="eco-widget eco-widget-error">
        <span className="error-icon">⚠️</span>
        <p>{error}</p>
      </div>
    )
  }

  if (!product) {
    return (
      <div className="eco-widget eco-widget-empty">
        <p>No product selected</p>
      </div>
    )
  }

  const { eco_score, breakdown, ingredients, labels, title, brand } = product

  return (
    <div className="eco-widget">
      {/* Header */}
      <div className="eco-widget-header">
        <div className="product-info">
          <h3 className="product-title">{title}</h3>
          {brand && <span className="product-brand">{brand}</span>}
        </div>
        <div 
          className="score-badge"
          style={{ backgroundColor: eco_score.color }}
        >
          <span className="score-letter">{eco_score.letter}</span>
        </div>
      </div>

      {/* Score Bar */}
      <div className="score-bar-container">
        <div className="score-bar">
          <div className="score-bar-segment" style={{ backgroundColor: '#1E8449' }}>A</div>
          <div className="score-bar-segment" style={{ backgroundColor: '#82E0AA' }}>B</div>
          <div className="score-bar-segment" style={{ backgroundColor: '#F4D03F' }}>C</div>
          <div className="score-bar-segment" style={{ backgroundColor: '#E67E22' }}>D</div>
          <div className="score-bar-segment" style={{ backgroundColor: '#E74C3C' }}>E</div>
        </div>
        <div 
          className="score-indicator"
          style={{ left: `${eco_score.numeric}%` }}
        >
          ▲
        </div>
      </div>

      {/* Numeric Score */}
      <div className="score-numeric">
        <span>Score: {eco_score.numeric}/100</span>
        <span className="score-explanation">
          ({eco_score.numeric < 40 ? 'Faible impact' : eco_score.numeric < 60 ? 'Impact modéré' : 'Impact élevé'})
        </span>
        {eco_score.confidence && (
          <span className="confidence">
            Confiance: {Math.round(eco_score.confidence * 100)}%
          </span>
        )}
      </div>

      {/* Breakdown */}
      <div className="breakdown-section">
        <h4 onClick={() => setExpanded(!expanded)} className="breakdown-toggle">
          Environmental Impact {expanded ? '▼' : '▶'}
        </h4>
        
        {expanded && (
          <div className="breakdown-details">
            {breakdown && (
              <>
                <div className="breakdown-item">
                  <span className="breakdown-icon">🏭</span>
                  <div className="breakdown-content">
                    <span className="breakdown-label">{breakdown.co2.label}</span>
                    <span className="breakdown-value">
                      {breakdown.co2.value} {breakdown.co2.unit}
                    </span>
                  </div>
                  <div className="breakdown-bar">
                    <div 
                      className="breakdown-bar-fill co2"
                      style={{ width: `${Math.min(breakdown.co2.value / 30 * 100, 100)}%` }}
                    ></div>
                  </div>
                </div>
                
                <div className="breakdown-item">
                  <span className="breakdown-icon">💧</span>
                  <div className="breakdown-content">
                    <span className="breakdown-label">{breakdown.water.label}</span>
                    <span className="breakdown-value">
                      {breakdown.water.value} {breakdown.water.unit}
                    </span>
                  </div>
                  <div className="breakdown-bar">
                    <div 
                      className="breakdown-bar-fill water"
                      style={{ width: `${Math.min(breakdown.water.value / 15000 * 100, 100)}%` }}
                    ></div>
                  </div>
                </div>
                
                <div className="breakdown-item">
                  <span className="breakdown-icon">⚡</span>
                  <div className="breakdown-content">
                    <span className="breakdown-label">{breakdown.energy.label}</span>
                    <span className="breakdown-value">
                      {breakdown.energy.value} {breakdown.energy.unit}
                    </span>
                  </div>
                  <div className="breakdown-bar">
                    <div 
                      className="breakdown-bar-fill energy"
                      style={{ width: `${Math.min(breakdown.energy.value / 50 * 100, 100)}%` }}
                    ></div>
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </div>

      {/* Labels */}
      {labels && labels.length > 0 && (
        <div className="labels-section">
          {labels.map((label, index) => (
            <span key={index} className={`label-badge label-${label}`}>
              {formatLabel(label)}
            </span>
          ))}
        </div>
      )}

      {/* Ingredients Preview */}
      {ingredients && ingredients.length > 0 && (
        <div className="ingredients-section">
          <span className="ingredients-label">Main ingredients: </span>
          <span className="ingredients-list">
            {ingredients
              .slice(0, 4)
              .map(ing => typeof ing === 'string' ? ing : ing.name || ing.normalized_name)
              .filter(Boolean)
              .join(', ')}
            {ingredients.length > 4 && ` +${ingredients.length - 4} more`}
          </span>
        </div>
      )}

      {/* Footer */}
      <div className="eco-widget-footer">
        <span className="powered-by">Powered by EcoLabel-MS</span>
      </div>
    </div>
  )
}

function formatLabel(label) {
  const labelNames = {
    bio: '🌱 Organic',
    recyclable: '♻️ Recyclable',
    vegan: '🥬 Vegan',
    fair_trade: '🤝 Fair Trade',
    local_sourcing: '📍 Local',
    non_gmo: '🧬 Non-GMO',
    gluten_free: '🌾 Gluten-Free'
  }
  return labelNames[label] || label
}

export default EcoScoreWidget
