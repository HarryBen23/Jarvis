# Proxmox LXC Container Template - JARVIS

## 📋 Configuration recommandée pour nouveau conteneur

### Via CLI Proxmox

```bash
#!/bin/bash
# Script de création de conteneur JARVIS optimal

CONTAINER_ID=100
HOSTNAME="jarvis"
MEMORY=8192        # 8GB
CORES=4            # 4 cores
DISK=50            # 50GB
GATEWAY="192.168.1.1"
BRIDGE="vmbr0"     # Ajuster selon votre setup

# Créer le conteneur
pct create $CONTAINER_ID \
  /var/lib/vz/template/cache/ubuntu-24.04-standard_24.04-1_amd64.tar.zst \
  --hostname $HOSTNAME \
  --memory $MEMORY \
  --cores $CORES \
  --storage local-lvm \
  --rootfs local-lvm:$DISK \
  --net0 name=eth0,bridge=$BRIDGE,type=veth \
  --password PASSWORD_AUTO_GENERATE_THIS \
  --onboot 1

# Configuration réseau (DHCP)
echo -e "auto eth0\niface eth0 inet dhcp" > /var/lib/lxc/$CONTAINER_ID/rootfs/etc/network/interfaces

# Ou IP statique
# pct set $CONTAINER_ID -net0 name=eth0,bridge=$BRIDGE,ip=192.168.1.150/24,gw=$GATEWAY

# Démarrer
pct start $CONTAINER_ID

# Vérifier
pct status $CONTAINER_ID
```

### Paramètres pour différents cas d'usage

#### Cas A: Solo JARVIS (Décor de maison)
```bash
CORES=2
MEMORY=4096       # 4GB
DISK=30           # 30GB minimal
```

#### Cas B: Utilisation standard (Vous!)
```bash
CORES=4
MEMORY=8192       # 8GB
DISK=50           # 50GB
```

#### Cas C: Production avec monitoring
```bash
CORES=6
MEMORY=12288      # 12GB
DISK=100          # 100GB
```

#### Cas D: Multiple instances (5+ maisons)
```bash
CORES=8
MEMORY=16384      # 16GB
DISK=200          # 200GB
```

---

## 🔧 Configuration post-création

### Une fois le conteneur créé

```bash
# Entrer dans le conteneur
pct enter 100

# Ou SSH
ssh root@192.168.1.150

# Mettre à jour
apt update && apt upgrade -y

# Installation rapide
cd /root
git clone https://github.com/HarryBen23/Jarvis.git
cd Jarvis

# Lancer l'installation automatique complète
sudo bash scripts/proxmox-install.sh
```

---

## 🔐 Sécurité recommandée

### Firewall Proxmox

```bash
# Activer firewall conteneur
pct firewall set 100 ENABLE 1

# Ajouter règles
pct firewall add 100 IN -p tcp -dport 8000 -j ACCEPT  # JARVIS API
pct firewall add 100 IN -p tcp -dport 8123 -j ACCEPT  # Home Assistant
pct firewall add 100 IN -p tcp -dport 22 -j ACCEPT    # SSH

# SSH seulement depuis IP spécifique
pct firewall add 100 IN -p tcp -dport 22 -s 192.168.1.100 -j ACCEPT
```

### SecureStart

```bash
# Root password sécurisé
chpasswd <<< "root:YourSecurePassword"

# Désactiver SSH password auth
sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

# Redémarrer SSH
systemctl restart sshd

# Ajouter votre clé SSH publique
mkdir ~/.ssh
echo "ssh-rsa AAAA...YourPublicKey..." >> ~/.ssh/authorized_keys
```

---

## 📊 Monitoring et alertes

### Setup Prometheus (Optionnel)

```bash
# Dans le conteneur JARVIS
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v /etc/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

### Backup automatique Proxmox

```bash
# Configuration dans Proxmox
pvesh create /nodes/YOUR_NODE/vzdump \
  vmid 100 \
  storage local-lvm \
  mode snapshot \
  compress zstd \
  scriptexec 1
