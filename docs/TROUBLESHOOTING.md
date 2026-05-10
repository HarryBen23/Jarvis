# 🔧 Guide de Dépannage Complet

Tout ce que vous devez faire si quelque chose ne marche pas.

---

## 🚀 Guide de démarrage rapide du dépannage

### Étape 1: Identifier le problème
```
Où est l'erreur? (Cochez une case)

[ ] Avant les clés API
[ ] 🌐 Interface web n'ouvre pas
[ ] 🎙️ Microphone ne fonctionne pas
[ ] 💬 JARVIS ne répond pas
[ ] 🏠 Appareils ne contrôlent pas
[ ] ⚠️ Message d'erreur spécifique
[ ] 📊 Performance lente/lag
[ ] 🐳 Problème Docker
```

### Étape 2: Utiliser la section correspondante ci-dessous
Parcourez le guide pour votre problème spécifique.

---

## ❌ PROBLÈME 1: Interface web n'ouvre pas

### Symptôme:
```
http://localhost:8000 → Erreur de connexion
Ou: "ERR_CONNECTION_REFUSED"
```

### Diagnostic:

**Étape 1**: Vérifier que le conteneur tourne
```bash
docker-compose ps
```

**Vous devriez voir**:
```
NAME                COMMAND    STATUS
jarvis-api          python...  Up 5 minutes
home-assistant      ...        Up 10 minutes
```

**Si pas "Up"**:
```bash
docker-compose logs jarvis-api | tail -20
```

### Solutions:

#### 🔧 Solution 1: Port occupé par autre chose

**Vérifier**:
```bash
lsof -i :8000
```

**Si quelque chose utilise le port**:
```bash
# Option A: Tuer le processus
kill -9 <PID>

# Option B: Changer le port dans .env
API_PORT=8001

# Relancer
docker-compose down
docker-compose up -d
```

#### 🔧 Solution 2: API n'a pas démarré

**Vérifier les erreurs**:
```bash
docker-compose logs jarvis-api | grep -i error
```

**Si erreur Python**:
```bash
# Relancer avec logs verbeux
docker-compose restart jarvis-api
docker-compose logs -f jarvis-api
```

#### 🔧 Solution 3: Firewall bloque le port

```bash
# Sur Ubuntu/Debian
sudo ufw allow 8000

# Sur CentOS/RHEL
sudo firewall-cmd --add-port=8000/tcp --permanent
sudo firewall-cmd --reload
```

#### 🔧 Solution 4: Attendre plus longtemps

```bash
# Les services peuvent prendre 30-60 secondes au premier démarrage
# Attendre 1-2 minutes puis réessayer
sleep 30
docker-compose up -d
sleep 30
# Puis tester http://localhost:8000
```

---

## ❌ PROBLÈME 2: "OPENAI_API_KEY not found"

### Symptôme:
```
Error: OPENAI_API_KEY not found
Ou: ValueError: OPENAI_API_KEY non configurée
```

### Diagnostic:

**Étape 1**: Vérifier que .env existe
```bash
ls -la /root/Jarvis/.env
```

**Si fichier manquant**:
```bash
cp .env.example .env
nano .env
```

**Étape 2**: Vérifier le contenu
```bash
cat .env | grep OPENAI_API_KEY
```

**Vous devriez voir**:
```
OPENAI_API_KEY=sk-proj-xyz123...
```

**Jamais voir**:
```
OPENAI_API_KEY=${OPENAI_API_KEY}   # ❌ Mauvais!
OPENAI_API_KEY=                    # ❌ Vide!
OPENAI_API_KEY=sk-proj            # ❌ Trop court!
```

### Solutions:

#### 🔧 Solution 1: Ajouter la clé

```bash
# Éditer .env
nano .env

# Trouver la ligne:
# OPENAI_API_KEY=...

# Remplacer par votre vraie clé:
# OPENAI_API_KEY=sk-proj-ABCxyz123...

# Sauvegarder: Ctrl+O, Entrée, Ctrl+X

# Vérifier
cat .env | grep OPENAI_API_KEY
```

