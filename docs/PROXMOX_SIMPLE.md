# 🐳 Proxmox pour Débutants - Simple & Direct

Guide simple pour mettre JARVIS sur Proxmox sans complications.

---

## C'est quoi Proxmox?

```
Proxmox = Hyperviseur virtualization
= Vous pouvez lancer plusieurs "ordinateurs" sur le même serveur
= Parfait pour centraliser toute votre domotique!
```

---

## Étape 1: Accéder à Proxmox

### Ouvrir l'interface web

```
https://VOTRE_IP_PROXMOX:8006
```

Exemple:
```
https://192.168.1.100:8006
```

Login avec:
```
User: root
Password: (celui que vous avez défini)
Realm: Linux PAM
```

---

## Étape 2: Créer un conteneur pour JARVIS

### Via l'interface (le plus simple)

**Étape 2.1**: Cliquer sur `Datacenter` (à gauche)

```
Datacenter
└─ Créer CT
```

**Étape 2.2**: Cliquer sur le bouton **Create CT**

```
[+ Create CT]  ← Cliquer ici
```

**Étape 2.3**: Remplir les infos

```
┌─────────────────────────────────────┐
│ General                             │
├─────────────────────────────────────┤
│ Node: YOUR_NODE (déjà sélectionné)  │
│ CT ID: 100 ← numéro du conteneur    │
│ Hostname: jarvis                    │
│ Password: (générer un bon password) │
│ Resource Pool: (laisser défaut)     │
└─────────────────────────────────────┘

[Next]
```

**Étape 2.4**: Choix du template

```
┌─────────────────────────────────────┐
│ Template                            │
├─────────────────────────────────────┤
│ Storage: local (ou votre storage)   │
│                                     │
│ Select OS Image:                    │
│ ☑ ubuntu-24.04-standard             │
│   (☐ debian-12-standard)            │
│ ☐ debian-11-standard               │
│                                     │
│ Content Type:                       │
│ ○ CT (conteneur LXC)  ← C'EST BON   │
│ ○ VM (machine virtuelle)            │
└─────────────────────────────────────┘

[Next]
```

**Étape 2.5**: Disque

```
┌─────────────────────────────────────┐
│ Disks                               │
├─────────────────────────────────────┤
│ Storage: local-lvm                  │
│ Disk Size: 50 ← 50 GB               │
│                                     │
│ (Suffisant pour JARVIS + HA)        │
└─────────────────────────────────────┘

[Next]
```

**Étape 2.6**: CPU & Mémoire

```
┌─────────────────────────────────────┐
│ CPU                                 │
├─────────────────────────────────────┤
│ Cores: 4                            │
│ (Vous avez 20 cores, utiliser 4)    │
│                                     │
│ Memory                              │
│ ├─ Memory (MB): 8192 ← 8GB         │
│ └─ Swap (MB): 512                   │
└─────────────────────────────────────┘

[Next]
```

**Étape 2.7**: Réseau

```
┌─────────────────────────────────────┐
│ Network                             │
├─────────────────────────────────────┤
│ Hostname: jarvis (déjà rempli)      │
│                                     │
│ Network Interface 0:                │
│ ├─ Name: eth0                       │
│ ├─ Bridge: vmbr0 (défaut, c'est bon)│
│ ├─ IP: dhcp ← OK pour commencer    │
│ │  (Ou: 192.168.1.150/24)           │
│ ├─ Gateway: 192.168.1.1             │
│ └─ Firewall: ☐ (laisser décochée)   │
│                                     │
│ DNS                                 │
│ ├─ DNS: 8.8.8.8 (ou votre DNS)     │
│ └─ DNS domain: local (défaut ok)    │
└─────────────────────────────────────┘

[Next]
```

**Étape 2.8**: Options

```
┌─────────────────────────────────────┐
│ Confirm                             │
├─────────────────────────────────────┤
│ Vérifier les paramètres:            │
│ ✓ CT 100                            │
│ ✓ jarvis                            │
│ ✓ 4 cores, 8GB RAM                 │
│ ✓ 50GB disque                       │
│ ✓ Ubuntu 24.04                      │
│                                     │
│ [Create]                            │
└─────────────────────────────────────┘
```

### ✅ Conteneur créé!

Vous allez voir:
```
TaskViewer - Create Container
████████████ 100%
✓ Created container 100
```

---

## Étape 3: Démarrer le conteneur

**Trouver votre conteneur**:

```
À gauche:
Datacenter
└─ YOUR_NODE
    └─ 100 (jarvis) ← C'est celui-là!
```

**Démarrer**:
```
Click droit sur "100" ou cliquer le bouton [Start]
```

Vous devriez voir:
```
Status: running
```

---

## Étape 4: Entrer dans le conteneur

### Connexion directe (console web)

```
Cliquer sur "100" (jarvis)
└─ Tab "Console"
```

Vous voyez:
```
jarvis login: _
```

Se connecter:
```
Username: root
Password: (celui que vous avez défini)
```

### Ou SSH (depuis votre PC)

```bash
ssh root@192.168.1.150
# (remplacer l'IP par celle du conteneur)
```

---

## Étape 5: Installer JARVIS (automatique!)

Dans le conteneur, copier-coller cette commande:

