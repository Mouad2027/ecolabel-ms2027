# 🚀 Guide Rapide - Upload de Produits

## Accéder à l'application

Ouvrez votre navigateur et allez sur :
```
http://localhost:3000
```

## Utilisation de l'Upload

### Méthode 1 : Glisser-Déposer 🖱️

1. Trouvez la section **"📸 Upload Product Information"**
2. Glissez votre fichier (photo, PDF, HTML) sur la zone d'upload
3. Relâchez le fichier
4. Attendez l'analyse (2-5 secondes)
5. Consultez les informations extraites ci-dessous

### Méthode 2 : Bouton Parcourir 📁

1. Cliquez sur **"📁 Parcourir les fichiers"**
2. Sélectionnez votre fichier dans l'explorateur
3. Cliquez "Ouvrir"
4. Attendez l'analyse
5. Consultez les résultats

## Formats Acceptés

### Images 📷
- JPG / JPEG
- PNG
- GIF
- BMP
- TIFF

**Utilisez pour** :
- Photos de produits
- Étiquettes photographiées
- Codes-barres scannés

### Documents 📄
- PDF
- HTML

**Utilisez pour** :
- Étiquettes nutritionnelles PDF
- Fiches techniques
- Pages web sauvegardées

## Ce qui est extrait

L'application extrait automatiquement :
- ✅ **Nom du produit**
- ✅ **Marque**
- ✅ **Code-barres (GTIN/EAN)**
- ✅ **Pays d'origine**
- ✅ **Type d'emballage**
- ✅ **Liste complète des ingrédients**

## Exemples d'utilisation

### 🛒 Au supermarché
1. Prenez une photo du produit avec votre téléphone
2. Transférez la photo sur votre ordinateur
3. Uploadez-la sur http://localhost:3000
4. Obtenez instantanément toutes les infos !

### 📧 Document reçu par email
1. Téléchargez le PDF joint
2. Glissez-le dans la zone d'upload
3. Les données sont extraites automatiquement

### 🌐 Produit en ligne
1. Sauvegardez la page web (Ctrl+S)
2. Uploadez le fichier HTML
3. Récupérez les informations structurées

## Limites

- **Taille maximale** : 10 MB par fichier
- **Formats** : Seulement PDF, HTML, et images listées
- **Qualité** : Photos nettes donnent de meilleurs résultats
- **Langue** : OCR optimisé pour français et anglais

## Problèmes courants

### ❌ "Type de fichier non supporté"
**Solution** : Vérifiez que votre fichier est bien un PDF, HTML ou une image (JPG, PNG, etc.)

### ❌ "Fichier trop volumineux"
**Solution** : Compressez votre image ou PDF en dessous de 10 MB

### ❌ "Erreur lors de l'analyse"
**Solutions** :
- Vérifiez que le texte est lisible dans votre image
- Essayez avec une photo plus nette
- Vérifiez que le service Parser est démarré

### ⏳ Analyse très lente
**Causes possibles** :
- Fichier très volumineux
- Image de haute résolution
- PDF avec beaucoup de pages

**Solution** : Utilisez des fichiers optimisés

## Architecture Technique

```
Frontend (React)
    ↓
FileUpload Component
    ↓
HTTP POST multipart/form-data
    ↓
Parser-Produit Service (Port 8001)
    ↓
OCR / PDF Parser / HTML Parser
    ↓
Extraction de données structurées
    ↓
Réponse JSON
    ↓
Affichage dans l'interface
```

## Services nécessaires

Pour que l'upload fonctionne, ces services doivent être actifs :

1. ✅ **Frontend** (port 3000)
2. ✅ **Parser-Produit** (port 8001)
3. ✅ **PostgreSQL** (base de données)
4. ✅ **MinIO** (stockage fichiers)

Vérifier avec :
```powershell
docker ps
```

Démarrer tous les services :
```powershell
cd c:\projects\ecolabel-ms
docker-compose up -d
```

## Astuces pour de meilleurs résultats

### 📸 Pour les photos
- ✅ Éclairage uniforme
- ✅ Texte bien visible et net
- ✅ Évitez les reflets
- ✅ Cadrage centré sur l'étiquette

### 📄 Pour les PDFs
- ✅ Utilisez des PDFs avec texte (pas des scans)
- ✅ Évitez les PDFs protégés
- ✅ Limitez le nombre de pages

### 🏷️ Pour les codes-barres
- ✅ Code-barres complet et visible
- ✅ Pas de flou
- ✅ Bon contraste noir/blanc
- ✅ Évitez les déformations

## Support

### Problème technique
1. Vérifiez les logs Docker
2. Vérifiez que tous les services sont actifs
3. Consultez la documentation complète : `FILE_UPLOAD_FEATURE.md`

### Logs Parser-Produit
```powershell
docker logs ecolabel-parser
```

### Redémarrer le service
```powershell
docker-compose restart parser-produit
docker-compose restart widget-frontend
```

## Prochaines étapes

Après avoir uploadé et extrait les données :

1. **Recherchez le produit** dans la barre de recherche
2. **Consultez le score environnemental** si disponible
3. **Comparez** avec d'autres produits similaires

---

**Status** : ✅ Fonctionnalité active et opérationnelle

**URL** : http://localhost:3000

**Essayez maintenant** ! 🎉
