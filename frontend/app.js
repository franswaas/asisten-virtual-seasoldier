/**
 * ====================================================================
 * ASISTEN VIRTUAL SEASOLDIER — CLIENT APPLICATION LOGIC
 * Chatwoot Mobile App UX, Real-Time SSE Streaming, & Multi-Backend
 * ====================================================================
 */

// ============================================
// CONFIGURATION & STATE
// ============================================
const DEFAULT_LOCAL_BACKEND = 'http://localhost:4001';

function getBackendUrl() {
  // 1. Check URL query parameters (e.g. ?backend=https://xxxx.trycloudflare.com or ?api=...)
  try {
    const urlParams = new URLSearchParams(window.location.search);
    const paramBackend = urlParams.get('backend') || urlParams.get('api');
    if (paramBackend && paramBackend.trim()) {
      const cleanUrl = paramBackend.trim().replace(/\/+$/, '');
      localStorage.setItem('seasoldier_backend_url', cleanUrl);
      return cleanUrl;
    }
  } catch (e) {}

  // 2. Check localStorage saved custom backend
  const custom = localStorage.getItem('seasoldier_backend_url');
  if (custom !== null && custom !== undefined && custom.trim() !== '') {
    return custom.trim().replace(/\/+$/, '');
  }

  const h = window.location.hostname;
  // If running directly on localhost / 127.0.0.1
  if (h === 'localhost' || h === '127.0.0.1') {
    return `http://${h}:4001`;
  }

  // If running on Firebase Hosting (*.web.app or *.firebaseapp.com)
  if (h.includes('web.app') || h.includes('firebaseapp.com')) {
    return ''; // Relative /api endpoint
  }

  // Fallback
  return DEFAULT_LOCAL_BACKEND;
}

let BACKEND_URL = getBackendUrl();
let sessionId = localStorage.getItem('seasoldier_session_id') || null;
let isLoading = false;
let isRecording = false;
let autoSpeak = localStorage.getItem('seasoldier_auto_speak') === 'true';
let recognition = null;
let chatLog = [];

// ============================================
// DOM ELEMENTS
// ============================================
const chatViewport = document.getElementById('chatViewport');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const micBtn = document.getElementById('micBtn');
const voiceToggle = document.getElementById('voiceToggle');
const voiceIconOff = document.getElementById('voiceIconOff');
const voiceIconOn = document.getElementById('voiceIconOn');
const scrollFab = document.getElementById('scrollFab');
const connectionStatus = document.getElementById('connectionStatus');
const statusText = document.getElementById('statusText');
const toastContainer = document.getElementById('toastContainer');
const settingsModal = document.getElementById('settingsModal');
const customBackendUrlInput = document.getElementById('customBackendUrl');
const voiceWaveOverlay = document.getElementById('voiceWaveOverlay');
const welcomeTime = document.getElementById('welcomeTime');

// ============================================
// INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', () => {
  if (welcomeTime) {
    welcomeTime.textContent = getCurrentTimeString();
  }
  initVoiceToggleUI();
  initSpeechRecognition();
  initScrollListener();
  checkHealth();
  if (window.innerWidth > 768) {
    chatInput.focus();
  }
});

function getCurrentTimeString() {
  const d = new Date();
  return d.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' });
}

