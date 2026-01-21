// E-commerce page with integrated chatbot widget
class EcommerceChatWidget {
  constructor() {
    console.log("🚀 Initializing E-commerce Chat Widget...");

    // Initialize basic state first
    this.isOpen = false;
    this.isRecording = false;
    this.isSending = false;
    this.ttsEnabled = true;
    this.hasSpokenWithBrowser = false;
    this.socket = null;
    this.recognition = null;
    this.synthesis = window.speechSynthesis;

    // Advanced features state (initialize later)
    this.isDragging = false;
    this.isResizing = false;
    this.dragOffset = { x: 0, y: 0 };
    this.resizeData = {
      direction: null,
      startX: 0,
      startY: 0,
      startWidth: 0,
      startHeight: 0,
      startLeft: 0,
      startTop: 0,
    };
    this.defaultSize = { width: 420, height: 650 };
    this.currentPosition = { right: 0, bottom: 90 };

    // Initialize step by step with error handling
    this.initializeStepByStep();
  }

  async initializeStepByStep() {
    try {
      // Step 1: Initialize DOM elements (critical)
      console.log("📋 Step 1: Initializing DOM elements...");
      const elementsOk = this.initializeElements();
      if (!elementsOk) {
        throw new Error("Critical DOM elements missing");
      }

      // Step 2: Basic event listeners (critical)
      console.log("🎧 Step 2: Setting up basic event listeners...");
      this.initializeBasicEventListeners();

      // Step 3: Socket connection (critical for chat)
      console.log("🔌 Step 3: Initializing Socket.IO...");
      this.initializeSocket();

      // Step 4: Optional features (non-critical)
      console.log("🎤 Step 4: Initializing optional features...");
      this.initializeSpeechRecognition();
      this.initializeTTS();
      this.initializeQuickActions();

      // Step 5: Advanced features (non-critical)
      console.log("🎯 Step 5: Initializing advanced features...");
      this.initializeDragAndResize();

      // Step 6: Final setup
      console.log("⚡ Step 6: Final setup...");
      this.updateWelcomeTime();

      console.log("✅ SupportX AI Chat Widget initialized successfully");
      
      // Test basic functionality
      this.testBasicFunctionality();
      
    } catch (error) {
      console.error("❌ Failed to initialize chat widget:", error);
      console.log("🔄 Attempting fallback initialization...");
      this.initializeFallback();
    }
  }

  testBasicFunctionality() {
    console.log("🧪 Testing basic chat functionality...");
    
    if (this.elements.chatButton && this.elements.chatPanel) {
      console.log("✅ Basic elements available");
      
      // Test click handler
      const testClick = () => {
        console.log("🎯 Chat button click test successful");
      };
      
      // Temporarily test the click
      this.elements.chatButton.addEventListener("click", testClick, { once: true });
      
      console.log("✅ Basic functionality test complete");
    } else {
      console.error("❌ Basic functionality test failed - missing elements");
    }
  }

  initializeFallback() {
    console.log("🆘 Initializing fallback mode...");
    
    try {
      // Minimal functionality
      const chatButton = document.getElementById("chatButton");
      const chatPanel = document.getElementById("chatPanel");
      
      if (chatButton && chatPanel) {
        chatButton.addEventListener("click", () => {
          console.log("🔄 Fallback: Toggling chat panel");
          chatPanel.classList.toggle("open");
          this.isOpen = !this.isOpen;
        });
        
        console.log("✅ Fallback mode initialized - basic toggle works");
      } else {
        console.error("❌ Fallback failed - critical elements missing");
      }
    } catch (error) {
      console.error("❌ Fallback initialization failed:", error);
    }
  }

