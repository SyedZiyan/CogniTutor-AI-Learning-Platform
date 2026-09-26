// Main Application Controller for CogniTutor AI Learning Platform

const appState = {
  activeTab: 'dashboard',
  currentQuiz: null,
  quizCurrentIndex: 0,
  quizAnswers: {},
  streak: 7,
  difficulty: 'medium',
  streakCorrectCount: 0,
  soundEnabled: true
};

// Sound effects using Web Audio API
const audioCtx = (typeof window !== 'undefined' && (window.AudioContext || window.webkitAudioContext)) ? new (window.AudioContext || window.webkitAudioContext)() : null;

function playSuccessChime() {
  if (!appState.soundEnabled || !audioCtx) return;
  try {
    if (audioCtx.state === 'suspended') audioCtx.resume();
    const now = audioCtx.currentTime;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(587.33, now); // D5
    osc.frequency.setValueAtTime(880.00, now + 0.08); // A5
    gain.gain.setValueAtTime(0.1, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.3);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start(now);
    osc.stop(now + 0.3);
  } catch (e) {
    console.warn("Audio chime error:", e);
  }
}

function playMistakeSound() {
  if (!appState.soundEnabled || !audioCtx) return;
  try {
    if (audioCtx.state === 'suspended') audioCtx.resume();
    const now = audioCtx.currentTime;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(260, now);
    osc.frequency.exponentialRampToValueAtTime(190, now + 0.15);
    gain.gain.setValueAtTime(0.08, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.2);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start(now);
    osc.stop(now + 0.2);
  } catch (e) {
    console.warn("Audio chime error:", e);
  }
}

// Floating Frosted Glass Toast Notification System
function showToast(message, type = 'info') {
  let container = document.getElementById('cogni-toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'cogni-toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `cogni-toast toast-${type}`;
  
  let iconName = 'info';
  if (type === 'success') iconName = 'check-circle-2';
  if (type === 'error') iconName = 'alert-triangle';

  toast.innerHTML = `
    <i data-lucide="${iconName}" class="w-4 h-4 shrink-0"></i>
    <span class="flex-1">${message}</span>
  `;

  container.appendChild(toast);
  lucide.createIcons({ root: toast });

  setTimeout(() => {
    toast.classList.add('toast-leave');
    setTimeout(() => {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 280);
  }, 3600);
}

// Theme Toggle (Obsidian Dark Glass vs Frosted Light Glass)
function initTheme() {
  const savedTheme = localStorage.getItem('cogni_theme') || 'dark'; // Default to sleek obsidian dark glass
  if (savedTheme === 'dark') {
    document.body.classList.add('dark-theme');
  } else {
    document.body.classList.remove('dark-theme');
  }
  updateThemeIcon();
}

function toggleTheme() {
  document.body.classList.toggle('dark-theme');
  const isDark = document.body.classList.contains('dark-theme');
  localStorage.setItem('cogni_theme', isDark ? 'dark' : 'light');
  updateThemeIcon();
  showToast(isDark ? "🌙 Obsidian Dark Glass Mode activated" : "☀️ Frosted Light Glass Mode activated", "info");
}

function updateThemeIcon() {
  const icon = document.getElementById('theme-toggle-icon');
  if (!icon) return;
  const isDark = document.body.classList.contains('dark-theme');
  icon.setAttribute('data-lucide', isDark ? 'sun' : 'moon');
  lucide.createIcons();
}

// Initialize App
document.addEventListener('DOMContentLoaded', async () => {
  initTheme();
  lucide.createIcons();
  setupNavigation();
  setupVoice();
  setupUpload();
  setupDoubtSolver();
  setupQuizControls();

  // Load initial data
  await refreshGamificationUI();
  await refreshDashboard();

  // Visual confirmation toast
  setTimeout(() => {
    showToast("✨ CogniTutor Pro Glass v3.5 Loaded (Animations & Blurs Active)", "success");
  }, 400);
});

// Navigation Controller
function setupNavigation() {
  const navButtons = document.querySelectorAll('[data-tab-target]');
  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.getAttribute('data-tab-target');
      switchTab(target);
    });
  });
}

function switchTab(tabId) {
  appState.activeTab = tabId;

  // Update nav button states
  document.querySelectorAll('[data-tab-target]').forEach(btn => {
    const isCurrent = btn.getAttribute('data-tab-target') === tabId;
    btn.classList.toggle('active', isCurrent);
  });

  // Switch tab content views
  document.querySelectorAll('.tab-view').forEach(view => {
    view.classList.toggle('hidden', view.id !== `view-${tabId}`);
  });

  // Specific tab actions
  if (tabId === 'dashboard') refreshDashboard();
  if (tabId === 'documents') loadDocumentLibrary();
  if (tabId === 'roadmap') loadRoadmapView();
  if (tabId === 'achievements') loadAchievementsView();
  if (tabId === 'quiz') initializeQuizView();
  if (tabId === 'graph') loadConceptGraphView();
  if (tabId === 'viva') loadVivaView();

  lucide.createIcons();
}

// 1. Dashboard Controller
async function refreshDashboard() {
  try {
    const [comp, gam, docs] = await Promise.all([
      api.getCompetency(),
      api.getGamification(),
      api.getDocuments()
    ]);

    // Update Top Overview Cards
    document.getElementById('dash-overall-progress').innerText = `${comp.overall_mastery}%`;
    document.getElementById('dash-strongest-topic').innerText = comp.strongest_topic;
    document.getElementById('dash-weakest-topic').innerText = comp.weakest_topic;
    document.getElementById('dash-quizzes-count').innerText = gam.quizzes_completed;

    // Render Charts
    chartManager.renderCompetencyRadar('competency-radar-chart', comp.all_topics, comp.all_scores);
    chartManager.renderMasteryBars('competency-bars-chart', comp.all_topics, comp.all_scores);

    // Diagnostic summary
    const diagSummaryEl = document.getElementById('dash-diagnostic-summary');
    if (diagSummaryEl) {
      diagSummaryEl.innerText = comp.diagnostic_summary;
    }

    // Render Topic Breakdown Pills
    renderCompetencyBreakdown(comp);

    // Render Smart Recommendations
    renderRecommendations(comp.recommendations);

    // Refresh gamification header
    updateGamificationHeader(gam);
  } catch (err) {
    console.error("Dashboard refresh error:", err);
  }
}

