#!/bin/bash
set -e

echo "🐳 Installation de Docker et Docker Compose..."
echo "========================================"

# Détecter le système
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Système Linux détecté"
    
    # Vérifier si Docker est déjà installé
    if command -v docker &> /dev/null; then
        echo "✅ Docker déjà installé: $(docker --version)"
    else
        echo "📥 Installation de Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo bash get-docker.sh
        rm get-docker.sh
        
        # Ajouter l'utilisateur au groupe docker
        sudo usermod -aG docker $USER
        echo "⚠️  Veuillez redémarrer votre session ou faire: newgrp docker"
    fi
    
    # Vérifier Docker Compose
    if command -v docker-compose &> /dev/null; then
        echo "✅ Docker Compose déjà installé: $(docker-compose --version)"
    else
        echo "📥 Installation de Docker Compose..."
        sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    fi

elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 macOS détecté"
    echo "Installer Docker Desktop depuis https://www.docker.com/products/docker-desktop"

elif [[ "$OSTYPE" == "msys" ]]; then
    echo "🪟 Windows détecté"
    echo "Installer Docker Desktop depuis https://www.docker.com/products/docker-desktop"
fi

echo ""
echo "✅ Docker installé avec succès!"
echo "🚀 Lancez: docker-compose up -d"
echo ""
