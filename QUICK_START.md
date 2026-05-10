# ⚡ QUICK START - JARVIS

## 🎯 2 options: Web UI ou CLI

### Option 1: 🌐 Interface Web (RECOMMANDÉ)

**Accédez depuis n'importe quel navigateur!**

```bash
# 1. Cloner et configurer
git clone https://github.com/HarryBen23/Jarvis.git
cd Jarvis
cp .env.example .env
nano .env  # Ajouter vos clés

# 2. Lancer
bash scripts/start-web.sh

# 3. Ouvrir
http://localhost:8000
```

### Option 2: 🎤 CLI (Microphone local)

**Parler directement au serveur**

```bash
# 1. Cloner et configurer
git clone https://github.com/HarryBen23/Jarvis.git
cd Jarvis
cp .env.example .env
nano .env

# 2. Lancer
docker-compose up -d jarvis-cli

# 3. Vérifier
docker-compose logs -f jarvis-cli
```

---

## 🔑 Obtenir les clés API (2 min)

### OpenAI (Whisper + ChatGPT)
1. Aller sur https://platform.openai.com/api-keys
2. **+ Create new secret key**
3. Copier la clé

### Home Assistant Token
1. Ouvrir Home Assistant: `http://localhost:8123`
2. **Settings** → **Devices & Services** → (bas de page) **API Tokens**
3. **+ Create Token**
4. Copier le token

### Éditer .env
```bash
nano .env
```

```ini
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
HA_TOKEN=eyJhbGciOiJIUzI1NiIsInR5......
HA_URL=http://home-assistant:8123
```

---

## ✅ Test rapide

```bash
# Vérifier la connexion
python scripts/test-connection.py

# Ou manuellement
curl http://localhost:8000/health  # Web UI
docker-compose logs -f             # Voir les logs
```

---

## 🚀 C'est parti!

### Web UI
```bash
bash scripts/start-web.sh
# Puis ouvrir http://localhost:8000
```

### CLI
```bash
docker-compose up -d jarvis-cli
docker-compose logs -f jarvis-cli
```

---

## 📚 Docs complètes

- [Documentation complète](README.md)
- [Interface Web](docs/WEB_INTERFACE.md)
- [Architecture](docs/ARCHITECTURE.md) (à venir)

---

## 🐛 Problèmes?

| Problème | Solution |
|----------|----------|
| Port 8000 occupé | `lsof -i :8000` puis tuer le process |
| Pas de microphone | Vérifier `/dev/snd` permissions |
| HA not found | Vérifier `HA_URL` dans `.env` |
| API Key error | Vérifier `OPENAI_API_KEY` |

**Plus d'aide dans README.md** ↗️
