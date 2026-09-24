// Voice AI Tutor module supporting Speech-to-Text and Text-to-Speech
class VoiceAITutor {
  constructor() {
    this.recognition = null;
    this.isListening = false;
    this.isSpeaking = false;
    this.synth = window.speechSynthesis || null;
    this.selectedVoice = null;
    this.initRecognition();
    this.initVoices();
  }

  initRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = false;
      this.recognition.interimResults = false;
      this.recognition.lang = 'en-US';

      this.recognition.onstart = () => {
        this.isListening = true;
        this.updateMicUI(true);
      };

      this.recognition.onend = () => {
        this.isListening = false;
        this.updateMicUI(false);
      };

      this.recognition.onerror = (event) => {
        console.warn("Speech recognition error:", event.error);
        this.isListening = false;
        this.updateMicUI(false);
      };
    } else {
      console.warn("Speech Recognition API not supported in this browser.");
    }
  }

  initVoices() {
    if (!this.synth) return;
    const loadVoices = () => {
      const voices = this.synth.getVoices();
      // Prefer natural English voices (Google, Natural, Samantha, Microsoft Zira/David)
      this.selectedVoice = voices.find(v => v.lang.startsWith("en") && (v.name.includes("Natural") || v.name.includes("Google") || v.name.includes("Samantha"))) || voices.find(v => v.lang.startsWith("en")) || voices[0];
    };
    loadVoices();
    if (this.synth.onvoiceschanged !== undefined) {
      this.synth.onvoiceschanged = loadVoices;
    }
  }

  startListening(onResultCallback) {
    if (!this.recognition) {
      alert("Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari.");
      return;
    }
    if (this.isSpeaking) {
      this.stopSpeaking();
    }
    this.recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      if (onResultCallback) {
        onResultCallback(transcript);
      }
    };
    try {
      this.recognition.start();
    } catch (e) {
      console.warn("Recognition already started:", e);
    }
  }

  stopListening() {
    if (this.recognition && this.isListening) {
      this.recognition.stop();
      this.isListening = false;
      this.updateMicUI(false);
    }
  }

  speak(text, onEndCallback) {
    if (!this.synth) return;
    this.stopSpeaking();

    // Clean text of markdown symbols and LaTeX formulas for smooth speech
    let cleanText = text
      .replace(/\\\(.*?\\\)/g, "")
      .replace(/\$\$.*?\$\$/g, "")
      .replace(/\`\`\`[\s\S]*?\`\`\`/g, "Code example provided below.")
      .replace(/[*#_`>]/g, "")
      .replace(/\[Source:.*?\]/g, "")
      .replace(/\s+/g, " ")
      .trim();

    if (!cleanText) return;

    const utterance = new SpeechSynthesisUtterance(cleanText);
    if (this.selectedVoice) {
      utterance.voice = this.selectedVoice;
    }
    utterance.rate = 1.05;
    utterance.pitch = 1.0;

    utterance.onstart = () => {
      this.isSpeaking = true;
      this.updateAudioWaveUI(true);
    };

    utterance.onend = () => {
      this.isSpeaking = false;
      this.updateAudioWaveUI(false);
      if (onEndCallback) onEndCallback();
    };

    utterance.onerror = () => {
      this.isSpeaking = false;
      this.updateAudioWaveUI(false);
    };

    this.synth.speak(utterance);
  }

  stopSpeaking() {
    if (this.synth && this.isSpeaking) {
      this.synth.cancel();
      this.isSpeaking = false;
      this.updateAudioWaveUI(false);
    }
  }

  updateMicUI(active) {
    const micBtns = document.querySelectorAll(".voice-mic-btn");
    micBtns.forEach(btn => {
      if (active) {
        btn.classList.add("bg-rose-600", "animate-pulse", "text-white");
        btn.classList.remove("bg-indigo-600/30", "text-indigo-400");
      } else {
        btn.classList.remove("bg-rose-600", "animate-pulse", "text-white");
        btn.classList.add("bg-indigo-600/30", "text-indigo-400");
      }
    });

    const statusBadge = document.getElementById("voice-status-badge");
    if (statusBadge) {
      statusBadge.classList.toggle("hidden", !active);
    }
  }

  updateAudioWaveUI(active) {
    const waveContainers = document.querySelectorAll(".audio-wave-container");
    waveContainers.forEach(c => {
      c.classList.toggle("hidden", !active);
    });
  }
}

const voiceTutor = new VoiceAITutor();
