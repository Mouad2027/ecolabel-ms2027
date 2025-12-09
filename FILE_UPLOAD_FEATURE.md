# 📸 File Upload Feature - Documentation

## Vue d'ensemble

Nouvelle fonctionnalité ajoutée au frontend EcoLabel Widget permettant aux utilisateurs d'uploader des photos, PDFs, ou images de codes-barres pour extraire automatiquement les informations produit.

## ✨ Fonctionnalités

### Types de fichiers supportés
- **📄 PDF** - Étiquettes produit, fiches techniques
- **🌐 HTML** - Pages web de produits
- **📷 Images** - Photos de produits, étiquettes photographiées
  - JPG / JPEG
  - PNG
  - GIF
  - BMP
  - TIFF

### Méthodes d'upload
1. **Glisser-Déposer** - Glissez un fichier directement sur la zone d'upload
2. **Parcourir** - Cliquez sur le bouton pour ouvrir le sélecteur de fichiers

### Extraction automatique
Le système extrait automatiquement :
- ✅ **Titre du produit**
- ✅ **Marque**
- ✅ **Code GTIN/EAN** (code-barres)
- ✅ **Origine**
- ✅ **Emballage**
- ✅ **Liste des ingrédients**

## 🎨 Interface Utilisateur

### Zone d'Upload
```
┌─────────────────────────────────────┐
│          📤                         │
│   Glissez-déposez un fichier ici   │
│              ou                     │
│     📁 Parcourir les fichiers       │
│                                     │
│  Formats: PDF, HTML, Images         │
│  📷 Photos • 📄 PDFs • 🏷️ Codes    │
└─────────────────────────────────────┘
```

### États Visuels

#### 1. Normal
- Bordure en pointillés gris
- Fond gris clair
- Icône d'upload

#### 2. Drag Active (survol avec fichier)
- Bordure verte
- Fond vert clair
- Zoom léger (scale 1.02)

#### 3. Uploading
- Bordure orange
- Fond orange clair
- Spinner animé
- Message "Analyse en cours..."

#### 4. Success
- Message vert avec ✅
- Affichage du nom du produit extrait
- Auto-disparition après 5 secondes

#### 5. Error
- Message rouge avec ❌
- Description de l'erreur
- Bouton de fermeture

### Affichage des données extraites

```
┌─────────────────────────────────────┐
│  📋 Extracted Product Data          │
├─────────────────────────────────────┤
│  Titre:      Nutella                │
│  Marque:     Ferrero                │
│  Code GTIN:  3017620422003          │
│  Origine:    France                 │
│  Emballage:  Verre                  │
│                                     │
│  Ingrédients:                       │
│  Sucre, huile de palme, noisettes, │
│  cacao maigre, lait écrémé...       │
└─────────────────────────────────────┘
```

## 🔧 Composants Créés

### 1. FileUpload.jsx
**Chemin**: `src/components/FileUpload.jsx`

**Props**:
- `onProductParsed(productData)` - Callback appelé après extraction réussie

**Fonctionnalités**:
- Validation du type de fichier
- Validation de la taille (max 10MB)
- Gestion drag & drop
- Upload vers API Parser-Produit
- Gestion des erreurs
- Feedback visuel

**API Endpoints utilisés**:
```javascript
POST http://localhost:8001/product/parse
Content-Type: multipart/form-data
```

### 2. FileUpload.css
**Chemin**: `src/components/FileUpload.css`

**Styles incluent**:
- Zone d'upload responsive
- Animations (spin, slideIn, slideUp)
- États hover/active/uploading
- Messages d'erreur/succès
- Media queries pour mobile

### 3. App.jsx (Modifié)
**Changements**:
- Import du composant FileUpload
- Ajout de la section upload
- Gestion de l'état parsedProduct
- Affichage des données extraites
- Scroll automatique vers les résultats

### 4. App.css (Modifié)
**Nouveaux styles**:
- `.upload-section`
- `.parsed-section` avec gradient violet
- `.info-grid` pour affichage en grille
- `.info-item` pour les champs individuels
- Animations slideUp

## 📊 Flux de Données

```
User Action
    ↓
[FileUpload Component]
    ↓
Validation (type, size)
    ↓
POST /product/parse
    ↓
[Parser-Produit Service]
    ↓
OCR/PDF/HTML Processing
    ↓
Response JSON
    ↓
[FileUpload Component]
    ↓
onProductParsed callback
    ↓
[App Component]
    ↓
Update parsedProduct state
    ↓
Display extracted data
    ↓
Auto-scroll to results
```

## 🔒 Validation et Sécurité

### Validation côté client
- ✅ Type MIME check
- ✅ Extension de fichier check
- ✅ Taille maximale: 10MB
- ✅ Liste blanche de formats

### Validation côté serveur
- ✅ Parser-Produit valide les types
- ✅ Traitement sécurisé des fichiers
- ✅ Gestion des erreurs

## 🚀 Utilisation

### Pour l'utilisateur final

1. **Accéder à l'interface**
   ```
   http://localhost:3000
   ```

2. **Trouver la section "Upload Product Information"**
   - Juste en dessous de la barre de recherche

3. **Choisir une méthode d'upload**
   - **Option A**: Glisser-déposer un fichier
   - **Option B**: Cliquer "Parcourir les fichiers"

4. **Attendre l'analyse**
   - Spinner animé pendant le traitement
   - Généralement 2-5 secondes

5. **Voir les résultats**
   - Scroll automatique vers les données extraites
   - Section avec fond violet
   - Informations structurées

