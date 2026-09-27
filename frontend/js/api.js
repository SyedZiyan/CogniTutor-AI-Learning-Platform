// API Client for CogniTutor AI Learning Platform
const API_BASE = window.location.origin;

const api = {
  async getStatus() {
    const res = await fetch(`${API_BASE}/api/status`);
    return res.json();
  },

  async getDocuments() {
    const res = await fetch(`${API_BASE}/api/documents`);
    return res.json();
  },

  async getDocumentChunks(docId) {
    const res = await fetch(`${API_BASE}/api/documents/${docId}/chunks`);
    return res.json();
  },

  getDocumentFileUrl(docId) {
    return `${API_BASE}/api/documents/${encodeURIComponent(docId)}/file`;
  },

  async uploadDocument(file) {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}/api/upload`, {
      method: "POST",
      body: formData
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Upload failed");
    }
    return res.json();
  },

  async askTutor(query, topK = 4) {
    const res = await fetch(`${API_BASE}/api/tutor/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, top_k: topK })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to query tutor");
    }
    return res.json();
  },

  async solveDoubt(topicOrQuestion) {
    const res = await fetch(`${API_BASE}/api/tutor/doubt-solver`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic_or_question: topicOrQuestion })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to solve doubt");
    }
    return res.json();
  },

  async generateQuiz(topic = null, difficulty = "adaptive") {
    const url = new URL(`${API_BASE}/api/quiz/generate`);
    if (topic && topic !== "all") url.searchParams.append("topic", topic);
    if (difficulty) url.searchParams.append("difficulty", difficulty);
    const res = await fetch(url.toString());
    return res.json();
  },

  async evaluateMCQ(questionId, selectedOptionIndex, currentStreak = 0, currentDifficulty = "medium") {
    const res = await fetch(`${API_BASE}/api/quiz/evaluate-mcq`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question_id: questionId,
        selected_option_index: selectedOptionIndex,
        current_streak: currentStreak,
        current_difficulty: currentDifficulty
      })
    });
    return res.json();
  },

  async evaluateShortAnswer(questionId, studentAnswer) {
    const res = await fetch(`${API_BASE}/api/quiz/evaluate-short`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question_id: questionId,
        student_answer: studentAnswer
      })
    });
    return res.json();
  },

  async getCompetency() {
    const res = await fetch(`${API_BASE}/api/competency/analysis`);
    return res.json();
  },

  async getRoadmap() {
    const res = await fetch(`${API_BASE}/api/roadmap`);
    return res.json();
  },

  async toggleMilestone(milestoneId) {
    const res = await fetch(`${API_BASE}/api/roadmap/milestone/${milestoneId}/toggle`, {
      method: "POST"
    });
    return res.json();
  },

  async getGamification() {
    const res = await fetch(`${API_BASE}/api/gamification`);
    return res.json();
  },

  async unlockBadge(badgeId) {
    const res = await fetch(`${API_BASE}/api/gamification/badge/${badgeId}/unlock`, {
      method: "POST"
    });
    return res.json();
  },

  async updateSettings(settingsData) {
    const res = await fetch(`${API_BASE}/api/settings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(settingsData)
    });
    return res.json();
  },

  async getConceptGraph() {
    const res = await fetch(`${API_BASE}/api/graph`);
    return res.json();
  },

  async startViva(topic = "Sequential Modeling & RNNs", studentName = "Scholar") {
    const res = await fetch(`${API_BASE}/api/viva/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic, student_name: studentName })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to start viva examination");
    }
    return res.json();
  },

  async respondViva(sessionId, studentTranscript) {
    const res = await fetch(`${API_BASE}/api/viva/respond`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, student_transcript: studentTranscript })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to submit viva response");
    }
    return res.json();
  }
};

