# Makefile pour JARVIS

.PHONY: help setup install-docker build up down logs test clean

help:
	@echo "🤖 JARVIS - Commands"
	@echo ""
	@echo "setup              - Initialiser le projet"
	@echo "install-docker     - Installer Docker et Docker Compose"
	@echo "build              - Construire l'image Docker"
	@echo "up                 - Lancer JARVIS (docker-compose up -d)"
	@echo "down               - Arrêter JARVIS"
	@echo "logs               - Afficher les logs"
	@echo "test               - Tester la connexion"
	@echo "shell              - Shell Python interactif"
	@echo "clean              - Nettoyer les fichiers temporaires"
	@echo ""

setup:
	@echo "🚀 Setup JARVIS..."
	@chmod +x scripts/setup.sh
	@./scripts/setup.sh

install-docker:
	@echo "🐳 Installing Docker..."
	@chmod +x scripts/install-docker.sh
	@./scripts/install-docker.sh

build:
	@echo "🏗️  Building Docker image..."
	docker-compose build

up:
	@echo "🚀 Launching JARVIS..."
	docker-compose up -d
	@echo "✅ JARVIS is running!"

down:
	@echo "⏹️  Stopping JARVIS..."
	docker-compose down

logs:
	docker-compose logs -f jarvis

test:
	@echo "🧪 Testing connections..."
	python scripts/test-connection.py

shell:
	source venv/bin/activate && python

clean:
	@echo "🧹 Cleaning..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf *.egg-info
	@echo "✅ Clean done"

.DEFAULT_GOAL := help
