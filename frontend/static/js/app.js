/* =====================================================
   MedPredict — Main JavaScript
   Handles: Auth, Routing, All Feature Interactions
   ===================================================== */

const API = '';   // same origin

// ─── Auth Helpers ─────────────────────────────────────────
const Auth = {
  token: () => localStorage.getItem('mp_token'),
  user:  () => localStorage.getItem('mp_user'),
  save:  (token, username) => {
    localStorage.setItem('mp_token', token);
    localStorage.setItem('mp_user', username);
  },
  clear: () => {
    localStorage.removeItem('mp_token');
    localStorage.removeItem('mp_user');
  },
  headers: () => ({
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${Auth.token()}`
  }),
  guard: () => {
    if (!Auth.token()) {
      window.location.href = '/login.html';
      return false;
    }
    return true;
  }
};

// ─── Fetch Wrapper ─────────────────────────────────────────
async function apiFetch(path, options = {}) {
  const res = await fetch(API + path, {
    headers: Auth.headers(),
    ...options
  });
  if (res.status === 401) { Auth.clear(); window.location.href = '/login.html'; }
  return res;
}

// ─── UI Helpers ────────────────────────────────────────────
function showAlert(container, type, msg) {
  const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
  container.innerHTML = `
    <div class="alert alert-${type}">
      <span>${icons[type] || ''}</span>
      <span>${msg}</span>
    </div>`;
  container.classList.remove('hidden');
}

function setLoading(btn, loading) {
  if (loading) {
    btn.dataset.orig = btn.innerHTML;
    btn.innerHTML = `<span class="spinner"></span> Please wait…`;
    btn.disabled = true;
  } else {
    btn.innerHTML = btn.dataset.orig || btn.innerHTML;
    btn.disabled = false;
  }
}

function animateGauge(svgFill, percent) {
  const circumference = 408;
  const offset = circumference - (percent / 100) * circumference;
  setTimeout(() => { svgFill.style.strokeDashoffset = offset; }, 100);
}

function animateProgress(bar, percent) {
  setTimeout(() => { bar.style.width = percent + '%'; }, 100);
}

// ─── Populate Sidebar User Info ─────────────────────────────
function populateSidebarUser() {
  const name = Auth.user() || 'User';
  document.querySelectorAll('.sidebar-username').forEach(el => el.textContent = name);
  document.querySelectorAll('.user-avatar').forEach(el => {
    if (!el.dataset.noInit) el.textContent = name.charAt(0).toUpperCase();
  });
}

function markActiveNav() {
  const path = window.location.pathname.replace(/^\//, '') || 'dashboard.html';
  document.querySelectorAll('.nav-item').forEach(el => {
    el.classList.toggle('active', el.dataset.page === path);
  });
}

// ═══════════════════════════════════════════════════════════
// PAGE: Login / Register
// ═══════════════════════════════════════════════════════════
function initAuthPage() {
  const loginTab   = document.getElementById('loginTab');
  const registerTab= document.getElementById('registerTab');
  const loginForm  = document.getElementById('loginFormEl');
  const regForm    = document.getElementById('registerFormEl');
  const alertBox   = document.getElementById('authAlert');

  if (!loginTab) return;

  if (Auth.token()) { window.location.href = '/dashboard.html'; return; }

  loginTab.addEventListener('click', () => {
    loginTab.classList.add('active');
    registerTab.classList.remove('active');
    loginForm.classList.remove('hidden');
    regForm.classList.add('hidden');
    alertBox.innerHTML = '';
  });
  registerTab.addEventListener('click', () => {
    registerTab.classList.add('active');
    loginTab.classList.remove('active');
    regForm.classList.remove('hidden');
    loginForm.classList.add('hidden');
    alertBox.innerHTML = '';
  });

  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = loginForm.querySelector('button[type="submit"]');
    setLoading(btn, true);
    const data = Object.fromEntries(new FormData(loginForm));
    try {
      const res = await fetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.detail || 'Login failed');
      Auth.save(json.access_token, data.username);
      window.location.href = '/dashboard.html';
    } catch (err) {
      showAlert(alertBox, 'error', err.message);
    } finally { setLoading(btn, false); }
  });

  regForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = regForm.querySelector('button[type="submit"]');
    setLoading(btn, true);
    const data = Object.fromEntries(new FormData(regForm));
    try {
      const res = await fetch('/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.detail || 'Registration failed');
      showAlert(alertBox, 'success', 'Account created! Please log in.');
      loginTab.click();
    } catch (err) {
      showAlert(alertBox, 'error', err.message);
    } finally { setLoading(btn, false); }
  });
}

// ═══════════════════════════════════════════════════════════
// PAGE: Dashboard
// ═══════════════════════════════════════════════════════════
function initDashboard() {
  if (!document.getElementById('dashboardPage')) return;
  if (!Auth.guard()) return;
  populateSidebarUser();
  markActiveNav();

  // Animate stat counters
  document.querySelectorAll('[data-count]').forEach(el => {
    const target = parseFloat(el.dataset.count);
    let current = 0;
    const step = target / 40;
    const timer = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = Number.isInteger(target) ? Math.round(current) : current.toFixed(1);
      if (current >= target) clearInterval(timer);
    }, 30);
  });
}

// ═══════════════════════════════════════════════════════════
// PAGE: Disease Prediction
// ═══════════════════════════════════════════════════════════
function initDiseasePrediction() {
  const form = document.getElementById('predictForm');
  const resultSection = document.getElementById('predictResult');
  if (!form) return;
  if (!Auth.guard()) return;
  populateSidebarUser();
  markActiveNav();

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    setLoading(btn, true);
    const raw = Object.fromEntries(new FormData(form));
    const features = {};
    for (const [k, v] of Object.entries(raw)) features[k] = parseFloat(v) || 0;

    try {
      const res = await apiFetch('/predict/tabular', {
        method: 'POST',
        body: JSON.stringify({ features })
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.detail || 'Prediction failed');
      displayTabularResult(json, resultSection);
    } catch (err) {
      resultSection.innerHTML = `<div class="alert alert-error">❌ ${err.message}</div>`;
      resultSection.classList.remove('hidden');
    } finally { setLoading(btn, false); }
  });
}

function displayTabularResult(data, container) {
  const { disease, probability, confidence, explanation } = data;
  const prob = Math.round(probability * 100);
  const isPositive = disease !== 'no_disease_detected';
  const diseaseLabel = isPositive
    ? disease.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    : 'No Disease Detected';
  const badgeClass = isPositive ? 'badge-red' : 'badge-green';
  const explanationHtml = (explanation || []).map(e =>
    `<div class="explanation-item">${e}</div>`
  ).join('');

  container.innerHTML = `
    <div class="result-box animate-fade">
      <div class="flex items-center justify-between mb-3">
        <h3>Prediction Result</h3>
        <span class="badge ${badgeClass}">${isPositive ? '⚠️ Risk Detected' : '✅ Healthy'}</span>
      </div>
      <div class="flex gap-3 items-center mb-4" style="flex-wrap:wrap;">
        <div class="gauge-wrap">
          <div class="gauge-circle">
            <svg width="160" height="160" viewBox="0 0 160 160">
              <defs>
                <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="${isPositive ? '#ef4444' : '#10b981'}"/>
                  <stop offset="100%" stop-color="${isPositive ? '#f59e0b' : '#00e5ff'}"/>
                </linearGradient>
              </defs>
              <circle class="gauge-bg" cx="80" cy="80" r="65"/>
              <circle class="gauge-fill" id="gaugeFill" cx="80" cy="80" r="65"/>
            </svg>
            <div class="gauge-text">
              <span class="gauge-percent" style="color:${isPositive ? 'var(--accent-red)' : 'var(--accent-green)'}">${prob}%</span>
              <span class="gauge-label">Probability</span>
            </div>
          </div>
        </div>
        <div style="flex:1; min-width:200px;">
          <p class="text-sm text-muted mb-1">Detected Condition</p>
          <h2 style="margin-bottom:0.5rem;">${diseaseLabel}</h2>
          <p class="text-sm text-muted mb-1">Confidence</p>
          <div class="progress-bar-wrap mb-2">
            <div class="progress-bar-fill" id="confBar" style="width:0%"></div>
          </div>
          <p class="text-sm text-cyan font-semibold">${confidence}% confidence</p>
        </div>
      </div>
      ${explanationHtml ? `<h4 class="mb-2">Key Influencing Factors</h4>${explanationHtml}` : ''}
      <p class="text-xs text-muted mt-3">⚕️ This is an AI-assisted prediction. Always consult a qualified medical professional for diagnosis.</p>
    </div>`;
  container.classList.remove('hidden');
  animateGauge(document.getElementById('gaugeFill'), prob);
  animateProgress(document.getElementById('confBar'), confidence);
}

// ═══════════════════════════════════════════════════════════
// PAGE: Image Prediction
// ═══════════════════════════════════════════════════════════
function initImagePrediction() {
  const form = document.getElementById('imageForm');
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('imageFile');
  const preview = document.getElementById('imagePreview');
  const resultSection = document.getElementById('imgResult');
  if (!form) return;
  if (!Auth.guard()) return;
  populateSidebarUser();
  markActiveNav();

  // Drag & drop
  dropZone.addEventListener('click', () => fileInput.click());
  dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
  dropZone.addEventListener('drop', e => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    if (e.dataTransfer.files[0]) { fileInput.files = e.dataTransfer.files; showPreview(e.dataTransfer.files[0]); }
  });
  fileInput.addEventListener('change', () => { if (fileInput.files[0]) showPreview(fileInput.files[0]); });

  function showPreview(file) {
    const reader = new FileReader();
    reader.onload = ev => {
      preview.innerHTML = `<img src="${ev.target.result}" alt="Preview" style="max-width:100%;max-height:250px;border-radius:var(--radius-md);margin-top:1rem;border:1px solid var(--border);">`;
    };
    reader.readAsDataURL(file);
    dropZone.querySelector('.drop-label').textContent = `📎 ${file.name}`;
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!fileInput.files[0]) {
      showAlert(resultSection, 'error', 'Please select an image file first.');
      resultSection.classList.remove('hidden');
      return;
    }
    const btn = form.querySelector('button[type="submit"]');
    setLoading(btn, true);

    const fd = new FormData();
    fd.append('file', fileInput.files[0]);
    try {
      const res = await fetch('/predict/image', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${Auth.token()}` },
        body: fd
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.detail || 'Image prediction failed');
      displayImageResult(json, resultSection);
    } catch (err) {
      showAlert(resultSection, 'error', err.message);
      resultSection.classList.remove('hidden');
    } finally { setLoading(btn, false); }
  });
}

