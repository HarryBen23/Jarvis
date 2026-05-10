# 🤖 JARVIS - Assistant IA Home Assistant

Système de contrôle domotique style Iron Man avec reconnaissance vocale et IA.

## 🎯 Fonctionnalités

- **Reconnaissance vocale** : Whisper (OpenAI) pour transcrire votre voix en français
- **IA conversationnelle** : ChatGPT pour comprendre vos demandes
- **Contrôle domotique** : Intégration complète avec Home Assistant
- **🌐 Interface Web** : Contrôle depuis le navigateur (PC/Tablette/Téléphone)
- **🎙️ Mode CLI** : Écoute microphone en continu
- **Docker Ready** : Déploiement facile sur Proxmox
- **Mode continu** : Écoute et exécute les commandes en boucle

## 🚀 Démarrage ultra-rapide

### 1️⃣ Interface Web (Recommandé - 2 min)
```bash
git clone https://github.com/HarryBen23/Jarvis.git
cd Jarvis
cp .env.example .env
nano .env  # Ajouter vos clés

bash scripts/start-web.sh
# Puis ouvrir: http://localhost:8000
```

### 2️⃣ Mode CLI (Microphone local)
```bash
docker-compose up -d jarvis-cli
docker-compose logs -f jarvis-cli
```

## 📋 Prérequis

- **Proxmox** avec ressources (vous avez 20 cœurs + 64GB ✅)
- **Clés API** :
  - OpenAI : https://platform.openai.com/api-keys
  - Home Assistant token (créer dans Home Assistant)
