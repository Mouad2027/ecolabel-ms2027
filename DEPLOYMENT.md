# 🚀 Guide de Démarrage - EcoLabel-MS2027

## ✅ Projet Lancé avec Succès!

Tous les microservices sont opérationnels et accessibles.

## 🌐 Services Disponibles

| Service | URL | Description |
|---------|-----|-------------|
| **Parser-Produit** | http://localhost:8001 | Extraction de données depuis PDF/HTML/images |
| **NLP-Ingredients** | http://localhost:8002 | Extraction et normalisation d'ingrédients par NLP |
| **LCA-Lite** | http://localhost:8003 | Calcul d'analyse du cycle de vie simplifiée |
| **Scoring** | http://localhost:8004 | Calcul du score écologique (A-E) |
| **Widget-API** | http://localhost:8005 | API principale du widget |
| **Provenance** | http://localhost:8006 | Traçabilité des données |
| **Frontend** | http://localhost:3000 | Interface utilisateur React |
| **MinIO Console** | http://localhost:9001 | Console de stockage d'objets |
| **MLflow** | http://localhost:5000 | Suivi des expériences ML |
| **PostgreSQL** | localhost:5432 | Base de données |

## 📚 Documentation API

Chaque service expose une documentation Swagger interactive:

- Parser-Produit: http://localhost:8001/docs
- NLP-Ingredients: http://localhost:8002/docs
- LCA-Lite: http://localhost:8003/docs
- Scoring: http://localhost:8004/docs
- Widget-API: http://localhost:8005/docs
- Provenance: http://localhost:8006/docs

## 🔍 Vérification de l'État

### Vérifier tous les services
```powershell
docker compose ps
```

### Vérifier les health checks
```powershell
curl http://localhost:8001/health  # Parser
curl http://localhost:8002/health  # NLP
curl http://localhost:8003/health  # LCA
curl http://localhost:8004/health  # Scoring
curl http://localhost:8005/health  # Widget API
```

### Voir les logs d'un service
```powershell
docker logs ecolabel-parser
docker logs ecolabel-nlp
docker logs ecolabel-lca
docker logs ecolabel-scoring
docker logs ecolabel-widget-api
docker logs ecolabel-provenance
```

## 🛠️ Commandes Utiles

### Démarrer tous les services
```powershell
docker compose up -d
```

### Arrêter tous les services
```powershell
docker compose down
```

### Redémarrer un service spécifique
```powershell
docker compose restart ecolabel-parser
```

### Reconstruire et redémarrer
```powershell
docker compose up -d --build
```

### Supprimer tous les conteneurs et volumes
```powershell
docker compose down -v
```

## 🧪 Exécuter les Tests

### Tous les tests
```powershell
.\run-tests.ps1
```

### Test d'un service spécifique
```powershell
cd parser-produit
python -m pytest tests/ -v
```

## 📊 Accès aux Services Infrastructure

### MinIO (Stockage d'objets)
- **URL**: http://localhost:9001
- **Username**: minioadmin
- **Password**: minioadmin123
- **Buckets créés**:
  - ecolabel-artifacts
  - ecolabel-datasets
  - ecolabel-provenance
  - ecolabel-models

### MLflow (Suivi ML)
- **URL**: http://localhost:5000
- Tracking des expériences et versions de modèles

### PostgreSQL
- **Host**: localhost
- **Port**: 5432
- **Username**: postgres
- **Password**: postgres
- **Databases**:
  - parser_db
  - nlp_db
  - lca_db
  - scoring_db
  - widget_db
  - provenance_db

## 🔐 Identifiants par Défaut

Tous les identifiants peuvent être modifiés via les variables d'environnement dans le fichier `.env` (à créer).

**PostgreSQL**:
- User: postgres
- Password: postgres

**MinIO**:
- Root User: minioadmin
- Root Password: minioadmin123

**PgAdmin** (si activé):
- Email: admin@ecolabel.local
- Password: admin

## 📝 Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EcoLabel-MS2027 Architecture                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │   Frontend   │───▶│  Widget-API  │───▶│   Scoring    │◀──▶│ Provenance │ │
│  │   :3000      │    │   :8005      │    │   :8004      │    │   :8006    │ │
│  └──────────────┘    └──────┬───────┘    └──────┬───────┘    └────────────┘ │
│                             │                   │                            │
│                             ▼                   ▼                            │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   Parser     │───▶│     NLP      │───▶│   LCA-Lite   │                   │
│  │   :8001      │    │   :8002      │    │   :8003      │                   │
│  └──────────────┘    └──────────────┘    └──────────────┘                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## ✨ Prochaines Étapes

1. **Tester les endpoints** via Swagger UI
2. **Charger des datasets** dans MinIO
3. **Créer des expériences** dans MLflow
4. **Utiliser l'interface** frontend sur http://localhost:3000

## 🐛 Dépannage

### Les conteneurs ne démarrent pas
```powershell
docker compose logs
```

### Port déjà utilisé
Vérifier et arrêter les services qui utilisent les ports:
```powershell
netstat -ano | findstr "8001"
```

### Problème de base de données
Réinitialiser complètement:
```powershell
docker compose down -v
docker compose up -d
```

## 📞 Support

Pour plus d'informations, consultez:
- README.md - Documentation complète du projet
- TESTS.md - Documentation des tests
- Documentation Swagger de chaque service