function displayImageResult(data, container) {
  const { disease, probability, confidence } = data;
  const prob = Math.round(probability * 100);
  const label = disease.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  container.innerHTML = `
    <div class="result-box animate-fade">
      <div class="flex items-center justify-between mb-3">
        <h3>Image Analysis Result</h3>
        <span class="badge badge-orange">🔬 AI Diagnosis</span>
      </div>
      <h2 style="color:var(--accent-orange); margin-bottom:0.5rem;">${label}</h2>
      <p class="text-sm text-muted mb-2">Detection probability: <strong class="text-cyan">${prob}%</strong></p>
      <div class="progress-bar-wrap mb-3">
        <div class="progress-bar-fill" id="imgBar" style="width:0%;background:linear-gradient(90deg,var(--accent-orange),var(--accent-red))"></div>
      </div>
      <p class="text-xs text-muted">⚕️ AI image analysis. For clinical use, always verify with a radiologist.</p>
    </div>`;
  container.classList.remove('hidden');
  animateProgress(document.getElementById('imgBar'), confidence);
}

// ═══════════════════════════════════════════════════════════
// PAGE: Chatbot
// ═══════════════════════════════════════════════════════════
function initChatbot() {
  const chatMessages = document.getElementById('chatMessages');
  const chatInput    = document.getElementById('chatInput');
  const sendBtn      = document.getElementById('sendBtn');
  if (!chatMessages) return;
  if (!Auth.guard()) return;
  populateSidebarUser();
  markActiveNav();

  async function sendMessage() {
    const query = chatInput.value.trim();
    if (!query) return;
    chatInput.value = '';

    appendBubble(chatMessages, 'user', query);
    const typingEl = appendTyping(chatMessages);

    try {
      const res = await apiFetch('/ai/chatbot', {
        method: 'POST',
        body: JSON.stringify({ query })
      });
      const json = await res.json();
      typingEl.remove();
      appendBubble(chatMessages, 'bot', json.reply || 'Sorry, I could not understand that.');
    } catch {
      typingEl.remove();
      appendBubble(chatMessages, 'bot', 'Connection error. Please try again.');
    }
  }

  sendBtn.addEventListener('click', sendMessage);
  chatInput.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } });
}