// ============================================
// HEALTH CHECK & CONNECTION
// ============================================
async function checkHealth() {
  updateConnectionStatus('checking', 'Connecting');

  let target = (BACKEND_URL || '').trim().replace(/\/+$/, '');

  // 1. Try existing target backend first
  if (target) {
    for (const url of [`${target}/health`, `${target}/api/health`]) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3500);
        const res = await fetch(url, { signal: controller.signal });
        clearTimeout(timeoutId);
        if (res.ok) {
          updateConnectionStatus('online', 'Online');
          return;
        }
      } catch (e) {}
    }
  }

  // 2. Dynamic Discovery: Fetch active_backend.json published by launcher
  try {
    const metaRes = await fetch(`/active_backend.json?_t=${Date.now()}`);
    if (metaRes.ok) {
      const meta = await metaRes.json();
      const discoveredUrl = (meta.backend_url || '').trim().replace(/\/+$/, '');
      if (discoveredUrl) {
        for (const url of [`${discoveredUrl}/health`, `${discoveredUrl}/api/health`]) {
          try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 4000);
            const res = await fetch(url, { signal: controller.signal });
            clearTimeout(timeoutId);
            if (res.ok) {
              BACKEND_URL = discoveredUrl;
              localStorage.setItem('seasoldier_backend_url', BACKEND_URL);
              updateConnectionStatus('online', 'Online');
              return;
            }
          } catch (e) {}
        }
      }
    }
  } catch (e) {}

  // 3. Try localhost:4001 if on laptop/local network
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 1500);
    const res = await fetch('http://localhost:4001/health', { signal: controller.signal });
    clearTimeout(timeoutId);
    if (res.ok) {
      BACKEND_URL = 'http://localhost:4001';
      localStorage.setItem('seasoldier_backend_url', BACKEND_URL);
      updateConnectionStatus('online', 'Online');
      return;
    }
  } catch (e) {}

  // 4. Try default relative endpoints
  for (const url of ['/api/health', '/health']) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);
      const res = await fetch(url, { signal: controller.signal });
      clearTimeout(timeoutId);
      if (res.ok) {
        updateConnectionStatus('online', 'Online');
        return;
      }
    } catch (e) {}
  }

  updateConnectionStatus('offline', 'Offline');
}

function updateConnectionStatus(type, label) {
  connectionStatus.className = `connection-status status-${type}`;
  statusText.textContent = label;
}

// ============================================
// TOAST NOTIFICATIONS
// ============================================
function showToast(message, type = 'info', duration = 3000) {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-10px)';
    toast.style.transition = 'all 0.25s ease';
    setTimeout(() => toast.remove(), 250);
  }, duration);
}

// ============================================
// MODAL & SETTINGS
// ============================================
function openSettingsModal() {
  customBackendUrlInput.value = localStorage.getItem('seasoldier_backend_url') || (BACKEND_URL || '');
  const statusBadge = document.getElementById('modalStatusBadge');
  const statusDetails = document.getElementById('modalStatusDetails');
  statusBadge.textContent = 'Status: ' + statusText.textContent;
  statusBadge.style.color = statusText.textContent.includes('Online') ? '#10b981' : '#a1a1aa';
  statusDetails.textContent = `Endpoint: ${BACKEND_URL || '(Firebase Cloud / Relative URL)'}`;
  settingsModal.classList.remove('hidden');
}

function closeSettingsModal() {
  settingsModal.classList.add('hidden');
}

function closeSettingsModalOnBackdrop(e) {
  if (e.target === settingsModal) {
    closeSettingsModal();
  }
}

function setPresetBackend(url) {
  customBackendUrlInput.value = url;
}

async function testBackendConnection() {
  const rawTarget = customBackendUrlInput.value.trim();
  const targetUrl = rawTarget.replace(/\/+$/, '');
  const testUrls = targetUrl ? [`${targetUrl}/health`, `${targetUrl}/api/health`] : ['/api/health', '/health'];
  const badge = document.getElementById('modalStatusBadge');
  const details = document.getElementById('modalStatusDetails');
  
  badge.textContent = 'Menguji...';
  badge.style.color = '#a1a1aa';
  details.textContent = `Menghubungi ${targetUrl || 'Firebase Cloud Endpoint'}...`;

  for (const url of testUrls) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 4000);
      const res = await fetch(url, { signal: controller.signal });
      clearTimeout(timeoutId);

      if (res.ok) {
        const data = await res.json();
        badge.textContent = '✓ Terhubung!';
        badge.style.color = '#10b981';
        details.textContent = `Layanan: ${data.service || 'Asisten Seasoldier'} | Status: OK`;
        showToast('Koneksi ke backend berhasil!', 'success');
        return;
      }
    } catch (e) {
      // try next
    }
  }

  badge.textContent = '✗ Tidak dapat terhubung';
  badge.style.color = '#ef4444';
  details.textContent = `Gagal menghubungi endpoint. Pastikan backend di laptop aktif dan URL benar.`;
}

function saveBackendSettings() {
  const newUrl = customBackendUrlInput.value.trim().replace(/\/+$/, '');
  if (newUrl) {
    localStorage.setItem('seasoldier_backend_url', newUrl);
  } else {
    localStorage.removeItem('seasoldier_backend_url');
  }
  BACKEND_URL = newUrl;
  closeSettingsModal();
  showToast('Pengaturan backend disimpan!', 'success');
  checkHealth();
}

