let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let selectedMicDeviceId = null;
let selectedSpeakerDeviceId = null;
let ttsVoice = null;
let ttsEnabled = true;

function isMicrophoneSupported() {
    // Vérifier navigator.mediaDevices (standard moderne)
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        return true;
    }
    
    // Fallback pour les anciens navigateurs
    if (navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia) {
        return true;
    }
    
    return false;
}

function showMicWarningBanner() {
    const banner = document.getElementById('mic-warning-banner');
    if (banner) {
        banner.style.display = 'block';
        document.body.classList.add('mic-warning-visible');
    }
}

function hideMicWarningBanner() {
    const banner = document.getElementById('mic-warning-banner');
    if (banner) {
        banner.style.display = 'none';
        document.body.classList.remove('mic-warning-visible');
    }
}

function logAudioDiagnostics() {
    const info = {
        userAgent: navigator.userAgent,
        mediaDevices: !!navigator.mediaDevices,
        getUserMedia: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
        enumerateDevices: !!(navigator.mediaDevices && navigator.mediaDevices.enumerateDevices),
        webkitGetUserMedia: !!navigator.webkitGetUserMedia,
        mozGetUserMedia: !!navigator.mozGetUserMedia,
        msGetUserMedia: !!navigator.msGetUserMedia,
        isSecureContext: window.isSecureContext,
        location: window.location.origin,
        protocol: window.location.protocol
    };
    
    console.log('📊 Diagnostic audio:', info);
    console.log('🎤 Microphone supporté:', isMicrophoneSupported());
    
    // Afficher dans un élément de la page si présent
    const debugElement = document.getElementById('audio-debug-info');
    if (debugElement) {
        debugElement.innerHTML = `<pre>${JSON.stringify(info, null, 2)}</pre>`;
    }
}

// Initialisation
async function init() {
    try {
        const health = await fetch('/health').then(r => r.json());
        
        // Mettre à jour les indicateurs de statut
        const apiStatus = document.getElementById('api-status');
        const haStatus = document.getElementById('ha-status');
        const aiStatus = document.getElementById('ai-status');
        
        // API est considérée comme connectée si on reçoit la réponse
        apiStatus.classList.add('api');
        
        if (health.home_assistant === 'connected') {
            haStatus.classList.add('ha');
        }
        
        if (health.openai === 'configured') {
            aiStatus.classList.add('ai');
        }
        
        // Vérifier la disponibilité du micro
        const recordBtn = document.getElementById('record-btn');
        if (!isMicrophoneSupported()) {
            recordBtn.disabled = true;
            recordBtn.title = 'Microphone non supporté par ce navigateur.';
            recordBtn.style.opacity = '0.5';
            showMicWarningBanner();
        } else {
            hideMicWarningBanner();
            loadAudioDevices();
        }
        
        // Charger les entités, la voix TTS et le statut OpenAI
        loadEntities();
        loadOpenAIKeyInfo();
        loadTTSVoices();
        
        // Afficher les infos de diagnostic
        logAudioDiagnostics();
    } catch (error) {
        console.error('Erreur initialisation:', error);
    }
}

function toggleTTS() {
    const toggle = document.getElementById('tts-toggle');
    ttsEnabled = toggle ? toggle.checked : true;
}

function setJarvisVoice(voices) {
    if (!voices || voices.length === 0) return;

    const preferred = voices.find(voice => {
        const name = voice.name.toLowerCase();
        return name.includes('fr') || name.includes('french') || name.includes('audrey') || name.includes('samantha');
    });

    ttsVoice = preferred || voices[0];
    console.log('Voix Jarvis sélectionnée:', ttsVoice.name);
}

function loadTTSVoices() {
    if (!window.speechSynthesis) {
        console.warn('SpeechSynthesis non supporté par ce navigateur.');
        return;
    }

    const voices = window.speechSynthesis.getVoices();
    if (voices.length > 0) {
        setJarvisVoice(voices);
        return;
    }

    window.speechSynthesis.onvoiceschanged = () => {
        const newVoices = window.speechSynthesis.getVoices();
        setJarvisVoice(newVoices);
    };
}

function speakText(text) {
    if (!ttsEnabled || !window.speechSynthesis || !text) return;

    try {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text.replace(/\n+/g, '. '));
        utterance.lang = 'fr-FR';
        utterance.rate = 0.95;
        utterance.pitch = 1;
        if (ttsVoice) {
            utterance.voice = ttsVoice;
        }
        window.speechSynthesis.speak(utterance);
    } catch (error) {
        console.warn('Erreur TTS:', error);
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
            speakText(data.response);
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
        if (!isMicrophoneSupported()) {
            showError('❌ Microphone non supporté. Vérifiez votre navigateur.');
            return;
        }

        // Récupérer les paramètres du microphone
        const micSelect = document.getElementById('mic-select');
        
        let stream;
        
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            // API moderne
            const constraints = {
                audio: {
                    deviceId: micSelect && micSelect.value ? { exact: micSelect.value } : undefined
                }
            };
            stream = await navigator.mediaDevices.getUserMedia(constraints);
        } else if (navigator.getUserMedia) {
            // Fallback ancien navigateur
            stream = await new Promise((resolve, reject) => {
                navigator.getUserMedia({ audio: true }, resolve, reject);
            });
        } else if (navigator.webkitGetUserMedia) {
            // Safari fallback
            stream = await new Promise((resolve, reject) => {
                navigator.webkitGetUserMedia({ audio: true }, resolve, reject);
            });
        } else if (navigator.mozGetUserMedia) {
            // Firefox fallback
            stream = await new Promise((resolve, reject) => {
                navigator.mozGetUserMedia({ audio: true }, resolve, reject);
            });
        } else {
            throw new Error('Aucune API de microphone disponible');
        }

        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        // Sauvegarder le deviceId sélectionné
        if (micSelect && micSelect.value) {
            selectedMicDeviceId = micSelect.value;
        }
        
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };
        
        mediaRecorder.onstop = async () => {
            await processAudio();
            stream.getTracks().forEach(track => track.stop());
        };
        
        mediaRecorder.start();
        isRecording = true;
        
        const btn = document.getElementById('record-btn');
        btn.classList.add('recording');
        btn.textContent = '⏹️ Arrêter';
        
        showResponse('🎤 Enregistrement en cours...');
    } catch (error) {
        showError(`Erreur microphone: ${error.message}`);
        console.error('Erreur startRecording:', error);
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
    }
    isRecording = false;
    
    const btn = document.getElementById('record-btn');
    btn.classList.remove('recording');
    btn.textContent = '🎤 Voix';
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
            showResponse(`📝 "${data.input_text}"\n\n🤖 ${data.response}`);
            speakText(data.response);
            loadEntities();
        } else {
            let message = 'Erreur transcription vocale';
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    message += `: ${errorData.detail}`;
                }
            } catch (_e) {
                // ignore non-JSON error response
            }
            showError(message);
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