- **Docker & Docker Compose**
- **Navigateur moderne** (pour l'interface web)

## 🌐 Interface Web

```
http://localhost:8000
```

### Fonctionnalités de la Web UI :
- ✅ Envoi de commandes texte
- ✅ Enregistrement vocal depuis le navigateur
- ✅ Transcription en temps réel
- ✅ Tableau de bord des appareils domotiques
- ✅ Responsive (PC, tablette, téléphone)
- ✅ WebSocket pour communication temps réel

**Documentation détaillée**: [Interface Web](docs/WEB_INTERFACE.md)

## 🐳 Déploiement sur Proxmox

### Setup complet Proxmox:
1. Créer un conteneur LXC Ubuntu 24.04
2. Installer Docker
3. Cloner JARVIS
4. Configurer `.env`
5. Lancer `docker-compose up -d`

**Guide complet**: [Proxmox Deployment](docs/PROXMOX_DEPLOYMENT.md)

## 🔑 Obtenir les clés API

### OpenAI (Whisper + ChatGPT)
1. Aller sur https://platform.openai.com/api-keys
2. Create new secret key
3. Copier dans `.env` → `OPENAI_API_KEY`

### Home Assistant Token
1. Home Assistant → Settings → Devices & Services
2. API Tokens (bas de page) → Create Token
3. Copier dans `.env` → `HA_TOKEN`

## 📂 Structure du projet

```
Jarvis/
├── src/
│   ├── jarvis.py           # Code principal (CLI)
│   └── api.py              # API FastAPI (Web UI)
├── config/
│   ├── jarvis.json         # Configuration
│   └── home-assistant/     # Config HA
├── docker/
│   ├── Dockerfile          # Pour le CLI
│   └── Dockerfile.api      # Pour l'API Web
├── scripts/
│   ├── start-web.sh        # Lancer l'interface web
│   ├── setup.sh            # Installation locale
│   ├── test-connection.py  # Tests
│   └── init-homeassistant.sh
├── docs/
│   ├── WEB_INTERFACE.md    # Doc interface web
│   ├── PROXMOX_DEPLOYMENT.md # Guide Proxmox
│   └── ARCHITECTURE.md     # (À venir)
├── docker-compose.yml      # Services
├── requirements.txt        # Dépendances
├── Makefile                # Commandes raccourcies
└── QUICK_START.md         # Démarrage rapide
```

## 📝 Exemples de commandes

Une fois JARVIS en écoute :

```
"Jarvis, allume la lumière du salon"
"Jarvis, quelle est la température?"
"Jarvis, quel est le statut de la serrure?"
"Jarvis, baisse les volets"
```

## 🧪 Tests

```bash
# Tester les connexions
python scripts/test-connection.py

# Tester l'API web
curl http://localhost:8000/health

# Tester le microphone
docker exec jarvis-cli arecord -l

# Logs en temps réel
docker-compose logs -f jarvis-api
```

## 🔧 Configuration avancée

### Modifier le wake word
```json
{
  "wake_word": "jarvis"  // À modifier dans config/jarvis.json
}
```

### Utiliser un autre microphone
```bash
# Lister les microphones
docker exec jarvis-cli arecord -l

# Configurer dans .env
AUDIO_DEVICE_INDEX=2
```

### Changer le port web
```bash
# Dans .env
API_PORT=8001
```

## 🛠️ Troubleshooting

### "OPENAI_API_KEY not found"
```bash
# Vérifier .env
cat .env | grep OPENAI_API_KEY

# Relancer
docker-compose restart jarvis-api
```

### "No microphone detected"
```bash
# Installer dépendances audio
apt-get install -y libasound2 libsndfile1 ffmpeg

# Redémarrer Docker
docker-compose down && docker-compose up -d
```

### "Home Assistant connection failed"
```bash
# Vérifier que HA est accessible
curl http://home-assistant:8123

# Vérifier le token
curl -H "Authorization: Bearer YOUR_TOKEN" http://home-assistant:8123/api/
```

### "Port déjà utilisé"
```bash
# Voir qui utilise le port
lsof -i :8000

# Ou changer dans .env
API_PORT=8001
```

## 📊 Performance

Avec **20 cœurs + 64GB RAM** :
- ✅ Temps de réponse < 2s
- ✅ Reconnaissance vocale très précise
- ✅ Plusieurs instances simultanées
- ✅ Processing IA en parallèle
- ✅ Support des utilisateurs multiples (web)

## 📋 Commandes utiles

```bash
# Lancer les services
docker-compose up -d

# Arrêter
docker-compose down

# Voir les logs
docker-compose logs -f

# Redémarrer un service
docker-compose restart jarvis-api

# Rentrer dans un conteneur
docker-compose exec jarvis-api bash

# Voir l'utilisation CPU/RAM
docker stats
```

## 🔮 Améliorations futures

- [ ] Reconnaissance de wake word local (Porcupine)
- [ ] Synthèse vocale (TTS) pour les réponses
- [ ] Intégration caméras (vision)
- [ ] Scénarios complexes
- [ ] Web UI avancée avec historique
- [ ] Support multilingue
- [ ] Client Raspberry Pi dédié

## 📚 Documentation Complète

### 🎯 Par où commencer?

**Ne sais pas quoi lire?** → [docs/INDEX.md](docs/INDEX.md) - Choisissez votre chemin!

### 📖 Guides principaux

| Guide | Durée | Contenu |
|-------|-------|---------|
| **[QUICK_START.md](QUICK_START.md)** | 5 min | Lancer en 2 commandes ⚡ |
| **[docs/GUIDE_VISUEL.md](docs/GUIDE_VISUEL.md)** | 20 min | Schémas et diagrammes 📊 |
| **[docs/TUTORIAL_COMPLET_FR.md](docs/TUTORIAL_COMPLET_FR.md)** | 1-2h | Guide A-Z complète en français 🇫🇷 |
| **[docs/WEB_INTERFACE.md](docs/WEB_INTERFACE.md)** | 30 min | Tous les endpoints API 🌐 |
| **[docs/PROXMOX_DEPLOYMENT.md](docs/PROXMOX_DEPLOYMENT.md)** | 45 min | Installation sur serveur 🐳 |
| **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** | Variable | Guide de dépannage 🔧 |

### 📍 Index complète
→ [docs/INDEX.md](docs/INDEX.md) - Tous les documents listés

## 📊 Logs

```bash
# Suivi en temps réel
docker-compose logs -f jarvis-api

# Audit des commandes
tail -f logs/jarvis.log

# Voir tout
docker-compose logs
```

## 🤝 Support

Pour les problèmes :
1. Consulter [QUICK START](QUICK_START.md)
2. Vérifier les logs : `docker-compose logs`
3. Lancer le test : `python scripts/test-connection.py`
4. Consulter la documentation complète

## 💡 Conseils

- ✅ Utiliser l'interface web pour une meilleure expérience
- ✅ Configurer correctement Home Assistant pour de meilleurs résultats
- ✅ Garder les clés API sauvegardes en lieu sûr
- ✅ Tester les connexions régulièrement

---

**Créé par** : HarryBen23  
**Stack** : OpenAI Whisper + ChatGPT + Home Assistant + FastAPI + Docker  
**Inspiré par** : JARVIS (Iron Man) 🎬  
**License** : MIT