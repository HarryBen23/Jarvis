#!/bin/bash

# Dossier de config Home Assistant pour docker-compose
VOLUME_PATH="config/home-assistant"

if [ ! -d "$VOLUME_PATH" ]; then
    mkdir -p "$VOLUME_PATH"
    echo "📁 Dossier créé: $VOLUME_PATH"
fi

# Créer la structure de base HA
mkdir -p "$VOLUME_PATH/entities"

# Créer configuration.yaml minimal
cat > "$VOLUME_PATH/configuration.yaml" << 'EOF'
homeassistant:
  name: "Maison"
  latitude: 48.8566
  longitude: 2.3522
  elevation: 0
  unit_system: metric
  time_zone: "Europe/Paris"

http:
  cors_allowed_origins:
    - "http://localhost:3000"
    - "http://127.0.0.1:3000"

# Habilitez le logging
logger:
  default: info

# Texte pour le frontend
frontend:

# Commandes shell
shell_command:

# Automations
automation: !include automations.yaml
script: !include scripts.yaml
scene: !include scenes.yaml
EOF

# Créer les fichiers d'automations vides
touch "$VOLUME_PATH/automations.yaml"
touch "$VOLUME_PATH/scripts.yaml"
touch "$VOLUME_PATH/scenes.yaml"

echo "✅ Configuration Home Assistant initialisée"
ls -la "$VOLUME_PATH"