```bash
# Mettre à jour
apt update && apt upgrade -y

# Cloner le projet
cd /root
git clone https://github.com/HarryBen23/Jarvis.git
cd Jarvis

# INSTALLATION AUTOMATIQUE (tout fera seul!)
sudo bash scripts/proxmox-install.sh
```

Le script va:
- ✅ Installer Docker
- ✅ Installer les dépendances
- ✅ Cloner JARVIS
- ✅ Créer la config
- ✅ Lancer les services
- ✅ Tester tout

Vous verrez à la fin:
```
✅ Installation terminée!
🌐 Interface Web: http://localhost:8000
```

---

## Étape 6: Éditer la configuration

```bash
# Éditer .env
nano /root/Jarvis/.env
```

Trouver et remplir:

```
OPENAI_API_KEY=sk-proj-VOTRE_CLE_ICI
HA_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.VOTRE_TOKEN_ICI
```

**Sauvegarder**: `Ctrl+O` → Entrée → `Ctrl+X`

**Redémarrer**:
```bash
docker-compose restart jarvis-api
```

---

## Étape 7: Accéder à JARVIS!

### Depuis le conteneur (local)

```
http://localhost:8000
```

### Depuis un autre PC (même réseau)

```
http://192.168.1.150:8000
```

Remplacer `192.168.1.150` par l'IP de votre conteneur.

**For check the IP**:
```bash
# Dans le conteneur
ip a
```

Chercher: `inet 192.168.1.XXX`

---

## Et maintenant?

### Tester que ça marche

```bash
# Dans le conteneur
python scripts/test-connection.py
```

Vous devriez voir:
```
✅ OpenAI OK
✅ Home Assistant OK
✅ Tous les tests réussis!
```

### Utiliser JARVIS

Ouvrir: http://192.168.1.150:8000

```
┌──────────────────────────────────┐
│ 🤖 JARVIS                        │
├──────────────────────────────────┤
│ [Allume la lumière]    [Envoyer]│
│                                  │
│ [🎤 Enregistrer]                │
│                                  │
│ 🤖 Réponse: Lumière allumée    │
└──────────────────────────────────┘
```

---

## 🛠️ Commandes utiles

### Voir les logs

```bash
cd /root/Jarvis
docker-compose logs -f jarvis-api
```

Appuyer `Ctrl+C` pour quitter.

### État des services

```bash
docker-compose ps
```

Vous voyez:
```
NAME          STATUS
jarvis-api    Up 5 minutes
home-assistant Up 10 minutes
```

### Redémarrer JARVIS

```bash
docker-compose restart
```

### Arrêter JARVIS

```bash
docker-compose down
```

### Relancer JARVIS

```bash
docker-compose up -d
```

---

## 🆘 Problèmes?

### "Can't connect to http://192.168.1.150:8000"

```bash
# Vérifier que les services tournent
docker-compose ps

# Attendre 30 secondes et réessayer
```

### "API Key not found"

```bash
# Vérifier que .env est bien rempli
cat .env | grep OPENAI_API_KEY

# Si vide, éditer
nano .env
```

### "Home Assistant connection failed"

```bash
# Vérifier que HA tourne
docker-compose ps

# Vérifier le token
cat .env | grep HA_TOKEN
```

### Autres problèmes

```bash
# Voir les erreurs détaillées
docker-compose logs | tail -50

# Lire le guide troubleshooting
cat docs/TROUBLESHOOTING.md
```

---

## 📊 Proxmox - Votre Proxmox

Vous pouvez voir tout depuis l'interface:

```
Datacenter
└─ YOUR_NODE
    └─ 100 (jarvis)
        ├─ Status: running
        ├─ CPU: 2% (utilisation actuelle)
        ├─ Memory: 1.2GB / 8GB
        ├─ Disk: 15GB / 50GB
        └─ Network: 10Mbps
```

---

## 💡 Tips

✅ Faire un **backup rapide** avant d'ajouter beaucoup d'appareils:
```bash
# Cliquer droit sur "100" → Backup
```

✅ **Allouer plus de CPU/RAM** au fur et à mesure:
```bash
# Cliquer sur "100" → Tab "Resources"
```

✅ **Accéder à Proxmox** depuis l'extérieur (VPN recommandé)

✅ **Monitorer les ressources** via le tableau de bord Proxmox

---

## 🎉 C'est fini!

Vous avez:
- ✅ Un conteneur JARVIS sur Proxmox
- ✅ Docker installé
- ✅ JARVIS fonctionnel
- ✅ Home Assistant configuré

**Prochains pas**:
- Lire: /root/Jarvis/GETTING_STARTED.md
- Ou: /root/Jarvis/TUTORIAL_COMPLET_FR.md
- Tester les commandes vocales
- Ajouter vos appareils Home Assistant

---

## 📚 Ressources

- [Proxmox Web](https://www.proxmox.com/)
- [Proxmox Docs](https://pve.proxmox.com/wiki/)
- [JARVIS GitHub](https://github.com/HarryBen23/Jarvis)

---

**Vous avez des questions?** 

Consultez les guides complets:
- [docs/PROXMOX_COMPLET.md](PROXMOX_COMPLET.md) - Guide avancé
- [docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Problèmes
- [docs/TUTORIAL_COMPLET_FR.md](TUTORIAL_COMPLET_FR.md) - Utiliser JARVIS

**Bon amusement avec JARVIS sur Proxmox! 🤖🐳**
