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
            showResponse(`📝 "${data.input_text}"\n\n🤖 ${data.response}`);
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

async function listDevices() {
    showResponse('📋 Appareils audio disponibles\n(Vérifiez la console du navigateur)');
    
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
