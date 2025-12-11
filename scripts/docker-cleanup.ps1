# Script de nettoyage Docker - Libère l'espace disque
# Run: .\scripts\docker-cleanup.ps1

Write-Host "🧹 Nettoyage Docker en cours..." -ForegroundColor Cyan

# 1. Arrêt de tous les conteneurs
Write-Host "`n📦 Arrêt des conteneurs..." -ForegroundColor Yellow
docker-compose down

# 2. Suppression des conteneurs arrêtés
Write-Host "`n🗑️  Suppression des conteneurs arrêtés..." -ForegroundColor Yellow
docker container prune -f

# 3. Suppression des images non utilisées
Write-Host "`n🖼️  Suppression des images non utilisées..." -ForegroundColor Yellow
docker image prune -a -f

# 4. Suppression des volumes non utilisés
Write-Host "`n💾 Suppression des volumes non utilisés..." -ForegroundColor Yellow
docker volume prune -f

# 5. Suppression des réseaux non utilisés
Write-Host "`n🌐 Suppression des réseaux non utilisés..." -ForegroundColor Yellow
docker network prune -f

# 6. Suppression du cache de build
Write-Host "`n🏗️  Suppression du cache de build..." -ForegroundColor Yellow
docker builder prune -a -f

# 7. Nettoyage système complet
Write-Host "`n🚀 Nettoyage système complet..." -ForegroundColor Yellow
docker system prune -a --volumes -f

Write-Host "`n✅ Nettoyage terminé!" -ForegroundColor Green
Write-Host "`n📊 Espace libéré:" -ForegroundColor Cyan
docker system df

Write-Host "`n💡 Pour redémarrer le projet:" -ForegroundColor Cyan
Write-Host "   docker-compose up -d" -ForegroundColor White
