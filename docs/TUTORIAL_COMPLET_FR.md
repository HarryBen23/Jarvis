# 📚 Tutoriel Complet JARVIS de A à Z

## 🎯 Objectif final
Avoir un assistant JARVIS (style Iron Man) qui répond à vos commandes vocales/textuelles et contrôle votre domotique via une interface web.

---

## PARTIE 1: Comprendre JARVIS (5 min)

### 🤖 Qu'est-ce que JARVIS?

JARVIS = **Assistant IA vocal pour Home Assistant**

```
Vous parlez/écrivez
         ↓
    JARVIS écoute
         ↓
  Reconnaissance vocale (Whisper)
         ↓
    Traitement IA (ChatGPT)
         ↓
   Commandes exécutées (Home Assistant)
         ↓
    Réponse affichée/lue
```

### 📋 Composants:

| Composant | Rôle |
|-----------|------|
| **Whisper** | Convertit votre voix en texte |
| **ChatGPT** | Comprend vos demandes |
| **Home Assistant** | Contrôle les appareils |
| **FastAPI** | Interface web |

### 🌐 Deux façons de l'utiliser:

1. **Interface Web** (Navigateur PC/Tablette/Téléphone) ← RECOMMANDÉ
2. **Microphone local** (Branché au serveur)

---

## PARTIE 2: Obtenir les clés API (10 min)

### 🔑 Clé 1: OpenAI (pour Whisper + ChatGPT)

**Étape 1**: Aller sur https://platform.openai.com/api-keys