// ============================================
// CHAT LOGIC & SSE STREAMING
// ============================================
function handleFormSubmit(e) {
  e.preventDefault();
  const text = chatInput.value.trim();
  if (!text || isLoading) return;
  sendMessage(text);
}

function handleTextareaKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    handleFormSubmit(e);
  }
}

function autoResizeTextarea(textarea) {
  textarea.style.height = 'auto';
  textarea.style.height = Math.min(textarea.scrollHeight, 130) + 'px';
}

function sendQuickQuestion(questionText) {
  if (isLoading) return;
  sendMessage(questionText);
}

async function sendMessage(questionText) {
  if (isLoading || !questionText) return;
  isLoading = true;
  sendBtn.disabled = true;

  const msgTime = getCurrentTimeString();

  // Add Chatwoot-style user message
  appendUserMessage(questionText, msgTime);
  chatInput.value = '';
  chatInput.style.height = 'auto';

  // Create assistant streaming placeholder item
  const assistantMessageId = 'msg-' + Date.now();
  const { messageItem, bubble, contentDiv, statusDiv } = createAssistantMessageItem(assistantMessageId, msgTime);
  chatMessages.appendChild(messageItem);
  scrollToBottom();

  const base = (BACKEND_URL || '').trim().replace(/\/+$/, '');
  const streamEndpoint = base ? `${base}/chat/stream` : '/api/chat/stream';
  const restEndpoint = base ? `${base}/chat` : '/api/chat';

  try {
    let response;
    let isStreamMode = true;

    try {
      response = await fetch(streamEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: questionText,
          session_id: sessionId,
        }),
      });

      if (!response.ok || !response.body) {
        throw new Error(`Stream not available (${response.status})`);
      }
    } catch (streamErr) {
      // Fallback to REST endpoint
      isStreamMode = false;
      statusDiv.innerHTML = `<span class="tool-status-pill">🔍 Menghubungi backend Seasoldier...</span>`;
      response = await fetch(restEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: questionText,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status} ${response.statusText}`);
      }
    }

    let buffer = '';
    let incomingText = '';
    let renderedLength = 0;
    let isStreamFinished = false;
    let typingTimer = null;

    contentDiv.classList.add('streaming-cursor');

    // Smooth typewriter tick function (optimized for mobile & desktop)
    function updateTypingAnimation() {
      if (renderedLength < incomingText.length) {
        const backlog = incomingText.length - renderedLength;
        const step = backlog > 150 ? 8 : backlog > 60 ? 4 : backlog > 20 ? 2 : 1;
        renderedLength = Math.min(renderedLength + step, incomingText.length);
        const currentSlice = incomingText.slice(0, renderedLength);
        renderAssistantMarkdown(contentDiv, currentSlice);
        smoothScrollIfNeeded();
      }

      if (renderedLength < incomingText.length || !isStreamFinished) {
        typingTimer = setTimeout(updateTypingAnimation, 24);
      } else {
        // Finished typing all incoming text
        contentDiv.classList.remove('streaming-cursor');
        statusDiv.innerHTML = '';
        
        if (!incomingText.trim()) {
          incomingText = '⚠️ *Maaf, server sedang memproses antrean pertanyaan. Silakan kirim ulang pesan Anda.*';
        }
        renderAssistantMarkdown(contentDiv, incomingText);
        smoothScrollIfNeeded();

        // Save to export log
        chatLog.push({ role: 'User', content: questionText });
        chatLog.push({ role: 'Asisten Virtual Seasoldier', content: incomingText });

        // Append Chatwoot-style action toolbar
        appendMessageToolbar(bubble, assistantMessageId, incomingText);

        // Text to speech if enabled
        if (autoSpeak && incomingText) {
          speakText(cleanMarkdownForSpeech(incomingText));
        }
      }
    }

    // Start typewriter loop
    typingTimer = setTimeout(updateTypingAnimation, 25);

    if (isStreamMode) {
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.type === 'token') {
                if (statusDiv.innerHTML) statusDiv.innerHTML = '';
                incomingText += data.content;
              } else if (data.type === 'tool_start') {
                statusDiv.innerHTML = `<span class="tool-status-pill">🔍 Mengakses basis data Seasoldier...</span>`;
              } else if (data.type === 'done') {
                if (data.session_id) {
                  sessionId = data.session_id;
                  localStorage.setItem('seasoldier_session_id', sessionId);
                }
              } else if (data.type === 'error') {
                statusDiv.innerHTML = '';
                incomingText += `\n\n*${data.message || 'Terjadi kendala saat memproses jawaban.'}*`;
              }
            } catch (jsonErr) {
              // Ignore partial SSE lines
            }
          }
        }
      }
      isStreamFinished = true;
    } else {
      // REST Response
      const restData = await response.json();
      if (restData.session_id) {
        sessionId = restData.session_id;
        localStorage.setItem('seasoldier_session_id', sessionId);
      }
      incomingText = restData.answer || restData.error || 'Tidak ada jawaban dari server.';
      isStreamFinished = true;
    }

  } catch (err) {
    console.error('Chat error:', err);
    contentDiv.classList.remove('streaming-cursor');
    statusDiv.innerHTML = '';
    contentDiv.innerHTML = `
      <p>⚠️ <strong>Gagal mendapatkan respon dari server backend.</strong></p>
      <p style="font-size:0.78rem; color:var(--text-muted); margin-top:4px;">Server backend di <code>${BACKEND_URL || 'localhost:4001'}</code> sedang offline atau URL tunnel telah berganti.</p>
      <div style="margin-top:10px; display:flex; flex-wrap:wrap; gap:8px; align-items:center;">
        <button class="action-btn" onclick="openSettingsModal()" style="font-size:0.78rem; padding:4px 10px; border-radius:6px; background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.15); color:var(--text-main); cursor:pointer;">⚙️ Buka Pengaturan Server</button>
        <span style="font-size:0.75rem; color:var(--text-muted);">atau buka link dari terminal <code>start_public_server.bat</code></span>
      </div>
    `;
    showToast('Koneksi terputus ke server backend.', 'error');
  } finally {
    isLoading = false;
    sendBtn.disabled = false;
    smoothScrollIfNeeded();
  }
}

let isUserInteracting = false;
let userScrollTimeout = null;

function initScrollListeners() {
  if (typeof chatViewport !== 'undefined' && chatViewport) {
    chatViewport.addEventListener('touchstart', () => { isUserInteracting = true; }, { passive: true });
    chatViewport.addEventListener('touchend', () => {
      clearTimeout(userScrollTimeout);
      userScrollTimeout = setTimeout(() => { isUserInteracting = false; }, 1000);
    }, { passive: true });
    chatViewport.addEventListener('wheel', () => {
      isUserInteracting = true;
      clearTimeout(userScrollTimeout);
      userScrollTimeout = setTimeout(() => { isUserInteracting = false; }, 1000);
    }, { passive: true });
  }
}
initScrollListeners();

function smoothScrollIfNeeded() {
  if (isUserInteracting) return;
  const threshold = 160;
  const isNearBottom = chatViewport.scrollHeight - chatViewport.scrollTop - chatViewport.clientHeight < threshold;
  if (isNearBottom) {
    chatViewport.scrollTop = chatViewport.scrollHeight;
  }
}

// ============================================
// CHATWOOT MESSAGE RENDERING
// ============================================
function appendUserMessage(text, timeStr) {
  const item = document.createElement('div');
  item.className = 'message-item user-message-item';
  item.innerHTML = `
    <div class="message-meta-header" style="justify-content: flex-end;">
      <div class="sender-info">
        <span class="sender-name">Anda</span>
      </div>
      <span class="message-time" style="margin-left: 8px;">${timeStr}</span>
    </div>
    <div class="bubble-container user-bubble-container">
      <div class="message-bubble user-bubble">
        <div>${escapeHtml(text)}</div>
        <div class="user-meta-footer">
          <span>${timeStr}</span>
          <span class="delivery-checks">✓✓</span>
        </div>
      </div>
    </div>
  `;
  chatMessages.appendChild(item);
}

function createAssistantMessageItem(msgId, timeStr) {
  const item = document.createElement('div');
  item.className = 'message-item assistant-message-item';
  item.id = msgId;

  item.innerHTML = `
    <div class="message-meta-header">
      <div class="sender-info">
        <span class="sender-name">Asisten Seasoldier</span>
        <span class="role-badge">Official Assistant</span>
      </div>
      <span class="message-time">${timeStr}</span>
    </div>
  `;

  const bubbleContainer = document.createElement('div');
  bubbleContainer.className = 'bubble-container assistant-bubble-container';

  const bubble = document.createElement('div');
  bubble.className = 'message-bubble assistant-bubble';

  const statusDiv = document.createElement('div');
  const contentDiv = document.createElement('div');
  contentDiv.className = 'assistant-markdown-content';
  contentDiv.innerHTML = `
    <div class="typing-dots-wrap">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>
  `;

  bubble.appendChild(statusDiv);
  bubble.appendChild(contentDiv);
  bubbleContainer.appendChild(bubble);
  item.appendChild(bubbleContainer);

  return { messageItem: item, bubble, contentDiv, statusDiv };
}

function renderAssistantMarkdown(container, rawMarkdown) {
  if (typeof marked !== 'undefined' && marked.parse) {
    marked.setOptions({
      breaks: true,
      gfm: true,
    });
    container.innerHTML = marked.parse(rawMarkdown);
  } else {
    container.textContent = rawMarkdown;
  }
}

function appendMessageToolbar(bubble, messageId, fullText) {
  const toolbar = document.createElement('div');
  toolbar.className = 'message-actions-toolbar';
  toolbar.innerHTML = `
    <div class="toolbar-left">
      <button class="action-chip-btn" onclick="copyMessageText(this, ${JSON.stringify(fullText)})" title="Salin Teks">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
        </svg>
        <span>Salin</span>
      </button>
      <button class="action-chip-btn" onclick="speakText(${JSON.stringify(cleanMarkdownForSpeech(fullText))})" title="Dengarkan Suara">
        🔊 Baca
      </button>
    </div>
    <div class="toolbar-right">
      <button class="action-chip-btn" onclick="sendFeedback('${messageId}', 'up', this)" title="Membantu">
        👍
      </button>
      <button class="action-chip-btn" onclick="sendFeedback('${messageId}', 'down', this)" title="Kurang Sesuai">
        👎
      </button>
    </div>
  `;
  bubble.appendChild(toolbar);
}

// ============================================
// COPY & FEEDBACK
// ============================================
async function copyMessageText(buttonElement, text) {
  try {
    await navigator.clipboard.writeText(text);
    const span = buttonElement.querySelector('span');
    const prev = span.textContent;
    span.textContent = 'Tersalin!';
    buttonElement.classList.add('active');
    setTimeout(() => {
      span.textContent = prev;
      buttonElement.classList.remove('active');
    }, 1800);
    showToast('Teks berhasil disalin!', 'success');
  } catch (err) {
    showToast('Gagal menyalin teks.', 'error');
  }
}

async function sendFeedback(messageId, rating, btn) {
  btn.classList.add('active');
  const endpoint = BACKEND_URL ? `${BACKEND_URL}/feedback` : '/feedback';
  try {
    await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId || 'anonymous',
        message_id: messageId,
        rating: rating,
      }),
    });
    showToast(rating === 'up' ? 'Terima kasih atas jempolnya! 🌿' : 'Terima kasih atas masukannya. 🌿');
  } catch (e) {
    // ignore
  }
}

// ============================================
// SPEECH RECOGNITION (STT) & SYNTHESIS (TTS)
// ============================================
function initVoiceToggleUI() {
  if (autoSpeak) {
    voiceIconOff.classList.add('hidden');
    voiceIconOn.classList.remove('hidden');
    voiceToggle.style.color = '#ffffff';
  } else {
    voiceIconOff.classList.remove('hidden');
    voiceIconOn.classList.add('hidden');
    voiceToggle.style.color = 'var(--text-secondary)';
  }
}

function toggleAutoSpeak() {
  autoSpeak = !autoSpeak;
  localStorage.setItem('seasoldier_auto_speak', autoSpeak);
  initVoiceToggleUI();
  showToast(autoSpeak ? 'Auto-speak Suara aktif 🔊' : 'Auto-speak dinonaktifkan 🔇');
}

function initSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    micBtn.style.display = 'none';
    return;
  }

  recognition = new SpeechRecognition();
  recognition.lang = 'id-ID';
  recognition.continuous = false;
  recognition.interimResults = false;

  recognition.onstart = () => {
    isRecording = true;
    micBtn.classList.add('recording');
    if (voiceWaveOverlay) voiceWaveOverlay.classList.remove('hidden');
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    if (transcript) {
      chatInput.value = transcript;
      autoResizeTextarea(chatInput);
      sendMessage(transcript);
    }
  };

  recognition.onerror = (event) => {
    console.warn('Speech error:', event.error);
    isRecording = false;
    micBtn.classList.remove('recording');
    if (voiceWaveOverlay) voiceWaveOverlay.classList.add('hidden');
    if (event.error !== 'no-speech') {
      showToast('Gagal mengenali suara: ' + event.error, 'error');
    }
  };

  recognition.onend = () => {
    isRecording = false;
    micBtn.classList.remove('recording');
    if (voiceWaveOverlay) voiceWaveOverlay.classList.add('hidden');
  };
}

function toggleVoiceInput() {
  if (!recognition) {
    showToast('Browser Anda tidak mendukung input suara.', 'error');
    return;
  }

  if (isRecording) {
    recognition.stop();
  } else {
    try {
      recognition.start();
    } catch (e) {}
  }
}

function speakText(text) {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'id-ID';
  utterance.rate = 1.05;
  utterance.pitch = 1.0;

  const voices = window.speechSynthesis.getVoices();
  const idVoice = voices.find(v => v.lang.includes('id') || v.lang.includes('ID'));
  if (idVoice) utterance.voice = idVoice;

  window.speechSynthesis.speak(utterance);
}

function cleanMarkdownForSpeech(md) {
  return md
    .replace(/[#*_`~\[\]\(\)]/g, '')
    .replace(/💡 Pertanyaan terkait:[\s\S]*/, '')
    .replace(/🌿 \*Sumber:[\s\S]*/, '')
    .trim();
}

