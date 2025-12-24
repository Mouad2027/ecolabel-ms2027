import { useState, useRef } from 'react'
import axios from 'axios'
import { Upload, FolderOpen, Camera, FileText, Barcode, X, CheckCircle, AlertCircle } from 'lucide-react'
import './FileUpload.css'

// Use relative URLs that will be proxied by nginx
const API_BASE = '/public'

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
      
      // Add weight if provided
      const response = await axios.post(`${API_BASE}/products/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 120000  // 2 minute timeout for file processing
      })

      const data = response.data
      console.log('Upload response data:', data)

      const weightInfo = data.weight_g || data.parsed_data?.weight_g
      const weightStr = weightInfo ? (weightInfo >= 1000 ? `${(weightInfo/1000).toFixed(1)}kg` : `${weightInfo}g`) : ''
      setSuccess(`✅ Produit analysé et noté: ${data.eco_score?.letter || 'N/A'} - ${data.title || data.parsed_data?.title || 'Sans nom'}${weightStr ? ` (${weightStr})` : ''}`)
      
      // Call parent callback with full product data including score
      if (onProductParsed) {
        // Ensure arrays are always arrays
        const ensureArray = (val) => Array.isArray(val) ? val : (val ? [val] : [])
        
        const productData = {
          title: data.title || data.parsed_data?.title || 'Produit',
          brand: data.brand || data.parsed_data?.brand || '',
          gtin: data.gtin || data.parsed_data?.gtin || '',
          weight_g: data.weight_g || data.parsed_data?.weight_g,
          ingredients: ensureArray(data.ingredients || data.parsed_data?.ingredients),
          origins: ensureArray(data.origins || (data.parsed_data?.origin ? [data.parsed_data.origin] : data.parsed_data?.origins)),
          labels: ensureArray(data.labels || data.parsed_data?.labels),
          eco_score: data.eco_score,
          id: data.id
        }
        console.log('Calling onProductParsed with:', productData)
        onProductParsed(productData)
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
              <div className="upload-icon"><Upload size={48} strokeWidth={1.5} /></div>
              <p className="upload-title">
                <strong>Glissez-déposez</strong> un fichier ici
              </p>
              <p className="upload-subtitle">ou</p>
              <button 
                type="button" 
                className="upload-button"
                onClick={onButtonClick}
              >
                <FolderOpen size={20} /> Parcourir les fichiers
              </button>
              <p className="upload-hint">
                Formats supportés: PDF, HTML, Images (JPG, PNG, GIF, BMP, TIFF)
              </p>
              <p className="upload-hint">
                <Camera size={16} className="inline-icon" /> Photos de produits • <FileText size={16} className="inline-icon" /> Étiquettes PDF • <Barcode size={16} className="inline-icon" /> Codes-barres
              </p>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="upload-message error">
          <span><AlertCircle size={20} /></span>
          <span>{error}</span>
          <button onClick={() => setError(null)}><X size={18} /></button>
        </div>
      )}

      {success && (
        <div className="upload-message success">
          <span><CheckCircle size={20} className="inline-icon" /> {success}</span>
          <button onClick={() => setSuccess(null)}><X size={18} /></button>
        </div>
      )}
    </div>
  )
}

export default FileUpload