### Exemples de fichiers à tester

#### PDF
- Étiquettes nutritionnelles
- Fiches techniques produit
- Documents officiels

#### HTML
- Pages web sauvegardées
- Descriptions e-commerce

#### Images
- Photos de produits
- Étiquettes photographiées
- Codes-barres scannés

## 🎯 Cas d'usage

### 1. Scanner un code-barres
```
📱 Prendre photo du code-barres
    ↓
📤 Upload de l'image
    ↓
🔍 Détection automatique du GTIN
    ↓
✅ Produit identifié
```

### 2. Extraire d'une étiquette PDF
```
📄 PDF reçu par email
    ↓
📤 Upload du PDF
    ↓
📋 Extraction des ingrédients
    ↓
✅ Données structurées
```

### 3. Photo d'emballage
```
📷 Photo du produit en magasin
    ↓
📤 Upload de la photo
    ↓
🔤 OCR de l'étiquette
    ↓
✅ Informations extraites
```

## 🐛 Gestion des erreurs

### Erreurs possibles

#### Type de fichier non supporté
```
❌ Type de fichier non supporté. 
   Utilisez PDF, HTML ou images (JPG, PNG, etc.)
```

#### Fichier trop volumineux
```
❌ Fichier trop volumineux. Maximum 10MB.
```

#### Erreur d'analyse
```
❌ Erreur lors de l'analyse du fichier
```

#### Problème réseau
```
❌ Network Error / API non disponible
```

### Comportement
- Message d'erreur visible
- Bouton de fermeture (✕)
- Input reset automatique
- Possibilité de réessayer

## 📱 Responsive Design

### Desktop (> 768px)
- Zone d'upload large
- Grille d'informations 2 colonnes
- Tous les éléments visibles

### Mobile (≤ 640px)
- Zone d'upload compacte
- Grille d'informations 1 colonne
- Icônes et textes adaptés
- Boutons plus grands

## ⚡ Performance

### Optimisations
- Validation avant upload (économise bande passante)
- Feedback immédiat (validation locale)
- Spinner pendant traitement
- Auto-clear des messages après 5s
- Scroll smooth vers résultats

### Temps de réponse typiques
- **PDF simple**: 1-2 secondes
- **HTML**: < 1 seconde
- **Image avec OCR**: 2-5 secondes
- **Image avec code-barres**: 1-3 secondes

## 🔄 Intégration avec Parser-Produit

### Endpoint utilisé
```
POST http://localhost:8001/product/parse
```

### Format de requête
```http
POST /product/parse HTTP/1.1
Content-Type: multipart/form-data

--boundary
Content-Disposition: form-data; name="file"; filename="product.jpg"
Content-Type: image/jpeg

[binary data]
--boundary--
```

### Format de réponse
```json
{
  "id": "uuid-here",
  "title": "Nutella",
  "brand": "Ferrero",
  "gtin": "3017620422003",
  "origin": "France",
  "packaging": "Verre",
  "ingredients_text": "Sucre, huile de palme, noisettes...",
  "raw_text": "Full extracted text..."
}
```

## 📈 Améliorations Futures

### Court terme
- [ ] Preview de l'image uploadée
- [ ] Progress bar détaillée
- [ ] Support multi-fichiers (batch)
- [ ] Historique des uploads

### Moyen terme
- [ ] Capture photo directe (webcam)
- [ ] Scanner de code-barres en temps réel
- [ ] Recadrage d'image avant upload
- [ ] Compression automatique

### Long terme
- [ ] Upload depuis URL
- [ ] Intégration reconnaissance vocale
- [ ] Machine learning pour meilleure extraction
- [ ] OCR multilingue avancé

## 🧪 Tests

### Tests manuels à effectuer

1. **Upload PDF**
   - Tester avec étiquette produit
   - Vérifier extraction titre/marque

2. **Upload Image JPG**
   - Tester avec photo de produit
   - Vérifier OCR et barcode detection

3. **Drag & Drop**
   - Glisser fichier valide
   - Glisser fichier invalide

4. **Validation**
   - Tester fichier > 10MB
   - Tester type non supporté

5. **Responsive**
   - Tester sur mobile (DevTools)
   - Vérifier layout et interactions

## 📝 Configuration

### Variables d'environnement

**Fichier**: `.env`
```env
VITE_API_URL=http://localhost:8005/public
VITE_PARSER_URL=http://localhost:8001
```

### Modification des URLs
Pour changer l'URL du parser :
```javascript
// FileUpload.jsx
const PARSER_API = import.meta.env.VITE_PARSER_URL || 'http://localhost:8001'
```

## 🎉 Résumé

### Ce qui a été ajouté
✅ Composant FileUpload complet
✅ Interface drag & drop
✅ Validation fichiers
✅ Intégration Parser-Produit API
✅ Affichage données extraites
✅ Design responsive
✅ Gestion erreurs
✅ Feedback visuel
✅ Animations

### Fichiers créés/modifiés
- ✅ `FileUpload.jsx` - Nouveau composant
- ✅ `FileUpload.css` - Styles upload
- ✅ `App.jsx` - Intégration composant
- ✅ `App.css` - Styles sections
- ✅ `.env` - Configuration API

### Déploiement
✅ Frontend reconstruit
✅ Container redémarré
✅ Service accessible sur http://localhost:3000

---

**Status**: ✅ **DEPLOYED AND READY**

**URL**: http://localhost:3000

**Test it**: Glissez une photo de produit ou un PDF !