```

---

## 🔄 Snapshot et Restore

### Créer snapshot régulièrement

```bash
# Snapshot avant mise à jour majeure
pct snapshot 100 "before-jarvis-update-$(date +%Y%m%d)"

# Lister snapshots
pct listsnapshots 100

# Restaurer
pct rollback 100 "before-jarvis-update-20260510"
```

---

## 🌐 Accès réseau avancé

### Statique IP

```bash
# Modifier config
pct set 100 -net0 name=eth0,bridge=vmbr0,ip=192.168.1.150/24,gw=192.168.1.1

# Appliquer
pct stop 100
pct start 100
```

### Bridge réseau

```bash
# Si vous voulez un reseau isolé
pct set 100 -net0 name=eth0,bridge=vmbr1,type=veth
```

---

## 💾 Stockage

### Options de stockage

| Type | Performance | Espace | Coût |
|------|-------------|--------|------|
| local-lvm | ⭐⭐⭐ | Local | Bas |
| local-zfs | ⭐⭐⭐⭐ | Local | Moyen |
| NFS | ⭐⭐ | Réseau | Bas |
| iSCSI | ⭐⭐⭐ | Réseau | Moyen |
| Ceph | ⭐⭐⭐⭐ | Réseau | Haut |

### Migration vers autre storage

```bash
# Migrer conteneur vers nouveau storage
pct migrate 100 \
  --storage local-zfs \
  --disk rootfs
```

---

## 📈 Croissance future

### Scénario 1: Plus de ressources

```bash
# Augmenter CPU
pct set 100 -cores 8

# Augmenter RAM
pct set 100 -memory 16384

# Augmenter disque
pct resize 100 disk rootfs +50G
```

### Scénario 2: Ajouter des conteneurs

```bash
# Container 2: Backup
pct create 101 \
  /var/lib/vz/template/cache/ubuntu-24.04-standard_24.04-1_amd64.tar.zst \
  --hostname jarvis-backup \
  --memory 4096 \
  --cores 2

# Container 3: Database
pct create 102 \
  /var/lib/vz/template/cache/ubuntu-24.04-standard_24.04-1_amd64.tar.zst \
  --hostname jarvis-db \
  --memory 8192 \
  --cores 4
```

### Scénario 3: Cluster Proxmox

```bash
# Avec 64GB RAM et 20 cores:
# Possible de supporter 10+ conteneurs JARVIS
# Chacun pour une maison différente
```

---

## 🆘 Troubleshooting Proxmox

### Conteneur ne démarre pas

```bash
# Logs détaillés
tail -f /var/log/pve/lxc/100.log

# Unlock si nécessaire
pct unlock 100

# Forcer redémarrage
pct stop 100 --force
pct start 100
```

### Performances dégradées

```bash
# Vérifier pression CPU
top

# Vérifier I/O disque
iostat -x

# Vérifier réseau
iftop

# Augmenter ressources si nécessaire
pct set 100 -cores 6
pct restart 100
```

### Problème de réseau

```bash
# Vérifier depuis conteneur
ip a
ip route

# Ping gateway
ping 192.168.1.1

# Tester DNS
ping 8.8.8.8

# Relancer networking
systemctl restart networking
```

---

## ✅ Checklist post-installation

```
[ ] Conteneur créé et running
[ ] SSH fonctionne
[ ] Docker installé
[ ] JARVIS cloné et configuré
[ ] .env avec clés API
[ ] Services Docker en cours
[ ] http://localhost:8000 accessible
[ ] Tests passent
[ ] Snapshot créé
[ ] Backup configuré
[ ] Firewall configuré
[ ] Monitoring en place
```

---

## 📞 Support

- Proxmox: https://pve.proxmox.com/wiki/
- LXC: https://linuxcontainers.org/
- Docker in LXC: Bien supporté depuis Proxmox 7.0+

---

**Conteneur Proxmox JARVIS prêt! 🚀**
