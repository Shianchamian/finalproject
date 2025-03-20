"""
Manages text-to-speech functionality using pyttsx3,
providing simple methods to speak various messages in the background.
"""
import logging
logging.getLogger("comtypes").setLevel(logging.ERROR)
from threading import Thread

import platform

AndroidTTS = None 
if platform.system() == "Linux":
    try:
        from jnius import autoclass
        AndroidTTS = autoclass('android.speech.tts.TextToSpeech')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
    except ImportError:
        AndroidTTS = None

class VoiceManager:
    """
    Handles all spoken feedback to the user.
    Uses pyttsx3 to speak asynchronously on a separate thread.
    """
    def __init__(self):
        self.is_speaking = False
        self.tts = None

        if platform.system() == "Linux" and AndroidTTS:
            self.tts = AndroidTTS(PythonActivity.mActivity, None)
        else:
            import pyttsx3
            self.tts = pyttsx3.init()
            self.tts.setProperty('rate', 150)
            self.tts.setProperty('volume', 1.0)

    def speak(self, text):
        """
        Plays the given text in a separate thread
        so it won't block the main application.
        """
        def run():
            self.is_speaking = True
            if AndroidTTS and platform.system() == "Linux":
                self.tts.speak(text, AndroidTTS.QUEUE_FLUSH, None)
            else:
                self.tts.say(text)
                self.tts.runAndWait()
            self.is_speaking = False
        
        if not self.is_speaking:
            thread = Thread(target=run)
            thread.start()
    
    def verification_success(self, name, relation):
        """
        Announce a successful recognition match,
        mentioning the recognized person's name and relation.
        """
        success_text = f"Welcome, {name}! I recognize you as my {relation}."
        self.speak(success_text)
    
    def alert_message(self):
        """Warn the user if a face is unknown."""
        alert_text = "This face is not in your database. Please carefully verify their identity."
        self.speak(alert_text)

    def no_face_detected(self):
        """Prompt the user if no face is visible."""
        prompt_text = "Face is not visible. Please try again."
        self.speak(prompt_text)
