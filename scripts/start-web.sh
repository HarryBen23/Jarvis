#!/bin/bash

# Script pour démarrer JARVIS avec interface web

set -e

echo "🚀 Démarrage de JARVIS avec Interface Web"
echo "========================================"

# Vérifier que docker-compose est disponible
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose non trouvé. Installez Docker."
    exit 1
fi

# Vérifier le fichier .env
if [ ! -f .env ]; then
    echo "❌ Fichier .env manquant"
    echo "Créez un fichier .env à partir de .env.example:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# Initialiser Home Assistant si nécessaire
echo "📋 Initialisation Home Assistant..."
bash scripts/init-homeassistant.sh

# Lancer les services
echo "🐳 Lancement des services Docker..."
docker-compose up -d

# Attendre que l'API soit prête
echo "⏳ Attente du démarrage de l'API..."
sleep 5

# Vérifier la santé
API_URL="http://localhost:8000"
for i in {1..30}; do
    if curl -s "$API_URL/health" > /dev/null 2>&1; then
        echo "✅ API prête!"
        break
    fi
    echo "⏳ Tentative $i/30..."
    sleep 2
done

echo ""
echo "========================================"
echo "🎉 JARVIS est prêt!"
echo ""
echo "🌐 Ouvrir dans le navigateur:"
echo "   http://localhost:8000"
echo ""
echo "📊 Voir les logs:"
echo "   docker-compose logs -f jarvis-api"
echo ""
echo "⏹️  Arrêter:"
echo "   docker-compose down"
echo ""