#### 🔧 Solution 2: Clé incorrecte

**Votre clé doit ressembler à**:
```
sk-proj-aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890
```

**Vérifier que**:
- ✅ Commence par `sk-proj-`
- ✅ Fait 48+ caractères
- ✅ Contient lettres et chiffres
- ✅ Pas d'espaces avant/après

**Si clé mal formée**:
1. Aller sur https://platform.openai.com/api-keys
2. Supprimer l'ancienne clé
3. Créer une nouvelle et copier correctement

#### 🔧 Solution 3: Relancer Docker

```bash
# Après éditer .env:
docker-compose restart jarvis-api

# Vérifier les logs
docker-compose logs jarvis-api | tail -5
```

---

## ❌ PROBLÈME 3: "Home Assistant connection failed"

### Symptôme:
```
Error: Home Assistant connection failed
Connexion refusée
home-assistant: Résolution de noms impossible
```

### Diagnostic:

**Étape 1**: Vérifier que HA tourne
```bash
docker-compose ps | grep home-assistant
```

**Devrait être "Up"**:
```
home-assistant    ...    Up 10 minutes
```

**Étape 2**: Vérifier le token
```bash
cat .env | grep HA_TOKEN
```

**Devrait commencer par "eyJhbGc"**:
```
HA_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Étape 3**: Tester la connexion
```bash
# Tester que HA répond
curl http://localhost:8123

# Tester avec le token
curl -H "Authorization: Bearer eyJhbGc..." \
  http://localhost:8123/api/
```

### Solutions:

#### 🔧 Solution 1: Home Assistant ne tourne pas

```bash
# Redémarrer HA
docker-compose restart home-assistant

# Attendre 30 secondes
sleep 30

# Vérifier
docker-compose logs home-assistant | tail -20
```

#### 🔧 Solution 2: Token absent ou mal formé

```bash
# Le token doit commencer par eyJhbGci
# Et contenir beaucoup de caractères (300+)

# Si vide ou court:
nano .env

# Aller dans Home Assistant:
# Settings → Devices & Services → (bas) API Tokens
# Créer un nouveau token
# Copier exactement (sans espaces!)
```

#### 🔧 Solution 3: URL incorrecte

```bash
# Vérifier dans .env:
cat .env | grep HA_URL

# Devrait être:
# HA_URL=http://home-assistant:8123

# Si différent, éditer:
nano .env
```

#### 🔧 Solution 4: Home Assistant pas initialisé

```bash
# Initialiser HA si première fois
bash scripts/init-homeassistant.sh

# Puis redémarrer
docker-compose restart home-assistant
sleep 60
```

---

## ❌ PROBLÈME 4: Microphone ne fonctionne pas

### Symptôme:
```
No microphone found
Enregistrement ne démarre pas
Audio device not found
```

### Type A: Microphone navigateur (Web UI)

**Diagnostic**:
```
Avez-vous autorisé l'accès au microphone?
│
├─ Non (vous avez vu la popup "Refuse?")
│  └─ Cliquer sur 🔒 (cadenas) dans la barre d'adresse
│     └─ Microphone: Autoriser
│
├─ Oui
│  └─ Test avec Firefox/Chrome/Edge
│     └─ Parfois un navigateur marche mieux
│
└─ Pas de popup?
   └─ Vérifier que https n'est pas requis
      └─ Utiliser http://localhost:8000
```

**Solutions**:

```bash
# Test 1: Essayer un autre navigateur
# Chrome, Firefox, Edge - en rotation

# Test 2: Réinitialiser les permissions
# Chrome: Settings → Privacy → Microphone → Reinitialize

# Test 3: Redémarrer le navigateur
# Fermer complètement et rouvrir

