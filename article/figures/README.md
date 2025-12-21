# Figures pour l'article scientifique

Ce dossier contient les captures d'écran et images à utiliser dans l'article LaTeX.

## Images requises

### 1. Interface principale (`interface_home.png`)
**Capture d'écran de** : `http://localhost:3000`
- Affiche la page d'accueil avec la zone d'upload
- Doit montrer le bouton "Parcourir les fichiers" et la zone de glisser-déposer
- Résolution recommandée : 1920x1080

**Comment capturer** :
1. Ouvrir `http://localhost:3000` dans un navigateur
2. Prendre une capture d'écran de la section "📸 Analyser un Produit"
3. Sauvegarder comme `interface_home.png`

### 2. Résultat Nutella (`result_nutella.png`)
**Capture d'écran de** : Page de résultats après upload d'un produit
- Doit montrer l'éco-score (lettre + couleur)
- Détails des impacts (CO2, eau, énergie)
- Liste des ingrédients
- Poids du produit affiché

**Comment capturer** :
1. Upload une image de Nutella ou utiliser le barcode
2. Attendre l'analyse complète
3. Capturer la section "Analyse Terminée" avec l'éco-score
4. Sauvegarder comme `result_nutella.png`

### 3. Services Docker (`docker_services.png`)
**Capture d'écran de** : Sortie de la commande `docker ps`
- Affiche tous les conteneurs actifs
- Doit montrer les ports et status
- Utiliser un terminal avec fond clair pour meilleure lisibilité

**Comment capturer** :
```powershell
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```
Capturer la sortie et sauvegarder comme `docker_services.png`

### 4. Trace de provenance (`provenance_json.png`)
**Capture d'écran de** : Réponse JSON du service provenance
- Endpoint : `http://localhost:8006/provenance/{score_id}`
- Doit montrer la structure JSON complète avec UUID, ingrédients, facteurs

**Comment capturer** :
1. Récupérer un `score_id` depuis un résultat d'analyse
2. Ouvrir `http://localhost:8006/provenance/{score_id}` dans un navigateur
3. Utiliser un formatteur JSON (extension Chrome/Firefox)
4. Capturer et sauvegarder comme `provenance_json.png`

## Captures d'écran supplémentaires (optionnelles)

### 5. Pipeline NLP (`nlp_processing.png`)
- Capture de la console pendant extraction NLP
- Logs montrant le traitement des ingrédients

### 6. Dashboard MLflow (`mlflow_dashboard.png`)
- Interface MLflow : `http://localhost:5000`
- Expériences de scoring ML

### 7. Architecture réseau (`docker_network.png`)
- Sortie de `docker network inspect ecolabel-ms_default`
- Montre les connexions entre services

## Format et résolution

- **Format** : PNG (meilleure qualité pour LaTeX)
- **Résolution minimale** : 1200x800 pixels
- **DPI** : 150-300 pour impression
- **Taille maximale** : 5 MB par image

## Compilation LaTeX

Une fois les images ajoutées dans ce dossier, compiler l'article avec :

```bash
cd article
pdflatex article_scientifique.tex
bibtex article_scientifique
pdflatex article_scientifique.tex
pdflatex article_scientifique.tex
```

## Notes

- Les images doivent être nommées exactement comme indiqué
- Vérifier que le dossier `figures/` est au même niveau que `article_scientifique.tex`
- Si une image manque, LaTeX affichera un warning mais compilera quand même