  initializeElements() {
    console.log("🔧 Initializing DOM elements...");

    // Get all required elements
    this.elements = {
      // Chat widget elements
      chatButton: document.getElementById("chatButton"),
      chatPanel: document.getElementById("chatPanel"),
      chatMessages: document.getElementById("chatMessages"),
      chatInput: document.getElementById("chatInput"),
      chatSendBtn: document.getElementById("chatSendBtn"),
      chatVoiceBtn: document.getElementById("chatVoiceBtn"),
      chatTtsBtn: document.getElementById("chatTtsBtn"),
      chatMinimizeBtn: document.getElementById("chatMinimizeBtn"),
      chatCloseBtn: document.getElementById("chatCloseBtn"),
      chatResetSizeBtn: document.getElementById("chatResetSizeBtn"),
      chatNotification: document.getElementById("chatNotification"),
      typingIndicator: document.getElementById("typingIndicator"),
      connectionStatus: document.getElementById("connectionStatus"),
      ttsStatus: document.getElementById("ttsStatus"),
      welcomeTime: document.getElementById("welcomeTime"),
      quickActions: document.getElementById("quickActions"),
      chatDragHandle: document.getElementById("chatDragHandle"),
    };

    // Validate critical elements
    const criticalElements = ['chatButton', 'chatPanel', 'chatMessages', 'chatInput', 'chatSendBtn'];
    let missingCritical = false;

    for (const [name, element] of Object.entries(this.elements)) {
      if (!element) {
        if (criticalElements.includes(name)) {
          console.error(`❌ CRITICAL: Missing element: ${name}`);
          missingCritical = true;
        } else {
          console.warn(`⚠️ Optional element missing: ${name}`);
        }
      } else {
        console.log(`✅ Found element: ${name}`);
      }
    }

    if (missingCritical) {
      console.error("❌ Critical elements missing - chat may not work properly");
      alert("Chat widget initialization failed. Please refresh the page.");
      return false;
    }

    console.log("✅ DOM elements initialized");
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

  initializeBasicEventListeners() {
    console.log("🎧 Initializing basic event listeners...");

    try {
      // Chat button - toggle widget (CRITICAL)
      if (this.elements.chatButton) {
        this.elements.chatButton.addEventListener("click", () => {
          console.log("🖱️ Chat button clicked");
          this.toggleChatWidget();
        });
        console.log("✅ Chat button listener added");
      } else {
        throw new Error("Chat button not found");
      }

      // Chat controls (IMPORTANT)
      if (this.elements.chatMinimizeBtn) {
        this.elements.chatMinimizeBtn.addEventListener("click", () => {
          console.log("➖ Minimize button clicked");
          this.minimizeChatWidget();
        });
      }

      if (this.elements.chatCloseBtn) {
        this.elements.chatCloseBtn.addEventListener("click", () => {
          console.log("❌ Close button clicked");
          this.closeChatWidget();
        });
      }

      // Send functionality (CRITICAL)
      if (this.elements.chatSendBtn) {
        this.elements.chatSendBtn.addEventListener("click", () => {
          console.log("🖱️ Send button clicked");
          this.sendMessage();
        });
      }

      if (this.elements.chatInput) {
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
      }

      // TTS button (OPTIONAL)
      if (this.elements.chatTtsBtn) {
        this.elements.chatTtsBtn.addEventListener("click", () => {
          console.log("🔊 TTS button clicked");
          this.toggleTTS();
        });
      }

      // Reset size button (OPTIONAL)
      if (this.elements.chatResetSizeBtn) {
        this.elements.chatResetSizeBtn.addEventListener("click", () => {
          console.log("🔄 Reset size button clicked");
          this.resetChatSize();
        });
      }

      console.log("✅ Basic event listeners initialized");
    } catch (error) {
      console.error("❌ Error initializing basic event listeners:", error);
      throw error;
    }
  }

  initializeEventListeners() {
    console.log("🎧 Initializing additional event listeners...");

    try {
      // Voice button (OPTIONAL)
      if (this.elements.chatVoiceBtn) {
        this.elements.chatVoiceBtn.addEventListener("click", () => {
          console.log("🎤 Voice button clicked");
          this.toggleVoiceRecording();
        });
      }

      // Close widget when clicking outside (OPTIONAL)
      document.addEventListener("click", (e) => {
        if (
          this.isOpen &&
          this.elements.chatPanel &&
          this.elements.chatButton &&
          this.elements.ttsStatus &&
          !this.elements.chatPanel.contains(e.target) &&
          !this.elements.chatButton.contains(e.target)
        ) {
          // Don't close if clicking on TTS status
          if (!this.elements.ttsStatus.contains(e.target)) {
            this.minimizeChatWidget();
          }
        }
      });

      console.log("✅ Additional event listeners initialized");
    } catch (error) {
      console.error("❌ Error initializing additional event listeners:", error);
      // Don't throw - these are optional
    }
  }

  initializeQuickActions() {
    console.log("🎯 Initializing quick actions...");

    const quickActionBtns = document.querySelectorAll(".quick-action-btn");
    quickActionBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        const message = btn.getAttribute("data-message");
        if (message && !btn.classList.contains("used")) {
          console.log("🎯 Quick action clicked:", message);

          // Mark button as used
          btn.classList.add("used");

          // Send the message
          this.sendQuickMessage(message);
        }
      });
    });

    console.log("✅ Quick actions initialized");
  }

  initializeDragAndResize() {
    console.log("🎯 Initializing drag and resize functionality...");

    try {
      // Drag functionality
      if (this.elements.chatDragHandle) {
        this.elements.chatDragHandle.addEventListener("mousedown", (e) => {
          this.startDrag(e);
        });
      } else {
        console.warn("⚠️ Drag handle not found");
      }

      // Resize functionality
      const resizeHandles = document.querySelectorAll(".resize-handle");
      if (resizeHandles.length > 0) {
        resizeHandles.forEach((handle) => {
          handle.addEventListener("mousedown", (e) => {
            this.startResize(e, handle.getAttribute("data-direction"));
          });
        });
      } else {
        console.warn("⚠️ Resize handles not found");
      }

      // Global mouse events
      document.addEventListener("mousemove", (e) => {
        if (this.isDragging) {
          this.drag(e);
        } else if (this.isResizing) {
          this.resize(e);
        }
      });

      document.addEventListener("mouseup", () => {
        this.stopDrag();
        this.stopResize();
      });

      // Prevent text selection during drag/resize
      document.addEventListener("selectstart", (e) => {
        if (this.isDragging || this.isResizing) {
          e.preventDefault();
        }
      });

      console.log("✅ Drag and resize initialized");
    } catch (error) {
      console.error("❌ Error initializing drag and resize:", error);
      // Continue without drag/resize functionality
    }
  }

  startDrag(e) {
    e.preventDefault();
    this.isDragging = true;
    this.elements.chatPanel.classList.add("dragging");

    const rect = this.elements.chatPanel.getBoundingClientRect();
    this.dragOffset.x = e.clientX - rect.left;
    this.dragOffset.y = e.clientY - rect.top;

    console.log("🎯 Started dragging");
  }

  drag(e) {
    if (!this.isDragging) return;

    const x = e.clientX - this.dragOffset.x;
    const y = e.clientY - this.dragOffset.y;

    // Keep within viewport bounds
    const maxX = window.innerWidth - this.elements.chatPanel.offsetWidth;
    const maxY = window.innerHeight - this.elements.chatPanel.offsetHeight;

    const boundedX = Math.max(0, Math.min(x, maxX));
    const boundedY = Math.max(0, Math.min(y, maxY));

    this.elements.chatPanel.style.left = boundedX + "px";
    this.elements.chatPanel.style.top = boundedY + "px";
    this.elements.chatPanel.style.right = "auto";
    this.elements.chatPanel.style.bottom = "auto";
  }

  stopDrag() {
    if (!this.isDragging) return;

    this.isDragging = false;
    this.elements.chatPanel.classList.remove("dragging");
    console.log("🎯 Stopped dragging");
  }

  startResize(e, direction) {
    e.preventDefault();
    e.stopPropagation();
    
    this.isResizing = true;
    this.elements.chatPanel.classList.add("resizing");

    const rect = this.elements.chatPanel.getBoundingClientRect();
    
    this.resizeData = {
      direction: direction,
      startX: e.clientX,
      startY: e.clientY,
      startWidth: rect.width,
      startHeight: rect.height,
      startLeft: rect.left,
      startTop: rect.top
    };

    console.log("🎯 Started resizing:", direction);
  }

  resize(e) {
    if (!this.isResizing) return;

    const deltaX = e.clientX - this.resizeData.startX;
    const deltaY = e.clientY - this.resizeData.startY;
    const direction = this.resizeData.direction;

    let newWidth = this.resizeData.startWidth;
    let newHeight = this.resizeData.startHeight;
    let newLeft = this.resizeData.startLeft;
    let newTop = this.resizeData.startTop;

    // Calculate new dimensions based on resize direction
    if (direction.includes("e")) {
      newWidth = this.resizeData.startWidth + deltaX;
    }
    if (direction.includes("w")) {
      newWidth = this.resizeData.startWidth - deltaX;
      newLeft = this.resizeData.startLeft + deltaX;
    }
    if (direction.includes("s")) {
      newHeight = this.resizeData.startHeight + deltaY;
    }
    if (direction.includes("n")) {
      newHeight = this.resizeData.startHeight - deltaY;
      newTop = this.resizeData.startTop + deltaY;
    }

    // Apply constraints
    const minWidth = 320;
    const minHeight = 400;
    const maxWidth = 600;
    const maxHeight = 800;

    newWidth = Math.max(minWidth, Math.min(newWidth, maxWidth));
    newHeight = Math.max(minHeight, Math.min(newHeight, maxHeight));

    // Apply new dimensions
    this.elements.chatPanel.style.width = newWidth + "px";
    this.elements.chatPanel.style.height = newHeight + "px";

    // Update position if resizing from top or left
    if (direction.includes("w") || direction.includes("n")) {
      if (direction.includes("w")) {
        this.elements.chatPanel.style.left = newLeft + "px";
      }
      if (direction.includes("n")) {
        this.elements.chatPanel.style.top = newTop + "px";
      }
      this.elements.chatPanel.style.right = "auto";
      this.elements.chatPanel.style.bottom = "auto";
    }
  }

  stopResize() {
    if (!this.isResizing) return;

    this.isResizing = false;
    this.elements.chatPanel.classList.remove("resizing");
    console.log("🎯 Stopped resizing");
  }

  resetChatSize() {
    console.log("🔄 Resetting chat size to default");
    
    // Reset to default size and position
    this.elements.chatPanel.style.width = this.defaultSize.width + "px";
    this.elements.chatPanel.style.height = this.defaultSize.height + "px";
    this.elements.chatPanel.style.right = this.currentPosition.right + "px";
    this.elements.chatPanel.style.bottom = this.currentPosition.bottom + "px";
    this.elements.chatPanel.style.left = "auto";
    this.elements.chatPanel.style.top = "auto";
    
    // Remove any transition classes
    this.elements.chatPanel.classList.remove("dragging", "resizing");
  }
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

        if (event.error === "not-allowed") {
          alert(
            "Microphone permission denied. Please allow microphone access and try again.",
          );
        }
      };

      console.log("✅ Speech recognition initialized");
    } else {
      console.warn("⚠️ Speech recognition not supported");
      this.elements.chatVoiceBtn.style.display = "none";
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
      this.elements.chatTtsBtn.style.display = "none";
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

  toggleChatWidget() {
    console.log("🔄 Toggling chat widget, current state:", this.isOpen);
    
    try {
      if (this.isOpen) {
        this.minimizeChatWidget();
      } else {
        this.openChatWidget();
      }
    } catch (error) {
      console.error("❌ Error toggling chat widget:", error);
      // Fallback: try basic toggle
      if (this.elements.chatPanel) {
        this.elements.chatPanel.classList.toggle("open");
        this.isOpen = !this.isOpen;
      }
    }
  }

  openChatWidget() {
    console.log("📂 Opening chat widget");
    
    try {
      if (this.elements.chatPanel && this.elements.chatNotification) {
        this.elements.chatPanel.classList.add("open");
        this.elements.chatNotification.style.display = "none";
        this.isOpen = true;

        // Focus on input
        setTimeout(() => {
          if (this.elements.chatInput) {
            this.elements.chatInput.focus();
          }
        }, 300);

        // Scroll to bottom
        this.scrollToBottom();
      }
    } catch (error) {
      console.error("❌ Error opening chat widget:", error);
    }
  }

  minimizeChatWidget() {
    console.log("📁 Minimizing chat widget");
    
    try {
      if (this.elements.chatPanel) {
        this.elements.chatPanel.classList.remove("open");
        this.isOpen = false;
      }
    } catch (error) {
      console.error("❌ Error minimizing chat widget:", error);
    }
  }

  closeChatWidget() {
    console.log("❌ Closing chat widget");
    
    try {
      this.minimizeChatWidget();
      // Could add additional cleanup here if needed
    } catch (error) {
      console.error("❌ Error closing chat widget:", error);
    }
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
    textarea.style.height = Math.min(textarea.scrollHeight, 80) + "px";
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
      // In a real app, this would trigger search results
      alert(`Searching for: ${query}`);
    }
  }

  handleCategoryClick(categoryName) {
    console.log("📂 Category clicked:", categoryName);
    // In a real app, this would navigate to category page
    alert(`Browsing ${categoryName} category`);
  }

  handleProductClick(productName) {
    console.log("📦 Product clicked:", productName);
    // In a real app, this would navigate to product page
    alert(`Viewing ${productName} details`);
  }

  handleCTAClick() {
    console.log("🎯 CTA button clicked");
    // In a real app, this would navigate to sale page
    alert("Redirecting to Festival Sale!");
  }

  handleHeaderAction(actionText) {
    console.log("🔗 Header action:", actionText);
    // In a real app, these would navigate to respective pages
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
  console.log("📄 DOM loaded, initializing E-commerce components...");

  // Initialize e-commerce page functionality
  new EcommercePage();

  // Initialize chat widget
  new EcommerceChatWidget();

  console.log("🎉 E-commerce page fully initialized!");
});