# Test 4: Vérifier que le microphone physique marche
# Aller à: System Settings → Sound → Input
# Parler → la barre doit bouger
```

### Type B: Microphone Server (CLI ou direct)

**Diagnostic**:
```bash
# Lister les appareils audio
docker exec jarvis-cli arecord -l
```

**Vous devriez voir**:
```
**** List of CAPTURE Hardware Devices ****
card 0: ALSA [ALSA default]
  device 0: Dummy 1 [Dummy PCM]
card 1: USB [USB Audio Device]
  device 0: USB Audio [USB Audio Stream]  ← Votre microphone
```

**Si rien ou que "Dummy"**:
```bash
# Le microphone n'est pas détecté par le système
# Solutions:
# 1. Essayer un autre microphone USB
# 2. Redémarrer le serveur
# 3. Vérifier les permissions USB
```

**Solutions**:

#### 🔧 Solution 1: Configurer le device

```bash
# À partir de la liste, votre microphone est probablement:
# card 1, device 0 (le dernier)

# Configurer dans .env:
nano .env
# Ajouter ou modifier:
AUDIO_DEVICE_INDEX=1

# Relancer
docker-compose restart jarvis-cli

# Voir les logs
docker-compose logs -f jarvis-cli
```

#### 🔧 Solution 2: Tester le microphone directement

```bash
# Tester une enregistrement court
docker exec jarvis-cli arecord -f cd -d 3 /tmp/test.wav

# Vérifier que le fichier fut créé
docker exec jarvis-cli ls -l /tmp/test.wav

# Jouer le fichier (si disponible)
docker exec jarvis-cli aplay /tmp/test.wav
```

#### 🔧 Solution 3: Installer support audio

```bash
# Peut-être que les libs audio manquent
apt-get update
apt-get install -y \
  alsa-utils \
  pulseaudio \
  libsndfile1 \
  ffmpeg

# Redémarrer Docker
docker-compose restart jarvis-cli
```

#### 🔧 Solution 4: Permissions

```bash
# L'utilisateur docker a besoin d'accès audio
# Vérifier que /dev/snd existe:
ls -la /dev/snd

