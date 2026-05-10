# 🐳 Proxmox Deployment - Configuration avancée

Guide complet pour déployer JARVIS sur votre infrastructure Proxmox.

---

## 📋 Table des matières

1. [Architecture recommandée](#architecture)
2. [Prérequis Proxmox](#prérequis)
3. [Créer un conteneur LXC](#lxc-container)
4. [Installation rapide](#installation-rapide)
5. [Accès réseau](#réseau)
6. [Backup et restore](#backup)
7. [Monitoring](#monitoring)
8. [Troubleshooting Proxmox](#troubleshooting)
9. [Optimisations](#optimisations)
10. [FAQ Proxmox](#faq)

---

## 🏗️ Architecture recommandée {#architecture}

### Votre setup (20 cœurs + 64GB RAM)

```
PROXMOX (Hôte physique)
├── 20 cœurs CPU
├── 64 GB RAM
└── Stockage SSD/HDD

    ├─ LXC Container 1: JARVIS
    │  ├─ 4 cœurs (configurable)
    │  ├─ 8 GB RAM (configurable)
    │  ├─ 50 GB stockage
    │  └─ Ubuntu 24.04
    │
    └─ (Optionnel) LXC Container 2: Backup
       ├─ 2 cœurs
       ├─ 4 GB RAM
       └─ Stockage supplémentaire
```

### Services dans le conteneur

```
LXC Container: JARVIS
├── Docker Daemon
├── Docker Compose
└── Services Docker:
    ├─ jarvis-api      (Port 8000)
    ├─ jarvis-cli      (Optional)
    ├─ home-assistant  (Port 8123)
    └─ Network: bridge
```

---

## ✅ Prérequis Proxmox {#prérequis}

### Matériel

- ✅ CPU moderne (Intel/AMD)
- ✅ 20 cœurs + 64 GB RAM (vous les avez!)
- ✅ 100+ GB stockage SSD disponible
- ✅ Réseau stable (Gigabit recommandé)

### Logiciel

- ✅ Proxmox VE 7.0+ (ou 8.0+)
- ✅ Ubuntu 24.04 LTS (ou Debian 12)
- ✅ Accès root Proxmox

### Vérifications

```bash
# Vérifier votre Proxmox
pveversion

# Résultat attendu:
# pve-manager/8.0.3/9356e11a (Proxmox VE 8.0)

# Vérifier les ressources disponibles
pvesh get /nodes/YOUR_NODE/status

# Vérifier le stockage
pvesh get /storage
```

---

## 🚀 Créer un conteneur LXC {#lxc-container}

### Option 1: Via l'interface Proxmox

**Étape 1**: Ouvrir Proxmox Web UI

```
https://votre-proxmox:8006
```

**Étape 2**: Aller à `Datacenter` → `Create CT`

```
┌─────────────────────────────────────┐
│ Create Container                    │
├─────────────────────────────────────┤
│ Node: YOUR_NODE                     │
│ CT ID: 100 (ou suivant)             │
│ Hostname: jarvis                    │
│ Password: (générer sécurisé)        │
└─────────────────────────────────────┘
```

**Étape 3**: Template & Storage

```
├─ OS Image: ubuntu-24.04-standard
├─ Storage: local-lvm (ou votre storage)
└─ Disk Size: 50 GB
```

**Étape 4**: CPU & Mémoire

```
├─ Cores: 4 (ou plus selon utilisation)
└─ Memory: 8192 MB
```

**Étape 5**: Réseau

```
├─ Network: eth0
├─ IP: DHCP (ou IP statique, ex: 192.168.1.150/24)
├─ Gateway: 192.168.1.1
└─ DNS: 8.8.8.8
```

**Étape 6**: Vérifier et Create

### Option 2: Via CLI Proxmox

```bash
# SSH au serveur Proxmox
ssh root@proxmox.local

# Créer le conteneur
pct create 100 \
  /var/lib/vz/template/cache/ubuntu-24.04-standard_24.04-1_amd64.tar.zst \
  -hostname jarvis \
  -cores 4 \
  -memory 8192 \
  -storage local-lvm \
  -disk 50 \
  -net0 name=eth0,ip=dhcp

# Démarrer
pct start 100

# Vérifier
pct status 100

# Entrer dans le conteneur
pct enter 100
```

---

## ⚡ Installation rapide {#installation-rapide}

### Dans le conteneur LXC (Ubuntu 24.04)

**Étape 1**: Entrer et mettre à jour

```bash
# Depuis Proxmox
pct enter 100

# Ou SSH
ssh root@192.168.1.150

# Mettre à jour
apt update && apt upgrade -y
```

**Étape 2**: Utiliser le script automatisé

```bash
# Cloner le repo
cd /root
git clone https://github.com/HarryBen23/Jarvis.git
cd Jarvis

# Lancer l'installation COMPLÈTE
sudo bash scripts/proxmox-install.sh
```

**Le script fera automatiquement**:
- ✅ Installer Docker
- ✅ Installer docker-compose
- ✅ Cloner JARVIS
- ✅ Créer la config
- ✅ Lancer les services
- ✅ Tester les connexions

### Après l'installation

```bash
# Éditer la config avec vos clés API
nano /root/Jarvis/.env

# Redémarrer
docker-compose restart jarvis-api

# Vérifier
docker-compose ps
http://localhost:8000
```

---

## 🌐 Accès réseau {#réseau}

### Accès local (même réseau)

```
http://192.168.1.150:8000
    ↓
Remplacer 192.168.1.150 par l'IP de votre conteneur
```

### Accès depuis l'extérieur

#### Option 1: Reverse Proxy Nginx (SÉCURISÉ ⭐)

**Installation dans le conteneur**:

```bash
apt install -y nginx
```

**Configuration** (`/etc/nginx/sites-available/jarvis`):

```nginx
server {
    listen 80;
    server_name _;
    client_max_body_size 100M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://localhost:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
```

**Activer**:

```bash
ln -s /etc/nginx/sites-available/jarvis /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

**Pour HTTPS (LetsEncrypt)**:

```bash
apt install -y certbot python3-certbot-nginx

certbot --nginx -d jarvis.votredomaine.com
```

#### Option 2: VPN (Recommandé pour sécurité)

**Installer WireGuard**:

```bash
apt install -y wireguard wireguard-tools

# Générer les clés
wg genkey | tee privatekey | wg pubkey > publickey

# Configuration complexe - voir docs WireGuard
```

#### Option 3: Portail Proxmox

Proxmox peut rediriger certains ports via l'interface:

```
Datacenter → Firewall → Port Forwarding
```

---

## 💾 Backup et Restore {#backup}

### Backup automatique via Proxmox

**Via l'interface Proxmox**:

```
Datacenter → Backup → Add
├─ CT: 100 (JARVIS)
├─ Storage: local-lvm
├─ Schedule: daily (2 AM)
├─ Retention: 7 days
└─ Save
```

### Backup manuel JARVIS

```bash
# Dans le conteneur
cd /root/Jarvis

# Sauvegarder config
tar -czf jarvis-backup-$(date +%Y%m%d).tar.gz \
  config/ .env logs/

# Copier sur Proxmox
scp jarvis-backup-*.tar.gz root@proxmox:/backups/

# Ou sur un serveur NAS
rsync -av --delete config/ nas:/backups/jarvis/config/
```

### Restore

```bash
# Restaurer depuis backup
cd /root/Jarvis

# Extraire
tar -xzf jarvis-backup-20260510.tar.gz

# Redémarrer
docker-compose restart

# Vérifier
docker-compose ps
```

---

## 📊 Monitoring {#monitoring}

### Ressources du conteneur

**Voir l'utilisation CPU/RAM en temps réel**:

```bash
# Dans le conteneur
htop

# Ou depuis Proxmox
pct status 100

# Ou API Proxmox
curl https://proxmox:8006/api2/json/nodes/YOUR_NODE/lxc/100/status/current
```

### Monitoring JARVIS

```bash
# Voir les statistiques Docker
docker stats

# Logs en temps réel
docker-compose logs -f

# Ressources des services
docker inspect jarvis-api | grep -A 20 MemLimit
```

### Alertes Proxmox

**Configurer les alertes**:

```
Datacenter → Alerts
├─ Email: votre@email.com
├─ Notification Level: Warning
└─ Enabled: Yes
```

---

## 🔧 Troubleshooting Proxmox {#troubleshooting}

### Le conteneur ne démarre pas

```bash
# Vérifier le status
pct status 100

# Voir les logs détaillés
pct unlock 100  # Si locked

# Vérifier les ressources
pct config 100

# Vérifier les erreurs
pvestatd status
```

### Performance lente

```bash
# Alouer plus de ressources
pct set 100 -cores 6 -memory 12288

# Redémarrer
pct stop 100
pct start 100
```

### Problème de réseau

```bash
# Vérifier la config réseau
cat /root/Jarvis/docker-compose.yml

# Redémarrer networking
systemctl restart networking

# Vérifier les règles firewall
iptables -L
```

### Conteneur plein

```bash
# Vérifier l'utilisation disque
df -h

# Nettoyer Docker
docker system prune -a

# Augmenter la taille du disque
pct resize 100 disk rootfs +20G
```

---

## ⚙️ Optimisations {#optimisations}

### Performance maximale

```bash
# Allouer plus de ressources
pct set 100 -cores 8 -memory 16384

# Activer nested virtualization (optionnel)
pct set 100 -features nesting=1

# Utiliser SSD storage
pct set 100 -storage local-lvm
```

### Économiser les ressources

```bash
# Si serveur partagé
pct set 100 -cores 2 -memory 4096

# Utiliser des images légères
# Debian 12 au lieu d'Ubuntu
```

### Sécurité

```bash
# Chiffrer le backup
gpg -c jarvis-backup.tar.gz

# Limiter l'accès firewall
pct firewall set 100 ENABLE 1
pct firewall add 100 IN -p tcp -dport 8000 -j ACCEPT
```

---

## ❓ FAQ Proxmox {#faq}

### Q: Combien de ressources allouer?

```
Minimum:
├─ CPU: 2 cœurs
├─ RAM: 4 GB
└─ Disque: 30 GB

Recommandé (vous):
├─ CPU: 4-6 cœurs
├─ RAM: 8-12 GB
└─ Disque: 50-100 GB

Idéal:
├─ CPU: 8+ cœurs
├─ RAM: 16+ GB
└─ Disque: 100+ GB
```

### Q: Quel template utiliser?

```
✅ Ubuntu 24.04 LTS (meilleur support)
✅ Debian 12 (léger)
❌ Pas CentOS (end-of-life)
```

### Q: Combien de conteneurs?

```
Dans Proxmox (avec 20 cores + 64GB):
├─ 1 conteneur JARVIS: 20%
├─ Plus plusieurs autres services: 80%
└─ Possible: 5-10 maisons intelligentes!
```

### Q: Accès SSH au conteneur?

```bash
# Depuis Proxmox
ssh root@192.168.1.150

# Ou via Proxmox console
pct enter 100

# Générer clés SSH
ssh-keygen -t ed25519
```

### Q: Snapshots avant mise à jour?

```bash
# Créer snapshot
pct snapshot 100 before-update

# Plus tard, restaurer
pct rollback 100 before-update
```

### Q: Migrater vers autre serveur Proxmox?

```bash
# Migration facile entre nœuds Proxmox
pct migrate 100 newnode

# Avec stockage partagé:
# Pratiquement sans downtime
```

### Q: Ajouter plus de stockage?

```bash
# Augmenter partition racine
pct resize 100 disk rootfs +50G

# Ajouter volume externe
pct set 100 -mp0 /local-lvm:vm-100-disk-2,size=100G
```

### Q: Backup vers NAS?

```bash
# Monter NAS dans le conteneur
apt install -y nfs-common cifs-utils

# Configurer backup auto
echo "NAS_IP:/export/backups /backups nfs defaults 0 0" >> /etc/fstab

# Ou utiliser rsync
rsync -av /root/Jarvis root@nas:/backups/jarvis/
```

---

## 📞 Support Proxmox

**Ressources**:
- [Proxmox Documentation](https://pve.proxmox.com/wiki/)
- [Proxmox Forum](https://forum.proxmox.com/)
- [Proxmox API](https://pve.proxmox.com/pve-docs/api-viewer/)

**Pour JARVIS**:
- [GitHub Issues](https://github.com/HarryBen23/Jarvis/issues)
- [Documentation JARVIS](../README.md)

---

**Installation Proxmox réussie? 🎉**

Prochaines étapes:
1. Configurer Home Assistant
2. Ajouter vos appareils domotiques
3. Lancer les testens
4. Profiter de JARVIS!

💡 **Conseil**: Faire un snapshot avant d'ajouter beaucoup d'appareils.
