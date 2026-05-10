#!/bin/bash
set -e

echo "🚀 Installation de JARVIS..."
echo "========================================"

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

echo "✅ Python 3 trouvé: $(python3 --version)"

# Créer l'environnement virtuel
echo "📦 Création de l'environnement virtuel..."
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# Créer les dossiers nécessaires
mkdir -p config/home-assistant
mkdir -p logs

# Copier .env
if [ ! -f .env ]; then
    echo "📋 Copie du fichier .env..."
    cp .env.example .env
    echo "⚠️  Veuillez configurer .env avec vos clés API"
else
    echo "✅ Fichier .env existant conservé"
fi

echo ""
echo "✅ Installation terminée!"
echo ""
echo "📝 Prochaines étapes:"
echo "  1. Éditer .env avec vos clés API OpenAI et Home Assistant"
echo "  2. Lancer: docker-compose up -d"
echo "  3. Ou en développement: source venv/bin/activate && python src/jarvis.py"
echo ""
