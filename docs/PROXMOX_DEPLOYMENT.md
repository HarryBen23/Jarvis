# 🐳 Guide de déploiement JARVIS sur Proxmox

## Architecture

```
Proxmox (Serveur physique)
└── LXC Container Ubuntu 24.04 ou VM
    ├── Docker
    ├── Docker Compose
    └── Services:
        ├── jarvis-api     (Port 8000) - Interface Web
        ├── jarvis-cli     (CLI)       - Microphone local
        └── home-assistant (Port 8123) - Domotique
```

## 📋 Prérequis Proxmox

- ✅ 20 cœurs + 64GB RAM (vous les avez!)
- ✅ Stockage: ~30GB minimum
- ✅ Réseau: accès internet

## 🚀 Étape 1: Créer un conteneur LXC

### Via l'interface Proxmox

1. **Proxmox Web UI** → `Datacenter` → `Create CT`
2. Configuration:
   - **OS**: Ubuntu 24.04
   - **CPU**: 4 cœurs (à adapter selon utilisation)
   - **Mémoire**: 8GB
   - **Stockage**: 50GB
   - **Network**: DHCP ou IP statique

3. **Create**

### Via CLI (plus rapide)

```bash
# SSH sur le serveur Proxmox
ssh root@proxmox.local

# Créer le conteneur
pct create 100 \
  /var/lib/vz/template/cache/ubuntu-24.04-standard_24.04-1_amd64.tar.zst \
  -hostname jarvis \
  -cores 4 \
  -memory 8192 \
  -storage local-lvm \
  -net0 name=eth0,ip=dhcp

# Démarrer
pct start 100

# Entrer dans le conteneur
pct enter 100
```

## 🔧 Étape 2: Configurer le conteneur

```bash
# 1. Mettre à jour le système
apt update && apt upgrade -y

# 2. Installer Docker et Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
bash get-docker.sh

# 3. Ajouter l'utilisateur au groupe docker
usermod -aG docker $USER
newgrp docker

# 4. Vérifier
docker --version
docker-compose --version
```

## 📥 Étape 3: Cloner JARVIS

```bash
# 1. Cloner le repo
cd /root
git clone https://github.com/HarryBen23/Jarvis.git
cd Jarvis

# 2. Copier la configuration
cp .env.example .env

# 3. Éditer avec vos clés
nano .env
```

### Remplir .env

```ini
# OpenAI - https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Home Assistant - Créer un token dans HA
HA_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# URLs
HA_URL=http://home-assistant:8123
API_PORT=8000
API_HOST=0.0.0.0
```

## 🎬 Étape 4: Lancer JARVIS

### Option A: Interface Web (Recommandé)

```bash
# Lancer le script
chmod +x scripts/start-web.sh
./scripts/start-web.sh

# Ou manuellement
docker-compose up -d

# Vérifier les services
docker-compose ps

# Voir les logs
docker-compose logs -f jarvis-api
```

### Option B: CLI avec microphone

```bash
# Assurez-vous d'avoir un microphone USB
# Vérifier les devices
docker exec jarvis-cli arecord -l

# Lancer le CLI
docker-compose up -d jarvis-cli

# Vérifier
docker-compose logs -f jarvis-cli
```

## 🌐 Étape 5: Accéder à JARVIS

### Interface Web

```
http://<IP_CONTENEUR>:8000
```

Exemple:
- Si l'IP du conteneur est `192.168.1.150` :
  - Ouvrir `http://192.168.1.150:8000`

### Home Assistant

```
http://<IP_CONTENEUR>:8123
```

## ✅ Vérifications

### Santé de l'API

```bash
# Depuis le conteneur
curl http://localhost:8000/health

# Depuis votre PC
curl http://<IP_CONTENEUR>:8000/health
```

### Logs des services

```bash
# Tous les logs
docker-compose logs

# API seulement
docker-compose logs jarvis-api

# Home Assistant
docker-compose logs home-assistant

# En temps réel (-f = follow)
docker-compose logs -f
```

## 🚪 Accès depuis votre PC

### En local (même réseau)

```
http://192.168.X.X:8000
```

### À distance (Internet)

#### Via Reverse Proxy (Recommandé)

```bash
# Installer Nginx dans le conteneur
apt install -y nginx

# Créer une config
cat > /etc/nginx/sites-available/jarvis << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Activer
ln -s /etc/nginx/sites-available/jarvis /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

#### Avec VPN

- Installer WireGuard ou OpenVPN
- Se connecter au VPN
- Accéder à `http://192.168.X.X:8000`

## 📊 Monitoring

### Vérifier l'utilisation CPU/RAM

```bash
# Depuis Proxmox
pct status 100

# Depuis le conteneur
top
# ou
htop
```

### Logs persistants

```bash
# Les logs sont dans ./logs/
ls -la logs/

# Voir les logs
tail -f logs/jarvis.log
```

## 🛠️ Maintenance

### Mise à jour JARVIS

```bash
# Arrêter les services
docker-compose down

# Mettre à jour le code
git pull

# Relancer
docker-compose up -d
```

### Sauvegarder la configuration

```bash
# Backup
tar -czf jarvis-backup.tar.gz config/ .env

# Restaurer
tar -xzf jarvis-backup.tar.gz
```

### Arrêter/Redémarrer

```bash
# Arrêter
docker-compose down

# Redémarrer
docker-compose up -d

# Redémarrer un service spécifique
docker-compose restart jarvis-api
```

## 🔌 Connecter le microphone

Si vous utilisez le mode CLI:

### Microphone USB

```bash
# Tester l'audio
docker exec jarvis-cli arecord -l

# Configurer dans .env
AUDIO_DEVICE_INDEX=1
```

### Microphone Réseau

- Connecter un Raspberry Pi avec microphone
- Rediriger vers JARVIS en réseau
- (Documentation à venir)

## 📈 Performances

Avec **20 cœurs + 64GB RAM** :

- **Plusieurs conteneurs** possibles
- **Temps de réponse** : <2s
- **Utilisateurs simultanés** : illimité (web)
- **Charge CPU** : très faible (<5%)

## 🐛 Troubleshooting

### Port déjà utilisé

```bash
# Voir qui utilise le port 8000
lsof -i :8000

# Changer le port dans .env
API_PORT=8001
```

### Pas de connexion internet

```bash
# Vérifier la réseau du conteneur
cat /etc/network/interfaces

# Redémarrer networking
systemctl restart networking
```

### DNS ne fonctionne pas

```bash
# Éditer resolv.conf
echo "nameserver 8.8.8.8" > /etc/resolv.conf
echo "nameserver 8.8.4.4" >> /etc/resolv.conf
```

### Docker ne démarre pas

```bash
# Vérifier le statut
systemctl status docker

# Redémarrer
systemctl restart docker

# Logs
journalctl -u docker -n 50
```

## 🎓 Ressources

- [Proxmox Documentation](https://pve.proxmox.com/wiki/)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Ubuntu Server Guide](https://ubuntu.com/server/docs)

---

**Besoin d'aide?** 
- Vérifier les logs: `docker-compose logs`
- Lancer le test: `python scripts/test-connection.py`
- Consulter le README.md