// ============================================
// EXPORT & CLEAR CHAT
// ============================================
function exportChat() {
  if (chatLog.length === 0) {
    showToast('Belum ada percakapan untuk diekspor.', 'info');
    return;
  }

  let text = '=== RIWAYAT CHAT ASISTEN VIRTUAL SEASOLDIER ===\n';
  text += `Waktu Ekspor: ${new Date().toLocaleString('id-ID')}\n\n`;

  for (const item of chatLog) {
    text += `[${item.role.toUpperCase()}]\n${item.content}\n\n----------------------------------------\n\n`;
  }

  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `Seasoldier-Chat-${Date.now()}.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast('Riwayat percakapan berhasil diunduh!', 'success');
}

async function clearChat() {
  if (!confirm('Hapus seluruh riwayat percakapan sesi ini?')) return;

  if (sessionId) {
    const endpoint = BACKEND_URL ? `${BACKEND_URL}/session/${sessionId}` : `/session/${sessionId}`;
    try {
      await fetch(endpoint, { method: 'DELETE' });
    } catch (e) {}
  }

  sessionId = null;
  localStorage.removeItem('seasoldier_session_id');
  chatLog = [];

  const welcomeItem = document.querySelector('.welcome-message-item');
  const dateSep = document.querySelector('.date-separator');
  chatMessages.innerHTML = '';
  if (dateSep) chatMessages.appendChild(dateSep);
  if (welcomeItem) chatMessages.appendChild(welcomeItem);

  showToast('Riwayat percakapan telah dibersihkan.', 'info');
}

// ============================================
// SCROLL LISTENER & FAB
// ============================================
function initScrollListener() {
  chatViewport.addEventListener('scroll', () => {
    const diff = chatViewport.scrollHeight - chatViewport.scrollTop - chatViewport.clientHeight;
    if (diff > 160) {
      scrollFab.classList.add('visible');
    } else {
      scrollFab.classList.remove('visible');
    }
  });
}

function scrollToBottom() {
  chatViewport.scrollTop = chatViewport.scrollHeight;
}

// ============================================
// UTILS & MOBILE KEYBOARD RESIZE
// ============================================
if (window.visualViewport) {
  window.visualViewport.addEventListener('resize', () => {
    const appLayout = document.querySelector('.app-layout');
    if (appLayout) {
      appLayout.style.height = `${window.visualViewport.height}px`;
    }
    setTimeout(scrollToBottom, 60);
  });
}

function escapeHtml(string) {
  const entityMap = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  };
  return String(string).replace(/[&<>"']/g, (s) => entityMap[s]);
}
