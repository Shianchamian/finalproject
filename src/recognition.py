"""
Contains the screen for real-time face recognition using the ArcFace model.
It captures frames from a chosen camera and compares any detected faces
to entries in the database.
"""

from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivymd.app import MDApp
from kivy.graphics.texture import Texture

import cv2
import os
import numpy as np
import sqlite3
from functools import partial
from src.util.face_manager import get_face, save_recognition
from src.util.voice_manager import VoiceManager
from src.util.image_manager import ImageManager



class ResultScreen(Screen):
    """Displays details about a single recognition attempt."""
    pass


class RecognitionScreen(Screen):
    """
    Captures frames from the camera and performs face recognition
    at regular intervals. Allows switching between front/rear cameras.
    """
    current_camera = 0  # 0: rear camera, 1: front camera

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.capture = None
        self.frame_counter = 0
        self.last_faces = []
        self.voice_manager = VoiceManager()
        self.image_manager = ImageManager()

    def on_enter(self, *args):
        """Start camera capture and load the face model."""
        self.start_capture()
        


    def start_capture(self):
        """Open the camera and schedule frame updates."""
        self.capture = cv2.VideoCapture(self.current_camera)
        Clock.schedule_interval(self.update_frame, 1.0 / 30)



    def update_frame(self, dt):
        ret, frame = self.capture.read()
        if not ret:
            return
        
        detected_name = "?"
        confidence_score = 0.0

        self.frame_counter += 1

        if self.frame_counter % 10 == 0:
            new_faces = self.image_manager.detect_faces(frame)

            if new_faces:
                self.last_faces = new_faces
            else:
                self.last_faces = []

        for (x1, y1, x2, y2) in self.last_faces:
            face_img = frame[y1:y2, x1:x2]

            new_face = self.image_manager.extract_features(face_img)
            detected_name, confidence_score, relationship = self.find_best_match(new_face)
        
        self.ids.recognition_label.text = f"{detected_name} ({confidence_score:.2f}%)"

        # OpenCV 转 Kivy 纹理
        buf = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.ids.camera_feed.texture = texture




    def find_best_match(self, new_face, threshold=0.75):
        """
        Compare the detected face embedding to stored embeddings.
        Returns the best name match, confidence, and relationship.
        """
        known_faces = get_face()
        best_match, best_score, best_relationship = "?", 0, "?"

        for face_id, name, relation, stored_features in known_faces:
            stored_features = np.frombuffer(stored_features, dtype=np.float32)

            # Cosine similarity
            score = (np.dot(new_face, stored_features) /
                     (np.linalg.norm(new_face) * np.linalg.norm(stored_features)))

            if score > best_score:
                best_match, best_score, best_relationship = name, score, relation

        if best_score > threshold:
            return best_match, best_score * 100, best_relationship
        else:
            return "?", best_score, "?"

    def switch_camera(self, *args):
        """Release the old camera and switch to the other camera."""
        self.capture.release()
        self.current_camera = 1 - self.current_camera
        self.start_capture()

    def on_leave(self, *args):
        """Release the camera when leaving this screen."""
        if self.capture:
            self.capture.release()

    def open_result_screen(self):
        """
        Take a final frame snapshot and show it on the ResultScreen,
        along with the recognition outcome.
        """
        ret, frame = self.capture.read()
        if not ret:
            return

        app = MDApp.get_running_app()
        result_screen = app.sm.get_screen("result")

        faces = self.image_manager.detect_faces(frame)

        if faces:
            x1, y1, x2, y2 = faces[0] 
            face_img = frame[y1:y2, x1:x2]  
            
            new_face = self.image_manager.extract_features(face_img) 

            detected_name, confidence_score, relationship = self.find_best_match(new_face)
        
        else:
            self.voice_manager.no_face_detected()
            detected_name, confidence_score, relationship = "?", 0.0, "?"
            return

        buf = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        result_screen.ids.result_image.texture = texture

        # Update the UI
        if detected_name != "?":
            result_screen.ids.result_label.text = f"Detected: {detected_name} ({confidence_score:.2f}%)"
            self.voice_manager.verification_success(detected_name, relationship)
            result_screen.ids.result_icon.icon = "check-circle"
            result_screen.ids.result_icon.text_color = (0, 0.6, 0.6, 1)

            # save result
            save_recognition(
                name=detected_name,
                relation=relationship,
                image_path=self.save_face_image(frame),
                result="Verified")
            
        else:
            result_screen.ids.result_label.text = f"No Match Found ({confidence_score:.2f}%)"
            result_screen.ids.result_icon.icon = "alert-circle"
            result_screen.ids.result_icon.text_color = (1, 0, 0, 1)
            self.voice_manager.alert_message()

            save_recognition(
                    name="Unknown",
                    relation="Stranger",
                    image_path=self.save_face_image(frame),
                    result="Failed"
                )

        app.sm.current = "result"
        
    def save_face_image(self, image):
        """Save the full image."""
        if not os.path.exists("captured_face"): os.makedirs("captured_face")

        existing_files = len(os.listdir("captured_face"))
        new_id = existing_files + 1
        save_path = f"captured_face/captured_face_{new_id}.png"

        cv2.imwrite(save_path, image)
        return save_path
