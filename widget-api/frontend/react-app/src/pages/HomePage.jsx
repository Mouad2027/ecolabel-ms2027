import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Leaf, BarChart3, Microscope, Zap, Globe, Camera, CheckCircle, Tag, Hash, Weight, MapPin, Award, List } from 'lucide-react'
import EcoScoreWidget from '../components/EcoScoreWidget'
import ProductSearch from '../components/ProductSearch'
import FileUpload from '../components/FileUpload'
import './HomePage.css'

// Helper function to clean ingredient text and remove OCR errors
const cleanIngredient = (text) => {
  if (!text || typeof text !== 'string') return ''
  
  let cleaned = text.trim()
  
  // Remove common OCR errors and artifacts
  cleaned = cleaned
    .replace(/[\u00fc\u00e9\u00e8\u00ea\u00eb_]/g, match => {
      const map = {
        '\u00fc': 'u',
        '\u00e9': 'e', 
        '\u00e8': 'e',
        '\u00ea': 'e',
        '\u00eb': 'e',
        '_': ' '
      }
      return map[match] || match
    })
    .replace(/\s+/g, ' ')  // Multiple spaces to one
    .replace(/([a-z])([A-Z])/g, '$1 $2')  // Add space between camelCase
    .replace(/\s*:\s*/g, ': ')  // Fix colons
    .replace(/\s*,\s*/g, ', ')   // Fix commas
    .replace(/\s*\(\s*/g, ' (')  // Fix parentheses
    .replace(/\s*\)\s*/g, ') ')
    .replace(/[\[\{]/g, '(')  // Convert brackets to parentheses
    .replace(/[\]\}]/g, ')')
    .replace(/\s+/g, ' ')  // Clean up spaces again
    .trim()
  
  // Filter out obvious garbage (too many special chars, too short, etc.)
  const specialCharCount = (cleaned.match(/[^a-zA-Z0-9\s\-,.:()%]/g) || []).length
  const totalLength = cleaned.length
  
  // If more than 30% special characters, probably garbage
  if (specialCharCount / totalLength > 0.3 && totalLength < 50) {
    return ''
  }
  
  // Filter out very short fragments that don't make sense
  if (cleaned.length < 3 && !cleaned.match(/^[a-z]{2,3}$/i)) {
    return ''
  }
  
  // Capitalize first letter
  if (cleaned.length > 0) {
    cleaned = cleaned.charAt(0).toUpperCase() + cleaned.slice(1)
  }
  
  return cleaned
}