function appendBubble(container, type, text) {
  const el = document.createElement('div');
  el.className = `chat-bubble ${type}`;
  el.textContent = text;
  container.appendChild(el);
  container.scrollTop = container.scrollHeight;
  return el;
}

function appendTyping(container) {
  const el = document.createElement('div');
  el.className = 'chat-bubble bot typing';
  el.innerHTML = `<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>`;
  container.appendChild(el);
  container.scrollTop = container.scrollHeight;
  return el;
}

// ═══════════════════════════════════════════════════════════
// PAGE: Health Tips (Health Score)
// ═══════════════════════════════════════════════════════════
function initHealthTips() {
  const form = document.getElementById('healthScoreForm');
  const resultSection = document.getElementById('healthResult');
  if (!form) return;
  if (!Auth.guard()) return;
  populateSidebarUser();
  markActiveNav();

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    setLoading(btn, true);
    const raw = Object.fromEntries(new FormData(form));
    const features = {};
    for (const [k, v] of Object.entries(raw)) features[k] = parseFloat(v) || 0;

    try {
      const res = await apiFetch('/ai/health-score', {
        method: 'POST',
        body: JSON.stringify({ features })
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.detail || 'Failed');
      displayHealthScore(json, resultSection);
    } catch (err) {
      showAlert(resultSection, 'error', err.message);
      resultSection.classList.remove('hidden');
    } finally { setLoading(btn, false); }
  });
}

