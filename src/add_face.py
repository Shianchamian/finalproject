"""
This file handles the logic for adding new face data to the system.
It captures live video from a camera, extracts face embeddings, and stores
them in the local database.
"""

from kivymd.app import MDApp
import cv2
import numpy as np
import os
import time
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.label import MDLabel
from src.util.face_manager import save_face_data
from src.util.voice_manager import VoiceManager
from src.util.image_manager import ImageManager


class SuccessScreen(Screen):
    """
    A screen that shows success information
    after a face has been added.
    """
    pass


class AddFaceScreen(Screen):
    """
    This class captures multiple frames from the camera,
    extracts embeddings for each face, then saves the averaged
    embedding and the best image to the database.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.face_info = {}
        self.voice_manager = VoiceManager()
        self.image_manager= ImageManager()

        self.capture = None  # camera instance
        self.clock_event = None  # scheduled clock event
        self.captured_features = []  # face embedding list
        self.captured_images = []  # face image list
        self.capture_count = 0  # how many images we captured

        # Basic UI setup
        self.layout = BoxLayout(orientation="vertical")
        self.image = Image()
        self.layout.add_widget(self.image)
        self.add_widget(self.layout)
        # self.current_camera=1

        # Capture state
        self.is_capturing = False
    
    def receive_face_info(self, name, relation):
        """Receive name and relation from FaceInfoScreen."""
        self.face_info["name"] = name
        self.face_info["relation"] = relation

    def on_enter(self, *args):
        """Start capturing and reset the progress bar when this screen is displayed."""
        self.start_camera()
        self.is_capturing = True

        self.ids.progress_bar.value = 0
        self.last_speech_time = 0  

        Clock.schedule_interval(self.update_frame, 1.0 / 60) 
        Clock.schedule_interval(self.capture_face, 0.2)

    def on_leave(self, *args):
        """Stop the camera when exiting this screen."""
        self.stop_camera()

    def start_camera(self):
        """Open the camera and schedule frame updates."""
        self.capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.capture_count = 0
        self.captured_features = []
        self.captured_images = []

    def stop_camera(self):
        """Release camera resources."""
        if self.capture:
            self.capture.release()
            self.capture = None
        self.is_capturing= False

        Clock.unschedule(self.update_frame)
        Clock.unschedule(self.capture_face)

    def update_frame(self, dt):
        """Get a new frame from the camera and show it on screen."""
        ret, frame = self.capture.read()

        if not ret:
            return
        
        self.current_frame = frame.copy()
      

        # Convert to Kivy texture
        buf = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.image.texture = texture

    def capture_face(self, dt=None):
        """
        Automatically capture faces.
        Once we have enough captures (20), we process them.
        """
        if self.capture_count >= 20:
            self.is_capturing = False

            Clock.unschedule(self.capture_face)

            self.process_captured_faces()
            return
        
        frame = getattr(self, 'current_frame', None)

        faces = self.image_manager.detect_faces(frame)
        if faces:
            x1, y1, x2, y2 = faces[0]
            face_img = frame[y1:y2, x1:x2]

            embedding = self.image_manager.extract_features(face_img) 

            # Update progress bar
            progress = (self.capture_count /20) * 100
            self.ids.progress_bar.value = progress

            # Avoid capturing very similar embeddings repeatedly
            if self.is_duplicate_embedding(embedding, 0.8):
                current_time = time.time()
                if progress < 50:
                    instruction = "Slowly turn your head left and right."
                else:
                    instruction = "Gently nod your head up and down."

                self.ids.label.text = instruction
                # Avoid speech spamming by limiting how often we speak
                if current_time - self.last_speech_time > 10:
                    self.voice_manager.speak(instruction)
                    self.last_speech_time = current_time
            else:
                self.captured_features.append(embedding)
                self.captured_images.append(frame)
                self.capture_count += 1
        else:
            self.voice_manager.no_face_detected()


    def is_duplicate_embedding(self, new_embedding, threshold):
        """Check if this embedding is similar to an already-captured one."""
        if not self.captured_features:
            return False

        similarities = [
            np.dot(new_embedding, stored) / (np.linalg.norm(new_embedding) * np.linalg.norm(stored))
            for stored in self.captured_features
        ]

        return any(sim > threshold for sim in similarities)

    def process_captured_faces(self):
        """Compute average features and save the best image."""
        avg_features = np.mean(self.captured_features, axis=0).astype(np.float32)

        # Pick the sharpest image as 'best'
        best_index = self.select_best_image(self.captured_images)
        best_image = self.captured_images[best_index]
        image_path = self.save_face_image(best_image)

        # Insert into database
        name = self.face_info["name"]
        relation = self.face_info["relation"]
        save_face_data(name, relation, image_path, avg_features)

        # Switch to success screen
        app = MDApp.get_running_app()
        app.root.current = "success"
        self.voice_manager.speak("Well done, this face is successfully added to the database.")

    def select_best_image(self, images):
        """Choose the sharpest image by measuring Laplacian variance."""
        def sharpness(img):
            return cv2.Laplacian(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()

        scores = [sharpness(img) for img in images]
        return np.argmax(scores)

    def save_face_image(self, image):
        """Save a cropped face image (if detected) or the full image."""
        if not os.path.exists("assets"):
            os.makedirs("assets")

        existing_files = len(os.listdir("assets"))
        new_id = existing_files + 1
        save_path = f"assets/face_{new_id}.png"

        face_image = image  # If no face detected, fallback to the original frame

        cv2.imwrite(save_path, face_image)
        return save_path

    def exit_screen(self):
        """Stop camera and go back to main screen."""
        self.stop_camera()
        MDApp.get_running_app().root.current = "main"
