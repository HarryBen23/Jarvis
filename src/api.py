#!/usr/bin/env python3
"""
API FastAPI pour JARVIS - Interface Web
"""

import os
import json
import logging
import asyncio
import tempfile
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path

# Imports du système JARVIS
from jarvis import (
    JarvisConfig, SpeechRecognition, AIBrain, 
    HomeAssistantClient, AudioCapture
)

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Créer l'app FastAPI
app = FastAPI(
    title="JARVIS API",
    description="API Web pour contrôler JARVIS",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales
config: Optional[JarvisConfig] = None
speech_recognition: Optional[SpeechRecognition] = None
ai_brain: Optional[AIBrain] = None
ha_client: Optional[HomeAssistantClient] = None


class UserMessage(BaseModel):
    """Message utilisateur"""
    text: str


class TranscriptionResponse(BaseModel):
    """Réponse de transcription"""
    text: str
    confidence: float = 0.95


class AIResponse(BaseModel):
    """Réponse IA"""
    response: str
    timestamp: str


@app.on_event("startup")
async def startup_event():
    """Initialiser JARVIS au démarrage"""
    global config, speech_recognition, ai_brain, ha_client
    
    try:
        logger.info("🚀 Initialisation de l'API JARVIS...")
        
        config = JarvisConfig()
        speech_recognition = SpeechRecognition(config.openai_api_key)
        ai_brain = AIBrain(config.openai_api_key, {})
        ha_client = HomeAssistantClient(
            config.home_assistant_url,
            config.home_assistant_token
        )
        
        logger.info("✅ API JARVIS prête!")
    except Exception as e:
        logger.error(f"❌ Erreur démarrage: {e}")
        raise


@app.get("/", response_class=HTMLResponse)
async def index():
    """Affiche l'interface web"""
    return get_html_interface()


@app.get("/health")
async def health_check():
    """Vérifier la santé de l'API"""
    try:
        states = await ha_client.get_states()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "home_assistant": "connected" if states else "disconnected",
            "openai": "configured" if config.openai_api_key else "not configured"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.post("/api/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcrire l'audio en texte"""
    try:
        # Lire le fichier
        audio_data = await file.read()
        
        # Transcrire
        text = await speech_recognition.transcribe(audio_data)
        
        return TranscriptionResponse(text=text)
    except Exception as e:
        logger.error(f"Erreur transcription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/process", response_model=AIResponse)
async def process_command(message: UserMessage):
    """Traiter une commande texte"""
    try:
        logger.info(f"📝 Traitement: {message.text}")
        
        # Traiter avec IA
        response = await ai_brain.process_request(message.text)
        
        # Exécuter les actions Home Assistant
        await execute_home_assistant_actions(message.text)
        
        return AIResponse(
            response=response,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Erreur traitement: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/voice")
async def process_voice(file: UploadFile = File(...)):
    """Traiter la voix: transcription + IA"""
    try:
        # Lire le fichier audio
        audio_data = await file.read()
        
        # Transcrire
        text = await speech_recognition.transcribe(audio_data)
        logger.info(f"Texte reconnu: {text}")
        
        # Traiter avec IA
        response = await ai_brain.process_request(text)
        
        # Exécuter les actions
        await execute_home_assistant_actions(text)
        
        return {
            "input_text": text,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/home-assistant/entities")
async def get_ha_entities():
    """Récupérer les entités Home Assistant"""
    try:
        states = await ha_client.get_states()
        
        # Organiser par domaine
        entities = {}
        for state in states:
            entity_id = state.get('entity_id', '')
            domain = entity_id.split('.')[0] if '.' in entity_id else 'unknown'
            
            if domain not in entities:
                entities[domain] = []
            
            entities[domain].append({
                "entity_id": entity_id,
                "state": state.get('state'),
                "attributes": state.get('attributes', {})
            })
        
        return entities
    except Exception as e:
        logger.error(f"Erreur récupération entités: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/home-assistant/service")
async def call_ha_service(service_call: dict):
    """Appeler un service Home Assistant"""
    try:
        domain = service_call.get('domain')
        service = service_call.get('service')
        data = service_call.get('data', {})
        
        success = await ha_client.call_service(domain, service, data)
        
        return {"success": success}
    except Exception as e:
        logger.error(f"Erreur appel service: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket pour écoute en continu"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            
            # Traiter le message
            try:
                response = await ai_brain.process_request(data)
                await websocket.send_json({
                    "type": "response",
                    "text": response,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "error": str(e)
                })
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


async def execute_home_assistant_actions(command: str):
    """Exécuter les actions HA basées sur la commande"""
    command_lower = command.lower()
    
    try:
        if "lumière" in command_lower:
            if "allume" in command_lower or "on" in command_lower:
                await ha_client.call_service("light", "turn_on", 
                                            {"entity_id": "light.salon"})
            elif "éteint" in command_lower or "off" in command_lower:
                await ha_client.call_service("light", "turn_off",
                                            {"entity_id": "light.salon"})
    except Exception as e:
        logger.warning(f"Impossible d'exécuter l'action: {e}")


def get_html_interface() -> str:
    """Retourner l'interface HTML"""
    return """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 JARVIS - Interface Web</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
            padding: 40px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 2.5em;
            color: #333;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 0.95em;
        }
        
        .status-bar {
            display: flex;
            justify-content: space-around;
            margin-bottom: 30px;
            padding: 15px;
            background: #f5f5f5;
            border-radius: 10px;
            font-size: 0.9em;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #ddd;
        }
        
        .status-dot.connected {
            background: #4CAF50;
        }
        
        .input-section {
            margin-bottom: 30px;
        }
        
        .input-section h2 {
            font-size: 1.1em;
            margin-bottom: 15px;
            color: #333;
        }
        
        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        input[type="text"] {
            flex: 1;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        button {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
            flex: 1;
        }
        
        .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: #f0f0f0;
            color: #333;
        }
        
        .btn-secondary:hover {
            background: #e0e0e0;
        }
        
        .btn-secondary.recording {
            background: #f44336;
            color: white;
            animation: pulse 1s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .response-section {
            background: #f9f9f9;
            border-radius: 10px;
            padding: 20px;
            min-height: 100px;
        }
        
        .response-section h3 {
            font-size: 0.95em;
            color: #666;
            margin-bottom: 10px;
            text-transform: uppercase;
        }
        
        .response-text {
            font-size: 1.05em;
            color: #333;
            line-height: 1.6;
            min-height: 60px;
        }
        
        .response-text.empty {
            color: #999;
            font-style: italic;
        }
        
        .response-text.loading {
            color: #667eea;
        }
        
        .voice-input {
            position: relative;
            margin: 20px 0;
        }
        
        .voice-waveform {
            display: flex;
            align-items: flex-end;
            justify-content: center;
            gap: 3px;
            height: 50px;
            margin-bottom: 15px;
        }
        
        .wave {
            width: 4px;
            height: 10px;
            background: #667eea;
            border-radius: 2px;
            animation: wave 0.6s ease-in-out infinite;
        }
        
        @keyframes wave {
            0%, 100% { height: 10px; }
            50% { height: 30px; }
        }
        
        .wave:nth-child(1) { animation-delay: 0s; }
        .wave:nth-child(2) { animation-delay: 0.1s; }
        .wave:nth-child(3) { animation-delay: 0.2s; }
        .wave:nth-child(4) { animation-delay: 0.3s; }
        .wave:nth-child(5) { animation-delay: 0.4s; }
        
        .hidden {
            display: none;
        }
        
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 12px;
            border-radius: 8px;
            margin: 10px 0;
            display: none;
        }
        
        .error.show {
            display: block;
        }
        
        .entities-section {
            margin-top: 30px;
            padding-top: 30px;
            border-top: 1px solid #eee;
        }
        
        .entities-section h3 {
            font-size: 1em;
            margin-bottom: 15px;
            color: #333;
        }
        
        .entity-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 10px;
        }
        
        .entity-item {
            padding: 10px;
            background: #f5f5f5;
            border-radius: 6px;
            font-size: 0.9em;
        }
        
        .entity-item .state {
            color: #667eea;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 JARVIS</h1>
            <p>Assistant IA pour Home Assistant</p>
        </div>
        
        <div class="status-bar">
            <div class="status-item">
                <span class="status-dot connected"></span>
                API: Connectée
            </div>
            <div class="status-item">
                <span class="status-dot" id="ha-status"></span>
                <span>Home Assistant</span>
            </div>
            <div class="status-item">
                <span class="status-dot" id="ai-status"></span>
                <span>OpenAI</span>
            </div>
        </div>
        
        <div class="input-section">
            <h2>📝 Texte</h2>
            <div class="input-group">
                <input type="text" id="text-input" placeholder="Dites votre commande...">
                <button class="btn-primary" onclick="sendText()">
                    📤 Envoyer
                </button>
            </div>
            
            <h2>🎙️ Voix</h2>
            <div class="voice-input">
                <div class="voice-waveform hidden" id="waveform">
                    <div class="wave"></div>
                    <div class="wave"></div>
                    <div class="wave"></div>
                    <div class="wave"></div>
                    <div class="wave"></div>
                </div>
                <div class="button-group">
                    <button class="btn-primary btn-secondary" id="record-btn" onclick="toggleRecording()">
                        🎤 Enregistrer
                    </button>
                    <button class="btn-secondary" onclick="listDevices()">
                        📋 Appareils
                    </button>
                </div>
            </div>
        </div>
        
        <div class="error" id="error-message"></div>
        
        <div class="response-section">
            <h3>💬 Réponse</h3>
            <div class="response-text empty" id="response-text">
                En attente de commande...
            </div>
        </div>
        
        <div class="entities-section hidden" id="entities-section">
            <h3>🏠 Appareils domotiques</h3>
            <div class="entity-list" id="entity-list"></div>
        </div>
    </div>
    
    <script>
        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;
        
        // Initialisation
        async function init() {
            try {
                const health = await fetch('/health').then(r => r.json());
                
                // Mettre à jour les statuts
                document.getElementById('ha-status').classList.toggle('connected', 
                    health.home_assistant === 'connected');
                document.getElementById('ai-status').classList.toggle('connected',
                    health.openai === 'configured');
                
                // Charger les entités
                loadEntities();
            } catch (error) {
                console.error('Erreur initialisation:', error);
            }
        }
        
        async function sendText() {
            const input = document.getElementById('text-input');
            const text = input.value.trim();
            
            if (!text) return;
            
            showLoading();
            
            try {
                const response = await fetch('/api/process', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    showResponse(data.response);
                    input.value = '';
                    loadEntities();
                } else {
                    showError('Erreur lors du traitement');
                }
            } catch (error) {
                showError(`Erreur: ${error.message}`);
            }
        }
        
        async function toggleRecording() {
            if (!isRecording) {
                startRecording();
            } else {
                stopRecording();
            }
        }
        
        async function startRecording() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                
                mediaRecorder.ondataavailable = (event) => {
                    audioChunks.push(event.data);
                };
                
                mediaRecorder.onstop = async () => {
                    await processAudio();
                    stream.getTracks().forEach(track => track.stop());
                };
                
                mediaRecorder.start();
                isRecording = true;
                
                document.getElementById('record-btn').classList.add('recording');
                document.getElementById('record-btn').textContent = '⏹️ Arrêter';
                document.getElementById('waveform').classList.remove('hidden');
                
                showResponse('🎤 Enregistrement en cours...');
            } catch (error) {
                showError(`Erreur microphone: ${error.message}`);
            }
        }
        
        function stopRecording() {
            mediaRecorder.stop();
            isRecording = false;
            
            document.getElementById('record-btn').classList.remove('recording');
            document.getElementById('record-btn').textContent = '🎤 Enregistrer';
            document.getElementById('waveform').classList.add('hidden');
        }
        
        async function processAudio() {
            showLoading();
            
            try {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const formData = new FormData();
                formData.append('file', audioBlob, 'audio.wav');
                
                const response = await fetch('/api/voice', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const data = await response.json();
                    showResponse(`📝 "${data.input_text}"\\n\\n🤖 ${data.response}`);
                    loadEntities();
                } else {
                    showError('Erreur transcription vocale');
                }
            } catch (error) {
                showError(`Erreur: ${error.message}`);
            }
        }
        
        async function loadEntities() {
            try {
                const response = await fetch('/api/home-assistant/entities');
                if (response.ok) {
                    const entities = await response.json();
                    displayEntities(entities);
                }
            } catch (error) {
                console.error('Erreur chargement entités:', error);
            }
        }
        
        function displayEntities(entities) {
            const section = document.getElementById('entities-section');
            const list = document.getElementById('entity-list');
            
            let hasEntities = false;
            list.innerHTML = '';
            
            for (const [domain, items] of Object.entries(entities)) {
                if (items.length > 0 && domain !== 'update') {
                    hasEntities = true;
                    items.slice(0, 5).forEach(item => {
                        const state = item.state || 'N/A';
                        const name = item.attributes.friendly_name || item.entity_id;
                        
                        const html = `
                            <div class="entity-item">
                                <div>${name}</div>
                                <div class="state">${state}</div>
                            </div>
                        `;
                        list.innerHTML += html;
                    });
                }
            }
            
            section.classList.toggle('hidden', !hasEntities);
        }
        
        function showLoading() {
            document.getElementById('response-text').innerHTML = '⏳ Traitement...';
            document.getElementById('response-text').classList.add('loading');
        }
        
        function showResponse(text) {
            const element = document.getElementById('response-text');
            element.innerHTML = text.replace(/\\n/g, '<br>');
            element.classList.remove('empty', 'loading');
        }
        
        function showError(message) {
            const element = document.getElementById('error-message');
            element.textContent = message;
            element.classList.add('show');
            
            setTimeout(() => {
                element.classList.remove('show');
            }, 5000);
        }
        
        async function listDevices() {
            showResponse('📋 Appareils audio disponibles\\n(Vérifiez la console du navigateur)');
            
            const devices = await navigator.mediaDevices.enumerateDevices();
            const audioDevices = devices.filter(d => d.kind === 'audioinput');
            console.log('Appareils audio:', audioDevices);
        }
        
        // Raccourcis clavier
        document.addEventListener('DOMContentLoaded', () => {
            init();
            
            document.getElementById('text-input').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendText();
            });
        });
    </script>
</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv('API_PORT', 8000))
    host = os.getenv('API_HOST', '0.0.0.0')
    
    logger.info(f"🚀 Lancement API sur {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")
