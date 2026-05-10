# ⚡ Démarrer JARVIS en 15 min (Guide super simple)

**Pas d'explications compliquées. Juste les commandes à copier-coller.**

---

## ÉTAPE 1: Obtenir 2 clés (5 min)

### Clé 1: OpenAI

1. Aller à: https://platform.openai.com/api-keys
2. Cliquer: **+ Create new secret key**
3. Copier la clé (ressemble à `sk-proj-xyz...`)

### Clé 2: Home Assistant Token

1. Ouvrir: http://localhost:8123
2. Aller: ⚙️ Settings → Devices & Services
3. Scroll down, cliquer: **+ Create Token** (en bas)
4. Copier le token (commence par `eyJhbGc...`)

---

## ÉTAPE 2: Configurer (2 min)

```bash
cd /root/Jarvis

# Créer le fichier config
cp .env.example .env

# Éditer
nano .env
```

**Remplacer ces lignes**:
```
OPENAI_API_KEY=votrecleapiici
HA_TOKEN=votretokenhici
```

**Sauvegarder**: `Ctrl+O` → `Entrée` → `Ctrl+X`

---

## ÉTAPE 3: Lancer (1 min)

```bash
bash scripts/start-web.sh
```

Attendre que ça dise: ✅ API prête!

---

## ÉTAPE 4: Utiliser (dans le navigateur)

```
http://localhost:8000
```

### Taper une commande:
```
Allume la lumière
```

### Ou enregistrer de la voix:
```
Cliquer sur 🎤 Enregistrer
Parler
Puis écouter la réponse
```

---

## ✅ C'est tout!

JARVIS marche maintenant. 🎉

---

## 🆘 Problème?

```bash
# Voir les erreurs
docker-compose logs

# Tester que tout marche
python scripts/test-connection.py

# Redémarrer
docker-compose restart
```

**Plus d'aide**: Voir [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## 📖 Veux en savoir plus?

- [GUIDE_VISUEL.md](docs/GUIDE_VISUEL.md) - Comprendre comment ça marche
- [TUTORIAL_COMPLET_FR.md](docs/TUTORIAL_COMPLET_FR.md) - Guide complet
- [docs/INDEX.md](docs/INDEX.md) - Tous les guides

---

**Voilà! JARVIS est maintenant à vos ordres!** 🤖