![](https://via.placeholder.com/800x400?text=OpenAI+Dashboard)

**Étape 2**: Cliquer sur **+ Create new secret key**

```
[Button: + Create new secret key]
```

**Étape 3**: Donner un nom (ex: "JARVIS")

```
Name: JARVIS
└─ OK
```

**Étape 4**: Copier la clé (exemple):
```
sk-proj-Xyz1234567890abcdefghijklmnopqrstuvwxyz
```

⚠️ **IMPORTANT**: Cette clé ne s'affichera qu'une fois! La copier dans un fichier texte.

---

### 🏠 Clé 2: Home Assistant Token

**Étape 1**: Ouvrir Home Assistant

```
http://votre-adresse:8123
```

**Étape 2**: Aller dans **Settings** (⚙️)

```
Écran d'accueil → ⚙️ (coin haut droit) → Settings
```

**Étape 3**: Aller dans **Devices & Services** (ou **Developer Tools**)

```
Settings → Devices & Services
                         OU
Settings → Developer Tools → API Tokens
```

**Étape 4**: Scroll vers le bas, trouver **Long-Lived Access Tokens**

```
[Section en bas de page]
□ Long-Lived Access Tokens
   [+ Create Token button]
```

**Étape 5**: Cliquer sur **+ Create Token**

```
Token name: JARVIS
```

**Étape 6**: Copier le token (exemple):
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI5YTQ4ZDlhZG...
```

⚠️ **Garder ces deux clés précieusement!**

---

## PARTIE 3: Installer JARVIS (15 min)

### Étape 1: Cloner le projet

**Sur votre serveur Proxmox** (ou conteneur LXC):

```bash
# Se connecter en SSH
ssh root@votre-serveur-proxmox

# Aller dans le répertoire
cd /root

# Cloner JARVIS
git clone https://github.com/HarryBen23/Jarvis.git

# Entrer dans le dossier
cd Jarvis
```

### Étape 2: Créer le fichier .env

```bash
# Copier l'exemple
cp .env.example .env

# Éditer avec nano
nano .env
```

**L'écran affiche** (environ):
```ini
OPENAI_API_KEY=${OPENAI_API_KEY}
HA_TOKEN=${HA_TOKEN}
HA_URL=http://home-assistant:8123
API_PORT=8000
API_HOST=0.0.0.0
WAKE_WORD=jarvis
LOG_LEVEL=INFO
```

### Étape 3: Remplir les clés

**Dans l'éditeur nano**:

1. Localisez `OPENAI_API_KEY=...`
2. Supprimez la partie après `=`
3. Collez votre clé OpenAI

**Avant:**
```ini
OPENAI_API_KEY=${OPENAI_API_KEY}
```

**Après:**
```ini
OPENAI_API_KEY=sk-proj-Xyz1234567890abcdefghijklmnopqrstuvwxyz
```

Faites la même chose pour `HA_TOKEN`:

```ini
HA_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI5YTQ4ZDlhZG...
```

### Étape 4: Sauvegarder

**Dans nano**:
```
Ctrl+O    (Save = Écrire le fichier)
Enter     (Confirmer le nom)
Ctrl+X    (Exit = Quitter)
```

**Vérifier que c'est bon**:
```bash
cat .env | head -5
```

Vous devriez voir:
```bash
OPENAI_API_KEY=sk-proj-...
HA_TOKEN=eyJ...
```

---

## PARTIE 4: Lancer JARVIS (5 min)

### Option A: Interface Web (RECOMMANDÉ) 🌐

**Commande unique**:
```bash
cd /root/Jarvis
bash scripts/start-web.sh
```

**Ce qui se passe**:
```
🚀 Démarrage de JARVIS avec Interface Web
======================================
📋 Initialisation Home Assistant...
🐳 Lancement des services Docker...
⏳ Attente du démarrage de l'API...
(Attendre 20-30 secondes)
✅ API prête!

======================================
🎉 JARVIS est prêt!

🌐 Ouvrir dans le navigateur:
   http://localhost:8000

📊 Voir les logs:
   docker-compose logs -f jarvis-api

⏹️  Arrêter:
   docker-compose down
```

Puis **ouvrir dans le navigateur**:
```
http://localhost:8000
        OU
http://<IP-DE-VOTRE-SERVEUR>:8000
```

### Option B: Microphone local (CLI) 🎤

```bash
cd /root/Jarvis
docker-compose up -d jarvis-cli
docker-compose logs -f jarvis-cli
```

---

## PARTIE 5: Premiers tests (10 min)

### Test 1: Vérifier que tout fonctionne

**Dans le terminal**:
```bash
cd /root/Jarvis
python scripts/test-connection.py
```

**Vous devriez voir**:
```
==================================================
🤖 Test de connexion JARVIS
==================================================

🧪 Test OpenAI...
✅ OpenAI OK: Bonjour à vous!

🧪 Test Home Assistant...
✅ Home Assistant OK: Connecté

==================================================
✅ Tous les tests réussis! JARVIS est prêt.
==================================================
```

Si vous voyez ✅ partout, c'est bon! 🎉

### Test 2: Utiliser l'interface web

**Ouvrir** http://localhost:8000 dans le navigateur

**Vous voyez**:
```
┌──────────────────────────────┐
│         🤖 JARVIS            │
│  Assistant IA pour Home      │
│        Assistant             │
│                              │
│ API: ● Connectée             │
│ HA:  ● Connected             │
│ AI:  ● Configured            │
│                              │
│ ┌─────────────────────────┐  │
│ │ Dites votre commande... │  │ ← Tapez ici
│ └─────────────────────────┘  │
│          [📤 Envoyer]        │
│                              │
│ 🎙️ [Enregistrer] [📋 Apps]  │
│                              │
│ ┌─────────────────────────┐  │
│ │ En attente...           │  │ ← Réponse ici
│ └─────────────────────────┘  │
└──────────────────────────────┘
```

---

## PARTIE 6: Utiliser JARVIS (20 min)

### 🎙️ Méthode 1: Voix (via navigateur)

**Étape 1**: Cliquer sur le bouton **🎤 Enregistrer**

```
[🎤 Enregistrer] ← Cliquer ici
```

**Étape 2**: Vous devriez entendre:
```
🎙️ Enregistrement en cours...
(avec animation d'ondes sonores)
```

**Étape 3**: Parler clairement en français
```
"Jarvis, allume la lumière du salon"
          OU
"Jarvis, quelle est la température?"
```

**Étape 4**: Après 5 secondes, l'enregistrement s'arrête automatiquement

**Étape 5**: JARVIS affiche:
```
📝 "Jarvis, allume la lumière du salon"

🤖 Lumière du salon allumée!
```

### 📝 Méthode 2: Texte (plus simple)

**Étape 1**: Cliquer dans le champ texte
```
[Dites votre commande...]
```

**Étape 2**: Taper votre commande
```
Allume les lumières
```

**Étape 3**: Appuyer sur **Entrée** ou cliquer **📤 Envoyer**

**Étape 4**: Voir la réponse
```
🤖 Lumières allumées!
```

### 📊 Méthode 3: Voir les appareils

**En bas de la page**, vous voyez:
```
🏠 Appareils domotiques

[Lumière salon]  [Lumière chambre]
   État: on          État: off

[Thermostat]     [Serrure entrée]
  État: 22°C         État: verrouillée
```

---

## PARTIE 7: Exemples de commandes

### 🏠 Contrôle d'éclairage

```
"Allume la lumière"
"Éteint toutes les lumières"
"Baisse la luminosité"
"Augmente la luminosité du salon"
"Lumière à 50%"
```

### 🌡️ Température

```
"Quelle est la température?"
"Règle le thermostat à 22 degrés"
"Augmente le chauffage"
"Baisse la climatisation"
```

### 🔒 Sécurité

```
"Verrouille la porte"
"Déverrouille l'entrée"
"Quel est le statut de la serrure?"
"Ferme les volets"
```

### 📊 Informations

```
"Quel est le statut?"
"Dis-moi l'état de la maison"
"Combien de portes sont ouvertes?"
```

### ⚙️ Automations

```
"Lance le scénario vacation"
"Active le mode nuit"
"Prépare la maison"
```

---

## PARTIE 8: Troubleshooting (Problèmes)

### ❌ Problème 1: "API not responding"

**Cause**: L'API n'a pas démarré

**Solution**:
```bash
# Vérifier l'état
docker-compose ps

# Vous devriez voir:
NAME              STATUS
jarvis-api        Up 2 minutes
home-assistant    Up 5 minutes

# Si pas "Up", relancer:
docker-compose down
docker-compose up -d
docker-compose logs -f jarvis-api
```

### ❌ Problème 2: "OPENAI_API_KEY not found"

**Cause**: La clé OpenAI n'est pas bien configurée

**Solution**:
```bash
# Vérifier le .env
cat .env | grep OPENAI_API_KEY

# Devrait afficher (sans ${}):
OPENAI_API_KEY=sk-proj-xyz...

# Si ce n'est pas bon:
nano .env
# Éditer et relancer:
docker-compose restart jarvis-api
```

### ❌ Problème 3: "Home Assistant connection failed"

**Cause**: Home Assistant n'est pas accessible

**Solution**:
```bash
# Vérifier que HA tourne
docker-compose ps | grep home-assistant

# Vérifier la connexion
curl http://home-assistant:8123

# Vérifier le token
curl -H "Authorization: Bearer $HA_TOKEN" \
  http://home-assistant:8123/api/

# Si erreur, relancer:
docker-compose restart home-assistant
```

### ❌ Problème 4: "Microphone not found"

**Cause**: Pas de microphone détecté (pour le CLI)

**Solution**:
```bash
# Lister les appareils audio
docker exec jarvis-cli arecord -l

# Vous devriez voir:
**** List of CAPTURE Hardware Devices ****
card 0: ALSA [ALSA default]
  device 0: Dummy 1 [Dummy PCM]
card 1: USB [USB Audio Device]
  device 0: USB Audio [USB Audio Stream]

# Configurer dans .env:
AUDIO_DEVICE_INDEX=1

# Redémarrer:
docker-compose restart jarvis-cli
```

### ❌ Problème 5: "Port 8000 already in use"

**Cause**: Un autre service utilise le port 8000

**Solution**:
```bash
# Voir qui utilise le port
lsof -i :8000

# Changer le port dans .env:
API_PORT=8001

# Relancer:
docker-compose down
docker-compose up -d

# Puis accéder à:
http://localhost:8001
```

---

## PARTIE 9: Personnalisation

### 🔧 Changer le mot de réveil

**Fichier**: `/root/Jarvis/config/jarvis.json`

**Avant**:
```json
{
  "wake_word": "jarvis"
}
```

**Après** (exemple avec "Friday"):
```json
{
  "wake_word": "friday"
}
```

Puis redémarrer:
```bash
docker-compose restart jarvis-api
```

### 🌍 Changer la langue

**Fichier**: `src/api.py` et `src/jarvis.py`

Chercher les sections avec `language="fr"` et remplacer par:
```python
language="en"    # Anglais
language="es"    # Espagnol
language="de"    # Allemand
```

### 🎨 Personaliser l'interface web

**Fichier**: `src/api.py` (section `<style>`)

Vous pouvez changer:
- Les couleurs (ex: `#667eea` → `#FF0000`)
- Les polices
- La mise en page

---

## PARTIE 10: Aller plus loin

### 🚀 Ajouter des automations Home Assistant

**Créer une automation** qui utilise JARVIS:

**Exemple**: "Quand JARVIS dit 'bon matin', alluman les lumières"

### 📱 Accéder depuis l'extérieur (Internet)

**Solution 1: Reverse Proxy Nginx**
```bash
# Installer Nginx
apt install -y nginx

# Configurer (voir docs/PROXMOX_DEPLOYMENT.md)
```

**Solution 2: VPN**
- Installer WireGuard ou OpenVPN
- Se connecter au VPN
- Accéder à http://192.168.X.X:8000

**Solution 3: Tunnel Ngrok**
```bash
ngrok http 8000
# Puis utiliser l'URL Ngrok
```

### 🎙️ Ajouter un Raspberry Pi

**Idée**: Mettre un Raspberry Pi avec microphone dans votre salon

**Voir**: `docs/PROXMOX_DEPLOYMENT.md`

---

## PARTIE 11: Maintenance

### 📊 Voir les logs

```bash
# Logs en temps réel
docker-compose logs -f jarvis-api

# Logs détaillés
docker-compose logs --tail 100 jarvis-api

# Logs de Home Assistant
docker-compose logs home-assistant
```

### 🔄 Mettre à jour JARVIS

```bash
cd /root/Jarvis

# Arrêter
docker-compose down

# Récupérer les mises à jour
git pull

# Redémarrer
docker-compose up -d
```

### 💾 Sauvegarder la configuration

```bash
# Backup
tar -czf jarvis-backup.tar.gz config/ .env

# Restaurer (si besoin)
tar -xzf jarvis-backup.tar.gz
```

### 🗑️ Arrêter JARVIS

```bash
# Arrêter sans supprimer les données
docker-compose stop

# Arrêter et supprimer les conteneurs
docker-compose down

# Arréter et tout supprimer (y compris les données)
docker-compose down -v
```

---

## PARTIE 12: Checklist finale ✅

Avant de dire que c'est prêt:

- [ ] **Clés API obtenues** (OpenAI + HA Token)
- [ ] **Fichier .env rempli** avec les clés
- [ ] **Docker installé** (`docker --version`)
- [ ] **JARVIS cloné** dans `/root/Jarvis`
- [ ] **Tests réussis** (`python scripts/test-connection.py`)
- [ ] **Interface web accessible** (http://localhost:8000)
- [ ] **Commande texte testée** ("Bonjour JARVIS")
- [ ] **Commande vocale testée** (Microphone ou navigateur)
- [ ] **Appareil domotique contrôlé** (Lumière, thermostat, etc.)

---

## 📚 Ressources

- [README.md](../README.md) - Documentation générale
- [docs/WEB_INTERFACE.md](../docs/WEB_INTERFACE.md) - API détaillée
- [docs/PROXMOX_DEPLOYMENT.md](../docs/PROXMOX_DEPLOYMENT.md) - Setup Proxmox
- [Home Assistant Docs](https://www.home-assistant.io/docs/) - Documentation HA
- [OpenAI API Docs](https://platform.openai.com/docs/api-reference) - API OpenAI

---

## 🎯 Résumé

```
1. Obtenir 2 clés API (5 min)
   ↓
2. Installer JARVIS (2 min)
   ↓
3. Lancer avec: bash scripts/start-web.sh (1 min)
   ↓
4. Ouvrir: http://localhost:8000 (1 min)
   ↓
5. Tester les commandes ✅
   ↓
6. JARVIS prêt à l'emploi! 🎉
```

**Total: ~15 minutes de setup**

---

## 💬 Besoin d'aide?

Si quelque chose ne marche pas:

1. 📖 Consulter ce tutoriel
2. 🔍 Vérifier les logs: `docker-compose logs`
3. 🧪 Lancer le test: `python scripts/test-connection.py`
4. 📞 Consulter le README.md ou docs/

---

**Bon amusement avec JARVIS! 🤖** 

Avez-vous des questions sur une étape? 😊
