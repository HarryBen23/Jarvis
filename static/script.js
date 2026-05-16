let mediaRecorder;
let audioChunks = [];
let isRecording = false;

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
        
        // Charger les entités et le statut OpenAI
        loadEntities();
        loadOpenAIKeyInfo();
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
        
        const btn = document.getElementById('record-btn');
        btn.classList.add('recording');
        btn.textContent = '⏹️ Arrêter';
        
        showResponse('🎤 Enregistrement en cours...');
    } catch (error) {
        showError(`Erreur microphone: ${error.message}`);
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
