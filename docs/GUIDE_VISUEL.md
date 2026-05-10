# 🎬 Guide de Démarrage Visuel

Ce guide utilise des diagrammes pour bien comprendre JARVIS.

---

## 1️⃣ L'architecture globale

```
          ┌─────────────────────────────────────┐
          │     VOUS (Utilisateur)              │
          │  💻 PC / 📱 Téléphone / 🎤 Voix    │
          └────────────┬────────────────────────┘
                       │
                       ↓
          ┌─────────────────────────────────────┐
          │  🌐 Interface Web (Navigateur)      │
          │          Port 8000                   │
          │  http://localhost:8000               │
          └────────────┬────────────────────────┘
                       │
                       ↓
          ┌─────────────────────────────────────┐
          │   📡 API FastAPI (Serveur)          │
          │   - Reçoit les commandes            │
          │   - Transcription vocale            │
          │   - Traitement IA                   │
          └────────────┬────────────────────────┘
                       │
              ┌────────┼────────┐
              ↓        ↓        ↓
          ╔═════╗ ╔═════╗ ╔═════════╗
          ║ 🎤  ║ ║ 🤖  ║ ║ 🏠      ║
          ║WhisℓE║ ║Chat║ ║HomeAsst ║
          ║Speech║ ║GPT ║ ║         ║
          ╚═════╝ ╚═════╝ ╚═════════╝
           OpenAI  OpenAI   (Votre HA)
                   
                       ↓
          
          ┌─────────────────────────────────────┐
          │   💡 Appareils domotiques           │
          │  - Lumières                         │
          │  - Climatisation                    │
          │  - Serrures                         │
          │  - Capteurs                         │
          └─────────────────────────────────────┘
```

---

## 2️⃣ Flux de communication (Exemple)

```
VOUS:  "Jarvis, allume la lumière du salon"

   │
   ├─ Interface Web reçoit le texte/audio
   │
   ├─ API FastAPI traite la demande
   │
   ├─ Whisper transcrit (si audio):
   │  "Jarvis, allume la lumière du salon"
   │
   ├─ ChatGPT comprend et crée la réponse:
   │  Intention: "Allumer une lumière"
   │  Pièce: "Salon"
   │
   ├─ Home Assistant exécute:
   │  Service: light.turn_on
   │  Entity: light.salon
   │
   ├─ Appareil domotique répond:
   │  Lumière du salon: ON ✅
   │
   └─ JARVIS répond:
      "Lumière du salon allumée!"
```

---

## 3️⃣ Les 4 étapes du setup

```
ÉTAPE 1: CLÉS API (10 min)
┌─────────────────────────────────────┐
│ 1. OpenAI: sk-proj-xyz...          │
│ 2. Home Assistant: eyJhbGc...      │
│ → Fichier .env rempli ✅            │
└─────────────────────────────────────┘
         │
         ↓
ÉTAPE 2: INSTALLATION (5 min)
┌─────────────────────────────────────┐
│ git clone JARVIS                    │
│ cp .env.example .env                │
│ nano .env (ajouter les clés)        │
│ → Fichier .env configuré ✅         │
└─────────────────────────────────────┘
         │
         ↓
ÉTAPE 3: LANCEMENT (2 min)
┌─────────────────────────────────────┐
│ bash scripts/start-web.sh          │
│ docker-compose up -d                │
│ → Services en cours d'exécution ✅  │
└─────────────────────────────────────┘
         │
         ↓
ÉTAPE 4: UTILISATION (∞)
┌─────────────────────────────────────┐
│ http://localhost:8000               │
│ Parler à JARVIS                     │
│ → JARVIS répond et agit ✅          │
└─────────────────────────────────────┘
```

---

## 4️⃣ Les 3 façons de parler à JARVIS

### Option A: Interface Web (Navigateur) 🌐

```
┌────────────────────────────────────┐
│ 🤖 JARVIS                          │
├────────────────────────────────────┤
│                                    │
│ ┌──────────────────────────────┐  │
│ │ Dites votre commande...      │  │
│ └──────────────────────────────┘  │
│                                    │
│   [📤 Envoyer]                    │
│                                    │
│   [🎤 Enregistrer] [📋 Appareils]│
│                                    │
│ ┌──────────────────────────────┐  │
│ │ Réponse...                   │  │
│ └──────────────────────────────┘  │
└────────────────────────────────────┘

Avantages: ✅ Pas de matériel
           ✅ Fonctionne partout
           ✅ Voix + texte
```

### Option B: Microphone USB 🎤

```
  [🎤 Microphone USB]
         │
         └──> Brancher au serveur
                     │
                     ↓
         JARVIS écoute en continu
         (Mode CLI)
         
Avantages: ✅ Toujours "à l'écoute"
           ✅ Plus immersif
    Inconvénients: ❌ Microphone physique nécessaire
```

