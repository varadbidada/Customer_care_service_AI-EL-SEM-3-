// Simple E-commerce Chat Widget - No Drag/Resize
class SimpleChatWidget {
  constructor() {
    console.log("🚀 Initializing Simple Chat Widget...");

    // Basic state
    this.isOpen = false;
    this.isRecording = false;
    this.isSending = false;
    this.ttsEnabled = true;
    this.hasSpokenWithBrowser = false;
    this.socket = null;
    this.recognition = null;
    this.synthesis = window.speechSynthesis;

    // Initialize step by step
    this.initializeElements();
    this.initializeSocket();
    this.initializeEventListeners();
    this.initializeSpeechRecognition();
    this.initializeTTS();
    this.initializeQuickActions();

    // Set welcome time
    this.updateWelcomeTime();

    console.log("✅ Simple Chat Widget initialized successfully");
  }

  initializeElements() {
    console.log("🔧 Getting DOM elements...");

    this.elements = {
      chatButton: document.getElementById("chatButton"),
      chatPanel: document.getElementById("chatPanel"),
      chatMessages: document.getElementById("chatMessages"),
      chatInput: document.getElementById("chatInput"),
      chatSendBtn: document.getElementById("chatSendBtn"),
      chatVoiceBtn: document.getElementById("chatVoiceBtn"),
      chatTtsBtn: document.getElementById("chatTtsBtn"),
      chatMinimizeBtn: document.getElementById("chatMinimizeBtn"),
      chatCloseBtn: document.getElementById("chatCloseBtn"),
      chatNotification: document.getElementById("chatNotification"),
      typingIndicator: document.getElementById("typingIndicator"),
      connectionStatus: document.getElementById("connectionStatus"),
      ttsStatus: document.getElementById("ttsStatus"),
      welcomeTime: document.getElementById("welcomeTime"),
      quickActions: document.getElementById("quickActions"),
    };

    // Check critical elements
    if (!this.elements.chatButton || !this.elements.chatPanel) {
      console.error("❌ Critical chat elements missing!");
      return false;
    }

    console.log("✅ All elements found");
    return true;
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
    console.log("🎧 Setting up event listeners...");

    // Chat button - toggle widget
    this.elements.chatButton.addEventListener("click", () => {
      console.log("🖱️ Chat button clicked");
      this.toggleChatWidget();
    });

    // Chat controls
    this.elements.chatMinimizeBtn.addEventListener("click", () => {
      console.log("➖ Minimize button clicked");
      this.minimizeChatWidget();
    });

    this.elements.chatCloseBtn.addEventListener("click", () => {
      console.log("❌ Close button clicked");
      this.closeChatWidget();
    });

    // Send button
    this.elements.chatSendBtn.addEventListener("click", () => {
      console.log("🖱️ Send button clicked");
      this.sendMessage();
    });

    // Message input
    this.elements.chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        console.log("⌨️ Enter key pressed");
        this.sendMessage();
      }
    });

    this.elements.chatInput.addEventListener("input", () => {
      this.handleInputChange();
    });

    // Voice button
    if (this.elements.chatVoiceBtn) {
      this.elements.chatVoiceBtn.addEventListener("click", () => {
        console.log("🎤 Voice button clicked");
        this.toggleVoiceRecording();
      });
    }

    // TTS button
    if (this.elements.chatTtsBtn) {
      this.elements.chatTtsBtn.addEventListener("click", () => {
        console.log("🔊 TTS button clicked");
        this.toggleTTS();
      });
    }

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
        this.elements.chatInput.value = transcript;
        this.handleInputChange();
        this.sendMessage();
      };

      this.recognition.onerror = (event) => {
        console.error("❌ Speech recognition error:", event.error);
        this.isRecording = false;
        this.updateVoiceButton();
      };

      console.log("✅ Speech recognition initialized");
    } else {
      console.warn("⚠️ Speech recognition not supported");
      if (this.elements.chatVoiceBtn) {
        this.elements.chatVoiceBtn.style.display = "none";
      }
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
      if (this.elements.chatTtsBtn) {
        this.elements.chatTtsBtn.style.display = "none";
      }
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

  initializeQuickActions() {
    console.log("🎯 Initializing quick actions...");

    const quickActionBtns = document.querySelectorAll(".quick-action-btn");
    quickActionBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        const message = btn.getAttribute("data-message");
        if (message) {
          console.log("🎯 Quick action clicked:", message);
          this.sendQuickMessage(message);
        }
      });
    });

    console.log("✅ Quick actions initialized");
  }

  toggleChatWidget() {
    console.log("🔄 Toggling chat widget");
    if (this.isOpen) {
      this.minimizeChatWidget();
    } else {
      this.openChatWidget();
    }
  }

  openChatWidget() {
    console.log("📂 Opening chat widget");
    this.elements.chatPanel.classList.add("open");
    this.elements.chatNotification.style.display = "none";
    this.isOpen = true;

    // Focus on input
    setTimeout(() => {
      this.elements.chatInput.focus();
    }, 300);

    // Scroll to bottom
    this.scrollToBottom();
  }

  minimizeChatWidget() {
    console.log("📁 Minimizing chat widget");
    this.elements.chatPanel.classList.remove("open");
    this.isOpen = false;
  }

  closeChatWidget() {
    console.log("❌ Closing chat widget");
    this.minimizeChatWidget();
  }

  handleInputChange() {
    const message = this.elements.chatInput.value.trim();
    const isEmpty = message.length === 0;

    // Update send button state
    this.elements.chatSendBtn.disabled = isEmpty || this.isSending;

    // Auto-resize textarea
    this.autoResizeTextarea();
  }

  autoResizeTextarea() {
    const textarea = this.elements.chatInput;
    textarea.style.height = "auto";
    textarea.style.height = Math.min(textarea.scrollHeight, 100) + "px";
  }

  sendQuickMessage(message) {
    console.log("📤 Sending quick message:", message);

    // Hide quick actions after first use
    if (this.elements.quickActions) {
      this.elements.quickActions.style.display = "none";
    }

    // Set the message in input and send
    this.elements.chatInput.value = message;
    this.handleInputChange();
    this.sendMessage();
  }

  sendMessage() {
    if (this.isSending) {
      console.log("⚠️ Already sending a message");
      return;
    }

    const message = this.elements.chatInput.value.trim();
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
    this.elements.chatSendBtn.disabled = true;

    // Add user message to UI
    this.addMessage(message, "user");

    // Clear input
    this.elements.chatInput.value = "";
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
      this.elements.chatSendBtn.disabled = false;
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

    // Show notification if widget is closed
    if (!this.isOpen) {
      this.showNotification();
    }

    // Use browser TTS immediately if enabled
    if (this.ttsEnabled) {
      console.log("🔊 Using browser TTS for speech");
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
    messageDiv.className = `chat-message ${sender}-message`;

    const avatarDiv = document.createElement("div");
    avatarDiv.className = "message-avatar";
    avatarDiv.innerHTML =
      sender === "user"
        ? '<i class="fas fa-user"></i>'
        : '<i class="fas fa-robot"></i>';

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
    this.elements.chatMessages.appendChild(messageDiv);

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

  showNotification() {
    this.elements.chatNotification.style.display = "flex";
    // Auto-hide after 5 seconds
    setTimeout(() => {
      if (!this.isOpen) {
        this.elements.chatNotification.style.display = "none";
      }
    }, 5000);
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
      this.elements.chatVoiceBtn.classList.add("recording");
      this.elements.chatVoiceBtn.innerHTML = '<i class="fas fa-stop"></i>';
    } else {
      this.elements.chatVoiceBtn.classList.remove("recording");
      this.elements.chatVoiceBtn.innerHTML =
        '<i class="fas fa-microphone"></i>';
    }
  }

  toggleTTS() {
    this.ttsEnabled = !this.ttsEnabled;

    if (this.ttsEnabled) {
      this.elements.chatTtsBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
      console.log("🔊 TTS enabled");
    } else {
      this.elements.chatTtsBtn.innerHTML = '<i class="fas fa-volume-mute"></i>';
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

  updateConnectionStatus(connected) {
    const statusIndicator =
      this.elements.connectionStatus.querySelector(".status-indicator");
    const statusLabel =
      this.elements.connectionStatus.querySelector(".status-label");

    if (connected) {
      statusIndicator.classList.remove("disconnected");
      statusLabel.textContent = "Connected";
    } else {
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
      this.elements.chatMessages.scrollTop =
        this.elements.chatMessages.scrollHeight;
    }, 100);
  }
}

// E-commerce page functionality
class EcommercePage {
  constructor() {
    console.log("🛒 Initializing E-commerce Page...");
    this.initializeEventListeners();
    console.log("✅ E-commerce Page initialized");
  }

  initializeEventListeners() {
    // Search functionality
    const searchInput = document.getElementById("searchInput");
    const searchBtn = document.querySelector(".search-btn");

    if (searchInput && searchBtn) {
      searchBtn.addEventListener("click", () => {
        this.handleSearch(searchInput.value);
      });

      searchInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          this.handleSearch(searchInput.value);
        }
      });
    }

    // Category cards
    const categoryCards = document.querySelectorAll(".category-card");
    categoryCards.forEach((card) => {
      card.addEventListener("click", () => {
        const categoryName = card.querySelector("h3").textContent;
        this.handleCategoryClick(categoryName);
      });
    });

    // Product cards
    const productCards = document.querySelectorAll(".product-card");
    productCards.forEach((card) => {
      card.addEventListener("click", () => {
        const productName = card.querySelector("h3").textContent;
        this.handleProductClick(productName);
      });
    });

    // CTA button
    const ctaButton = document.querySelector(".cta-button");
    if (ctaButton) {
      ctaButton.addEventListener("click", () => {
        this.handleCTAClick();
      });
    }

    // Header actions
    const actionItems = document.querySelectorAll(".action-item");
    actionItems.forEach((item) => {
      item.addEventListener("click", () => {
        const actionText = item.querySelector("span").textContent;
        this.handleHeaderAction(actionText);
      });
    });
  }

  handleSearch(query) {
    console.log("🔍 Search query:", query);
    if (query.trim()) {
      alert(`Searching for: ${query}`);
    }
  }

  handleCategoryClick(categoryName) {
    console.log("📂 Category clicked:", categoryName);
    alert(`Browsing ${categoryName} category`);
  }

  handleProductClick(productName) {
    console.log("📦 Product clicked:", productName);
    alert(`Viewing ${productName} details`);
  }

  handleCTAClick() {
    console.log("🎯 CTA button clicked");
    alert("Redirecting to Campus Store!");
  }

  handleHeaderAction(actionText) {
    console.log("🔗 Header action:", actionText);
    switch (actionText.toLowerCase()) {
      case "account":
        alert("Opening Account page");
        break;
      case "orders":
        alert("Opening Orders page");
        break;
      case "cart":
        alert("Opening Shopping Cart");
        break;
      default:
        alert(`Opening ${actionText} page`);
    }
  }
}

// Initialize everything when the page loads
document.addEventListener("DOMContentLoaded", () => {
  console.log("📄 DOM loaded, initializing components...");

  try {
    // Initialize e-commerce page functionality
    new EcommercePage();

    // Initialize simple chat widget
    new SimpleChatWidget();

    console.log("🎉 All components initialized successfully!");
  } catch (error) {
    console.error("❌ Initialization failed:", error);
    alert("Page initialization failed. Please refresh the page.");
  }
});
