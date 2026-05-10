#!/bin/bash

# Script principal pour gérer JARVIS facilement

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

show_menu() {
    echo ""
    echo "🤖 JARVIS - Control Menu"
    echo "======================================"
    echo "1) Démarrer l'interface web"
    echo "2) Démarrer le CLI (microphone)"
    echo "3) Arrêter tous les services"
    echo "4) Voir les logs"
    echo "5) Tester la connexion"
    echo "6) Initialiser (première fois)"
    echo "7) Quitter"
    echo "======================================"
    read -p "Choisir une option: " choice
}

start_web() {
    echo "🌐 Démarrage de l'interface web..."
    cd "$PROJECT_DIR"
    bash scripts/start-web.sh
}

start_cli() {
    echo "🎤 Démarrage du CLI..."
    cd "$PROJECT_DIR"
    docker-compose up -d jarvis-cli
    docker-compose logs -f jarvis-cli
}

stop_all() {
    echo "⏹️  Arrêt des services..."
    cd "$PROJECT_DIR"
    docker-compose down
    echo "✅ Services arrêtés"
}

show_logs() {
    echo "📊 Logs en temps réel..."
    cd "$PROJECT_DIR"
    docker-compose logs -f
}

test_connection() {
    echo "🧪 Test de connexion..."
    cd "$PROJECT_DIR"
    python scripts/test-connection.py
}

init_first_time() {
    echo "📋 Initialisation première fois..."
    cd "$PROJECT_DIR"
    
    if [ ! -f .env ]; then
        cp .env.example .env
        echo "✅ Fichier .env créé"
        echo "⚠️  Veuillez éditer .env avec vos clés API:"
        echo "   nano .env"
    else
        echo "✅ .env existe déjà"
    fi
    
    echo ""
    echo "📥 Installation des dépendances..."
    if command -v docker &> /dev/null; then
        echo "✅ Docker trouvé"
    else
        echo "❌ Docker non trouvé. Installation..."
        bash scripts/install-docker.sh
    fi
    
    echo "✅ Initialisation terminée!"
}

main_loop() {
    while true; do
        show_menu
        
        case $choice in
            1) start_web ;;
            2) start_cli ;;
            3) stop_all ;;
            4) show_logs ;;
            5) test_connection ;;
            6) init_first_time ;;
            7) 
                echo "👋 Au revoir!"
                exit 0
                ;;
            *)
                echo "❌ Option invalide"
                ;;
        esac
    done
}

# Si pas d'arguments, afficher le menu
if [ $# -eq 0 ]; then
    main_loop
else
    # Sinon exécuter la commande directement
    case $1 in
        web) start_web ;;
        cli) start_cli ;;
        stop) stop_all ;;
        logs) show_logs ;;
        test) test_connection ;;
        init) init_first_time ;;
        *)
            echo "Usage: $0 [web|cli|stop|logs|test|init]"
            exit 1
            ;;
    esac
fi
