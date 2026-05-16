#!/usr/bin/env python3
"""
JARVIS - Iron Man Style Home Assistant Control System
Contrôle Home Assistant par reconnaissance vocale + IA
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

import openai
import aiohttp
from openai import AsyncOpenAI
import sounddevice as sd
import soundfile as sf
import numpy as np

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JarvisConfig:
    """Configuration centralisée de JARVIS"""
    
    def __init__(self, config_path: str = "config/jarvis.json"):
        self.config_path = Path(config_path)
        self.load_config()
    
    def load_config(self):
        """Charge la configuration depuis le fichier JSON"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                self.openai_api_key = self._resolve_env_reference(config.get('openai_api_key')) or os.getenv('OPENAI_API_KEY')
                self.home_assistant_url = config.get('home_assistant_url', 'http://localhost:8123')
                self.home_assistant_token = self._resolve_env_reference(config.get('home_assistant_token')) or os.getenv('HA_TOKEN')
                self.wake_word = config.get('wake_word', 'jarvis')
                self.device_index = config.get('device_index', None)
                self.sample_rate = config.get('sample_rate', 16000)
                self.audio_duration = config.get('audio_duration', 5.0)
                self.log_level = config.get('log_level', os.getenv('LOG_LEVEL', 'INFO'))
        else:
            self.openai_api_key = os.getenv('OPENAI_API_KEY')
            self.home_assistant_url = os.getenv('HA_URL', 'http://localhost:8123')
            self.home_assistant_token = os.getenv('HA_TOKEN')
            self.wake_word = 'jarvis'
            self.device_index = None
            self.sample_rate = 16000
            self.audio_duration = 5.0
            self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # OPENAI_API_KEY peut être absent au démarrage si l'utilisateur souhaite
        # configurer la clé via l'interface web plus tard.
        # Home Assistant is optional. If HA_TOKEN is not configured, HA functionality is disabled.

    def _resolve_env_reference(self, value):
        """Résoudre une référence d'environnement du type ${VAR}."""
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            env_name = value[2:-1]
            return os.getenv(env_name)
        return value

    def save_config(self):
        """Sauvegarder la configuration dans le fichier JSON."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        config_data = {
            "openai_api_key": self.openai_api_key,
            "home_assistant_url": self.home_assistant_url,
            "home_assistant_token": self.home_assistant_token,
            "wake_word": self.wake_word,
            "device_index": self.device_index,
            "sample_rate": self.sample_rate,
            "audio_duration": self.audio_duration,
            "log_level": self.log_level
        }
        with open(self.config_path, 'w') as f:
            json.dump(config_data, f, indent=2)


class AudioCapture:
    """Capture audio depuis le microphone"""
    
    def __init__(self, sample_rate: int = 16000, duration: float = 5.0, device_index: Optional[int] = None):
        self.sample_rate = sample_rate
        self.duration = duration
        self.device_index = device_index
    
    async def record_audio(self) -> bytes:
        """Enregistre l'audio et retourne en bytes"""
        logger.info(f"🎙️ Enregistrement pendant {self.duration}s...")
        
        try:
            # Enregistrement dans un thread séparé (asyncio)
            loop = asyncio.get_event_loop()
            audio_data = await loop.run_in_executor(
                None,
                self._record_sync
            )
            logger.info("✅ Enregistrement terminé")
            return audio_data
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'enregistrement: {e}")
            raise
    
    def _record_sync(self) -> bytes:
        """Enregistrement synchrone"""
        audio_data = sd.rec(
            int(self.sample_rate * self.duration),
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.float32,
            device=self.device_index
        )
        sd.wait()
        
        # Convertir en bytes WAV
        import io
        buffer = io.BytesIO()
        sf.write(buffer, audio_data, self.sample_rate, format='WAV')
        return buffer.getvalue()


class SpeechRecognition:
    """Transcription vocale avec OpenAI Whisper"""
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def transcribe(self, audio_data: bytes) -> str:
        """Transcrit l'audio en texte"""
        logger.info("🗣️ Transcription en cours...")
        
        try:
            # Créer un fichier temporaire
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name
            
            # Transcription avec Whisper
            loop = asyncio.get_event_loop()
            with open(tmp_path, 'rb') as audio_file:
                transcript = await loop.run_in_executor(
                    None,
                    lambda: self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="fr"
                    )
                )
            
            text = transcript.text
            logger.info(f"📝 Texte reconnu: {text}")
            
            # Cleanup
            os.remove(tmp_path)
            return text
        
        except Exception as e:
            logger.error(f"❌ Erreur transcription: {e}")
            raise


class AIBrain:
    """Moteur IA utilisant ChatGPT"""
    
    def __init__(self, api_key: str, ha_config: Dict[str, Any]):
        self.client = AsyncOpenAI(api_key=api_key)
        self.ha_config = ha_config
        self.conversation_history = []
    
    async def process_request(self, user_input: str) -> str:
        """Traite la demande et retourne une réponse"""
        logger.info(f"🧠 Traitement: {user_input}")
        
        # Ajouter au contexte
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Limiter l'historique à 10 messages
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
        
        system_prompt = """Tu es JARVIS, un assistant IA de style Iron Man en français.
Tu contrôles une maison intelligente via Home Assistant.
Réponds de manière professionnelle et sophistiquée, comme un vrai butler IA.
Sois concis et utile. Si l'utilisateur demande une action sur la domotique, 
indique quelle action tu vas effectuer."""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *self.conversation_history
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            ai_response = response.choices[0].message.content
            
            # Ajouter la réponse à l'historique
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_response
            })
            
            logger.info(f"🤖 JARVIS: {ai_response}")
            return ai_response
        
        except Exception as e:
            logger.error(f"❌ Erreur IA: {e}")
            raise


