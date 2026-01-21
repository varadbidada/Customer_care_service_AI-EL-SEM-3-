class KiroChat {
  constructor() {
    console.log("🚀 Initializing Kiro Chat...");

    // Initialize state
    this.isRecording = false;
    this.isSending = false;
    this.ttsEnabled = true;
    this.hasSpokenWithBrowser = false;
    this.socket = null;
    this.recognition = null;
    this.synthesis = window.speechSynthesis;

    // Initialize components
    this.initializeElements();
    this.initializeSocket();
    this.initializeEventListeners();
    this.initializeSpeechRecognition();
    this.initializeTTS();

    // Set welcome time
    this.updateWelcomeTime();

    console.log("✅ Kiro Chat initialized successfully");
  }

  initializeElements() {
    console.log("🔧 Initializing DOM elements...");

    // Get all required elements
    this.elements = {
      messagesContainer: document.getElementById("messagesContainer"),
      messageInput: document.getElementById("messageInput"),
      sendBtn: document.getElementById("sendBtn"),
      voiceBtn: document.getElementById("voiceBtn"),
      voiceIcon: document.getElementById("voiceIcon"),
      ttsBtn: document.getElementById("ttsBtn"),
      clearBtn: document.getElementById("clearBtn"),
      typingIndicator: document.getElementById("typingIndicator"),
      statusDot: document.getElementById("statusDot"),
      statusText: document.getElementById("statusText"),
      connectionStatus: document.getElementById("connectionStatus"),
      ttsStatus: document.getElementById("ttsStatus"),
      welcomeTime: document.getElementById("welcomeTime"),
    };

    // Validate elements
    for (const [name, element] of Object.entries(this.elements)) {
      if (!element) {
        console.error(`❌ Missing element: ${name}`);
      } else {
        console.log(`✅ Found element: ${name}`);
      }
    }

    console.log("✅ DOM elements initialized");
  }

  initializeSocket() {
    console.log("🔌 Initializing Socket.IO...");

    try {
      this.socket = io();

      this.socket.on("connect", () => {
        console.log("✅ Socket connected");
        this.updateConnectionStatus(true);
      });

      this.socket.on("disconnect", () => {
        console.log("❌ Socket disconnected");
        this.updateConnectionStatus(false);
      });

      this.socket.on("connection_confirmed", (data) => {
        console.log("🎉 Connection confirmed:", data);
      });

      this.socket.on("bot_message", (data) => {
        console.log("📨 Received bot message:", data);
        this.handleBotMessage(data);
      });

      // NEW: Handle audio ready event
      this.socket.on("audio_ready", (data) => {
        console.log("🎤 Audio ready:", data);
        this.handleAudioReady(data);
      });

      console.log("✅ Socket.IO initialized");
    } catch (error) {
      console.error("❌ Socket.IO initialization failed:", error);
      this.updateConnectionStatus(false);
    }
  }

  initializeEventListeners() {
    console.log("🎧 Initializing event listeners...");

    // Send button
    this.elements.sendBtn.addEventListener("click", () => {
      console.log("🖱️ Send button clicked");
      this.sendMessage();
    });

    // Message input
    this.elements.messageInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        console.log("⌨️ Enter key pressed");
        this.sendMessage();
      }
    });

    this.elements.messageInput.addEventListener("input", () => {
      this.handleInputChange();
    });

    // Voice button
    this.elements.voiceBtn.addEventListener("click", () => {
      console.log("🎤 Voice button clicked");
      this.toggleVoiceRecording();
    });

    // TTS button
    this.elements.ttsBtn.addEventListener("click", () => {
      console.log("🔊 TTS button clicked");
      this.toggleTTS();
    });

    // Clear button
    this.elements.clearBtn.addEventListener("click", () => {
      console.log("🗑️ Clear button clicked");
      this.clearChat();
    });

    console.log("✅ Event listeners initialized");
  }

  initializeSpeechRecognition() {
    console.log("🎤 Initializing speech recognition...");

    if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
      const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;
      this.recognition = new SpeechRecognition();

      this.recognition.continuous = false;
      this.recognition.interimResults = false;
      this.recognition.lang = "en-US";

      this.recognition.onstart = () => {
        console.log("🎤 Speech recognition started");
        this.isRecording = true;
        this.updateVoiceButton();
      };

      this.recognition.onend = () => {
        console.log("🎤 Speech recognition ended");
        this.isRecording = false;
        this.updateVoiceButton();
      };

      this.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        console.log("🎤 Speech recognized:", transcript);
        this.elements.messageInput.value = transcript;
        this.handleInputChange();
        this.sendMessage();
      };

      this.recognition.onerror = (event) => {
        console.error("❌ Speech recognition error:", event.error);
        this.isRecording = false;
        this.updateVoiceButton();

        if (event.error === "not-allowed") {
          alert(
            "Microphone permission denied. Please allow microphone access and try again.",
          );
        }
      };

      console.log("✅ Speech recognition initialized");
    } else {
      console.warn("⚠️ Speech recognition not supported");
      this.elements.voiceBtn.style.display = "none";
    }
  }

  initializeTTS() {
    console.log("🔊 Initializing TTS...");

    if (this.synthesis) {
      this.synthesis.addEventListener("voiceschanged", () => {
        this.loadVoices();
      });
      this.loadVoices();
      console.log("✅ TTS initialized");
    } else {
      console.warn("⚠️ TTS not supported");
      this.elements.ttsBtn.style.display = "none";
    }
  }

  loadVoices() {
    this.voices = this.synthesis.getVoices();
    this.preferredVoice = this.voices.find(
      (voice) =>
        voice.name.includes("Google") ||
        voice.name.includes("Microsoft") ||
        (voice.lang.startsWith("en") && voice.localService),
    );
  }

  handleInputChange() {
    const message = this.elements.messageInput.value.trim();
    const isEmpty = message.length === 0;

    // Update send button state
    this.elements.sendBtn.disabled = isEmpty || this.isSending;

    // Auto-resize textarea
    this.autoResizeTextarea();
  }

  autoResizeTextarea() {
    const textarea = this.elements.messageInput;
    textarea.style.height = "auto";
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + "px";
  }

  sendMessage() {
    if (this.isSending) {
      console.log("⚠️ Already sending a message");
      return;
    }

    const message = this.elements.messageInput.value.trim();
    if (!message) {
      console.log("⚠️ Empty message");
      return;
    }

    if (!this.socket || !this.socket.connected) {
      console.error("❌ Socket not connected");
      alert("Connection lost. Please refresh the page.");
      return;
    }

    console.log("📤 Sending message:", message);

    // Reset TTS flag for new conversation
    this.hasSpokenWithBrowser = false;

    // Update UI state
    this.isSending = true;
    this.elements.sendBtn.disabled = true;

    // Add user message to UI
    this.addMessage(message, "user");

    // Clear input
    this.elements.messageInput.value = "";
    this.handleInputChange();

    // Show typing indicator
    this.showTypingIndicator();

    // Send to server
    const payload = {
      message: message,
      type: "text",
      session_id: this.socket.id,
    };

    console.log("📡 Emitting user_message:", payload);

    try {
      this.socket.emit("user_message", payload);
      console.log("✅ Message sent successfully");
    } catch (error) {
      console.error("❌ Error sending message:", error);
      this.isSending = false;
      this.elements.sendBtn.disabled = false;
      this.hideTypingIndicator();
      alert("Failed to send message. Please try again.");
    }
  }

  handleBotMessage(data) {
    console.log("🤖 Processing bot message");

    // Hide typing indicator
    this.hideTypingIndicator();

    // Reset sending state
    this.isSending = false;
    this.handleInputChange();

    // Add bot message to UI
    this.addMessage(data.message, "bot");

    // Use browser TTS immediately if enabled (fallback for when server TTS unavailable)
    if (this.ttsEnabled) {
      console.log("🔊 Using browser TTS for immediate speech");
      this.speakMessage(data.message);
      this.hasSpokenWithBrowser = true;
    }
  }

  handleAudioReady(data) {
    console.log("🎤 Handling audio ready event:", data);

    // Only use server audio if TTS is enabled and we haven't already spoken with browser TTS
    if (this.ttsEnabled && data.audio_url && !this.hasSpokenWithBrowser) {
      // Cancel browser TTS if server audio is available
      if (this.synthesis) {
        this.synthesis.cancel();
      }
      this.playServerAudio(data.audio_url);
    }

    // Reset flag for next message
    this.hasSpokenWithBrowser = false;
  }

  playServerAudio(audioUrl) {
    console.log("🔊 Playing server-generated audio:", audioUrl);

    try {
      // Show TTS status
      this.showTTSStatus();

      // Create and play audio
      const audio = new Audio(audioUrl);

      audio.onloadstart = () => {
        console.log("🎵 Audio loading started");
      };

      audio.oncanplay = () => {
        console.log("🎵 Audio can play");
        audio.play().catch((error) => {
          console.error("❌ Audio play failed:", error);
          this.hideTTSStatus();
        });
      };

      audio.onended = () => {
        console.log("🎵 Audio playback ended");
        this.hideTTSStatus();
      };

      audio.onerror = (error) => {
        console.error("❌ Audio error:", error);
        this.hideTTSStatus();
        // Fallback to browser TTS if server audio fails
        this.speakMessage(this.lastBotMessage);
      };

      // Store last message for fallback
      this.lastBotMessage = data.message || "";
    } catch (error) {
      console.error("❌ Error playing server audio:", error);
      this.hideTTSStatus();
      // Fallback to browser TTS
      this.speakMessage(this.lastBotMessage);
    }
  }

  addMessage(text, sender) {
    console.log(`💬 Adding ${sender} message:`, text);

    // Store last bot message for potential audio fallback
    if (sender === "bot") {
      this.lastBotMessage = text;
    }

    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}-message`;

    const avatarDiv = document.createElement("div");
    avatarDiv.className = "message-avatar";
    avatarDiv.innerHTML =
      sender === "user" ? "<span>👤</span>" : "<span>🤖</span>";

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    const bubbleDiv = document.createElement("div");
    bubbleDiv.className = "message-bubble";

    const textP = document.createElement("p");
    textP.textContent = text;

    const timeDiv = document.createElement("div");
    timeDiv.className = "message-time";
    timeDiv.textContent = this.getCurrentTime();

    // Assemble message
    bubbleDiv.appendChild(textP);
    contentDiv.appendChild(bubbleDiv);
    contentDiv.appendChild(timeDiv);
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);

    // Add to container
    this.elements.messagesContainer.appendChild(messageDiv);

    // Scroll to bottom
    this.scrollToBottom();
  }

  showTypingIndicator() {
    this.elements.typingIndicator.style.display = "flex";
    this.scrollToBottom();
  }

  hideTypingIndicator() {
    this.elements.typingIndicator.style.display = "none";
  }

  toggleVoiceRecording() {
    if (!this.recognition) {
      alert("Speech recognition is not supported in this browser.");
      return;
    }

    if (this.isRecording) {
      console.log("🛑 Stopping voice recording");
      this.recognition.stop();
    } else {
      console.log("▶️ Starting voice recording");
      try {
        this.recognition.start();
      } catch (error) {
        console.error("❌ Error starting voice recognition:", error);
        alert("Failed to start voice recording: " + error.message);
      }
    }
  }

  updateVoiceButton() {
    if (this.isRecording) {
      this.elements.voiceBtn.classList.add("recording");
      this.elements.voiceIcon.textContent = "🔴";
    } else {
      this.elements.voiceBtn.classList.remove("recording");
      this.elements.voiceIcon.textContent = "🎤";
    }
  }

  toggleTTS() {
    this.ttsEnabled = !this.ttsEnabled;

    if (this.ttsEnabled) {
      this.elements.ttsBtn.innerHTML = "<span>🔊</span>";
      console.log("🔊 TTS enabled");
    } else {
      this.elements.ttsBtn.innerHTML = "<span>🔇</span>";
      this.synthesis.cancel(); // Stop any ongoing speech
      this.hideTTSStatus();
      console.log("🔇 TTS disabled");
    }
  }

  speakMessage(text) {
    if (!this.synthesis || !this.ttsEnabled) return;

    // Cancel any ongoing speech
    this.synthesis.cancel();

    // Clean text for TTS
    const cleanText = text
      .replace(/<[^>]*>/g, "") // Remove HTML tags
      .replace(/[🤖👤🎯🔊✨]/g, "") // Remove emojis
      .trim();

    if (!cleanText) return;

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 0.9;
    utterance.pitch = 1.0;
    utterance.volume = 0.8;

    if (this.preferredVoice) {
      utterance.voice = this.preferredVoice;
    }

    utterance.onstart = () => {
      this.showTTSStatus();
    };

    utterance.onend = () => {
      this.hideTTSStatus();
    };

    utterance.onerror = () => {
      this.hideTTSStatus();
    };

    this.synthesis.speak(utterance);
  }

  showTTSStatus() {
    this.elements.ttsStatus.style.display = "flex";
  }

  hideTTSStatus() {
    this.elements.ttsStatus.style.display = "none";
  }

  clearChat() {
    if (confirm("Are you sure you want to clear the chat?")) {
      // Remove all messages except welcome message
      const messages = this.elements.messagesContainer.querySelectorAll(
        ".message:not(.bot-message)",
      );
      messages.forEach((msg) => msg.remove());

      // Also remove the first bot message if it's not the welcome
      const botMessages =
        this.elements.messagesContainer.querySelectorAll(".bot-message");
      if (botMessages.length > 1) {
        for (let i = 1; i < botMessages.length; i++) {
          botMessages[i].remove();
        }
      }

      console.log("🗑️ Chat cleared");
    }
  }

  updateConnectionStatus(connected) {
    const statusIndicator =
      this.elements.connectionStatus.querySelector(".status-indicator");
    const statusLabel =
      this.elements.connectionStatus.querySelector(".status-label");

    if (connected) {
      this.elements.statusDot.style.background = "#00ff88";
      this.elements.statusText.textContent = "Online";
      statusIndicator.classList.remove("disconnected");
      statusLabel.textContent = "Connected";
    } else {
      this.elements.statusDot.style.background = "#ff4757";
      this.elements.statusText.textContent = "Offline";
      statusIndicator.classList.add("disconnected");
      statusLabel.textContent = "Disconnected";
    }
  }

  updateWelcomeTime() {
    if (this.elements.welcomeTime) {
      this.elements.welcomeTime.textContent = this.getCurrentTime();
    }
  }

  getCurrentTime() {
    return new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  scrollToBottom() {
    setTimeout(() => {
      this.elements.messagesContainer.scrollTop =
        this.elements.messagesContainer.scrollHeight;
    }, 100);
  }
}

// Initialize the chat when the page loads
document.addEventListener("DOMContentLoaded", () => {
  console.log("📄 DOM loaded, initializing Kiro Chat...");
  new KiroChat();
});