### Option C: Raspberry Pi (Futur) 🍓

```
  [Microphone] → [RPi] → [Réseau] → [Serveur JARVIS]
                                           │
                                     [Home Assistant]
                                           │
                                    [Appareils]
```

---

## 5️⃣ Hiérarchie des fichiers

```
/root/Jarvis/
│
├── 📖 Documentation
│   ├── README.md                    ← Guide général
│   ├── QUICK_START.md              ← Démarrage rapide
│   └── docs/
│       ├── TUTORIAL_COMPLET_FR.md  ← CE FICHIER
│       ├── WEB_INTERFACE.md        ← API détaillée
│       └── PROXMOX_DEPLOYMENT.md   ← Setup serveur
│
├── 🔧 Configuration
│   ├── .env                        ← Vos clés API (SECRET!)
│   ├── .env.example                ← Template
│   ├── docker-compose.yml          ← Services Docker
│   └── config/
│       ├── jarvis.json            ← Config JARVIS
│       └── home-assistant/        ← Config HA
│
├── 💻 Code
│   ├── src/
│   │   ├── jarvis.py              ← Système principal (600 lignes)
│   │   └── api.py                 ← API Web (550 lignes)
│   │
│   └── docker/
│       ├── Dockerfile             ← Pour CLI
│       └── Dockerfile.api         ← Pour API
│
├── ⚙️  Utilitaires
│   ├── requirements.txt            ← Dépendances Python
│   ├── Makefile                   ← Commandes raccourcies
│   └── scripts/
│       ├── start-web.sh           ← Lancer Web UI ⭐
│       ├── setup.sh               ← Installation locale
│       ├── test-connection.py     ← Tests
│       ├── jarvis.sh              ← Menu de contrôle
│       └── + 4 autres scripts

Total: ~25 fichiers, 2500+ lignes de code
```

---

## 6️⃣ Cycle de vie d'une commande

```
                    Vous parlez
                         │
                         ↓
    ┌────────────────────────────────────┐
    │ 1. CAPTURE                         │
    │ • Son capturé (5 secondes)         │
    │ • Stocké temporairement            │
    └─────────────────┬──────────────────┘
                      ↓
    ┌────────────────────────────────────┐
    │ 2. TRANSCRIPTION (Whisper)         │
    │ • Envoyé à OpenAI                  │
    │ • Convertir audio → texte          │
    │ • Résultat: "Allume la lumière"   │
    └─────────────────┬──────────────────┘
                      ↓
    ┌────────────────────────────────────┐
    │ 3. COMPRÉHENSION (ChatGPT)         │
    │ • Analyser le texte                │
    │ • Comprendre l'intention           │
    │ • Préparer la réponse              │
    └─────────────────┬──────────────────┘
                      ↓
    ┌────────────────────────────────────┐
    │ 4. EXÉCUTION (Home Assistant)      │
    │ • Appeler le service               │
    │ • Contrôler l'appareil             │
    │ • Confirmer l'action               │
    └─────────────────┬──────────────────┘
                      ↓
    ┌────────────────────────────────────┐
    │ 5. RÉPONSE                         │
    │ • Afficher le résultat             │
    │ • "Lumière allumée!"              │
    └────────────────────────────────────┘

    ⏱️  Temps total: 2-3 secondes
```

---

## 7️⃣ Points de vérification

```
EST-CE QUE ÇA MARCHE?
  │
  ├─ Étape 1: Tests réussis?
  │  $ python scripts/test-connection.py
  │  └─ ✅ OpenAI + ✅ Home Assistant
  │
  ├─ Étape 2: Interface web accessible?
  │  $ curl http://localhost:8000/health
  │  └─ ✅ {"status": "healthy"}
  │
  ├─ Étape 3: Commande texte fonctionne?
  │  $ Taper "Bonjour JARVIS"
  │  └─ ✅ Réponse reçue
  │
  ├─ Étape 4: Commande vocale fonctionne?
  │  $ Cliquer sur enregistrer et parler
  │  └─ ✅ Texte transcrit
  │
  └─ Étape 5: Appareil contrôlé?
     $ "Allume la lumière du salon"
     └─ ✅ Lumière allumée
```

---

## 8️⃣ Raccourcis clavier/souris

```
Interface Web:

[Entrer]           → Envoyer le texte
[Escape]           → Effacer le champ
[🎤]               → Démarrer/arrêter enregistrement
[📋]               → Voir les appareils
[Actualiser]       → Rafraîchir l'état

Commandes CLI:

docker-compose up -d      → Démarrer tous les services
docker-compose down       → Arrêter tous les services  
docker-compose logs -f    → Voir les logs en temps réel
docker-compose ps         → Voir l'état des services
docker stats              → Voir CPU/RAM
```

---

## 9️⃣ Schéma des ports