class HomeAssistantClient:
    """Client pour contrôler Home Assistant"""
    
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    async def get_states(self) -> Dict[str, Any]:
        """Récupère l'état de tous les appareils"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/states",
                    headers=self.headers
                ) as resp:
                    if resp.status == 200:
                        states = await resp.json()
                        logger.info(f"📊 États: {len(states)} appareils")
                        return states
                    else:
                        logger.error(f"Erreur API: {resp.status}")
                        return {}
        except Exception as e:
            logger.error(f"❌ Erreur getLights: {e}")
            return {}
    
    async def call_service(self, domain: str, service: str, data: Dict = None) -> bool:
        """Appelle un service Home Assistant"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/services/{domain}/{service}",
                    headers=self.headers,
                    json=data or {}
                ) as resp:
                    success = resp.status == 200
                    if success:
                        logger.info(f"✅ Service appelé: {domain}.{service}")
                    else:
                        logger.error(f"❌ Erreur service: {resp.status}")
                    return success
        except Exception as e:
            logger.error(f"❌ Erreur call_service: {e}")
            return False


class JARVIS:
    """Système principal JARVIS"""
    
    def __init__(self, config: JarvisConfig):
        self.config = config
        self.audio_capture = AudioCapture(
            sample_rate=config.sample_rate,
            device_index=config.device_index
        )
        self.speech_recognition = SpeechRecognition(config.openai_api_key)
        self.ai_brain = AIBrain(config.openai_api_key, {})
        self.ha_client = None
        if config.home_assistant_token:
            self.ha_client = HomeAssistantClient(
                config.home_assistant_url,
                config.home_assistant_token
            )
        self.is_running = False
    
    async def listen_and_respond(self):
        """Boucle principale: écoute -> reconnaissance -> IA -> action"""
        logger.info(f"🎙️ JARVIS en écoute. Mot de réveil: '{self.config.wake_word}'...")
        
        try:
            # 1. Capturer l'audio
            audio_data = await self.audio_capture.record_audio()
            
            # 2. Transcrire
            user_text = await self.speech_recognition.transcribe(audio_data)
            
            # Vérifier le mot de réveil
            if self.config.wake_word.lower() not in user_text.lower():
                logger.info("⏭️ Mot de réveil non détecté")
                return
            
            # Nettoyer la commande
            command = user_text.lower().replace(self.config.wake_word.lower(), "").strip()
            if not command:
                logger.info("⏭️ Aucune commande après le mot de réveil")
                return
            
            # 3. Traiter avec IA
            response = await self.ai_brain.process_request(command)
            
            # 4. Exécuter les actions Home Assistant si nécessaire
            await self._execute_actions(command)
            
            print(f"\n🤖 JARVIS: {response}\n")
        
        except Exception as e:
            logger.error(f"❌ Erreur: {e}")
    
    async def _execute_actions(self, command: str):
        """Exécute les actions Home Assistant basées sur la commande"""
        command_lower = command.lower()
        
        # Pas de Home Assistant configuré : ignorer les actions HA
        if not self.ha_client:
            logger.warning("Home Assistant non configuré : actions HA désactivées")
            return

        # Exemples d'actions simples
        if "lumière" in command_lower and "on" in command_lower or "allume" in command_lower:
            await self.ha_client.call_service("light", "turn_on", {"entity_id": "light.salon"})
        
        elif "lumière" in command_lower and "off" in command_lower or "éteint" in command_lower:
            await self.ha_client.call_service("light", "turn_off", {"entity_id": "light.salon"})
        
        elif "climatisation" in command_lower or "température" in command_lower:
            states = await self.ha_client.get_states()
            logger.info(f"📊 Appareils disponibles: {json.dumps(states[:3], indent=2)}")
    
    async def run(self):
        """Lance JARVIS en mode continu"""
        self.is_running = True
        logger.info("🚀 JARVIS démarré - Mode écoute continue")
        print("=" * 60)
        print("🤖 JARVIS - Système de contrôle domotique IA")
        print("=" * 60)
        
        try:
            while self.is_running:
                try:
                    await self.listen_and_respond()
                    # Petit délai avant la prochaine écoute
                    await asyncio.sleep(1)
                except KeyboardInterrupt:
                    logger.info("⏹️ Arrêt de JARVIS...")
                    self.is_running = False
                except Exception as e:
                    logger.error(f"Erreur dans la boucle: {e}")
                    await asyncio.sleep(2)
        
        except KeyboardInterrupt:
            logger.info("JARVIS arrêté par l'utilisateur")


async def main():
    """Point d'entrée principal"""
    try:
        # Charger la configuration
        config = JarvisConfig()
        
        # Créer et lancer JARVIS
        jarvis = JARVIS(config)
        await jarvis.run()
    
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
