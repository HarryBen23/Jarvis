#!/usr/bin/env bash
set -euo pipefail

# Déploiement automatique pour le serveur
# Usage: sudo bash scripts/deploy_server.sh /opt/jarvis

REPO_URL="https://github.com/HarryBen23/Jarvis.git"
BRANCH="feature/mark-template"
REPO_DIR="${1:-/opt/jarvis}"

echo "Déploiement Jarvis -> repo: $REPO_URL, branch: $BRANCH, dir: $REPO_DIR"

if [ ! -d "$REPO_DIR" ]; then
  echo "Création du dossier $REPO_DIR"
  mkdir -p "$REPO_DIR"
fi

if [ ! -d "$REPO_DIR/.git" ]; then
  echo "Clonage du dépôt..."
  git clone "$REPO_URL" "$REPO_DIR"
fi

cd "$REPO_DIR"
echo "Récupération des refs distants..."
git fetch origin --prune

if git ls-remote --exit-code --heads origin "$BRANCH" >/dev/null 2>&1; then
  echo "Branche $BRANCH trouvée -> checkout"
  git checkout "$BRANCH"
  git reset --hard "origin/$BRANCH"
else
  echo "Branche $BRANCH non trouvée sur remote -> utilisation de 'main'"
  git checkout main
  git pull origin main
fi

# Installer dépendances Python si présentes
if [ -f requirements.txt ]; then
  echo "Installation des dépendances Python (requirements.txt)"
  python3 -m pip install -r requirements.txt --user || true
fi

# Si docker-compose présent : reconstruire et relancer
if [ -f docker-compose.yml ]; then
  echo "docker-compose détecté -> build & up"
  docker-compose pull || true
  docker-compose up -d --build
  echo "Déployé via docker-compose"
  exit 0
fi

# Si service systemd 'jarvis' présent : restart
if systemctl list-units --full -all | grep -q "jarvis"; then
  echo "Redémarrage du service systemd 'jarvis'"
  systemctl restart jarvis
  echo "Service 'jarvis' redémarré"
  exit 0
fi

# Sinon lancer uvicorn en arrière-plan
echo "Lancement uvicorn en arrière-plan (fallback)"
nohup python3 -m uvicorn src.api:app --host 0.0.0.0 --port 8000 > jarvis.log 2>&1 &
echo "Uvicorn démarré (voir jarvis.log)"
