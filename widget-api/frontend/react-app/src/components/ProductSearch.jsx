import { useState } from 'react'
import axios from 'axios'
import './ProductSearch.css'

const API_BASE = import.meta.env.VITE_API_URL || '/public'

function ProductSearch({ onProductSelect }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)

  const handleSearch = async (e) => {
    e.preventDefault()
    
    if (query.trim().length < 2) return

    try {
      setLoading(true)
      setSearched(true)
      const response = await axios.get(`${API_BASE}/products/search`, {
        params: { q: query, limit: 10 }
      })
      setResults(response.data.results)
    } catch (err) {
      console.error('Search error:', err)
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  const handleSelect = (product) => {
    onProductSelect(product)
    setResults([])
    setSearched(false)
  }

  return (
    <div className="product-search">
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search products by name, brand, or GTIN..."
          className="search-input"
        />
        <button type="submit" className="search-button" disabled={loading}>
          {loading ? '...' : '🔍'}
        </button>
      </form>

      {loading && (
        <div className="search-loading">
          <span>Searching...</span>
        </div>
      )}

      {!loading && searched && results.length === 0 && (
        <div className="search-empty">
          <p>No products found for "{query}"</p>
          <p className="hint">Try searching for common products or use a GTIN code</p>
        </div>
      )}

      {results.length > 0 && (
        <div className="search-results">
          {results.map((product) => (
            <div 
              key={product.id} 
              className="search-result-item"
              onClick={() => handleSelect(product)}
            >
              <div className="result-info">
                <span className="result-title">{product.title}</span>
                {product.brand && (
                  <span className="result-brand">{product.brand}</span>
                )}
                {product.gtin && (
                  <span className="result-gtin">GTIN: {product.gtin}</span>
                )}
              </div>
              {product.eco_score && (
                <div 
                  className="result-score"
                  style={{ backgroundColor: product.eco_score.color }}
                >
                  {product.eco_score.letter}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ProductSearch