function displayHealthScore(data, container) {
  const { health_score, recommendations } = data;
  const score = Math.round(health_score);
  const color = score >= 80 ? 'var(--accent-green)' : score >= 50 ? 'var(--accent-orange)' : 'var(--accent-red)';
  const label = score >= 80 ? 'Excellent' : score >= 50 ? 'Moderate' : 'Low';
  const recsHtml = (recommendations || []).map(r =>
    `<div class="explanation-item">💡 ${r}</div>`
  ).join('');

  container.innerHTML = `
    <div class="result-box animate-fade">
      <div class="flex items-center gap-3 mb-4" style="flex-wrap:wrap;">
        <div class="gauge-wrap">
          <div class="gauge-circle">
            <svg width="160" height="160" viewBox="0 0 160 160">
              <defs>
                <linearGradient id="healthGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="${color}"/>
                  <stop offset="100%" stop-color="${color}88"/>
                </linearGradient>
              </defs>
              <circle class="gauge-bg" cx="80" cy="80" r="65"/>
              <circle class="gauge-fill" id="healthGaugeFill" cx="80" cy="80" r="65" style="stroke:url(#healthGrad)"/>
            </svg>
            <div class="gauge-text">
              <span class="gauge-percent" style="color:${color}">${score}</span>
              <span class="gauge-label">/ 100</span>
            </div>
          </div>
        </div>
        <div>
          <p class="text-muted text-sm mb-1">Health Status</p>
          <h2 style="color:${color}; margin-bottom:0.5rem;">${label}</h2>
          <p class="text-muted text-sm">Your health score is <strong style="color:${color}">${score}/100</strong></p>
        </div>
      </div>
      ${recsHtml ? `<h4 class="mb-2">Lifestyle Recommendations</h4>${recsHtml}` : ''}
    </div>`;
  container.classList.remove('hidden');
  animateGauge(document.getElementById('healthGaugeFill'), score);
}

// ═══════════════════════════════════════════════════════════
// PAGE: Doctor Recommendation
// ═══════════════════════════════════════════════════════════
function initDoctorRecommendation() {
  const form = document.getElementById('doctorForm');
  const resultSection = document.getElementById('doctorResult');
  if (!form) return;
  if (!Auth.guard()) return;
  populateSidebarUser();
  markActiveNav();

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    setLoading(btn, true);
    const symptomsText = document.getElementById('symptomsInput').value;
    const symptoms = symptomsText.split(',').map(s => s.trim()).filter(Boolean);

    try {
      const res = await apiFetch('/ai/doctor-recommend', {
        method: 'POST',
        body: JSON.stringify({ symptoms })
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.detail || 'Failed');
      displaySpecialists(json.specialists, resultSection);
    } catch (err) {
      showAlert(resultSection, 'error', err.message);
      resultSection.classList.remove('hidden');
    } finally { setLoading(btn, false); }
  });
}