```
Votre PC/Tablette
        │
        ├─── HTTP ──→ :8000 (Interface Web)
        │              ↓
        │         jarvis-api
        │
        ├─────────────→ :8123 (Home Assistant)
        │              ↓
        │         home-assistant
        │
        └─────────────→ :5432 (Optionnel - Database)
                     ↓
                 PostgreSQL (si utilisé)

Commandes utiles:
lsof -i :8000          # Voir qui utilise le port 8000
netstat -tlnp | grep 8000
```

---

## 🔟 Arbre de décision (Que faire?)

```
                    PROBLÈME?
                        │
             ┌──────────┼──────────┐
             │                    │
        API ne         Pas de      Home-Assistant
        démarre        connexion    ne répond
             │              │          │
             ↓              ↓          ↓
    Logs:              Vérifier    Token HA
    docker logs     OPENAI_API_KEY    │
             │              │        nano .env
             ↓              ↓          │
    Relancer:         Ajouter        Vérifier HA
    docker-compose   dans .env       running
    restart          docker restart  docker-compose
                                    restart home-assistant
```

---

## 11️⃣ Checklist quotidienne

### ✅ Avant d'utiliser JARVIS:

```
□ JARVIS en cours d'exécution?
  $ docker-compose ps
  
□ Peut accéder à l'interface web?
  $ curl http://localhost:8000/health
  
□ Home Assistant connecté?
  $ Vérifier que status "connected"
  
□ Aucune erreur dans les logs?
  $ docker-compose logs | grep ERROR
```

### 📊 Monitoring

```
Voir la consommation:
$ docker stats jarvis-api home-assistant

Devrait voir:
CPU:     < 5% (par défaut)
MEM:     < 500MB (par service)
NET:     ~ 100KB/s (lectures)
```

---

## 12️⃣ Roadmap (Prochaines améliorations)

```
MAINTENANT ✅
├─ Reconnaissance vocale via navigateur
├─ Commandes texte
├─ Contrôle Home Assistant
└─ Interface web moderne

BIENTÔT 🚧
├─ Synthèse vocale (JARVIS qui parle)
├─ Wake word local (pas d'API)
├─ Historique des commandes
└─ Mode multilingue

FUTUR 🔮
├─ Vision (caméras)
├─ Client Raspberry Pi
├─ Automations avancées
└─ Intégration Siri/Google Home
```

---

## ❓ FAQ Visuelle

### Q: Par où commencer?
```
Débutant total?
├─ Lire ce guide
├─ Récupérer les clés API
├─ Lancer bash scripts/start-web.sh
└─ Ouvrir http://localhost:8000
```

### Q: Ça démarre mais l'interface ne charge pas?
```
1. Vérifier que jarvis-api est "Up"
   $ docker-compose ps
   
2. Vérifier les erreurs
   $ docker-compose logs jarvis-api | tail -20
   
3. Redémarrer
   $ docker-compose restart jarvis-api
```

### Q: La voix ne fonctionne pas?
```
Sur navigateur:
├─ Autoriser l'accès au microphone (🎙️ + ✅)
├─ Tester avec un autre navigateur
├─ Vérifier que Whisper API fonctionne

Sur CLI:
├─ Vérifier le microphone USB
├─ $ docker exec jarvis-cli arecord -l
├─ Configurer AUDIO_DEVICE_INDEX dans .env
```

### Q: Comment accéder depuis l'extérieur?
```
Option 1: Reverse Proxy Nginx (sécurisé)
Option 2: VPN (recommandé)
Option 3: Tunnel Ngrok (temporaire)

Voir: docs/PROXMOX_DEPLOYMENT.md
```

---

## 📈 Progression d'apprentissage

```
Jour 1: Setup (30 min)
├─ Obtenir clés API
├─ Installer JARVIS
└─ Tester la connexion

Jour 2: Exploration (1h)
├─ Interface web
├─ Premières commandes texte
└─ Premières commandes vocale

Jour 3: Personnalisation (1-2h)
├─ Configurer Home Assistant
├─ Ajouter appareils
└─ Tester le contrôle complet

Jour 4+: Avancé (∞)
├─ Automations complexes
├─ Multi-utilisateurs
├─ Intégrations supplémentaires
└─ Développement custom
```

---

## 🎓 Ressources d'apprentissage

```
Besoin d'aide sur:

JARVIS?
└─ Lire: README.md, TUTORIAL_COMPLET_FR.md

API Web?
└─ Lire: docs/WEB_INTERFACE.md

Home Assistant?
└─ Aller sur: https://www.home-assistant.io/docs/

OpenAI?
└─ Aller sur: https://platform.openai.com/docs/

Docker?
└─ Aller sur: https://docs.docker.com/
```

---

**Vous êtes prêt(e)! Commencez par lire le [TUTORIAL_COMPLET_FR.md](TUTORIAL_COMPLET_FR.md)** 🚀
