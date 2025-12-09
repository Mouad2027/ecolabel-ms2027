import { useState } from 'react'
import EcoScoreWidget from './components/EcoScoreWidget'
import ProductSearch from './components/ProductSearch'
import FileUpload from './components/FileUpload'
import './App.css'

function App() {
  const [selectedProduct, setSelectedProduct] = useState(null)
  const [parsedProduct, setParsedProduct] = useState(null)

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
        <h1>🌿 EcoLabel Widget</h1>
        <p>Environmental Score Display System</p>
      </header>

      <main className="app-main">
        <section className="search-section">
          <h2>Find a Product</h2>
          <ProductSearch onProductSelect={setSelectedProduct} />
        </section>

        <section className="upload-section">
          <h2>📸 Upload Product Information</h2>
          <p className="section-description">
            Upload a photo, PDF label, or barcode image to extract product information
          </p>
          <FileUpload onProductParsed={handleProductParsed} />
        </section>

        {parsedProduct && (
          <section id="parsed-section" className="parsed-section">
            <h2>📋 Extracted Product Data</h2>
            
            {parsedProduct.eco_score && (
              <div className="eco-score-badge">
                <div 
                  className="score-circle" 
                  style={{ backgroundColor: parsedProduct.eco_score.color }}
                >
                  {parsedProduct.eco_score.letter}
                </div>
                <div className="score-info">
                  <h3>Éco-Score: {parsedProduct.eco_score.letter}</h3>
                  <p>Score numérique: {parsedProduct.eco_score.numeric}/100</p>
                  <p>Confiance: {Math.round(parsedProduct.eco_score.confidence * 100)}%</p>
                </div>
              </div>
            )}

            <div className="parsed-info">
              <div className="info-grid">
                {parsedProduct.title && (
                  <div className="info-item">
                    <span className="info-label">Titre:</span>
                    <span className="info-value">{parsedProduct.title}</span>
                  </div>
                )}
                {parsedProduct.brand && (
                  <div className="info-item">
                    <span className="info-label">Marque:</span>
                    <span className="info-value">{parsedProduct.brand}</span>
                  </div>
                )}
                {parsedProduct.gtin && (
                  <div className="info-item">
                    <span className="info-label">Code GTIN:</span>
                    <span className="info-value">{parsedProduct.gtin}</span>
                  </div>
                )}
                {parsedProduct.origin && (
                  <div className="info-item">
                    <span className="info-label">Origine:</span>
                    <span className="info-value">{parsedProduct.origin}</span>
                  </div>
                )}
                {parsedProduct.packaging && (
                  <div className="info-item">
                    <span className="info-label">Emballage:</span>
                    <span className="info-value">{parsedProduct.packaging}</span>
                  </div>
                )}
              </div>
              {parsedProduct.ingredients_text && (
                <div className="info-item full-width">
                  <span className="info-label">Ingrédients:</span>
                  <p className="info-value ingredients">{parsedProduct.ingredients_text}</p>
                </div>
              )}
            </div>
          </section>
        )}

        {selectedProduct && (
          <section className="widget-section">
            <h2>Product Eco-Score</h2>
            <EcoScoreWidget productId={selectedProduct.id} />
          </section>
        )}

        <section className="demo-section">
          <h2>Demo Widgets</h2>
          <div className="demo-grid">
            <div className="demo-card">
              <h3>Score A - Excellent</h3>
              <EcoScoreWidget 
                demoMode={true}
                demoData={{
                  title: "Organic Vegetables Mix",
                  brand: "Green Farm",
                  eco_score: { letter: "A", numeric: 15, color: "#1E8449", confidence: 0.95 },
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

export default App