const SPECIALIST_ICONS = {
  'Pulmonologist': '🫁', 'Cardiologist': '❤️', 'Dermatologist': '🩺',
  'General Physician': '👨‍⚕️', 'Neurologist': '🧠', 'Orthopedist': '🦴',
  'Gastroenterologist': '🔬', 'Endocrinologist': '⚗️'
};

function displaySpecialists(specialists, container) {
  const cardsHtml = specialists.map(s => {
    // Handle both string format and object format {specialist, description, priority}
    const name = typeof s === 'string' ? s : s.specialist;
    const desc = typeof s === 'string' ? '' : (s.description || '');
    return `
    <div class="specialist-card animate-fade">
      <div class="specialist-icon">${SPECIALIST_ICONS[name] || '🏥'}</div>
      <div class="specialist-name">${name}</div>
      ${desc ? `<p class="text-xs text-muted mt-1" style="font-size:0.75rem;">${desc}</p>` : '<p class="text-xs text-muted mt-1">Recommended</p>'}
    </div>`;
  }).join('');

  container.innerHTML = `
    <div class="result-box animate-fade">
      <h3 class="mb-3">Recommended Specialists</h3>
      <div class="specialist-grid">${cardsHtml}</div>
      <p class="text-xs text-muted mt-3">⚕️ These are AI-based suggestions. Please seek professional medical advice.</p>
    </div>`;
  container.classList.remove('hidden');
}

// ═══════════════════════════════════════════════════════════
// PAGE: Analytics (Risk Calculator)
// ═══════════════════════════════════════════════════════════
function initAnalytics() {
  const form = document.getElementById('riskForm');
  const resultSection = document.getElementById('riskResult');
  if (!form) return;
  if (!Auth.guard()) return;
  populateSidebarUser();
  markActiveNav();

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    setLoading(btn, true);
    const raw = Object.fromEntries(new FormData(form));
    const features = {};
    for (const [k, v] of Object.entries(raw)) features[k] = parseFloat(v) || 0;

    try {
      const res = await apiFetch('/ai/risk', {
        method: 'POST',
        body: JSON.stringify({ features })
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.detail || 'Failed');
      displayRisk(json, resultSection);
    } catch (err) {
      showAlert(resultSection, 'error', err.message);
      resultSection.classList.remove('hidden');
    } finally { setLoading(btn, false); }
  });
}

function displayRisk(data, container) {
  const { risk_score, risk_level } = data;
  const normalized = Math.min(100, Math.max(0, risk_score));
  const color = risk_level === 'low' ? 'var(--accent-green)' : risk_level === 'high' ? 'var(--accent-red)' : 'var(--accent-orange)';
  const emoji = risk_level === 'low' ? '🟢' : risk_level === 'high' ? '🔴' : '🟡';

  container.innerHTML = `
    <div class="result-box animate-fade">
      <h3 class="mb-3">Risk Assessment</h3>
      <div class="flex items-center gap-2 mb-3">
        <span style="font-size:1.5rem;">${emoji}</span>
        <h2 style="color:${color}; text-transform:capitalize;">${risk_level} Risk</h2>
      </div>
      <p class="text-sm text-muted mb-3">Computed risk score: <strong style="color:${color}">${Math.round(risk_score)}</strong></p>
      <div class="risk-meter" style="margin-bottom:2.5rem;">
        <div class="risk-indicator" id="riskIndicator" style="left:0%"></div>
      </div>
      <p class="text-xs text-muted">⚕️ Risk scores are estimates based on provided biometric values. Consult a physician for clinical assessment.</p>
    </div>`;
  container.classList.remove('hidden');
  setTimeout(() => {
    const ind = document.getElementById('riskIndicator');
    if (ind) ind.style.left = Math.min(96, normalized) + '%';
  }, 100);
}