# Si permissions manquent:
sudo chmod 666 /dev/snd/*

# Redémarrer les conteneurs:
docker-compose restart jarvis-cli
```

---

## ❌ PROBLÈME 5: JARVIS ne répond pas

### Symptôme:
```
Taper "Bonjour JARVIS" → Rien
Ou: "Loading... loading... loading..."
Ou: La réponse prend 2+ minutes
```

### Diagnostic:

**Étape 1**: Vérifier l'API santé
```bash
curl http://localhost:8000/health
```

**Vous devriez voir**:
```json
{
  "status": "healthy",
  "home_assistant": "connected",
  "openai": "configured"
}
```

**Si `status": "unhealthy"`**:
```bash
docker-compose logs jarvis-api | tail -50
```

**Étape 2**: Vérifier les services

```bash
docker-compose ps
```

**Tous doivent être "Up"**:
```
jarvis-api          Up
home-assistant      Up
```

**Étape 3**: Vérifier l'utilisation ressources

```bash
docker stats --no-stream
```

**Si CPU 100% ou MEM full**:
```
Allouer plus de CPU/RAM
    OU
Redémarrer (réinitialiser)
```

### Solutions:

#### 🔧 Solution 1: API reboot

```bash
# Redémarrer juste l'API
docker-compose restart jarvis-api

# Attendre 10 secondes
sleep 10

# Tester
curl http://localhost:8000/health
```

#### 🔧 Solution 2: Erreur OpenAI API

```bash
# Vérifier les logs d'erreur
docker-compose logs jarvis-api | grep -i openai

# Possible causes:
# - API Key expiré
# - Quota d'utilisation dépassé
# - Service OpenAI inaccessible

# Vérifier:
# https://status.openai.com/

# Essayer:
# 1. Nouvelle clé API
# 2. Passer à un autre modèle (gpt-3.5-turbo)
```

#### 🔧 Solution 3: Réseau bloqué

```bash
# Tester la connexion Internet
docker exec jarvis-api curl https://api.openai.com/v1/models

# Si erreur = pas de connexion Internet
# Vérifier la configuration réseau du conteneur

# Redémarrer le réseau Docker
docker network prune
docker-compose down
docker-compose up -d
```

#### 🔧 Solution 4: Quota OpenAI dépassé

```bash
# Vérifier votre utilisation:
# https://platform.openai.com/account/usage

# Si quota dépassé:
# - Payer une facture outstanding
# - Ajouter une carte bancaire
# - Augmenter son compte
```

---

## ❌ PROBLÈME 6: Appareils ne contrôlent pas

### Symptôme:
```
"Allume la lumière" → JARVIS répond "OK!"
    Mais la lumière ne s'allume pas
```

### Diagnostic:

**Étape 1**: Appareil existe-t-il?

```bash
# Voir tous les appareils HA
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8123/api/states | grep light

# Vous devriez voir quelque chose comme:
# "entity_id": "light.salon"
```

**Si rien = appareil pas ajouté à HA**:
```bash
# Aller dans Home Assistant
# Settings → Devices & Services
# Ajouter votre appareil (ampoule Philips, etc.)
```

**Étape 2**: Service existe-t-il?

```bash
# Tester d'allumer la lumière depuis HA directement
# Settings → Developer Tools → Services
# Domain: light
# Service: turn_on
# Entity: light.salon
# Cliquer "Call Service"

# Si ça marche = le problème est dans JARVIS
# Si ça ne marche pas = problème Home Assistant
```

### Solutions:

#### 🔧 Solution 1: Ajouter l'appareil

```bash
# Aller dans Home Assistant Web UI:
# http://localhost:8123

# Settings → Devices & Services → + Create device

# Ou: Ajouter via l'intégration
# (Philips Hue, IKEA, etc.)

# Puis redémarrer JARVIS:
docker-compose restart jarvis-api
```

#### 🔧 Solution 2: Corriger l'entity_id

**Dans JARVIS, modifiez le mappage**:

Fichier: `src/api.py`

Chercher la section: `async def _execute_actions`

```python
# Avant (incorrect):
if "lumière" in command_lower and "on" in command:
    await ha_client.call_service("light", "turn_on", 
                                {"entity_id": "light.salon"})

# Après (remplacer par votre vraie entity_id):
if "lumière" in command_lower and "allume" in command:
    await ha_client.call_service("light", "turn_on",
                                {"entity_id": "light.votre_vraie_id"})
```

**Puis redémarrer**:
```bash
docker-compose restart jarvis-api
```

#### 🔧 Solution 3: Permissions Home Assistant

```bash
# Vérifier que le token a les droits
# Dans Home Assistant:
# Profil (coin bas) → API Tokens
# Vérifier que le token JARVIS existe et est actif

# Si besoin de plus de permissions:
# Supprimer le token
# Repasser par "Create Token" avec plus de droits
```

---

## ❌ PROBLÈME 7: Performance lente

### Symptôme:
```
Réponses prennent 5-10 secondes au lieu de 2-3
CPU à 100%
RAM pleine
```

### Diagnostic:

```bash
# Voir la consommation
docker stats --no-stream

# Devrait avoir < 5% CPU en inactivité
# < 500MB par service en mémoire
```

### Solutions:

#### 🔧 Solution 1: Allouer plus de ressources

**Redémarrer avec plus de RAM**:
```bash
# Dans docker-compose.yml, ajouter des limites:
services:
  jarvis-api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G

# Puis redémarrer
docker-compose down
docker-compose up -d
```

#### 🔧 Solution 2: Réduire la charge

```bash
# Trop de logs? Réduire le verbosité:
nano .env
LOG_LEVEL=WARNING  # Au lieu de INFO

# Redémarrer
docker-compose restart jarvis-api
```

#### 🔧 Solution 3: Optimiser OpenAI

```bash
# Utiliser un modèle plus rapide/pas cher:
src/api.py

# Avant:
model="gpt-4-turbo"

# Après:
model="gpt-3.5-turbo"  # Plus rapide et bon marché

# Puis relancer
docker-compose restart jarvis-api
```

#### 🔧 Solution 4: Nettoyer

```bash
# Supprimer les vieux logs/données
docker system prune

# Redémarrer
docker-compose down
docker-compose up -d
```

---

## ❌ PROBLÈME 8: Problèmes Docker

### Symptôme:
```
docker-compose: command not found
ERROR: Cannot connect to Docker daemon
permission denied
```

### Solutions:

#### 🔧 Solution 1: Docker pas installé

```bash
# Installer Docker
bash scripts/install-docker.sh

# Ou manuellement:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo bash get-docker.sh

# Ajouter à votre groupe:
sudo usermod -aG docker $USER
newgrp docker
```

#### 🔧 Solution 2: Permissions Docker

```bash
# Vous n'avez pas les permissions
sudo usermod -aG docker $USER

# Logout et login
exit
ssh root@serveur

# Tester
docker ps
```

#### 🔧 Solution 3: Docker daemon pas en cours

```bash
# Démarrer Docker
sudo systemctl start docker

# Ou si service:
sudo service docker start

# Vérifier
docker ps
```

#### 🔧 Solution 4: docker-compose pas installé

```bash
# Installer docker-compose v2
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Vérifier
docker-compose --version
```

---

## 🆘 Problème non listé?

### Récupérer les logs complets:

```bash
# Tous les logs
docker-compose logs > logs.txt

# Ou juste les erreurs
docker-compose logs | grep -i error > errors.txt

# Envoyer au support/GitHub issue
# En partageant les logs (sans clés API!)
```

### Faire un reset complet:

```bash
# Backup d'abord:
cp -r config/ config.backup

# Arrêter tout
docker-compose down -v

# Effacer les caches Python
rm -rf src/__pycache__ .pytest_cache

# Redémarrer du zéro
docker-compose up -d

# Tester
python scripts/test-connection.py
```

### Créer une issue GitHub:

```
Titre: Problème avec [description courte]

Contenu:
- Étapes pour reproduire
- Message d'erreur exact
- Logs pertinents (sans secrets!)
- Votre setup (Docker, Ubuntu, Proxmox, etc.)
```

---

## 📋 Checklist du troubleshooting

```
[ ] Avez-vous vérifié les logs?
    docker-compose logs | tail -50

[ ] Avez-vous redémarré?
    docker-compose restart

[ ] Avez-vous attendu 30+ secondes?
    (Les services prennent du temps au démarrage)

[ ] Avez-vous testé chaque service?
    python scripts/test-connection.py

[ ] Avez-vous .env bien rempli?
    cat .env | grep -E "OPENAI|HA_TOKEN"

[ ] Avez-vous la dernière version?
    git pull
    docker-compose pull

[ ] Avez-vous consulté la doc?
    readline README.md
    read TUTORIAL_COMPLET_FR.md
```

---

## 💡 Tips généraux

```
🔍 TOUJOURS commencer par:
   docker-compose ps       # État des services
   docker-compose logs -f  # Logs en temps réel

🔄 SOUVENT ça fixe les problèmes:
   docker-compose down
   docker-compose up -d
   # Attendre 30 secondes
   # Réessayer

⏰ LA PATIENCE EST CLÉE:
   Au démarrage: 30-60 secondes pour être prêt
   API call: 2-3 secondes normal
   Transcription: 1-3 secondes normal

🆘 DERNIER RECOURS:
   Reset complet:
   docker-compose down -v
   rm -rf config/home-assistant
   docker-compose up -d
   # Reconfigurer Home Assistant
```

---

**Vous avez toujours un problème?** 
- Relire ce guide (beaucoup de gens trouvent la solution ici!)
- Consulter README.md et TUTORIAL_COMPLET_FR.md
- Créer une issue GitHub avec les logs

Bonne chance! 🚀
