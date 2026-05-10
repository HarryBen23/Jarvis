FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système pour audio
RUN apt-get update && apt-get install -y \
    build-essential \
    libsndfile1 \
    ffmpeg \
    alsa-utils \
    pulseaudio \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/

# Volume pour la configuration runtime
VOLUME ["/app/config"]

# Lancer JARVIS
CMD ["python", "src/jarvis.py"]
