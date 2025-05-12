from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.app import App
from kivy.logger import Logger
from kivy.lang import Builder
import os
import shutil
import time
from datetime import datetime


class ImgTagsScreen(Screen):
    """Screen for adding tags to an uploaded image"""

    def __init__(self, **kwargs):
        super(ImgTagsScreen, self).__init__(**kwargs)

    def on_pre_enter(self):
        """Called when the screen is about to be shown"""
        # Get the selected file from the app
        app = App.get_running_app()
        if hasattr(app, 'selected_file') and app.selected_file:
            self.ids.image_preview.source = app.selected_file

            # Show the custom image name
            if hasattr(app, 'image_name'):
                self.ids.image_name.text = app.image_name

        # Display the description
        if hasattr(app, 'image_description'):
            self.ids.description_display.text = app.image_description

    def upload_image(self):
        """Process and upload the image"""
        app = App.get_running_app()

        # Check if we have a file
        if not hasattr(app, 'selected_file') or not app.selected_file:
            Logger.warning("ImgTagsScreen: No file selected for upload")
            return

        # Get the image name, description and tags
        image_name = ""
        if hasattr(app, 'image_name'):
            image_name = app.image_name

        description = ""
        if hasattr(app, 'image_description'):
            description = app.image_description

        tags = self.ids.tags_input.text

        # Get the current project directory
        if hasattr(app, 'current_project_path') and app.current_project_path:
            base_dir = app.current_project_path
        else:
            # Use default uploads directory if no project is selected
            base_dir = os.path.join(os.path.expanduser('~'), 'vpic_app', 'uploads')

            # Ensure directory exists
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)

        # Using timestamp for unique filename
        timestamp = int(time.time())
        orig_filename = os.path.basename(app.selected_file)
        file_ext = os.path.splitext(orig_filename)[1]
        new_filename = f"{image_name}_{timestamp}{file_ext}"

        dest_path = os.path.join(base_dir, new_filename)

        try:
            # Copy the file
            shutil.copy2(app.selected_file, dest_path)

            # Save metadata (in a real app, you'd probably use a database)
            metadata_file = os.path.join(base_dir, f"{image_name}_{timestamp}.txt")
            with open(metadata_file, 'w') as f:
                f.write(f"Filename: {new_filename}\n")
                f.write(f"Display Name: {image_name}\n")
                f.write(f"Original: {orig_filename}\n")
                f.write(f"Upload Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Description: {description}\n")
                f.write(f"Tags: {tags}\n")

            # Navigate to upload complete screen
            app.upload_filename = image_name  # Store for showing on complete screen
            self.manager.current = 'upload_complete'

            Logger.info(f"ImgTagsScreen: Image uploaded successfully to {dest_path}")
        except Exception as e:
            Logger.error(f"ImgTagsScreen: Error uploading image: {str(e)}")

    def go_back(self):
        """Return to description screen"""
        self.manager.current = 'img_description'