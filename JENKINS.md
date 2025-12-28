# Jenkins CI/CD pour EcoLabel Microservices

Ce document décrit comment configurer et utiliser Jenkins pour le projet EcoLabel.

## 🚀 Démarrage rapide

### 1. Créer le réseau Docker (si pas déjà fait)

```bash
docker network create ecolabel-network
```

### 2. Démarrer Jenkins

```bash
docker-compose -f docker-compose.jenkins.yml up -d
```

### 3. Accéder à Jenkins

- **URL**: http://localhost:8080
- **Utilisateur**: `admin`
- **Mot de passe**: `admin` (par défaut, à changer en production!)

## 📁 Structure des fichiers

```
├── Jenkinsfile                    # Pipeline principal
├── docker-compose.jenkins.yml     # Docker Compose pour Jenkins
└── jenkins/
    ├── Dockerfile                 # Image Jenkins personnalisée
    ├── plugins.txt               # Plugins Jenkins à installer
    └── casc.yaml                 # Configuration as Code
```

## 🔧 Configuration

### Variables d'environnement

Créez un fichier `.env` ou exportez ces variables :

```bash
# Credentials Jenkins Admin
JENKINS_ADMIN_PASSWORD=votre_mot_de_passe_securise

# Docker Registry (pour push des images)
DOCKER_REGISTRY_USER=votre_username
DOCKER_REGISTRY_PASSWORD=votre_password

# Base de données
POSTGRES_PASSWORD=postgres

# MinIO
MINIO_ROOT_PASSWORD=minioadmin123

# Git Repository (optionnel)
GIT_REPO_URL=https://github.com/votre-org/ecolabel-ms.git
```

### Configurer les credentials dans Jenkins

1. Aller dans **Manage Jenkins** → **Manage Credentials**
2. Ajouter les credentials suivants :
   - `docker-registry-credentials` : Username/Password pour Docker Hub
   - `postgres-password` : Secret text pour PostgreSQL
   - `minio-password` : Secret text pour MinIO

## 📋 Pipeline Stages

Le pipeline `Jenkinsfile` exécute les étapes suivantes :

| Stage | Description | Branches |
|-------|-------------|----------|
| **Checkout** | Clone le repository | Toutes |
| **Lint & Static Analysis** | Vérifie le code avec flake8/black | Toutes |
| **Build Docker Images** | Construit les images Docker | Toutes |
| **Run Unit Tests** | Exécute les tests unitaires | Toutes |
| **Integration Tests** | Tests d'intégration end-to-end | main, develop |
| **Security Scan** | Scan de vulnérabilités avec Trivy | main, develop |
| **Push to Registry** | Push les images vers le registry | main, develop, tags |
| **Deploy to Staging** | Déploiement staging | develop |
| **Deploy to Production** | Déploiement production (manuel) | main |

## 🎯 Création d'un Job

### Option 1: Pipeline Multibranch (recommandé)

1. **New Item** → **Multibranch Pipeline**
2. Nom: `ecolabel-ms`
3. **Branch Sources** → **Git**
   - Repository URL: votre repo Git
   - Credentials: si nécessaire
4. **Build Configuration**
   - Mode: `by Jenkinsfile`
   - Script Path: `Jenkinsfile`
5. **Save**

### Option 2: Pipeline simple

1. **New Item** → **Pipeline**
2. Nom: `ecolabel-build`
3. **Pipeline** → **Pipeline script from SCM**
   - SCM: Git
   - Repository URL: votre repo
   - Script Path: `Jenkinsfile`
4. **Save**

## 🔄 Webhooks (GitHub/GitLab)

### GitHub

1. Settings du repo → Webhooks → Add webhook
2. Payload URL: `http://votre-jenkins:8080/github-webhook/`
3. Content type: `application/json`
4. Events: Push events, Pull request events

### GitLab

1. Settings → Webhooks
2. URL: `http://votre-jenkins:8080/project/ecolabel-ms`
3. Trigger: Push events, Merge request events

## 🐳 Docker-in-Docker

Le setup utilise Docker-in-Docker (DinD) pour builder les images. Assurez-vous que :

1. Le socket Docker est monté : `/var/run/docker.sock`
2. Jenkins a les permissions nécessaires (mode `privileged`)

## 📊 Monitoring

### Logs Jenkins

```bash
docker logs -f ecolabel-jenkins
```

### État des builds

- Blue Ocean UI: http://localhost:8080/blue
- Classic UI: http://localhost:8080/job/ecolabel-ms/

## 🔒 Sécurité

### En production

1. **Changer le mot de passe admin par défaut**
2. **Configurer HTTPS** avec un reverse proxy (nginx/traefik)
3. **Limiter l'accès réseau** à Jenkins
4. **Activer l'audit logging**
5. **Utiliser des credentials sécurisés** (pas de mots de passe en clair)

### Exemple nginx reverse proxy

```nginx
server {
    listen 443 ssl;
    server_name jenkins.votre-domaine.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🛠️ Dépannage

### Jenkins ne démarre pas

```bash
# Vérifier les logs
docker logs ecolabel-jenkins

# Vérifier les permissions du socket Docker
ls -la /var/run/docker.sock
```

### Build échoue au push

Vérifiez que les credentials Docker Registry sont correctement configurés.

### Tests échouent

```bash
# Vérifier que le réseau existe
docker network ls | grep ecolabel

# Vérifier que les services sont up
docker-compose ps
```

## 📚 Ressources

- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Jenkins Pipeline Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [Configuration as Code Plugin](https://plugins.jenkins.io/configuration-as-code/)
- [Docker Pipeline Plugin](https://plugins.jenkins.io/docker-workflow/)