async function loadOpenAIKeyInfo() {
    try {
        const response = await fetch('/api/openai-key');
        if (!response.ok) {
            return;
        }
        const data = await response.json();
        const statusElement = document.getElementById('openai-key-status');

        if (data.configured) {
            statusElement.textContent = `OpenAI configuré (${data.masked_key || 'clé masquée'})`;
            statusElement.classList.remove('empty');
        } else {
            statusElement.textContent = 'OpenAI non configuré';
            statusElement.classList.add('empty');
        }
    } catch (error) {
        console.error('Erreur chargement statut OpenAI:', error);
    }
}

async function saveOpenAIKey() {
    const keyInput = document.getElementById('openai-key-input');
    const key = keyInput.value.trim();

    if (!key) {
        showError('Veuillez saisir une clé OpenAI');
        return;
    }

    showLoading();

    try {
        const response = await fetch('/api/openai-key', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key })
        });

        if (response.ok) {
            const data = await response.json();
            showResponse('Clé OpenAI enregistrée');
            keyInput.value = '';
            loadOpenAIKeyInfo();
            init();
        } else {
            const errorData = await response.json();
            showError(errorData.detail || 'Erreur sauvegarde clé');
        }
    } catch (error) {
        showError(`Erreur: ${error.message}`);
    }
}

async function loadAudioDevices() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) {
        console.warn('enumerateDevices non supporté');
        return;
    }

    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        
        const micSelect = document.getElementById('mic-select');
        const speakerSelect = document.getElementById('speaker-select');
        
        if (!micSelect || !speakerSelect) return;

        // Nettoyer les options existantes
        micSelect.querySelectorAll('option:not(:first-child)').forEach(o => o.remove());
        speakerSelect.querySelectorAll('option:not(:first-child)').forEach(o => o.remove());

        devices.forEach(device => {
            const option = document.createElement('option');
            option.value = device.deviceId;
            option.textContent = device.label || `${device.kind} ${device.deviceId.substring(0, 5)}`;
            
            if (device.kind === 'audioinput') {
                micSelect.appendChild(option);
            } else if (device.kind === 'audiooutput') {
                speakerSelect.appendChild(option);
            }
        });

        console.log('Appareils audio chargés:', devices.length);
    } catch (error) {
        console.error('Erreur chargement appareils:', error);
    }
}

function toggleAudioSettings() {
    const settings = document.getElementById('audio-settings');
    if (settings) {
        if (settings.style.display === 'none') {
            settings.style.display = 'block';
            loadAudioDevices();
            
            // Mettre à jour les sélections si elles ont été enregistrées
            const micSelect = document.getElementById('mic-select');
            const speakerSelect = document.getElementById('speaker-select');
            if (micSelect && selectedMicDeviceId) {
                micSelect.value = selectedMicDeviceId;
            }
            if (speakerSelect && selectedSpeakerDeviceId) {
                speakerSelect.value = selectedSpeakerDeviceId;
            }
        } else {
            settings.style.display = 'none';
        }
    }
}

async function testAudio() {
    try {
        showResponse('🔊 Test audio en cours...');
        
        // Créer un son de test
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 440; // La
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.5);
        
        showResponse('✅ Son de test joué');
    } catch (error) {
        showError(`Erreur test audio: ${error.message}`);
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
            items.slice(0, 8).forEach(item => {
                const state = item.state || 'N/A';
                const name = item.attributes.friendly_name || item.entity_id;
                
                const html = `
                    <div class="entity-item" title="${name}">
                        <div>${name.substring(0, 15)}</div>
                        <div class="state">${state}</div>
                    </div>
                `;
                list.innerHTML += html;
            });
        }
    }
    
    if (hasEntities) {
        section.style.display = 'block';
    } else {
        section.style.display = 'none';
    }
}

function showLoading() {
    const element = document.getElementById('response-text');
    element.innerHTML = '⏳ Traitement...';
    element.classList.add('loading');
    element.classList.remove('empty');
}

function showResponse(text) {
    const element = document.getElementById('response-text');
    element.innerHTML = text.replace(/\n/g, '<br>');
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

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendText();
    }
}

async function listDevices() {
    showResponse('📋 Appareils audio disponibles\n(Vérifiez la console du navigateur)');
    
    const devices = await navigator.mediaDevices.enumerateDevices();
    const audioDevices = devices.filter(d => d.kind === 'audioinput');
    console.log('Appareils audio:', audioDevices);
}

// Initialisation au chargement
document.addEventListener('DOMContentLoaded', () => {
    init();
});