function HomePage() {
  const [selectedProduct, setSelectedProduct] = useState(null)
  const [parsedProduct, setParsedProduct] = useState(null)
  const navigate = useNavigate()

  const handleProductParsed = (productData) => {
    setParsedProduct(productData)
    // If product has eco_score and id, also set it as selected product for widget display
    if (productData.eco_score && productData.id) {
      setSelectedProduct({ id: productData.id, title: productData.title })
    }
    // Scroll to the parsed product section
    setTimeout(() => {
      document.getElementById('parsed-section')?.scrollIntoView({ behavior: 'smooth' })
    }, 100)
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-container">
          <div className="header-brand">
            <h1><Leaf className="inline-icon" size={32} /> EcoLabel-MS</h1>
            <p>Plateforme d'évaluation environnementale intelligente</p>
          </div>
          <div className="header-actions">
            <button className="history-nav-button" onClick={() => navigate('/history')}>
              <BarChart3 size={20} /> Historique
            </button>
            <div className="header-search">
              <ProductSearch onProductSelect={setSelectedProduct} />
            </div>
          </div>
        </div>
      </header>

      <main className="app-main">
        <section className="hero-section">
          <div className="hero-content">
            <h2>Évaluez l'impact environnemental de vos produits</h2>
            <p className="hero-subtitle">Obtenez un éco-score précis basé sur des données scientifiques en quelques secondes</p>
            
            <div className="features-row">
              <div className="feature-badge">
                <span className="badge-icon"><Microscope size={20} /></span>
                <span>Données FAO & Ecoinvent</span>
              </div>
              <div className="feature-badge">
                <span className="badge-icon"><Zap size={20} /></span>
                <span>Analyse en temps réel</span>
              </div>
              <div className="feature-badge">
                <span className="badge-icon"><Globe size={20} /></span>
                <span>Impact multi-critères</span>
              </div>
            </div>
          </div>
        </section>

        <section className="upload-section">
          <div className="section-header">
            <h2><Camera className="inline-icon" size={28} /> Analyser un Produit</h2>
            <p>Téléchargez une photo d'étiquette ou un fichier texte pour obtenir l'éco-score</p>
          </div>
          <FileUpload onProductParsed={handleProductParsed} />
        </section>

        {parsedProduct && (
          <section className="parsed-section" id="parsed-section">
            <div className="product-info-banner">
              <div className="banner-header">
                <div className="banner-icon"><CheckCircle size={48} strokeWidth={2} /></div>
                <div className="banner-title-section">
                  <h3>Analyse Terminée</h3>
                  <p className="product-name">{parsedProduct.title || 'Produit'}</p>
                </div>
                <div className="banner-badge">
                  <div className="success-checkmark">
                    <div className="check-icon">
                      <span className="icon-line line-tip"></span>
                      <span className="icon-line line-long"></span>
                      <div className="icon-circle"></div>
                      <div className="icon-fix"></div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="product-details-grid">
                {parsedProduct.brand && (
                  <div className="detail-card">
                    <span className="detail-icon"><Tag size={24} /></span>
                    <div className="detail-content">
                      <span className="detail-label">Marque</span>
                      <span className="detail-value">{parsedProduct.brand}</span>
                    </div>
                  </div>
                )}
                
                {parsedProduct.gtin && (
                  <div className="detail-card">
                    <span className="detail-icon"><Hash size={24} /></span>
                    <div className="detail-content">
                      <span className="detail-label">Code</span>
                      <span className="detail-value">{parsedProduct.gtin}</span>
                    </div>
                  </div>
                )}

                {parsedProduct.weight_g && (
                  <div className="detail-card">
                    <span className="detail-icon"><Weight size={24} /></span>
                    <div className="detail-content">
                      <span className="detail-label">Poids</span>
                      <span className="detail-value">
                        {parsedProduct.weight_g >= 1000 
                          ? `${(parsedProduct.weight_g / 1000).toFixed(2)} kg` 
                          : `${parsedProduct.weight_g} g`}
                      </span>
                    </div>
                  </div>
                )}

                {Array.isArray(parsedProduct.origins) && parsedProduct.origins.length > 0 && (
                  <div className="detail-card">
                    <span className="detail-icon"><MapPin size={24} /></span>
                    <div className="detail-content">
                      <span className="detail-label">Origine</span>
                      <span className="detail-value">{parsedProduct.origins.join(', ')}</span>
                    </div>
                  </div>
                )}

                {Array.isArray(parsedProduct.labels) && parsedProduct.labels.length > 0 && (
                  <div className="detail-card full-width">
                    <span className="detail-icon"><Award size={24} /></span>
                    <div className="detail-content">
                      <span className="detail-label">Labels</span>
                      <div className="labels-list">
                        {parsedProduct.labels.map((label, idx) => (
                          <span key={idx} className="label-badge">{typeof label === 'string' ? label : label?.name || String(label)}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {Array.isArray(parsedProduct.ingredients) && parsedProduct.ingredients.length > 0 && (
                <div className="ingredients-section">
                  <h4><List className="inline-icon" size={20} /> Ingrédients</h4>
                  <div className="ingredients-list">
                    {parsedProduct.ingredients
                      .map(ingredient => {
                        const text = typeof ingredient === 'string' 
                          ? ingredient 
                          : ingredient?.name || ingredient?.normalized_name || String(ingredient)
                        return cleanIngredient(text)
                      })
                      .filter(text => text && text.length >= 2)  // Remove empty and very short
                      .filter((text, index, self) => {
                        // Remove duplicates (case insensitive)
                        const lowerText = text.toLowerCase().trim()
                        return self.findIndex(t => t.toLowerCase().trim() === lowerText) === index
                      })
                      .map((cleanedText, idx) => (
                        <div key={idx} className="ingredient-item">
                          <span className="ingredient-bullet">•</span>
                          <span className="ingredient-name">{cleanedText}</span>
                        </div>
                      ))
                    }
                  </div>
                </div>
              )}
            </div>
            
            <div className="section-header">
              <h2><BarChart3 className="inline-icon" size={28} /> Éco-Score</h2>
            </div>
            <EcoScoreWidget productId={parsedProduct.id} />
          </section>
        )}

        {selectedProduct && !parsedProduct && (
          <section className="selected-section">
            <div className="section-header">
              <h2><BarChart3 className="inline-icon" size={28} /> Détails du Produit</h2>
            </div>
            <EcoScoreWidget productId={selectedProduct.id} />
          </section>
        )}

        <section className="demo-section">
          <div className="section-header">
            <h2>🎯 Demo Widgets</h2>
            <p>Exemples d'éco-scores pour différents types de produits</p>
          </div>
          
          <div className="demo-grid">
            <div className="demo-card">
              <h3>Score A - Excellent</h3>
              <EcoScoreWidget 
                demoMode={true}
                demoData={{
                  title: "Organic Vegetables Mix",
                  brand: "Green Farm",
                  eco_score: { letter: "A", numeric: 15, color: "#27ae60", confidence: 0.95 },
                  breakdown: {
                    co2: { value: 0.3, unit: "kg CO2e", label: "Carbon Footprint" },
                    water: { value: 150, unit: "L", label: "Water Usage" },
                    energy: { value: 2.5, unit: "MJ", label: "Energy Consumption" }
                  },
                  ingredients: ["Carrots", "Tomatoes", "Lettuce", "Onions"],
                  labels: ["bio", "local_sourcing"]
                }}
              />
            </div>
            <div className="demo-card">
              <h3>Score C - Average</h3>
              <EcoScoreWidget 
                demoMode={true}
                demoData={{
                  title: "Chocolate Bar",
                  brand: "Sweet Treats",
                  eco_score: { letter: "C", numeric: 52, color: "#F4D03F", confidence: 0.85 },
                  breakdown: {
                    co2: { value: 3.2, unit: "kg CO2e", label: "Carbon Footprint" },
                    water: { value: 2500, unit: "L", label: "Water Usage" },
                    energy: { value: 12, unit: "MJ", label: "Energy Consumption" }
                  },
                  ingredients: ["Cocoa", "Sugar", "Milk Powder", "Cocoa Butter"],
                  labels: ["fair_trade"]
                }}
              />
            </div>
            <div className="demo-card">
              <h3>Score E - Poor</h3>
              <EcoScoreWidget 
                demoMode={true}
                demoData={{
                  title: "Premium Beef Steak",
                  brand: "Ranch Select",
                  eco_score: { letter: "E", numeric: 88, color: "#E74C3C", confidence: 0.90 },
                  breakdown: {
                    co2: { value: 27, unit: "kg CO2e", label: "Carbon Footprint" },
                    water: { value: 15400, unit: "L", label: "Water Usage" },
                    energy: { value: 35, unit: "MJ", label: "Energy Consumption" }
                  },
                  ingredients: ["Beef"],
                  labels: []
                }}
              />
            </div>
          </div>
        </section>
      </main>

      <footer className="app-footer">
        <p>EcoLabel-MS2027 - Environmental Scoring Platform</p>
      </footer>
    </div>
  )
}

export default HomePage
