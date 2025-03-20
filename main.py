"""
This is the main entry point of the app. It initializes the
ScreenManager, handles navigation, and sets up the face analysis model.
"""
import numpy as np
import cv2

from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, IconRightWidget, TwoLineAvatarIconListItem, ImageLeftWidget
from kivymd.uix.screen import Screen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDRectangleFlatButton, MDFillRoundFlatIconButton, MDFloatingActionButton
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.card import MDCard
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.metrics import dp

from src.util.face_manager import init_db, manage_face, delete_face, get_name_by_id,save_recognition,get_all_results, clear_recognition_history
from src.add_face import AddFaceScreen
from src.recognition import RecognitionScreen
from src.ui.helpers import screen_helper
from src.util.voice_manager import VoiceManager
from threading import Thread
from functools import partial
from kivy.clock import Clock

class LoginScreen(Screen):
    pass

class MainScreen(Screen):
    """The home screen; contains a navigation layout and bottom navigation."""
    pass

class UserScreen(Screen):
    """Allows users to input personal data such as name, address, and contact."""
    pass

class FacesScreen(Screen):
    """Displays list of all registered faces. User can manage them here."""
    pass

class TransferScreen(Screen):
    """Placeholder screen for data import/export functionality."""
    pass

class FaceInfoScreen(Screen):
    """Collects the user's name and relation before proceeding to face capture."""
    pass

class SuccessScreen(Screen):
    """Shows a success message when face data is successfully saved."""
    pass

class ResultScreen(Screen):
    """Shows the result of face recognition (e.g., matched name, confidence)."""
    pass
class HistoryScreen(Screen):
    """Shows the history of face recognition."""
    pass


class MyScreenManager(ScreenManager):
    """
    Custom ScreenManager that checks for right swipes
    to return to the main screen.
    """
    def on_touch_move(self, touch):
        """Detect right-swipe gesture to go back to main screen."""
        if touch.dx > 50:
            app = MDApp.get_running_app()
            # Only switch if we're not already on 'main'
            if self.current != "main":
                app.previous_screen = self.current
                self.transition.direction = "right"
                self.current = "main"
        return super().on_touch_move(touch)


