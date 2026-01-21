"""
Text-to-Speech Engine for Chatbot
Uses Coqui TTS for natural voice generation
"""

import os
import threading
import time
from pathlib import Path
from typing import Optional
import uuid

# Global TTS model instance (loaded once at startup)
_tts_model = None
_model_loaded = False
_model_lock = threading.Lock()

def initialize_tts():
    """
    Initialize TTS model once at application startup.
    CRITICAL: This should be called only once when the app starts.
    """
    global _tts_model, _model_loaded
    
    if _model_loaded:
        print("✅ TTS already initialized")
        return True
    
    try:
        print("🎤 Initializing TTS engine...")
        
        # Try to import TTS
        try:
            from TTS.api import TTS
        except ImportError:
            print("❌ TTS not installed. Install with: pip install TTS")
            return False
        
        with _model_lock:
            if not _model_loaded:  # Double-check inside lock
                # Initialize TTS model (recommended model from requirements)
                model_name = "tts_models/en/ljspeech/tacotron2-DDC"
                print(f"📥 Loading TTS model: {model_name}")
                
                _tts_model = TTS(model_name=model_name)
                _model_loaded = True
                
                print("✅ TTS engine initialized successfully")
                return True
        
    except Exception as e:
        print(f"❌ Failed to initialize TTS: {e}")
        print("💡 Install TTS with: pip install TTS")
        return False

def is_tts_available() -> bool:
    """Check if TTS is available and initialized"""
    return _model_loaded and _tts_model is not None

def should_speak_text(text: str) -> bool:
    """
    Determine if text should be spoken based on length and content.
    RULE: Only speak short responses (1-2 sentences)
    """
    if not text or len(text.strip()) == 0:
        return False
    
    # Count sentences (rough estimation)
    sentence_count = text.count('.') + text.count('!') + text.count('?')
    
    # Don't speak very long responses
    if len(text) > 200:
        return False
    
    # Don't speak if too many sentences
    if sentence_count > 3:
        return False
    
    # Don't speak lists or structured content
    if text.count('\n') > 2 or text.count('•') > 0:
        return False
    
    return True

def clean_text_for_speech(text: str) -> str:
    """
    Clean text for better speech synthesis.
    Remove special characters, format numbers, etc.
    """
    if not text:
        return ""
    
    # Remove markdown formatting
    cleaned = text.replace('**', '').replace('*', '')
    
    # Replace common symbols with words
    cleaned = cleaned.replace('&', ' and ')
    cleaned = cleaned.replace('@', ' at ')
    cleaned = cleaned.replace('#', ' number ')
    cleaned = cleaned.replace('₹', ' rupees ')
    cleaned = cleaned.replace('$', ' dollars ')
    
    # Remove extra whitespace
    cleaned = ' '.join(cleaned.split())
    
    # Limit length for speech
    if len(cleaned) > 150:
        # Find a good breaking point
        sentences = cleaned.split('.')
        if len(sentences) > 1:
            cleaned = sentences[0] + '.'
    
    return cleaned.strip()

def speak(text: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Generate speech from text using the pre-loaded TTS model.
    
    Args:
        text: Text to convert to speech
        output_path: Optional path to save audio file
        
    Returns:
        Path to generated audio file, or None if failed
    """
    if not is_tts_available():
        print("⚠️ TTS not available")
        return None
    
    if not should_speak_text(text):
        print(f"⚠️ Text not suitable for speech: {len(text)} chars")
        return None
    
    try:
        # Clean text for speech
        clean_text = clean_text_for_speech(text)
        if not clean_text:
            return None
        
        # Generate unique filename if not provided
        if output_path is None:
            audio_dir = Path("static/audio")
            audio_dir.mkdir(parents=True, exist_ok=True)
            
            # Use timestamp + UUID for unique filename
            timestamp = int(time.time())
            unique_id = str(uuid.uuid4())[:8]
            output_path = audio_dir / f"speech_{timestamp}_{unique_id}.wav"
        
        print(f"🎤 Generating speech: '{clean_text[:50]}...'")
        
        # Generate speech using the pre-loaded model
        with _model_lock:
            _tts_model.tts_to_file(text=clean_text, file_path=str(output_path))
        
        print(f"✅ Speech generated: {output_path}")
        return str(output_path)
        
    except Exception as e:
        print(f"❌ Speech generation failed: {e}")
        return None

def speak_async(text: str, callback=None) -> threading.Thread:
    """
    Generate speech asynchronously to avoid blocking the main thread.
    
    Args:
        text: Text to convert to speech
        callback: Optional callback function to call when done
        
    Returns:
        Thread object
    """
    def _async_speak():
        try:
            audio_path = speak(text)
            if callback and audio_path:
                callback(audio_path)
        except Exception as e:
            print(f"❌ Async speech generation failed: {e}")
    
    thread = threading.Thread(target=_async_speak, daemon=True)
    thread.start()
    return thread

def cleanup_old_audio_files(max_age_minutes: int = 30):
    """
    Clean up old audio files to prevent disk space issues.
    
    Args:
        max_age_minutes: Delete files older than this many minutes
    """
    try:
        audio_dir = Path("static/audio")
        if not audio_dir.exists():
            return
        
        current_time = time.time()
        max_age_seconds = max_age_minutes * 60
        
        deleted_count = 0
        for audio_file in audio_dir.glob("speech_*.wav"):
            try:
                file_age = current_time - audio_file.stat().st_mtime
                if file_age > max_age_seconds:
                    audio_file.unlink()
                    deleted_count += 1
            except Exception as e:
                print(f"⚠️ Error deleting {audio_file}: {e}")
        
        if deleted_count > 0:
            print(f"🧹 Cleaned up {deleted_count} old audio files")
            
    except Exception as e:
        print(f"⚠️ Audio cleanup failed: {e}")

# Test function for development
def test_tts():
    """Test TTS functionality"""
    if not initialize_tts():
        print("❌ TTS initialization failed")
        return False
    
    test_text = "Hello! I can help you with orders, returns, and billing issues."
    audio_path = speak(test_text)
    
    if audio_path:
        print(f"✅ TTS test successful: {audio_path}")
        return True
    else:
        print("❌ TTS test failed")
        return False

if __name__ == "__main__":
    # Test TTS when run directly
    test_tts()