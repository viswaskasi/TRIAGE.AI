const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatContainer = document.getElementById('chat-container');
const sendBtn = document.getElementById('send-btn');
const micBtn = document.getElementById('mic-btn');

// Generate or retrieve a unique session ID for memory tracking
let sessionId = localStorage.getItem('triage_session_id');
if (!sessionId) {
    sessionId = 'sess-' + Math.random().toString(36).substring(2, 15);
    localStorage.setItem('triage_session_id', sessionId);
}

// ── Voice Input (Web Speech API) ──────────────────────────────────────────────
let recognition = null;
let isRecording = false;

function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        showToast('Voice input is not supported in this browser. Try Chrome or Edge.', 'error');
        return null;
    }
    const rec = new SpeechRecognition();
    rec.lang = 'en-US';
    rec.interimResults = true;
    rec.maxAlternatives = 1;
    rec.continuous = false;

    rec.onstart = () => {
        isRecording = true;
        micBtn.classList.add('recording');
        micBtn.innerHTML = '<i class="fa-solid fa-circle-stop"></i>';
        userInput.placeholder = 'Listening...';
    };

    rec.onresult = (event) => {
        const transcript = Array.from(event.results)
            .map(r => r[0].transcript)
            .join('');
        userInput.value = transcript;
        // Auto-submit on final result
        if (event.results[0].isFinal) {
            stopRecording();
            if (transcript.trim()) {
                setTimeout(() => chatForm.requestSubmit(), 300);
            }
        }
    };

    rec.onerror = (event) => {
        stopRecording();
        if (event.error !== 'aborted') {
            showToast(`Voice error: ${event.error}`, 'error');
        }
    };

    rec.onend = () => stopRecording();

    return rec;
}

function startRecording() {
    recognition = initSpeechRecognition();
    if (!recognition) return;
    recognition.start();
}

function stopRecording() {
    isRecording = false;
    micBtn.classList.remove('recording');
    micBtn.innerHTML = '<i class="fa-solid fa-microphone"></i>';
    userInput.placeholder = 'Describe your issue...';
    if (recognition) {
        recognition.stop();
        recognition = null;
    }
}

micBtn.addEventListener('click', () => {
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
});

// ── Toast Notification ────────────────────────────────────────────────────────
function showToast(message, type = 'info') {
    const existing = document.getElementById('toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.id = 'toast';
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// ── Chat Messages ─────────────────────────────────────────────────────────────
function saveMessage(type, data) {
    const history = JSON.parse(localStorage.getItem('chat_history') || '[]');
    history.push({ type, data });
    localStorage.setItem('chat_history', JSON.stringify(history));
}

function loadHistory() {
    const history = JSON.parse(localStorage.getItem('chat_history') || '[]');
    history.forEach(item => {
        if (item.type === 'user') {
            appendUserMessage(item.data, false);
        } else {
            appendAIMessage(item.data, false);
        }
    });
}

function appendUserMessage(text, save = true) {
    const div = document.createElement('div');
    div.className = 'message user-message';
    div.innerHTML = `
        <div class="avatar"><i class="fa-solid fa-user"></i></div>
        <div class="bubble">${text}</div>
    `;
    chatContainer.appendChild(div);
    scrollToBottom();
    if (save) saveMessage('user', text);
}

function appendAIMessage(data, save = true) {
    const div = document.createElement('div');
    div.className = 'message ai-message';

    let riskClass = 'badge-risk-low';
    if (data.risk_level === 'MEDIUM') riskClass = 'badge-risk-medium';
    if (data.risk_level === 'HIGH') riskClass = 'badge-risk-high';

    let actionClass = data.action === 'RESPOND' ? 'badge-action-respond' : 'badge-action-escalate';
    let bubbleClass = data.action === 'ESCALATE' ? 'escalate-bubble' : '';
    
    let ticketBadge = data.ticket_id ? `<span class="badge" style="background: #eab308; color: #1e1e1e;"><i class="fa-solid fa-ticket"></i> ${data.ticket_id}</span>` : '';

    div.innerHTML = `
        <div class="avatar"><i class="fa-solid fa-brain"></i></div>
        <div class="bubble ${bubbleClass}">
            <div class="text-content">${data.response}</div>
            <div class="badge-container">
                <span class="badge badge-domain">${data.domain}</span>
                <span class="badge badge-type">${data.request_type}</span>
                <span class="badge ${riskClass}">${data.risk_level}</span>
                <span class="badge ${actionClass}">${data.action}</span>
                ${ticketBadge}
            </div>
        </div>
    `;
    chatContainer.appendChild(div);
    scrollToBottom();
    if (save) saveMessage('ai', data);
}

function appendLoading() {
    const div = document.createElement('div');
    div.className = 'message ai-message loading-message';
    div.id = 'loading-msg';
    div.innerHTML = `
        <div class="avatar"><i class="fa-solid fa-brain"></i></div>
        <div class="bubble">
            <div class="loading-dots">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    chatContainer.appendChild(div);
    scrollToBottom();
}

function removeLoading() {
    const loading = document.getElementById('loading-msg');
    if (loading) loading.remove();
}

function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Load history on startup
loadHistory();

// ── Form Submit ───────────────────────────────────────────────────────────────
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = userInput.value.trim();
    if (!text) return;

    appendUserMessage(text);
    userInput.value = '';
    appendLoading();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, session_id: sessionId })
        });
        const data = await response.json();
        removeLoading();
        appendAIMessage(data);
    } catch (err) {
        removeLoading();
        appendAIMessage({
            domain: "ERROR",
            request_type: "NETWORK_ERROR",
            risk_level: "HIGH",
            action: "ESCALATE",
            response: "Failed to connect to triage server."
        });
    }
});
