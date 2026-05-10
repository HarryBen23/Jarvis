#!/bin/bash

# ============================================
# 🐳 JARVIS - Script d'installation Proxmox
# Installation automatisée complète
# ============================================

set -e  # Exit on error

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# ============================================
# ÉTAPE 1: Vérifications initiales
# ============================================

print_header "ÉTAPE 1: Vérifications initiales"

# Vérifier root
if [[ $EUID -ne 0 ]]; then
    print_error "Ce script doit être lancé en tant que root"
    echo "Lancez: sudo bash scripts/proxmox-install.sh"
    exit 1
fi

print_success "Lancé en tant que root"

# Vérifier le système
if [[ ! -f /etc/os-release ]]; then
    print_error "Système non supporté"
    exit 1
fi

source /etc/os-release
print_info "OS détecté: $PRETTY_NAME"

# Vérifier Proxmox
if ! pveversion &>/dev/null; then
    print_warning "Vous n'êtes pas dans Proxmox"
    print_info "Continuez manuellement ou installez Proxmox d'abord"
fi

echo ""

# ============================================
# ÉTAPE 2: Mettre à jour le système
# ============================================

print_header "ÉTAPE 2: Mise à jour du système"

print_info "Mise à jour des paquets..."
apt update
apt upgrade -y

print_success "Système à jour"
echo ""

# ============================================
# ÉTAPE 3: Installer Docker
# ============================================

print_header "ÉTAPE 3: Installation de Docker"

if command -v docker &> /dev/null; then
    print_success "Docker déjà installé: $(docker --version)"
else
    print_info "Installation de Docker..."
    
    # Ajouter la clé GPG Docker
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Ajouter le repo Docker
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Installer Docker
    apt update
    apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    print_success "Docker installé"
fi

# Vérifier docker-compose
if command -v docker-compose &> /dev/null; then
    print_success "docker-compose déjà installé: $(docker-compose --version)"
elif command -v docker compose &> /dev/null; then
    print_success "Docker Compose V2 installé"
else
    print_info "Installation de docker-compose v2..."
    apt install -y docker-compose
    print_success "docker-compose installé"
fi

# Démarrer Docker
systemctl start docker
systemctl enable docker

print_success "Docker service démarré"
echo ""

# ============================================
# ÉTAPE 4: Dépendances supplémentaires
# ============================================

print_header "ÉTAPE 4: Installation des dépendances"

print_info "Installation des paquets système..."

apt install -y \
    curl \
    wget \
    git \
    nano \
    htop \
    net-tools \
    alsa-utils \
    pulseaudio \
    libsndfile1 \
    ffmpeg \
    build-essential \
    python3-pip

print_success "Dépendances installées"
echo ""

# ============================================
# ÉTAPE 5: Cloner JARVIS
# ============================================

print_header "ÉTAPE 5: Cloner le projet JARVIS"

if [ -d "/root/Jarvis" ]; then
    print_warning "Le dossier /root/Jarvis existe déjà"
    read -p "Voulez-vous le mettre à jour? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd /root/Jarvis
        git pull
        print_success "JARVIS mis à jour"
    else
        print_info "Dossier conservé"
    fi
else
    print_info "Clonage de JARVIS..."
    cd /root
    git clone https://github.com/HarryBen23/Jarvis.git
    cd Jarvis
    print_success "JARVIS cloné dans /root/Jarvis"
fi

echo ""

# ============================================
# ÉTAPE 6: Configuration
# ============================================

print_header "ÉTAPE 6: Configuration"

if [ ! -f /root/Jarvis/.env ]; then
    print_info "Création du fichier .env..."
    cp /root/Jarvis/.env.example /root/Jarvis/.env
    print_success "Fichier .env créé"
else
    print_success "Fichier .env existe déjà"
fi

print_warning "IMPORTANT: Éditer /root/Jarvis/.env avec vos clés API"
print_info "Commande: nano /root/Jarvis/.env"
echo ""

# Demander si l'utilisateur veut l'éditer maintenant
read -p "Éditer .env maintenant? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    nano /root/Jarvis/.env
    print_success "Fichier .env édité"
else
    print_warning "N'oubliez pas de l'éditer avant de lancer!"
fi

echo ""

# ============================================
# ÉTAPE 7: Initialiser Home Assistant
# ============================================

print_header "ÉTAPE 7: Initialisation Home Assistant"

print_info "Création de la structure Home Assistant..."
bash /root/Jarvis/scripts/init-homeassistant.sh

print_success "Configuration Home Assistant créée"
echo ""

# ============================================
# ÉTAPE 8: Lancer les services
# ============================================

print_header "ÉTAPE 8: Lancement des services Docker"

cd /root/Jarvis

print_info "Démarrage des services..."
docker-compose up -d

# Attendre que les services soient prêts
print_info "Attente du démarrage des services (60 secondes)..."
sleep 60

# Vérifier l'état
print_info "Vérification de l'état des services..."
docker-compose ps

echo ""

# ============================================
# ÉTAPE 9: Tests
# ============================================

print_header "ÉTAPE 9: Tests de connexion"

print_info "Test de connexion API..."
if curl -s http://localhost:8000/health > /dev/null; then
    print_success "API prête!"
else
    print_warning "API pas encore prête, attendre 30 secondes..."
    sleep 30
fi

print_info "Test complet..."
python3 /root/Jarvis/scripts/test-connection.py

echo ""

# ============================================
# ÉTAPE 10: Informations finales
# ============================================

print_header "✅ Installation terminée!"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 JARVIS est prêt!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "🌐 Interface Web:"
echo -e "   ${BLUE}http://localhost:8000${NC}"
echo ""
echo "🏠 Home Assistant:"
echo -e "   ${BLUE}http://localhost:8123${NC}"
echo ""
echo "📊 Commandes utiles:"
echo "   docker-compose logs -f          (voir les logs)"
echo "   docker-compose ps               (voir l'état)"
echo "   docker-compose restart          (redémarrer)"
echo "   docker-compose down             (arrêter)"
echo ""
echo "📖 Documentation:"
echo "   /root/Jarvis/README.md"
echo "   /root/Jarvis/GETTING_STARTED.md"
echo "   /root/Jarvis/docs/TUTORIAL_COMPLET_FR.md"
echo ""
echo -e "${YELLOW}⚠️  Important:${NC}"
echo "   1. Éditer /root/Jarvis/.env avec vos clés API"
echo "   2. Redémarrer: docker-compose restart"
echo "   3. Puis tester: http://localhost:8000"
echo ""
echo "Bon amusement avec JARVIS! 🤖"
echo ""
