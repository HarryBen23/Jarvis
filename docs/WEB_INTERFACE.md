# 🌐 Interface Web JARVIS

Interface web moderne pour contrôler JARVIS depuis votre navigateur.

## ✨ Fonctionnalités

- **📝 Contrôle par texte** : Tapez vos commandes
- **🎤 Contrôle vocal** : Parlez au microphone (enregistrement en navigateur)
- **📊 Tableau de bord** : Voir l'état des appareils domotiques
- **📱 Responsive** : Fonctionne sur PC, tablette, téléphone
- **🔄 Temps réel** : Mises à jour instantanées
- **🛡️ Sécurisé** : CORS configuré

## 🚀 Démarrage rapide

```bash
# 1. Cloner et configurer
git clone https://github.com/HarryBen23/Jarvis.git
cd Jarvis
cp .env.example .env
nano .env  # Ajouter vos clés API

# 2. Lancer avec script
chmod +x scripts/start-web.sh
./scripts/start-web.sh

# OU manuellement
docker-compose up -d

# 3. Ouvrir
Navigateur: http://localhost:8000
```

## 📡 API Endpoints

### Santé
```bash
GET /health
```
Retourne l'état de l'API, Home Assistant et OpenAI.

### Transcription vocale
```bash
POST /api/transcribe
Content-Type: multipart/form-data
- file: audio.wav
```
Transcrire l'audio en texte avec Whisper.

### Traitement texte
```bash
POST /api/process
Content-Type: application/json
{
  "text": "Allume la lumière du salon"
}
```
Traiter une commande texte et retourner la réponse IA.

### Traitement vocal complet
```bash
POST /api/voice
Content-Type: multipart/form-data
- file: audio.wav
```
Transcription + IA + exécution Home Assistant en une seule requête.

### Lister les entités
```bash
GET /api/home-assistant/entities
```
Récupérer tous les appareils domotiques organisés par domaine.

### Appeler un service
```bash
POST /api/home-assistant/service
Content-Type: application/json
{
  "domain": "light",
  "service": "turn_on",
  "data": {
    "entity_id": "light.salon"
  }
}
```

### WebSocket (temps réel)
```javascript
ws://localhost:8000/ws
// Envoyer un message texte
send("Allume la lumière")
// Recevoir une réponse
{
  "type": "response",
  "text": "Lumière allumée",
  "timestamp": "2026-05-10T..."
}
```

## 🎨 Interface utilisateur

### Sections

**Statut** 
- Affiche l'état de connexion
- Green dot = connecté

**Entrée Texte**
- Champ de texte pour taper les commandes
- Bouton Envoyer ou touche Entrée

**Entrée Vocale**
- 🎤 Enregistrer : Lance l'enregistrement du microphone
- Affiche l'onde sonore lors de l'enregistrement
- 📋 Appareils : Liste les appareils audio

**Réponse**
- Affiche la réponse de JARVIS
- Loading pendant le traitement
- Erreurs en rouge

**Appareils domotiques**
- Liste les lumières, capteurs, thermostats
- État actuel de chaque appareil

## 🔧 Configuration

### Pour la reconnaissance vocale

```bash
# Tester les microphones disponibles
docker exec jarvis-api arecord -l

# Si le micro n'est pas trouvé, configurez dans .env
AUDIO_DEVICE_INDEX=2
```

### Pour Home Assistant

```bash
# Vérifier la connexion
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8123/api/states
```

## 🧪 Tests

### Teste l'API directement

```bash
# Santé
curl http://localhost:8000/health

# Test texte
curl -X POST http://localhost:8000/api/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Allume la lumière"}'

# Test audio (nécessite un fichier audio.wav)
curl -X POST http://localhost:8000/api/voice \
  -F "file=@audio.wav"
```

### Test depuis Python

```python
import requests
import json

# Traiter une commande
response = requests.post(
    'http://localhost:8000/api/process',
    json={'text': 'Quel est le statut?'}
)
print(response.json())
```

## 🎯 Cas d'usage

### Taper une commande
1. Aller sur http://localhost:8000
2. Taper "Allume la lumière"
3. Cliquer "Envoyer"
4. Voir la réponse

### Utiliser la voix
1. Cliquer "Enregistrer"
2. Parler (5 secondes)
3. JARVIS transcrit et répond
4. Voir le résultat

### Voir les appareils
- Les appareils s'affichent automatiquement
- Cliquer sur un appareil pour voir son détail
- Utiliser la commande vocale pour le contrôler

## 🔒 Sécurité

- **CORS** : Accès depuis n'importe quel domaine (configurable)
- **Auth** : Basé sur le token Home Assistant
- **API** : HTTPS recommandé en production
- **Tokens** : Stockés dans les variables d'environnement

## 📊 Performance

- **Temps de réponse** : < 2 secondes (texte)
- **Transcription** : < 3 secondes (audio 5s)
- **Latence réseau** : < 100ms en local

## 🛠️ Troubleshooting

### "Cannot connect to API"
```bash
# Vérifier que le conteneur tourne
docker-compose ps

# Vérifier les logs
docker-compose logs jarvis-api

# Relancer
docker-compose restart jarvis-api
```

### "Microphone not found"
```bash
# Tester les devices
docker exec jarvis-api arecord -l

# Vérifier les permissions
docker-compose down
docker-compose up -d
```

### "Home Assistant connection failed"
```bash
# Vérifier le token
curl -H "Authorization: Bearer $HA_TOKEN" http://home-assistant:8123/api/

# Vérifier l'URL dans .env
```

## 🔮 Améliorations futures

- [ ] Support des notifications Push
- [ ] Historique des commandes
- [ ] Graphiques en temps réel
- [ ] Scénarios sauvegardés
- [ ] Authentification utilisateur
- [ ] Thème sombre/clair
- [ ] Export des données

## 📚 Ressources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Home Assistant API](https://developers.home-assistant.io/docs/api/)
- [OpenAI API](https://platform.openai.com/docs/api-reference)
- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)

---

**Besoin d'aide?** Ouvrez une issue sur GitHub!