function renderCompetencyBreakdown(comp) {
  const container = document.getElementById('dash-topic-breakdown');
  if (!container) return;

  let html = '';
  // Strong topics
  comp.strong.forEach(t => {
    html += `
      <div class="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-200">
        <div>
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span class="font-semibold text-xs text-slate-800">${t.topic}</span>
          </div>
          <p class="text-[11px] text-slate-500 mt-0.5">${t.description}</p>
        </div>
        <div class="text-right">
          <span class="text-xs font-bold text-emerald-700">${t.score}%</span>
          <span class="block text-[10px] uppercase font-bold text-emerald-600">Strong</span>
        </div>
      </div>
    `;
  });

  // Average topics
  comp.average.forEach(t => {
    html += `
      <div class="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-200">
        <div>
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-amber-500"></span>
            <span class="font-semibold text-xs text-slate-800">${t.topic}</span>
          </div>
          <p class="text-[11px] text-slate-500 mt-0.5">${t.description}</p>
        </div>
        <div class="text-right">
          <span class="text-xs font-bold text-amber-700">${t.score}%</span>
          <span class="block text-[10px] uppercase font-bold text-amber-600">Average</span>
        </div>
      </div>
    `;
  });

  // Weak topics
  comp.weak.forEach(t => {
    html += `
      <div class="flex items-center justify-between p-3 rounded-xl bg-rose-50/60 border border-rose-200">
        <div>
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-rose-500"></span>
            <span class="font-semibold text-xs text-slate-800">${t.topic}</span>
          </div>
          <p class="text-[11px] text-slate-500 mt-0.5">${t.description}</p>
        </div>
        <div class="text-right">
          <span class="text-xs font-bold text-rose-700">${t.score}%</span>
          <span class="block text-[10px] uppercase font-bold text-rose-600">Needs Work</span>
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}

function renderRecommendations(recs) {
  const container = document.getElementById('dash-recommendations-list');
  if (!container) return;

  if (!recs || recs.length === 0) {
    container.innerHTML = '<p class="text-xs text-slate-500">All competencies mastered! Take a practice test to maintain knowledge.</p>';
    return;
  }

  container.innerHTML = recs.map(r => {
    const isHigh = r.priority === 'HIGH';
    const borderStyle = isHigh ? 'border-rose-200 bg-rose-50/40' : 'border-slate-200 bg-white';
    const tagStyle = isHigh ? 'bg-rose-100 text-rose-800 border-rose-200' : 'bg-blue-100 text-blue-800 border-blue-200';

    return `
      <div class="p-4 rounded-xl border ${borderStyle} flex items-center justify-between gap-4 shadow-xs">
        <div class="flex-1">
          <div class="flex items-center gap-2 mb-1">
            <span class="text-[10px] font-bold px-2 py-0.5 rounded border ${tagStyle}">${r.priority} PRIORITY</span>
            <h4 class="font-semibold text-xs text-slate-900">${r.title}</h4>
          </div>
          <p class="text-xs text-slate-600">${r.action}</p>
        </div>
        <button onclick="handleRecommendationClick('${r.topic}')" class="px-3 py-1.5 text-xs font-semibold rounded-lg bg-blue-600 hover:bg-blue-700 text-white transition flex items-center gap-1.5 shrink-0 shadow-xs">
          <span>Start Drill</span>
          <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
        </button>
      </div>
    `;
  }).join('');
  lucide.createIcons();
}

function handleRecommendationClick(topic) {
  switchTab('doubt');
  const doubtInput = document.getElementById('doubt-query-input');
  if (doubtInput) {
    doubtInput.value = topic;
    triggerDoubtSolver(topic);
  }
}

// 2. Knowledge Base & Document Upload
function setupUpload() {
  const dropZone = document.getElementById('file-drop-zone');
  const fileInput = document.getElementById('file-input');

  if (dropZone && fileInput) {
    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (file) await handleFileUpload(file);
    });

    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.classList.add('border-blue-500', 'bg-blue-50/50');
    });

    dropZone.addEventListener('dragleave', () => {
      dropZone.classList.remove('border-blue-500', 'bg-blue-50/50');
    });

    dropZone.addEventListener('drop', async (e) => {
      e.preventDefault();
      dropZone.classList.remove('border-blue-500', 'bg-blue-50/50');
      const file = e.dataTransfer.files[0];
      if (file) await handleFileUpload(file);
    });
  }
}

async function handleFileUpload(file) {
  const uploadStatus = document.getElementById('upload-status-text');
  if (uploadStatus) {
    uploadStatus.innerText = `Reading and processing ${file.name}...`;
    uploadStatus.classList.remove('hidden');
  }

  try {
    const res = await api.uploadDocument(file);
    if (uploadStatus) {
      uploadStatus.innerText = `✓ Successfully added ${file.name} to library (+50 XP)`;
    }
    showToast(`Added ${file.name} to library (+50 XP)`, "success");
    triggerConfetti();
    playSuccessChime();
    await loadDocumentLibrary();
    await refreshGamificationUI();
  } catch (err) {
    showToast("Upload failed: " + err.message, "error");
    if (uploadStatus) uploadStatus.classList.add('hidden');
  }
}

async function loadDocumentLibrary() {
  try {
    const data = await api.getDocuments();
    const listEl = document.getElementById('documents-list');
    if (!listEl) return;

    if (!data.documents || data.documents.length === 0) {
      listEl.innerHTML = '<p class="text-xs text-slate-500 p-4">No documents uploaded yet.</p>';
      return;
    }

    listEl.innerHTML = data.documents.map(doc => {
      const typeIcons = {
        PDF: 'file-text',
        PPTX: 'presentation',
        DOCX: 'file',
        TXT: 'file-code'
      };
      const icon = typeIcons[doc.file_type] || 'file';

      return `
        <div class="human-card p-4 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">${doc.file_type}</span>
              <span class="text-xs text-slate-400 font-mono">${doc.file_size_kb} KB</span>
            </div>
            <h4 class="font-bold text-xs text-slate-900 mb-1 leading-snug truncate">${doc.file_name}</h4>
            <div class="flex flex-wrap gap-1 mt-2">
              ${doc.topics.slice(0, 3).map(t => `<span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">${t}</span>`).join('')}
            </div>
          </div>
          <div class="flex items-center justify-between pt-3 mt-3 border-t border-slate-100">
            <span class="text-xs font-semibold text-blue-600 font-mono">${doc.chunk_count} Chunks</span>
            <div class="flex items-center gap-2">
              <button onclick="viewDocumentChunks('${doc.doc_id}', '${doc.file_name}')" class="px-2.5 py-1 text-xs rounded bg-slate-100 hover:bg-slate-200 text-slate-700 transition">
                Inspect
              </button>
              <button onclick="askAboutDocument('${doc.file_name}')" class="px-2.5 py-1 text-xs rounded bg-blue-50 hover:bg-blue-100 text-blue-700 font-medium transition">
                Ask Notes
              </button>
            </div>
          </div>
        </div>
      `;
    }).join('');
    lucide.createIcons();
  } catch (err) {
    console.error("Error loading library:", err);
  }
}

function askAboutDocument(docName) {
  switchTab('tutor');
  const chatInput = document.getElementById('tutor-chat-input');
  if (chatInput) {
    chatInput.value = `Summarize key concepts from ${docName}`;
    sendTutorQuery();
  }
}

async function viewDocumentChunks(docId, docName) {
  try {
    const data = await api.getDocumentChunks(docId);
    const modal = document.getElementById('chunks-modal');
    const titleEl = document.getElementById('chunks-modal-title');
    const contentEl = document.getElementById('chunks-modal-content');

    if (!modal || !contentEl) return;

    titleEl.innerText = `${docName} (${data.total_chunks} Chunks)`;
    contentEl.innerHTML = data.chunks.map(c => `
      <div class="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs">
        <div class="flex items-center justify-between mb-1">
          <span class="font-bold text-blue-600 font-mono">${c.page_or_slide}</span>
          <span class="text-[10px] px-1.5 py-0.5 rounded bg-white border border-slate-200 text-slate-600">${c.topic}</span>
        </div>
        <p class="text-slate-700 leading-relaxed font-mono whitespace-pre-wrap">${c.text}</p>
      </div>
    `).join('');

    modal.classList.remove('hidden');
  } catch (err) {
    showToast("Could not load chunks: " + err.message, "error");
  }
}

function closeChunksModal() {
  const modal = document.getElementById('chunks-modal');
  if (modal) modal.classList.add('hidden');
}

// 3. AI Tutor & RAG Chat Controller
async function sendTutorQuery() {
  const input = document.getElementById('tutor-chat-input');
  if (!input || !input.value.trim()) return;

  const query = input.value.trim();
  input.value = '';

  let loadingId = null;

  try {
    // Append user message
    appendChatMessage('user', query);

    // Append loading bubble
    loadingId = appendChatLoading();

    const res = await api.askTutor(query);
    removeChatLoading(loadingId);
    appendChatMessage('tutor', res.answer, res.citations);
    await refreshGamificationUI();
  } catch (err) {
    console.error("sendTutorQuery error:", err);
    if (loadingId) removeChatLoading(loadingId);
    const orphanLoading = document.querySelector('[id^="loading-"]');
    if (orphanLoading) orphanLoading.remove();
    appendChatMessage('tutor', "I checked your study materials for this topic. Please make sure the notes cover this question or ask another question about Neural Networks, CNNs, RNNs, LSTMs, or Transformers.");
  }
}

function selectTutorPrompt(promptText) {
  const input = document.getElementById('tutor-chat-input');
  if (input) {
    input.value = promptText;
    sendTutorQuery();
  }
}

function appendChatMessage(sender, text, citations = []) {
  const container = document.getElementById('tutor-messages-container');
  if (!container) return;

  const msgDiv = document.createElement('div');
  msgDiv.className = `flex gap-3 mb-4 ${sender === 'user' ? 'justify-end' : 'justify-start'}`;

  let parsedMarkdown = text;
  try {
    if (typeof marked !== 'undefined') {
      parsedMarkdown = typeof marked.parse === 'function' ? marked.parse(text) : marked(text);
    }
  } catch (e) {
    console.warn("Markdown parse warning:", e);
    parsedMarkdown = `<p>${text.replace(/\n/g, '<br>')}</p>`;
  }

  let citationsHtml = '';
  if (citations && citations.length > 0) {
    citationsHtml = `
      <div class="mt-3.5 pt-3 border-t border-slate-100">
        <div class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
          <i data-lucide="book-open" class="w-3.5 h-3.5 text-blue-600"></i>
          <span>Cited Sources in Notes</span>
        </div>
        <div class="flex flex-wrap gap-2">
          ${citations.map(c => `
            <div class="p-2 rounded-lg bg-slate-50 border border-slate-200 text-xs max-w-sm">
              <div class="flex items-center justify-between font-semibold text-slate-800">
                <span class="truncate max-w-[150px]">${c.doc_name}</span>
                <span class="text-blue-600 font-mono text-[11px]">${c.page_or_slide}</span>
              </div>
              <p class="text-[11px] text-slate-500 mt-1 line-clamp-2">${c.snippet}</p>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  const voiceBtnHtml = sender === 'tutor' ? `
    <button onclick="speakMessageContent(this)" class="mt-2 text-xs flex items-center gap-1 text-slate-400 hover:text-blue-600 transition font-medium">
      <i data-lucide="volume-2" class="w-3.5 h-3.5"></i>
      <span>Listen Voice</span>
    </button>
  ` : '';

  if (sender === 'user') {
    msgDiv.innerHTML = `
      <div class="max-w-[75%] p-3.5 rounded-xl bg-blue-600 text-white rounded-tr-none shadow-xs text-sm leading-relaxed">
        <p>${text}</p>
      </div>
    `;
  } else {
    msgDiv.innerHTML = `
      <div class="w-8 h-8 rounded-lg bg-slate-100 text-slate-700 flex items-center justify-center shrink-0 mt-0.5 border border-slate-200">
        <i data-lucide="book-open" class="w-4 h-4 text-blue-600"></i>
      </div>
      <div class="max-w-[85%] p-4 rounded-xl bg-white border border-slate-200 text-slate-800 rounded-tl-none shadow-xs text-sm notes-prose">
        <div class="msg-content leading-relaxed">${parsedMarkdown}</div>
        ${citationsHtml}
        ${voiceBtnHtml}
      </div>
    `;
  }

  container.appendChild(msgDiv);
  container.scrollTop = container.scrollHeight;
  
  try {
    if (typeof lucide !== 'undefined' && lucide.createIcons) {
      lucide.createIcons();
    }
  } catch (e) {}

  safeRenderMath(msgDiv);
}

function appendChatLoading() {
  const container = document.getElementById('tutor-messages-container');
  if (!container) return null;

  const id = `loading-${Date.now()}`;
  const loadDiv = document.createElement('div');
  loadDiv.id = id;
  loadDiv.className = 'flex gap-3 mb-4 justify-start';
  loadDiv.innerHTML = `
    <div class="w-8 h-8 rounded-lg bg-slate-100 text-slate-700 flex items-center justify-center shrink-0 mt-0.5 border border-slate-200">
      <i data-lucide="book-open" class="w-4 h-4 text-blue-600"></i>
    </div>
    <div class="p-3.5 rounded-xl bg-white border border-slate-200 text-slate-600 rounded-tl-none flex items-center gap-2 text-xs">
      <div class="w-2 h-2 rounded-full bg-blue-600 animate-ping"></div>
      <span>Searching study notes and formulating answer...</span>
    </div>
  `;
  container.appendChild(loadDiv);
  container.scrollTop = container.scrollHeight;
  lucide.createIcons();
  return id;
}

function removeChatLoading(id) {
  if (!id) return;
  const el = document.getElementById(id);
  if (el) el.remove();
}

function speakMessageContent(button) {
  const card = button.closest('.max-w-\\[85\\%\\]');
  if (!card) return;
  const contentEl = card.querySelector('.msg-content');
  if (contentEl) {
    voiceTutor.speak(contentEl.innerText);
  }
}

// 4. Voice Controls
function setupVoice() {
  const voiceMicBtn = document.getElementById('tutor-voice-btn');
  if (voiceMicBtn) {
    voiceMicBtn.addEventListener('click', () => {
      if (voiceTutor.isListening) {
        voiceTutor.stopListening();
      } else {
        voiceTutor.startListening((transcript) => {
          const chatInput = document.getElementById('tutor-chat-input');
          if (chatInput) {
            chatInput.value = transcript;
            sendTutorQuery();
          }
        });
      }
    });
  }

  window.addEventListener('beforeunload', () => voiceTutor.stopSpeaking());
}

// 5. 3-Level Doubt Solver Controller
let currentDoubtData = null;
let currentDoubtLevel = 'beginner';

function setupDoubtSolver() {
  document.querySelectorAll('[data-doubt-level]').forEach(btn => {
    btn.addEventListener('click', () => {
      const level = btn.getAttribute('data-doubt-level');
      setDoubtLevel(level);
    });
  });

  const doubtInput = document.getElementById('doubt-query-input');
  if (doubtInput) {
    doubtInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        triggerDoubtSolver(doubtInput.value);
      }
    });
  }
}

async function triggerDoubtSolver(topic) {
  if (!topic || !topic.trim()) return;

  const titleEl = document.getElementById('doubt-topic-title');
  if (titleEl) titleEl.innerText = `Analyzing '${topic}'...`;

  try {
    const res = await api.solveDoubt(topic);
    currentDoubtData = res;
    if (titleEl) titleEl.innerText = res.topic;
    renderCurrentDoubtExplanation();
    await refreshGamificationUI();
  } catch (err) {
    showToast("Doubt solver error: " + err.message, "error");
  }
}

function setDoubtLevel(level) {
  currentDoubtLevel = level;
  document.querySelectorAll('[data-doubt-level]').forEach(btn => {
    const isCurrent = btn.getAttribute('data-doubt-level') === level;
    btn.classList.toggle('bg-white', isCurrent);
    btn.classList.toggle('text-blue-700', isCurrent);
    btn.classList.toggle('shadow-sm', isCurrent);
    btn.classList.toggle('text-slate-600', !isCurrent);
  });
  renderCurrentDoubtExplanation();
}

function renderCurrentDoubtExplanation() {
  if (!currentDoubtData) return;
  const contentEl = document.getElementById('doubt-explanation-content');
  if (!contentEl) return;

  const data = currentDoubtData[currentDoubtLevel];
  if (!data) return;

  let html = '';
  if (currentDoubtLevel === 'beginner') {
    html = `
      <div class="p-5 rounded-xl bg-emerald-50/70 border border-emerald-200 mb-4">
        <div class="flex items-center gap-1.5 text-emerald-800 font-bold text-xs uppercase tracking-wider mb-2">
          <i data-lucide="sparkles" class="w-3.5 h-3.5 text-emerald-600"></i>
          <span>${data.analogy || 'Simple Analogy'}</span>
        </div>
        <div class="text-sm text-slate-800 leading-relaxed space-y-2 notes-prose">
          ${marked.parse(data.explanation)}
        </div>
      </div>
    `;
  } else if (currentDoubtLevel === 'intermediate') {
    html = `
      <div class="p-5 rounded-xl bg-amber-50/70 border border-amber-200 mb-4">
        <div class="flex items-center gap-1.5 text-amber-800 font-bold text-xs uppercase tracking-wider mb-2">
          <i data-lucide="cpu" class="w-3.5 h-3.5 text-amber-600"></i>
          <span>${data.title || 'Technical & Mathematical Explanation'}</span>
        </div>
        <div class="text-sm text-slate-800 leading-relaxed space-y-2 notes-prose">
          ${marked.parse(data.explanation)}
        </div>
      </div>
    `;
  } else if (currentDoubtLevel === 'advanced') {
    html = `
      <div class="p-5 rounded-xl bg-blue-50/60 border border-blue-200 mb-4">
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-1.5 text-blue-800 font-bold text-xs uppercase tracking-wider">
            <i data-lucide="code" class="w-3.5 h-3.5 text-blue-600"></i>
            <span>${data.title || 'Architecture & PyTorch Implementation'}</span>
          </div>
          <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-100 text-blue-800">PyTorch Code</span>
        </div>
        <div class="text-sm text-slate-800 leading-relaxed space-y-2 notes-prose">
          ${marked.parse(data.explanation)}
        </div>
      </div>
    `;
  }

  contentEl.innerHTML = html;
  try {
    if (typeof lucide !== 'undefined' && lucide.createIcons) {
      lucide.createIcons();
    }
  } catch (e) {}
  safeRenderMath(contentEl);
}

// 6. Adaptive Quiz Hub Controller
function setupQuizControls() {
  const startBtn = document.getElementById('start-quiz-btn');
  if (startBtn) {
    startBtn.addEventListener('click', async () => {
      const topic = document.getElementById('quiz-topic-select').value;
      const difficulty = document.getElementById('quiz-difficulty-select').value;
      await startQuiz(topic, difficulty);
    });
  }
}

async function initializeQuizView() {
  if (!appState.currentQuiz) {
    await startQuiz('all', 'adaptive');
  }
}

async function startQuiz(topic, difficulty) {
  try {
    const quiz = await api.generateQuiz(topic, difficulty);
    appState.currentQuiz = quiz;
    appState.quizCurrentIndex = 0;
    appState.quizAnswers = {};
    renderQuizQuestion(0);
  } catch (err) {
    console.error("Quiz generation failed:", err);
  }
}

function renderQuizQuestion(index) {
  const quiz = appState.currentQuiz;
  if (!quiz || !quiz.mcqs || quiz.mcqs.length === 0) return;

  const q = quiz.mcqs[index];
  const container = document.getElementById('quiz-question-container');
  if (!container) return;

  const total = quiz.mcqs.length;
  document.getElementById('quiz-progress-text').innerText = `Question ${index + 1} of ${total}`;
  document.getElementById('quiz-progress-bar').style.width = `${((index + 1) / total) * 100}%`;
  document.getElementById('quiz-difficulty-badge').innerText = q.difficulty ? q.difficulty.toUpperCase() : 'MEDIUM';

  const answered = appState.quizAnswers[q.id];
  const optionLetters = ['A', 'B', 'C', 'D'];

  container.innerHTML = `
    <div class="mb-5 pb-4 border-b border-slate-100">
      <div class="flex items-center justify-between text-xs text-slate-400 mb-2">
        <span class="font-medium text-blue-600 font-mono">${q.topic}</span>
        <span>Reference: ${q.source_doc} (${q.source_page})</span>
      </div>
      <h3 class="text-base font-bold text-slate-900 leading-snug">${q.question}</h3>
    </div>

    <div class="space-y-2.5 mb-6" id="quiz-options-list">
      ${q.options.map((opt, optIdx) => {
        let btnClass = "";
        let badgeClass = "";
        let iconHtml = '';

        if (answered) {
          if (optIdx === answered.correct_index) {
            btnClass = "opt-correct";
            badgeClass = "opt-badge-correct";
            iconHtml = '<i data-lucide="check" class="w-4 h-4 text-emerald-600 ml-auto"></i>';
          } else if (optIdx === answered.user_selection) {
            btnClass = "opt-incorrect";
            badgeClass = "opt-badge-incorrect";
            iconHtml = '<i data-lucide="x" class="w-4 h-4 text-rose-600 ml-auto"></i>';
          }
        }

        const cleanOpt = opt.replace(/^[A-D]\.\s*/, '');

        return `
          <button onclick="handleOptionSelect('${q.id}', ${optIdx})" ${answered ? 'disabled' : ''} class="study-opt-btn ${btnClass}">
            <span class="opt-badge ${badgeClass}">${optionLetters[optIdx]}</span>
            <span class="flex-1">${cleanOpt}</span>
            ${iconHtml}
          </button>
        `;
      }).join('')}
    </div>

    ${answered ? `
      <div class="p-4 rounded-xl ${answered.is_correct ? 'bg-emerald-50 border border-emerald-200 text-emerald-900' : 'bg-rose-50 border border-rose-200 text-rose-900'} mb-5">
        <div class="flex items-center gap-1.5 font-bold text-xs uppercase mb-1">
          <i data-lucide="${answered.is_correct ? 'check-circle' : 'alert-circle'}" class="w-4 h-4"></i>
          <span>${answered.is_correct ? 'Correct! (+15 XP)' : 'Incorrect'}</span>
        </div>
        <p class="text-xs leading-relaxed text-slate-700">${answered.explanation}</p>
        <div class="mt-2.5 flex items-center gap-4 text-[11px] text-slate-500 pt-2 border-t border-slate-200/60">
          <span>Streak: <strong class="text-amber-700">${answered.streak} 🔥</strong></span>
          <span>Adaptive Level: <strong class="text-blue-700 uppercase">${answered.next_difficulty}</strong></span>
        </div>
      </div>
    ` : ''}

    <div class="flex items-center justify-between pt-4 border-t border-slate-100">
      <button onclick="prevQuizQuestion()" ${index === 0 ? 'disabled' : ''} class="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 disabled:opacity-40 transition">
        Previous
      </button>
      <button onclick="nextQuizQuestion()" class="px-4 py-2 text-xs font-semibold rounded-lg bg-blue-600 hover:bg-blue-700 text-white transition flex items-center gap-1.5 shadow-sm">
        <span>${index + 1 === total ? 'Proceed to Short Answers' : 'Next Question'}</span>
        <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
      </button>
    </div>
  `;
  lucide.createIcons();
}

async function handleOptionSelect(questionId, selectedIdx) {
  try {
    const res = await api.evaluateMCQ(
      questionId,
      selectedIdx,
      appState.streakCorrectCount,
      appState.difficulty
    );

    appState.quizAnswers[questionId] = res;
    if (res.is_correct) {
      appState.streakCorrectCount += 1;
      playSuccessChime();
      triggerConfetti();
    } else {
      appState.streakCorrectCount = 0;
      playMistakeSound();
    }
    appState.difficulty = res.next_difficulty;

    renderQuizQuestion(appState.quizCurrentIndex);
    await refreshGamificationUI();
  } catch (err) {
    console.error("Evaluation error:", err);
  }
}

function nextQuizQuestion() {
  const total = appState.currentQuiz.mcqs.length;
  if (appState.quizCurrentIndex + 1 < total) {
    appState.quizCurrentIndex++;
    renderQuizQuestion(appState.quizCurrentIndex);
  } else {
    renderShortAnswerSection();
  }
}

function prevQuizQuestion() {
  if (appState.quizCurrentIndex > 0) {
    appState.quizCurrentIndex--;
    renderQuizQuestion(appState.quizCurrentIndex);
  }
}

function renderShortAnswerSection() {
  const quiz = appState.currentQuiz;
  const container = document.getElementById('quiz-question-container');
  if (!container || !quiz.short_questions) return;

  container.innerHTML = `
    <div class="mb-5 pb-3 border-b border-slate-100">
      <h3 class="text-base font-bold text-slate-900 flex items-center gap-2">
        <i data-lucide="edit" class="w-4 h-4 text-blue-600"></i>
        <span>Part 2: Short Answer Concept Test</span>
      </h3>
      <p class="text-xs text-slate-500 mt-0.5">Explain each concept in your own words. The AI evaluates key conceptual points.</p>
    </div>

    <div class="space-y-4">
      ${quiz.short_questions.map((sq, i) => `
        <div class="p-4 rounded-xl bg-slate-50 border border-slate-200" id="sa-card-${sq.id}">
          <div class="flex items-center justify-between text-xs text-blue-600 mb-1">
            <span class="font-semibold">${sq.topic}</span>
            <span class="text-slate-400">${sq.source_doc}</span>
          </div>
          <h4 class="text-sm font-semibold text-slate-900 mb-2">${sq.question}</h4>
          <textarea id="sa-input-${sq.id}" rows="3" placeholder="Type your answer here..." class="w-full p-3 rounded-lg bg-white border border-slate-300 text-xs text-slate-800 focus:outline-none focus:border-blue-600"></textarea>
          <div class="mt-2 flex justify-end">
            <button onclick="submitShortAnswer('${sq.id}')" class="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-blue-600 hover:bg-blue-700 text-white transition shadow-sm">
              Grade Answer
            </button>
          </div>
          <div id="sa-feedback-${sq.id}" class="mt-3 hidden"></div>
        </div>
      `).join('')}
    </div>
  `;
  lucide.createIcons();
}

async function submitShortAnswer(questionId) {
  const input = document.getElementById(`sa-input-${questionId}`);
  const feedbackEl = document.getElementById(`sa-feedback-${questionId}`);
  if (!input || !feedbackEl || !input.value.trim()) return;

  try {
    const res = await api.evaluateShortAnswer(questionId, input.value.trim());
    feedbackEl.classList.remove('hidden');

    if (res.passed) {
      playSuccessChime();
      triggerConfetti();
    } else {
      playMistakeSound();
    }

    feedbackEl.innerHTML = `
      <div class="p-3.5 rounded-lg ${res.passed ? 'bg-emerald-50 border border-emerald-200' : 'bg-rose-50 border border-rose-200'}">
        <div class="flex items-center justify-between mb-1">
          <span class="text-xs font-bold ${res.passed ? 'text-emerald-800' : 'text-rose-800'}">Score: ${res.score}%</span>
          <span class="text-xs text-blue-700 font-mono font-medium">+${res.xp_earned} XP</span>
        </div>
        <p class="text-xs text-slate-700 mb-2 leading-relaxed">${res.feedback}</p>
        <div class="text-[11px] text-slate-500 pt-2 border-t border-slate-200">
          <strong class="text-slate-800">Model Answer:</strong> ${res.model_answer}
        </div>
      </div>
    `;
    await refreshGamificationUI();
  } catch (err) {
    showToast("Evaluation failed: " + err.message, "error");
  }
}

// 7. Dynamic Personalized Roadmap Controller
async function loadRoadmapView() {
  try {
    const data = await api.getRoadmap();
    const container = document.getElementById('roadmap-weeks-container');
    if (!container) return;

    document.getElementById('roadmap-overall-percent').innerText = `${data.overall_progress_percent}%`;
    document.getElementById('roadmap-progress-bar').style.width = `${data.overall_progress_percent}%`;

    container.innerHTML = data.weeks.map(w => {
      const isLocked = w.status === 'Locked';
      const isCompleted = w.status === 'Completed';

      return `
        <div class="human-card p-5 ${isLocked ? 'opacity-60 bg-slate-50' : 'bg-white'} mb-4">
          <div class="flex items-center justify-between mb-2">
            <div>
              <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${isCompleted ? 'bg-emerald-100 text-emerald-800' : (isLocked ? 'bg-slate-200 text-slate-600' : 'bg-blue-100 text-blue-800')}">
                ${w.status}
              </span>
              <h3 class="text-base font-bold text-slate-900 mt-1">${w.title}</h3>
            </div>
            <span class="text-xs font-mono font-bold text-blue-600">${w.progress_percent}%</span>
          </div>
          <p class="text-xs text-slate-500 mb-3">${w.description}</p>

          <div class="space-y-2">
            ${w.items.map(item => `
              <div class="p-3 rounded-lg border ${item.remedial_flag ? 'border-rose-200 bg-rose-50/40' : 'border-slate-200 bg-slate-50/50'} flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <input type="checkbox" onchange="toggleMilestoneCheck('${item.id}')" ${item.completed ? 'checked' : ''} ${isLocked ? 'disabled' : ''} class="roadmap-checkbox">
                  <div>
                    <div class="flex items-center gap-2">
                      <span class="text-xs font-semibold ${item.completed ? 'line-through text-slate-400' : 'text-slate-800'}">${item.title}</span>
                      ${item.remedial_flag ? '<span class="text-[9px] uppercase px-1.5 py-0.5 rounded bg-rose-100 text-rose-800 font-bold border border-rose-200">Weak Area</span>' : ''}
                    </div>
                    <span class="text-[11px] text-slate-500 font-mono">${item.type} • ${item.estimated_time}</span>
                  </div>
                </div>
                <span class="text-[11px] text-slate-400 hidden sm:inline font-mono">${item.source_ref}</span>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }).join('');
    lucide.createIcons();
  } catch (err) {
    console.error("Error loading roadmap:", err);
  }
}

async function toggleMilestoneCheck(milestoneId) {
  try {
    await api.toggleMilestone(milestoneId);
    triggerConfetti();
    playSuccessChime();
    await loadRoadmapView();
    await refreshGamificationUI();
  } catch (err) {
    console.error("Toggle milestone failed:", err);
  }
}

// 8. Achievements & Gamification Controller
async function loadAchievementsView() {
  try {
    const data = await api.getGamification();
    const badgesContainer = document.getElementById('badges-grid');
    const leaderboardContainer = document.getElementById('leaderboard-list');

    if (badgesContainer) {
      badgesContainer.innerHTML = data.badges.map(b => `
        <div class="human-card p-4 text-center flex flex-col items-center ${b.unlocked ? 'border-blue-200' : 'opacity-50'}">
          <div class="text-2xl mb-1">${b.icon}</div>
          <h4 class="font-bold text-xs text-slate-900 mb-0.5">${b.name}</h4>
          <p class="text-[11px] text-slate-500 leading-tight">${b.description}</p>
          <span class="mt-2 text-[10px] font-bold uppercase tracking-wider ${b.unlocked ? 'text-emerald-700' : 'text-slate-400'}">
            ${b.unlocked ? 'Earned ✓' : 'Locked'}
          </span>
        </div>
      `).join('');
    }

    if (leaderboardContainer) {
      leaderboardContainer.innerHTML = data.leaderboard.map(u => `
        <div class="human-card p-3 flex items-center justify-between ${u.is_user ? 'border-blue-300 bg-blue-50/30' : ''}">
          <div class="flex items-center gap-3">
            <span class="w-5 font-mono font-bold text-xs ${u.rank === 1 ? 'text-amber-600' : 'text-slate-400'}">#${u.rank}</span>
            <span class="text-xl">${u.avatar}</span>
            <div>
              <div class="flex items-center gap-1.5">
                <span class="font-semibold text-xs text-slate-800">${u.name}</span>
                ${u.is_user ? '<span class="text-[9px] uppercase px-1 py-0.2 rounded bg-blue-100 text-blue-800 font-bold">You</span>' : ''}
              </div>
              <span class="text-[11px] text-slate-500">Level ${u.level} • ${u.streak}d streak</span>
            </div>
          </div>
          <span class="font-mono font-bold text-xs text-blue-700">${u.xp} XP</span>
        </div>
      `).join('');
    }
  } catch (err) {
    console.error("Error loading achievements:", err);
  }
}

async function refreshGamificationUI() {
  try {
    const data = await api.getGamification();
    updateGamificationHeader(data);
  } catch (e) {
    console.warn("Could not refresh gamification header:", e);
  }
}

function updateGamificationHeader(data) {
  const lvlInfo = data.level_info;
  document.getElementById('header-streak-count').innerText = `${data.streak_days} Day Streak`;
  document.getElementById('header-level-badge').innerText = `Level ${lvlInfo.current_level}`;
  document.getElementById('header-xp-text').innerText = `${lvlInfo.current_xp} / ${lvlInfo.next_level_xp} XP`;
  document.getElementById('header-xp-bar').style.width = `${lvlInfo.level_progress_percent}%`;
}

// Settings Drawer
function toggleSettingsDrawer() {
  const drawer = document.getElementById('settings-drawer');
  if (drawer) {
    drawer.classList.toggle('hidden');
  }
}

async function savePlatformSettings() {
  const provider = document.getElementById('settings-llm-provider').value;
  const openaiKey = document.getElementById('settings-openai-key').value.trim();
  const geminiKey = document.getElementById('settings-gemini-key').value.trim();
  const soundToggle = document.getElementById('settings-sound-toggle');
  
  if (soundToggle) {
    appState.soundEnabled = soundToggle.checked;
  }

  try {
    await api.updateSettings({
      llm_provider: provider,
      openai_api_key: openaiKey || undefined,
      gemini_api_key: geminiKey || undefined
    });
    showToast("Settings saved successfully!", "success");
    toggleSettingsDrawer();
  } catch (e) {
    showToast("Error saving settings: " + e.message, "error");
  }
}

// LaTeX rendering helper (named safeRenderMath to prevent shadowing window.renderMathInElement)
function safeRenderMath(elem) {
  try {
    if (window.renderMathInElement && typeof window.renderMathInElement === 'function') {
      window.renderMathInElement(elem, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '\\(', right: '\\)', display: false }
        ],
        throwOnError: false
      });
    }
  } catch (e) {
    console.warn("KaTeX render error:", e);
  }
}

// Confetti effect helper
function triggerConfetti() {
  if (window.confetti) {
    window.confetti({
      particleCount: 35,
      spread: 55,
      origin: { y: 0.7 }
    });
  }
}

function escapeHtml(unsafe) {
  if (unsafe === undefined || unsafe === null) return '';
  return String(unsafe)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// ==========================================================================
// 8. Concept Knowledge Graph (Visual Ontology) Controller
// ==========================================================================
let graphNodesMap = {};
let isFilteringWeakNodes = false;

async function loadConceptGraphView() {
  try {
    const data = await api.getConceptGraph();
    appState.graphData = data;
    renderConceptGraph(data);
  } catch (err) {
    console.error("Failed to load concept graph:", err);
  }
}

function renderConceptGraph(data) {
  const edgesLayer = document.getElementById('graph-edges-layer');
  const nodesLayer = document.getElementById('graph-nodes-layer');
  if (!edgesLayer || !nodesLayer) return;

  edgesLayer.innerHTML = '';
  nodesLayer.innerHTML = '';
  graphNodesMap = {};

  data.nodes.forEach(n => {
    graphNodesMap[n.id] = n;
  });

  const nodeWidth = 145;
  const nodeHeight = 58;

  // Render Edges First
  data.edges.forEach(edge => {
    const src = graphNodesMap[edge.source];
    const tgt = graphNodesMap[edge.target];
    if (!src || !tgt) return;

    const x1 = src.x + nodeWidth;
    const y1 = src.y + (nodeHeight / 2);
    const x2 = tgt.x;
    const y2 = tgt.y + (nodeHeight / 2);

    const dx = Math.max(35, Math.abs(x2 - x1) * 0.5);
    const pathD = `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;

    const isWeakTarget = tgt.is_weak_gap;
    const strokeColor = isWeakTarget ? '#f43f5e' : (src.score >= 75 && tgt.score >= 75 ? '#10b981' : '#94a3b8');
    const markerUrl = isWeakTarget ? 'url(#arrow-rose)' : (src.score >= 75 && tgt.score >= 75 ? 'url(#arrow-emerald)' : 'url(#arrow-slate)');

    // Path
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', pathD);
    path.setAttribute('fill', 'none');
    path.setAttribute('stroke', strokeColor);
    path.setAttribute('stroke-width', isWeakTarget ? '2' : '1.5');
    path.setAttribute('marker-end', markerUrl);
    path.setAttribute('data-source', edge.source);
    path.setAttribute('data-target', edge.target);
    path.setAttribute('class', 'graph-edge-path transition-all duration-200');
    edgesLayer.appendChild(path);

    // Relationship Label Pill
    const mx = (x1 + x2) / 2;
    const my = (y1 + y2) / 2;
    const relText = edge.relationship.replace(/_/g, ' ');

    const labelG = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    labelG.setAttribute('class', 'graph-edge-label select-none pointer-events-none');

    const pillW = relText.length * 6.2 + 10;
    const pill = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    pill.setAttribute('x', mx - (pillW / 2));
    pill.setAttribute('y', my - 8);
    pill.setAttribute('width', pillW);
    pill.setAttribute('height', 15);
    pill.setAttribute('rx', 4);
    pill.setAttribute('fill', '#ffffff');
    pill.setAttribute('stroke', '#e2e8f0');
    pill.setAttribute('stroke-width', '1');

    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', mx);
    text.setAttribute('y', my + 3);
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('fill', '#64748b');
    text.setAttribute('font-size', '8.5');
    text.setAttribute('font-family', 'var(--font-mono)');
    text.textContent = relText;

    labelG.appendChild(pill);
    labelG.appendChild(text);
    edgesLayer.appendChild(labelG);
  });

  // Render Nodes
  data.nodes.forEach(node => {
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.setAttribute('class', `graph-node-group ${node.is_weak_gap ? 'weak-node' : ''}`);
    g.setAttribute('data-node-id', node.id);
    g.setAttribute('transform', `translate(${node.x}, ${node.y})`);

    const strokeColor = node.is_weak_gap ? '#f43f5e' : (node.score >= 75 ? '#10b981' : '#cbd5e1');
    const accentColor = node.is_weak_gap ? '#f43f5e' : (node.score >= 75 ? '#10b981' : '#f59e0b');

    // Node Base Card
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('class', 'node-card');
    rect.setAttribute('width', nodeWidth);
    rect.setAttribute('height', nodeHeight);
    rect.setAttribute('rx', '8');
    rect.setAttribute('fill', '#ffffff');
    rect.setAttribute('stroke', strokeColor);
    rect.setAttribute('stroke-width', node.is_weak_gap ? '2' : '1.2');

    // Accent Top Line
    const accent = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    accent.setAttribute('width', nodeWidth);
    accent.setAttribute('height', '3');
    accent.setAttribute('rx', '1.5');
    accent.setAttribute('fill', accentColor);

    // Category Text
    const catText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    catText.setAttribute('x', '10');
    catText.setAttribute('y', '16');
    catText.setAttribute('fill', '#64748b');
    catText.setAttribute('font-size', '8.5');
    catText.setAttribute('font-weight', '600');
    catText.setAttribute('letter-spacing', '0.5');
    catText.textContent = node.category.toUpperCase();

    // Node Title (Truncated if necessary)
    const titleText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    titleText.setAttribute('x', '10');
    titleText.setAttribute('y', '32');
    titleText.setAttribute('fill', '#0f172a');
    titleText.setAttribute('font-size', '11.5');
    titleText.setAttribute('font-weight', '700');
    const displayLabel = node.label.length > 17 ? node.label.slice(0, 16) + '…' : node.label;
    titleText.textContent = displayLabel;

    // Score Badge Pill
    const badgeW = 42;
    const badgeH = 14;
    const badgeBg = node.score >= 75 ? '#ecfdf5' : (node.score >= 50 ? '#fffbeb' : '#fef2f2');
    const badgeStroke = node.score >= 75 ? '#a7f3d0' : (node.score >= 50 ? '#fde68a' : '#fecaca');
    const badgeTextColor = node.score >= 75 ? '#065f46' : (node.score >= 50 ? '#92400e' : '#991b1b');

    const scoreRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    scoreRect.setAttribute('x', '10');
    scoreRect.setAttribute('y', '39');
    scoreRect.setAttribute('width', badgeW);
    scoreRect.setAttribute('height', badgeH);
    scoreRect.setAttribute('rx', '4');
    scoreRect.setAttribute('fill', badgeBg);
    scoreRect.setAttribute('stroke', badgeStroke);
    scoreRect.setAttribute('stroke-width', '0.8');

    const scoreText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    scoreText.setAttribute('x', '31');
    scoreText.setAttribute('y', '49.5');
    scoreText.setAttribute('fill', badgeTextColor);
    scoreText.setAttribute('font-size', '9.5');
    scoreText.setAttribute('font-family', 'var(--font-mono)');
    scoreText.setAttribute('font-weight', '600');
    scoreText.setAttribute('text-anchor', 'middle');
    scoreText.textContent = `${Math.round(node.score)}%`;

    g.appendChild(rect);
    g.appendChild(accent);
    g.appendChild(catText);
    g.appendChild(titleText);
    g.appendChild(scoreRect);
    g.appendChild(scoreText);

    // If Weak Gap, add a small warning badge
    if (node.is_weak_gap) {
      const warnRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      warnRect.setAttribute('x', '58');
      warnRect.setAttribute('y', '39');
      warnRect.setAttribute('width', '52');
      warnRect.setAttribute('height', badgeH);
      warnRect.setAttribute('rx', '4');
      warnRect.setAttribute('fill', '#fff1f2');
      warnRect.setAttribute('stroke', '#fecdd3');
      warnRect.setAttribute('stroke-width', '0.8');

      const warnText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      warnText.setAttribute('x', '84');
      warnText.setAttribute('y', '49.5');
      warnText.setAttribute('fill', '#be123c');
      warnText.setAttribute('font-size', '8.5');
      warnText.setAttribute('font-weight', '600');
      warnText.setAttribute('text-anchor', 'middle');
      warnText.textContent = 'Weak Spot';

      g.appendChild(warnRect);
      g.appendChild(warnText);
    }

    // Click handler to inspect node
    g.addEventListener('click', () => {
      selectGraphNode(node.id);
    });

    nodesLayer.appendChild(g);
  });

  // If a node was previously selected, restore inspection; else select first node
  if (appState.selectedGraphNode && graphNodesMap[appState.selectedGraphNode]) {
    selectGraphNode(appState.selectedGraphNode);
  } else if (data.nodes.length > 0) {
    selectGraphNode(data.nodes[0].id);
  }
}

function selectGraphNode(nodeId) {
  const node = graphNodesMap[nodeId];
  if (!node) return;

  appState.selectedGraphNode = nodeId;

  // Highlight selected node in SVG
  document.querySelectorAll('.graph-node-group').forEach(el => {
    el.classList.toggle('selected', el.getAttribute('data-node-id') === nodeId);
  });

  // Highlight connected edges
  document.querySelectorAll('.graph-edge-path').forEach(edge => {
    const isConnected = edge.getAttribute('data-source') === nodeId || edge.getAttribute('data-target') === nodeId;
    if (isConnected) {
      edge.setAttribute('stroke-width', '2.5');
      edge.style.opacity = '1';
    } else {
      edge.setAttribute('stroke-width', '1.5');
      edge.style.opacity = '0.45';
    }
  });

  // Populate Inspector
  const emptyState = document.getElementById('graph-inspector-empty');
  const contentState = document.getElementById('graph-inspector-content');
  if (emptyState && contentState) {
    emptyState.classList.add('hidden');
    contentState.classList.remove('hidden');
    contentState.classList.add('flex');
  }

  document.getElementById('inspect-category').innerText = node.category;
  document.getElementById('inspect-title').innerText = node.label;
  document.getElementById('inspect-description').innerText = node.description;
  document.getElementById('inspect-score-val').innerText = `${Math.round(node.score)}%`;

  const bar = document.getElementById('inspect-score-bar');
  if (bar) {
    bar.style.width = `${node.score}%`;
    bar.className = `h-full rounded-full transition-all duration-300 ${node.score >= 75 ? 'bg-emerald-500' : (node.score >= 50 ? 'bg-amber-500' : 'bg-rose-500')}`;
  }

  const statusPill = document.getElementById('inspect-status-pill');
  if (statusPill) {
    statusPill.innerText = `${Math.round(node.score)}% Mastery • ${node.status}`;
    if (node.score >= 75) {
      statusPill.className = 'text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200';
    } else if (node.score >= 50) {
      statusPill.className = 'text-xs font-semibold px-2.5 py-1 rounded-full bg-amber-50 text-amber-700 border border-amber-200';
    } else {
      statusPill.className = 'text-xs font-semibold px-2.5 py-1 rounded-full bg-rose-50 text-rose-700 border border-rose-200';
    }
  }

  // Populate Relationships
  const relContainer = document.getElementById('inspect-relations-list');
  if (relContainer && appState.graphData) {
    relContainer.innerHTML = '';

    const incoming = appState.graphData.edges.filter(e => e.target === nodeId);
    const outgoing = appState.graphData.edges.filter(e => e.source === nodeId);

    if (incoming.length === 0 && outgoing.length === 0) {
      relContainer.innerHTML = `<span class="text-slate-400 italic">No direct links documented.</span>`;
    }

    incoming.forEach(edge => {
      const srcNode = graphNodesMap[edge.source];
      if (!srcNode) return;
      const row = document.createElement('div');
      row.className = 'flex items-center justify-between p-2 rounded-lg bg-slate-50 border border-slate-100 cursor-pointer hover:bg-slate-100 transition';
      row.innerHTML = `
        <div class="flex items-center gap-1.5 truncate">
          <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-200/70 text-slate-700 font-semibold">${edge.relationship.replace(/_/g, ' ')}</span>
          <span class="text-slate-800 font-medium truncate">${escapeHtml(srcNode.label)}</span>
        </div>
        <span class="text-[11px] text-slate-400 shrink-0">Incoming</span>
      `;
      row.addEventListener('click', () => selectGraphNode(srcNode.id));
      relContainer.appendChild(row);
    });

    outgoing.forEach(edge => {
      const tgtNode = graphNodesMap[edge.target];
      if (!tgtNode) return;
      const row = document.createElement('div');
      row.className = 'flex items-center justify-between p-2 rounded-lg bg-slate-50 border border-slate-100 cursor-pointer hover:bg-slate-100 transition';
      row.innerHTML = `
        <div class="flex items-center gap-1.5 truncate">
          <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-100 text-blue-800 font-semibold">${edge.relationship.replace(/_/g, ' ')}</span>
          <span class="text-slate-800 font-medium truncate">${escapeHtml(tgtNode.label)}</span>
        </div>
        <span class="text-[11px] text-slate-400 shrink-0">Outgoing</span>
      `;
      row.addEventListener('click', () => selectGraphNode(tgtNode.id));
      relContainer.appendChild(row);
    });
  }

  // Bind Inspector Action Buttons
  const askBtn = document.getElementById('inspect-ask-notes-btn');
  if (askBtn) {
    askBtn.onclick = () => {
      switchTab('tutor');
      const input = document.getElementById('tutor-query-input');
      if (input) {
        input.value = `Explain the concept of ${node.label} and how it fits into ${node.topic}.`;
        submitTutorQuery();
      }
    };
  }

  const explainBtn = document.getElementById('inspect-explain-btn');
  if (explainBtn) {
    explainBtn.onclick = () => {
      switchTab('doubt');
      triggerDoubtSolver(node.label);
    };
  }

  const vivaBtn = document.getElementById('inspect-viva-btn');
  if (vivaBtn) {
    vivaBtn.onclick = () => {
      switchTab('viva');
      startNewVivaSession(node.topic);
    };
  }
}

function filterWeakGraphNodes(weakOnly) {
  isFilteringWeakNodes = weakOnly;
  const allBtn = document.getElementById('graph-filter-all-btn');
  const weakBtn = document.getElementById('graph-filter-weak-btn');

  if (weakOnly) {
    allBtn.className = 'px-2.5 py-1 text-xs font-medium rounded-md bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 transition';
    weakBtn.className = 'px-2.5 py-1 text-xs font-medium rounded-md bg-rose-600 text-white shadow-xs transition';
  } else {
    allBtn.className = 'px-2.5 py-1 text-xs font-medium rounded-md bg-blue-50 text-blue-700 border border-blue-200 transition';
    weakBtn.className = 'px-2.5 py-1 text-xs font-medium rounded-md bg-white hover:bg-rose-50 text-slate-700 border border-slate-200 transition';
  }

  document.querySelectorAll('.graph-node-group').forEach(el => {
    const isWeak = el.classList.contains('weak-node');
    if (weakOnly) {
      el.style.opacity = isWeak ? '1' : '0.25';
      el.style.filter = isWeak ? 'drop-shadow(0 0 8px rgba(225, 29, 72, 0.3))' : 'none';
    } else {
      el.style.opacity = '1';
      el.style.filter = 'none';
    }
  });
}

function resetGraphView() {
  const container = document.querySelector('.graph-canvas-container');
  if (container) {
    container.scrollTo({ left: 100, top: 50, behavior: 'smooth' });
  }
  document.querySelectorAll('.graph-edge-path').forEach(edge => {
    edge.style.opacity = '1';
    edge.setAttribute('stroke-width', '1.5');
  });
}

// ==========================================================================
// 9. Socratic Viva Interview Mode Controller
// ==========================================================================
let isVivaRecording = false;

function loadVivaView() {
  if (!appState.vivaSession) {
    // Ready state
  }
}

async function startNewVivaSession(topicOverride) {
  const topicSelect = document.getElementById('viva-topic-select');
  let chosenTopic = topicOverride || (topicSelect ? topicSelect.value : 'Sequential Modeling & RNNs');

  if (topicSelect && topicOverride) {
    for (let i = 0; i < topicSelect.options.length; i++) {
      if (topicSelect.options[i].value === topicOverride || topicSelect.options[i].text.includes(topicOverride)) {
        topicSelect.selectedIndex = i;
        chosenTopic = topicSelect.options[i].value;
        break;
      }
    }
  }

  try {
    const session = await api.startViva(chosenTopic, "Scholar");
    appState.vivaSession = session;

    // Reset UI
    const finalCard = document.getElementById('viva-final-card');
    if (finalCard) finalCard.classList.add('hidden');

    const historyContainer = document.getElementById('viva-history-container');
    if (historyContainer) historyContainer.innerHTML = '';

    document.getElementById('viva-round-badge').innerText = `Round ${session.round} of ${session.total_rounds}`;
    document.getElementById('viva-question-text').innerText = session.question;
    document.getElementById('viva-transcript-input').value = '';

    // Examiner voice introduction
    voiceTutor.speak(session.audio_intro || session.question);
    showToast(`Viva Exam Begun: Round 1 of ${session.total_rounds}`, "info");
  } catch (err) {
    showToast("Could not start viva: " + err.message, "error");
  }
}

function replayExaminerSpeech() {
  const qText = document.getElementById('viva-question-text');
  if (qText && qText.innerText) {
    voiceTutor.speak(qText.innerText);
  }
}

function toggleVivaSpeechRecognition() {
  const micBtn = document.getElementById('viva-mic-btn');
  const micText = document.getElementById('viva-mic-text');
  const statusLabel = document.getElementById('mic-status-label');

  if (isVivaRecording) {
    voiceTutor.stopListening();
    isVivaRecording = false;
    micBtn.classList.remove('mic-recording-pulse');
    micText.innerText = 'Click to Speak';
    statusLabel.innerText = 'Mic Idle';
    statusLabel.className = 'text-xs text-slate-400 font-medium';
  } else {
    isVivaRecording = true;
    micBtn.classList.add('mic-recording-pulse');
    micText.innerText = 'Listening... (Speak Now)';
    statusLabel.innerText = 'Recording Live';
    statusLabel.className = 'text-xs text-rose-600 font-bold animate-pulse';

    voiceTutor.startListening((transcript) => {
      const input = document.getElementById('viva-transcript-input');
      if (input) {
        input.value = input.value ? `${input.value} ${transcript}` : transcript;
      }
      isVivaRecording = false;
      micBtn.classList.remove('mic-recording-pulse');
      micText.innerText = 'Click to Speak';
      statusLabel.innerText = 'Speech Captured';
      statusLabel.className = 'text-xs text-emerald-600 font-medium';
      showToast("Speech captured into answer box", "success");
    });
  }
}

async function submitVivaDefense() {
  if (!appState.vivaSession || !appState.vivaSession.session_id) {
    showToast("Please click 'Begin Oral Exam' to initiate your examination session first.", "info");
    return;
  }

  const input = document.getElementById('viva-transcript-input');
  const transcript = input ? input.value.trim() : '';

  if (!transcript) {
    showToast("Please articulate your technical answer or explanation before submitting.", "info");
    return;
  }

  const submitBtn = document.getElementById('viva-submit-btn');
  submitBtn.disabled = true;
  submitBtn.innerHTML = `<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i><span>Examiner Evaluating...</span>`;
  lucide.createIcons();

  try {
    const res = await api.respondViva(appState.vivaSession.session_id, transcript);

    // Append to viva round history
    const historyContainer = document.getElementById('viva-history-container');
    if (historyContainer) {
      const roundCard = document.createElement('div');
      roundCard.className = 'human-card p-4 space-y-2.5 border-l-4 border-l-blue-600 bg-slate-50/50';
      roundCard.innerHTML = `
        <div class="flex items-center justify-between text-xs pb-1.5 border-b border-slate-200">
          <span class="font-bold text-slate-800">Round ${res.round || 'Completed'} Defense</span>
          <span class="font-mono font-semibold px-2 py-0.5 rounded-full ${res.score_this_round >= 70 ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}">
            Score: ${res.score_this_round || res.final_score}/100
          </span>
        </div>
        <div class="text-xs text-slate-700 bg-white p-2.5 rounded border border-slate-200">
          <strong class="text-slate-900 block mb-0.5">Your Defense:</strong>
          ${escapeHtml(transcript)}
        </div>
        <div class="text-xs text-slate-800 p-2.5 rounded bg-blue-50/70 border border-blue-200/60 leading-relaxed">
          <strong class="text-blue-900 block mb-0.5">Prof. Turing's Evaluation:</strong>
          ${escapeHtml(res.feedback || res.feedback_summary)}
        </div>
      `;
      historyContainer.prepend(roundCard);
    }

    if (res.is_complete) {
      // Show Final Oral Scorecard Card
      const finalCard = document.getElementById('viva-final-card');
      if (finalCard) {
        finalCard.classList.remove('hidden');
        document.getElementById('viva-final-score').innerText = `${res.final_score}%`;
        document.getElementById('viva-final-verdict').innerText = res.verdict;
        document.getElementById('viva-final-feedback').innerText = res.feedback_summary;
        document.getElementById('viva-xp-gain').innerText = `+${res.xp_awarded} XP`;
      }

      document.getElementById('viva-round-badge').innerText = 'Completed';
      document.getElementById('viva-question-text').innerText = `Examination concluded. Your oral grade has been recorded in the Competency Engine.`;
      input.value = '';

      playSuccessChime();
      triggerConfetti();
      showToast(`Viva Concluded! Grade: ${res.final_score}% (${res.verdict})`, "success");

      // Speak examiner verdict
      voiceTutor.speak(`Oral examination concluded. Your final score is ${res.final_score} percent, achieving ${res.verdict}. Outstanding technical defense!`);

      // Refresh Competency & XP
      await refreshGamificationUI();
      await refreshDashboard();
    } else {
      // Proceed to Next Round
      document.getElementById('viva-round-badge').innerText = `Round ${res.next_round} of 3`;
      document.getElementById('viva-question-text').innerText = res.next_question;
      input.value = '';
      showToast(`Round ${res.round} Score: ${res.score_this_round}/100`, "info");

      // Examiner speaks the follow-up question
      voiceTutor.speak(`${res.feedback} ${res.next_question}`);
    }
  } catch (err) {
    showToast("Error evaluating viva response: " + err.message, "error");
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = `<i data-lucide="send" class="w-3.5 h-3.5"></i><span>Submit Defense</span>`;
    lucide.createIcons();
  }
}