class MyApp(MDApp):
    """
    The main application class. It initializes the face model,
    sets up the database, and controls screen navigation.
    """
    current_camera = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.voice_manager = VoiceManager()
        self.face_info = {}  # Store temporary info about the face being added

        init_db()

    def build(self):
        """Initialize the ScreenManager and load the UI from screen_helper."""
        self.theme_cls.primary_palette = 'Teal'
        self.sm = MyScreenManager(transition=SlideTransition(direction="left"))

        # Load Kivy layout
        Builder.load_string(screen_helper)

        # Add all screens
        self.sm.add_widget(LoginScreen(name="login"))
        self.sm.add_widget(MainScreen(name="main"))
        self.sm.add_widget(UserScreen(name="user"))
        self.sm.add_widget(FaceInfoScreen(name="face_info"))
        self.sm.add_widget(AddFaceScreen(name="add"))
        self.sm.add_widget(RecognitionScreen(name="recognize"))
        self.sm.add_widget(ResultScreen(name="result"))
        self.sm.add_widget(FacesScreen(name="db"))
        self.sm.add_widget(TransferScreen(name="transfer"))
        self.sm.add_widget(SuccessScreen(name="success"))
        self.sm.add_widget(HistoryScreen(name="history"))
        return self.sm
        
    def on_start(self):
        """Called when the app starts. We go to the home screen by default."""
        # if is_password():
        #     self.check_login()
        # else:
        #     self.go_home()
        self.sm.current = "main"
        self.go_home()


    def check_login(self, password):
        user_password = "1234"  
        if password == user_password:
            self.go_home()
        else:
            from kivymd.uix.dialog import MDDialog
            MDDialog(text="Wrong password!").open()
    

    def toggle_theme(self, is_active):
        """Switch between dark and light mode."""
        if is_active:
            self.theme_cls.theme_style = "Dark"
        else:
            self.theme_cls.theme_style = "Light"
            self.theme_cls.primary_palette = 'Teal'

    def go_home(self):
        """Clear main screen content and show a welcome label."""
        self.clean_content()
        content_area = self.sm.get_screen("main").ids.content_area

        label = MDLabel(
            text="Homepage",
            halign="center",
            theme_text_color="Primary",
            font_style="H5",
        )

        welcome_label = MDLabel(
                text=(
                    "Here is a quick guide on how to get started:\n"
                    "1. [b]Register a Face[/b]: Go to the 'Add' tab or menu option to register a new face.\n"
                    "2. [b]Recognize[/b]: Go to the 'Recognition' tab to start real-time face recognition.\n"
                    "3. [b]Manage Faces[/b]: Access 'Manage Faces' from the menu to edit or delete stored faces.\n\n"
                    "If you need more detailed instructions, please refer to the user manual."
                ),
                markup=True,
                halign="left",
                theme_text_color="Secondary",
                font_style="Caption"
            )

        content_area.add_widget(label)
        content_area.add_widget(welcome_label)
        self.sm.transition.direction = "left"
        self.sm.current = "main"

    def go_back(self):
        """Return to the previously visited screen."""
        if self.sm.current != "main":
            self.sm.transition.direction = "left"
            self.sm.current = self.previous_screen

    def add_face(self):
        """
        Switch to the face registration 'info' screen.
        Also update the main screen content to show instructions.
        """
        self.previous_screen = self.sm.current
        self.sm.transition.direction = "left"
        self.clean_content()

        content_area = self.root.get_screen('main').ids.content_area
        label = MDLabel(
            text="Add A Face",
            halign="center",
            theme_text_color="Primary",
            font_style="H5",
        )
        info_card = MDCard(
            size_hint=(1, None),
            height=dp(200),
            padding=dp(10),
            md_bg_color=(
                (0.2, 0.2, 0.2, 1) 
                if self.theme_cls.theme_style == "Dark" 
                else (0.95, 0.95, 0.95, 1)
            ),
            radius=[dp(10)]
        )
        label1 = MDLabel(
            text=(
                "[b]To Ensure the Best Results:[/b]\n"
                "- Ensure good lighting conditions.\n"
                "- Keep your face fully visible and centered.\n"
                "- Try different angles for better accuracy.\n"
                "- Avoid obstructions like glasses or hats.\n\n"
                "[b]Privacy Notice:[/b]\n"
                "- No images or personal data will be uploaded.\n"
                "- You can delete your face data anytime from settings."
            ),
            markup=True,
            halign="left",
            theme_text_color="Secondary",
            font_style="Caption",
        )
        button = MDFillRoundFlatIconButton(
            text="Start",
            icon="plus",
            pos_hint={"center_x": 0.5},
        )
        button.bind(on_release=lambda x: setattr(self.root, 'current', 'face_info'))

        content_area.add_widget(label)
        info_card.add_widget(label1)
        content_area.add_widget(info_card)
        content_area.add_widget(button)

    def recognize_face(self):
        """
        Switch to the face recognition screen.
        Also update the main screen content with instructions.
        """
        self.previous_screen = self.sm.current
        self.sm.transition.direction = "left"
        self.clean_content()

        content_area = self.root.get_screen('main').ids.content_area
        label = MDLabel(
            text="Face Recognition",
            halign="center",
            theme_text_color="Primary",
            font_style="H5"
        )
        content_area.add_widget(label)

        info_card = MDCard(
            size_hint=(1, None),
            height=dp(200),
            padding=dp(10),
            md_bg_color=(
                (0.2, 0.2, 0.2, 1) 
                if self.theme_cls.theme_style == "Dark" 
                else (0.95, 0.95, 0.95, 1)
            ),
            radius=[dp(10)]
        )
        label1 = MDLabel(
            text=(
                "[b]To Ensure the Best Recognition Results:[/b]\n"
                "- Maintain good lighting conditions to improve accuracy.\n"
                "- Maintain a neutral expression and face the camera directly.\n\n"
                "[b]Important Notice:[/b]\n"
                "- Recognition results may not always be accurate.\n"
                "- Carefully verify the result before making any decisions."
            ),
            markup=True,
            halign="left",
            theme_text_color="Secondary",
            font_style="Caption",
        )
        info_card.add_widget(label1)
        content_area.add_widget(info_card)

        button = MDFillRoundFlatIconButton(
            text="Start",
            icon="magnify",
            pos_hint={"center_x": 0.5},
        )
        button.bind(on_release=lambda x: setattr(self.root, 'current', 'recognize'))
        content_area.add_widget(button)

    def manage_face(self):
        """Go to the faces list screen and load data from the database."""
        self.previous_screen = self.sm.current
        self.sm.transition.direction = "left"
        self.sm.current = "db"

        faces_list = self.root.get_screen('db').ids.faces_list
        faces_list.clear_widgets()
        faces_screen = self.root.get_screen('db')

        faces = manage_face()  # Fetch stored face data
        if not faces:
            no_data_label = MDLabel(
                text="No face data found.",
                halign="center",
                theme_text_color="Secondary",
            )
            faces_screen.add_widget(no_data_label)
            return

        for face_id, name, relation, image_path in faces:
            item = TwoLineAvatarIconListItem(text=name, secondary_text=relation)
            item.add_widget(ImageLeftWidget(source=image_path))

            delete_btn = IconRightWidget(icon="delete")
            delete_btn.bind(on_release=lambda instance, fid=face_id: self.confirm_delete(fid))

            edit_btn = IconRightWidget(icon="pencil")
            # If needed, you could bind it like:
            # edit_btn.bind(on_release=lambda instance, fid=face_id: self.update(fid))

            item.add_widget(delete_btn)
            faces_list.add_widget(item)

    def clear_history(self):
        """Clear the history list and remove all history data from the database."""
        clear_recognition_history()
        self.see_history()


    def see_history(self):
        """Go to the faces list screen and load data from the database."""
        self.previous_screen = self.sm.current
        self.sm.transition.direction = "left"
        self.sm.current = "history"

        history_list = self.root.get_screen('history').ids.history_list
        history_list.clear_widgets()
        history_screen = self.root.get_screen('history')

        history = get_all_results()  # Fetch stored face data

        if not history:
            no_data_label = MDLabel(
                text="No history found.",
                halign="center",
                theme_text_color="Secondary",
            )
            history_screen.add_widget(no_data_label)
            return

        for name, relation, image_path, result, timestamp  in history:
            item = TwoLineAvatarIconListItem(text=name, secondary_text=relation)
            item.add_widget(ImageLeftWidget(source=image_path))

            # delete_btn = IconRightWidget(icon="delete")
            # delete_btn.bind(on_release=lambda instance, fid=face_id: self.confirm_delete(fid))

            # item.add_widget(delete_btn)
            history_list.add_widget(item)

    def confirm_delete(self, face_id):
        """Show a confirmation dialog before deleting a face record."""
        name = get_name_by_id(face_id)
        confirm_text = f"Are you sure you want to delete {name}'s face?"
        self.voice_manager.speak(confirm_text)

        self.dialog = MDDialog(
            title="Confirm Delete",
            text=confirm_text,
            buttons=[
                MDFlatButton(
                    text="Delete",
                    on_release=lambda x: self.delete_face(face_id, name)
                ),
                MDRaisedButton(
                    text="Cancel",
                    on_release=lambda x: self.cancel_delete()
                )
            ]
        )
        self.dialog.open()

    def cancel_delete(self):
        """If user cancels, say so and dismiss the dialog."""
        self.voice_manager.speak("Operation cancelled")
        self.dialog.dismiss()

    def delete_face(self, face_id, name):
        """Delete a face record from the database, then refresh the list."""
        self.voice_manager.speak(f"Deleted {name}'s face")
        delete_face(face_id)
        self.dialog.dismiss()
        self.manage_face()

    def clean_content(self):
        """Helper function to clear the main screen's content area."""
        content_area = self.root.get_screen('main').ids.content_area
        content_area.clear_widgets()

    def switch_camera(self):
        """Call switch_camera from RecognitionScreen."""
        recognition_screen = self.root.get_screen('recognize')
        recognition_screen.switch_camera()

    def go_to_add_face(self):
        """Collect name and relation from FaceInfoScreen, move to AddFaceScreen."""
        self.previous_screen = self.sm.current
        self.sm.transition.direction = "left"
        self.sm.current = "face_info"

        face_info_screen = self.root.get_screen("face_info")
        name = face_info_screen.ids.name_input.text
        relation = face_info_screen.ids.relation_input.text

        if not name or not relation:
            self.show_message("Name and Relation are required!")
            self.voice_manager.speak("Please input the Name and Relation!")
            return

        self.face_info = {"name": name, "relation": relation}
        self.root.current = "add"
        add_face_screen = self.root.get_screen("add")
        add_face_screen.receive_face_info(name, relation)

    def show_message(self, message):
        """Display a popup dialog with a message."""
        self.dialog = MDDialog(
            title="Notification",
            text=message,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
        )
        self.dialog.open()


if __name__ == "__main__":
    MyApp().run()
    
