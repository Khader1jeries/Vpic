from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.app import App
from kivy.logger import Logger
from kivy.lang import Builder
import os


class ImgDescriptionScreen(Screen):
    """Screen for adding description to an uploaded image"""

    def __init__(self, **kwargs):
        super(ImgDescriptionScreen, self).__init__(**kwargs)

    def on_pre_enter(self):
        """Called when the screen is about to be shown"""
        # Get the selected file from the app
        app = App.get_running_app()
        if hasattr(app, 'selected_file') and app.selected_file:
            self.ids.image_preview.source = app.selected_file

            # Set the initial image name to be the original filename
            filename = os.path.basename(app.selected_file)
            name_without_ext = os.path.splitext(filename)[0]
            self.ids.image_name_input.text = name_without_ext

        # Clear any previous error message
        self.ids.error_message.text = ""

    def save_and_continue(self):
        """Save description and move to tags screen"""
        # Check if image name is provided
        image_name = self.ids.image_name_input.text.strip()
        if not image_name:
            self.ids.error_message.text = "Please provide a name for your image"
            return

        # Get the app
        app = App.get_running_app()

        # Store the image name and description
        app.image_name = image_name
        app.image_description = self.ids.description_input.text

        # Navigate to tags screen
        self.manager.current = 'img_tags'

    def go_back(self):
        """Return to upload screen"""
        self.manager.current = 'upload'