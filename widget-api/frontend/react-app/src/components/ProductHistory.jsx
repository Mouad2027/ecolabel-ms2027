import { useState, useEffect } from 'react'
import './ProductHistory.css'

function ProductHistory({ onProductSelect }) {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [totalProducts, setTotalProducts] = useState(0)
  const [currentPage, setCurrentPage] = useState(0)
  const productsPerPage = 12

  useEffect(() => {
    fetchHistory()
  }, [currentPage])

  const fetchHistory = async () => {
    try {
      setLoading(true)
      const offset = currentPage * productsPerPage
      const response = await fetch(
        `/api/public/history?limit=${productsPerPage}&offset=${offset}`
      )
      
      if (!response.ok) {
        throw new Error('Failed to fetch history')
      }

      const data = await response.json()
      setProducts(data.products)
      setTotalProducts(data.total)
      setError(null)
    } catch (err) {
      console.error('Error fetching history:', err)
      setError('Impossible de charger l\'historique')
    } finally {
      setLoading(false)
    }
  }

  const getScoreClass = (letter) => {
    return `score-badge score-${letter.toLowerCase()}`
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const totalPages = Math.ceil(totalProducts / productsPerPage)

  if (loading && products.length === 0) {
    return (
      <div className="history-loading">
        <div className="spinner"></div>
        <p>Chargement de l'historique...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="history-error">
        <p>⚠️ {error}</p>
        <button onClick={fetchHistory} className="retry-button">
          Réessayer
        </button>
      </div>
    )
  }

  return (
    <div className="product-history">
      <div className="history-header">
        <h2>📊 Historique des Analyses</h2>
        <p className="history-count">
          {totalProducts} produit{totalProducts > 1 ? 's' : ''} analysé{totalProducts > 1 ? 's' : ''}
        </p>
      </div>

      {products.length === 0 ? (
        <div className="history-empty">
          <p>🔍 Aucun produit analysé pour le moment</p>
          <p className="empty-subtitle">Commencez par analyser un produit ci-dessus</p>
        </div>
      ) : (
        <>
          <div className="history-grid">
            {products.map((product) => (
              <div 
                key={product.id} 
                className="history-card"
                onClick={() => onProductSelect && onProductSelect({ id: product.id, title: product.title })}
              >
                <div className="card-header">
                  {product.eco_score && (
                    <div className={getScoreClass(product.eco_score.letter)}>
                      {product.eco_score.letter}
                    </div>
                  )}
                  <div className="card-date">
                    {formatDate(product.created_at)}
                  </div>
                </div>
                
                <div className="card-body">
                  <h3 className="card-title">{product.title || 'Sans titre'}</h3>
                  {product.brand && (
                    <p className="card-brand">🏷️ {product.brand}</p>
                  )}
                  {product.weight_g && (
                    <p className="card-weight">💪 {
                      product.weight_g >= 1000 
                        ? `${(product.weight_g / 1000).toFixed(1)} kg`
                        : `${product.weight_g} g`
                    }</p>
                  )}
                  {product.origin && (
                    <p className="card-origin">📍 {product.origin}</p>
                  )}
                  
                  {product.impacts && (
                    <div className="card-impacts">
                      <div className="impact-item">
                        <span className="impact-icon">💨</span>
                        <span className="impact-value">
                          {product.impacts.co2?.toFixed(2) || 0} kg CO₂
                        </span>
                      </div>
                      <div className="impact-item">
                        <span className="impact-icon">💧</span>
                        <span className="impact-value">
                          {product.impacts.water?.toFixed(0) || 0} L
                        </span>
                      </div>
                      <div className="impact-item">
                        <span className="impact-icon">⚡</span>
                        <span className="impact-value">
                          {product.impacts.energy?.toFixed(1) || 0} MJ
                        </span>
                      </div>
                    </div>
                  )}
                </div>

                <div className="card-footer">
                  <button className="view-details-btn">
                    Voir détails →
                  </button>
                </div>
              </div>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button
                onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
                disabled={currentPage === 0}
                className="pagination-btn"
              >
                ← Précédent
              </button>
              
              <div className="pagination-info">
                Page {currentPage + 1} sur {totalPages}
              </div>
              
              <button
                onClick={() => setCurrentPage(Math.min(totalPages - 1, currentPage + 1))}
                disabled={currentPage >= totalPages - 1}
                className="pagination-btn"
              >
                Suivant →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default ProductHistory