// ═══════════════════════════════════════════════════════════
// PAGE: Upload Report
// ═══════════════════════════════════════════════════════════
function initUploadReport() {
  const form = document.getElementById('reportForm');
  const textArea = document.getElementById('reportText');
  const resultSection = document.getElementById('reportResult');
  if (!form) return;
  if (!Auth.guard()) return;
  populateSidebarUser();
  markActiveNav();

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    setLoading(btn, true);
    const text = textArea.value.trim();
    if (!text) {
      showAlert(resultSection, 'error', 'Please paste your report text first.');
      resultSection.classList.remove('hidden');
      setLoading(btn, false);
      return;
    }
    try {
      const res = await apiFetch('/ai/upload-report', {
        method: 'POST',
        body: JSON.stringify({ text })
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.detail || 'Failed');
      displayReportResult(json, resultSection);
    } catch (err) {
      showAlert(resultSection, 'error', err.message);
      resultSection.classList.remove('hidden');
    } finally { setLoading(btn, false); }
  });
}

function displayReportResult(data, container) {
  const { sentences, summary, flagged_findings, lab_values, has_abnormal } = data;

  // Lab values table
  let labHtml = '';
  if (lab_values && Object.keys(lab_values).length > 0) {
    const rows = Object.entries(lab_values).map(([k, v]) =>
      `<tr><td>${k}</td><td><strong style="color:var(--accent-cyan)">${v}</strong></td></tr>`
    ).join('');
    labHtml = `<h4 class="mb-2 mt-3">🧪 Extracted Lab Values</h4>
      <div class="table-wrap"><table>
        <thead><tr><th>Test</th><th>Value</th></tr></thead>
        <tbody>${rows}</tbody>
      </table></div>`;
  }

  // Flagged findings
  const flagHtml = (flagged_findings || []).map(f =>
    `<div class="explanation-item" style="border-left:3px solid var(--accent-orange);padding-left:1rem;">${f}</div>`
  ).join('');

  // Normal sentences
  const sentHtml = (sentences || []).slice(0, 8).map(s =>
    `<div class="explanation-item">${s}</div>`
  ).join('');

  container.innerHTML = `
    <div class="result-box animate-fade">
      <div class="flex items-center justify-between mb-3">
        <h3>Report Analysis</h3>
        ${has_abnormal ? '<span class="badge badge-orange">⚠️ Abnormal Findings</span>' : '<span class="badge badge-green">✅ No Flags</span>'}
      </div>
      ${summary ? `<div class="alert alert-info mb-3">📋 <strong>Summary:</strong> ${summary}</div>` : ''}
      ${labHtml}
      ${flagHtml ? `<h4 class="mb-2 mt-3">🚩 Flagged Findings (${(flagged_findings||[]).length})</h4>${flagHtml}` : ''}
      ${sentHtml ? `<h4 class="mb-2 mt-3">📝 Key Sentences</h4>${sentHtml}` : ''}
    </div>`;
  container.classList.remove('hidden');
}

// ═══════════════════════════════════════════════════════════
// PAGE: Profile
// ═══════════════════════════════════════════════════════════
function initProfile() {
  const page = document.getElementById('profilePage');
  if (!page) return;
  if (!Auth.guard()) return;
  populateSidebarUser();
  markActiveNav();

  const usernameEl = document.getElementById('profileUsername');
  const tokenEl = document.getElementById('profileToken');
  if (usernameEl) usernameEl.textContent = Auth.user() || 'Unknown';
  if (tokenEl) {
    const t = Auth.token() || '';
    tokenEl.textContent = t ? `${t.slice(0, 20)}…${t.slice(-10)}` : 'N/A';
  }
}

// ═══════════════════════════════════════════════════════════
// Logout
// ═══════════════════════════════════════════════════════════
function initLogout() {
  document.querySelectorAll('[data-logout]').forEach(el => {
    el.addEventListener('click', () => { Auth.clear(); window.location.href = '/'; });
  });
}

// ═══════════════════════════════════════════════════════════
// Boot
// ═══════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  initLogout();
  initAuthPage();
  initDashboard();
  initDiseasePrediction();
  initImagePrediction();
  initChatbot();
  initHealthTips();
  initDoctorRecommendation();
  initAnalytics();
  initUploadReport();
  initProfile();
});
