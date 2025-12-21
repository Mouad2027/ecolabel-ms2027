import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './HistoryPage.css'

function HistoryPage() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [totalProducts, setTotalProducts] = useState(0)
  const [currentPage, setCurrentPage] = useState(1)
  const [filterScore, setFilterScore] = useState('all')
  const [lastRefresh, setLastRefresh] = useState(Date.now())
  const navigate = useNavigate()
  
  const productsPerPage = 12

  // Auto-refresh every 10 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setLastRefresh(Date.now())
    }, 10000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    fetchHistory()
  }, [currentPage, filterScore, lastRefresh])

  const fetchHistory = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const offset = (currentPage - 1) * productsPerPage
      const response = await fetch(`/public/history?limit=${productsPerPage}&offset=${offset}`)
      
      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`)
      }
      
      const data = await response.json()
      
      // Filtrer par score si nécessaire
      let filteredProducts = data.products || []
      if (filterScore !== 'all') {
        filteredProducts = filteredProducts.filter(p => 
          p.eco_score && p.eco_score.letter === filterScore
        )
      }
      
      setProducts(filteredProducts)
      setTotalProducts(data.total)
    } catch (err) {
      console.error('Erreur lors du chargement de l\'historique:', err)
      setError('Impossible de charger l\'historique des produits')
    } finally {
      setLoading(false)
    }
  }

  const getScoreBadgeClass = (letter) => {
    const classMap = {
      'A': 'score-a',
      'B': 'score-b',
      'C': 'score-c',
      'D': 'score-d',
      'E': 'score-e'
    }
    return `score-badge ${classMap[letter] || 'score-default'}`
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Date inconnue'
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('fr-FR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date)
  }

  const formatImpact = (value, unit) => {
    if (value === null || value === undefined) return 'N/A'
    if (value >= 1000) {
      return `${(value / 1000).toFixed(1)}k ${unit}`
    }
    return `${value.toFixed(1)} ${unit}`
  }

  const totalPages = Math.ceil(totalProducts / productsPerPage)

  return (
    <div className="history-page">
      <header className="history-header">
        <div className="header-top">
          <button className="back-button" onClick={() => navigate('/')}>
            ← Retour à l'accueil
          </button>
          <h1>📊 Historique des Analyses</h1>
        </div>
        <div className="header-stats">
          <div className="stat-card">
            <span className="stat-number">{totalProducts}</span>
            <span className="stat-label">Produits analysés</span>
          </div>
          <button 
            onClick={() => {
              setLastRefresh(Date.now())
              setCurrentPage(1)
            }} 
            className="refresh-button"
            title="Actualiser la liste"
          >
            🔄 Actualiser
          </button>
          <div className="filter-section">
            <label htmlFor="score-filter">Filtrer:</label>
            <select 
              id="score-filter"
              value={filterScore} 
              onChange={(e) => {
                setFilterScore(e.target.value)
                setCurrentPage(1)
              }}
              className="score-filter"
            >
              <option value="all">Tous les scores</option>
              <option value="A">🟢 Score A</option>
              <option value="B">🟢 Score B</option>
              <option value="C">🟡 Score C</option>
              <option value="D">🟠 Score D</option>
              <option value="E">🔴 Score E</option>
            </select>
          </div>
        </div>
      </header>

      <main className="history-main">
        {loading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Chargement de l'historique...</p>
          </div>
        ) : error ? (
          <div className="error-state">
            <div className="error-icon">⚠️</div>
            <p>{error}</p>
            <button onClick={fetchHistory} className="retry-button">
              Réessayer
            </button>
          </div>
        ) : products.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📦</div>
            <h2>Aucun produit analysé</h2>
            <p>Commencez par analyser des produits pour les voir apparaître ici</p>
            <button onClick={() => navigate('/')} className="cta-button">
              Analyser un produit
            </button>
          </div>
        ) : (
          <>
            <div className="history-grid">
              {products.map((product) => (
                <div key={product.id} className="product-card">
                  <div className="card-header">
                    <div className="product-main-info">
                      <div className="product-date">
                        {formatDate(product.created_at)}
                      </div>
                      
                      <h3 className="product-title">
                        {product.title || 'Produit sans nom'}
                      </h3>
                      
                      {product.brand && (
                        <p className="product-brand">
                          {product.brand}
                        </p>
                      )}
                    </div>
                    
                    {product.eco_score && (
                      <div className={getScoreBadgeClass(product.eco_score.letter)}>
                        <span className="score-letter">{product.eco_score.letter}</span>
                      </div>
                    )}
                  </div>

                  <div className="card-details">
                    {product.origin && (
                      <div className="detail-item">
                        <span className="detail-icon">📍</span>
                        <span className="detail-text">{product.origin}</span>
                      </div>
                    )}
                    
                    {product.gtin && (
                      <div className="detail-item">
                        <span className="detail-icon">🔢</span>
                        <span className="detail-text">{product.gtin}</span>
                      </div>
                    )}
                  </div>

                  {product.impacts && (
                    <div className="product-impacts">
                      <div className="impact-item">
                        <span className="impact-icon">🌍</span>
                        <div className="impact-content">
                          <span className="impact-label">CO₂</span>
                          <span className="impact-value">
                            {formatImpact(product.impacts.co2, 'kg')}
                          </span>
                        </div>
                      </div>
                      
                      <div className="impact-item">
                        <span className="impact-icon">💧</span>
                        <div className="impact-content">
                          <span className="impact-label">Eau</span>
                          <span className="impact-value">
                            {formatImpact(product.impacts.water, 'L')}
                          </span>
                        </div>
                      </div>
                      
                      <div className="impact-item">
                        <span className="impact-icon">⚡</span>
                        <div className="impact-content">
                          <span className="impact-label">Énergie</span>
                          <span className="impact-value">
                            {formatImpact(product.impacts.energy, 'MJ')}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {totalPages > 1 && (
              <div className="pagination">
                <button
                  onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                  className="pagination-button"
                >
                  ← Précédent
                </button>
                
                <div className="pagination-info">
                  Page {currentPage} sur {totalPages}
                </div>
                
                <button
                  onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                  disabled={currentPage === totalPages}
                  className="pagination-button"
                >
                  Suivant →
                </button>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}

export default HistoryPage
