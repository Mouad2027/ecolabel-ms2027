import { useState, useRef } from 'react'
import axios from 'axios'
import './FileUpload.css'

const PARSER_API = import.meta.env.VITE_PARSER_URL || 'http://localhost:8001'

function FileUpload({ onProductParsed }) {
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef(null)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = async (file) => {
    // Validate file type
    const validTypes = [
      'application/pdf',
      'text/html',
      'image/jpeg',
      'image/jpg', 
      'image/png',
      'image/gif',
      'image/bmp',
      'image/tiff'
    ]

    if (!validTypes.includes(file.type) && !file.name.match(/\.(pdf|html?|jpe?g|png|gif|bmp|tiff?)$/i)) {
      setError('Type de fichier non supporté. Utilisez PDF, HTML ou images (JPG, PNG, etc.)')
      return
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('Fichier trop volumineux. Maximum 10MB.')
      return
    }

    try {
      setUploading(true)
      setError(null)
      setSuccess(null)

      const formData = new FormData()
      formData.append('file', file)

      const response = await axios.post(`${PARSER_API}/product/parse`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      const parsedData = response.data

      // Step 2: Send ingredients to NLP for analysis
      setSuccess(`✅ Produit analysé, calcul du score en cours...`)
      
      const WIDGET_API = import.meta.env.VITE_API_URL || 'http://localhost:8005/public'
      
      // Create full product with score calculation
      const productPayload = {
        title: parsedData.title || 'Produit sans nom',
        brand: parsedData.brand || '',
        gtin: parsedData.gtin || '',
        ingredients_text: parsedData.ingredients_text || '',
        origin: parsedData.origin || '',
        packaging: parsedData.packaging || ''
      }

      // Send to widget API to create product with eco-score
      const scoreResponse = await axios.post(`${WIDGET_API}/products`, productPayload)
      
      setSuccess(`✅ Produit analysé et noté: ${scoreResponse.data.eco_score?.letter || 'N/A'} - ${parsedData.title || 'Sans nom'}`)
      
      // Call parent callback with full product data including score
      if (onProductParsed) {
        onProductParsed({
          ...parsedData,
          eco_score: scoreResponse.data.eco_score,
          id: scoreResponse.data.id
        })
      }

      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }

      // Clear success message after 5 seconds
      setTimeout(() => setSuccess(null), 5000)

    } catch (err) {
      console.error('Upload error:', err)
      setError(err.response?.data?.detail || 'Erreur lors de l\'analyse du fichier')
    } finally {
      setUploading(false)
    }
  }

  const onButtonClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="file-upload">
      <div 
        className={`upload-area ${dragActive ? 'drag-active' : ''} ${uploading ? 'uploading' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          id="file-input"
          className="file-input"
          onChange={handleChange}
          accept=".pdf,.html,.htm,.jpg,.jpeg,.png,.gif,.bmp,.tiff"
          disabled={uploading}
        />
        
        <div className="upload-content">
          {uploading ? (
            <>
              <div className="spinner"></div>
              <p>Analyse en cours...</p>
            </>
          ) : (
            <>
              <div className="upload-icon">📤</div>
              <p className="upload-title">
                <strong>Glissez-déposez</strong> un fichier ici
              </p>
              <p className="upload-subtitle">ou</p>
              <button 
                type="button" 
                className="upload-button"
                onClick={onButtonClick}
              >
                📁 Parcourir les fichiers
              </button>
              <p className="upload-hint">
                Formats supportés: PDF, HTML, Images (JPG, PNG, GIF, BMP, TIFF)
              </p>
              <p className="upload-hint">
                📷 Photos de produits • 📄 Étiquettes PDF • 🏷️ Codes-barres
              </p>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="upload-message error">
          <span>❌</span>
          <span>{error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {success && (
        <div className="upload-message success">
          <span>{success}</span>
          <button onClick={() => setSuccess(null)}>✕</button>
        </div>
      )}
    </div>
  )
}

export default FileUpload
