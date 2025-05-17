from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.app import App
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
import os
import json


class ImageViewScreen(Screen):
    """Screen for viewing a single image with details"""
    image_path = StringProperty("")
    image_name = StringProperty("")
    image_description = StringProperty("")
    image_tags = StringProperty("")
    album_name = StringProperty("")
    upload_date = StringProperty("")

    def __init__(self, **kwargs):
        super(ImageViewScreen, self).__init__(**kwargs)
        Logger.info("ImageViewScreen: Initialized")

    def on_pre_enter(self):
        """Called before the screen is shown"""
        Logger.info("ImageViewScreen: on_pre_enter called")
        # Get the image filename from app if available
        app = App.get_running_app()
        if hasattr(app, 'current_image') and app.current_image:
            self.load_image(app.current_image)

    def load_image(self, image_filename):
        """Load image and its metadata"""
        Logger.info(f"ImageViewScreen: Loading image {image_filename}")
        app = App.get_running_app()

        if not hasattr(app, 'current_project_path') or not app.current_project_path:
            Logger.warning("ImageViewScreen: No project selected")
            self._show_error("Please select a project first")
            return

        # Get paths to necessary directories
        images_dir = os.path.join(app.current_project_path, "images")
        images_meta_dir = os.path.join(app.current_project_path, "images_metadata")

        # Construct full path to image
        self.image_path = os.path.join(images_dir, image_filename)

        # Check if image exists
        if not os.path.exists(self.image_path):
            Logger.warning(f"ImageViewScreen: Image not found: {self.image_path}")
            self._show_error(f"Image not found: {image_filename}")
            return

        # Update UI with image path
        if hasattr(self, 'ids') and hasattr(self.ids, 'image_display'):
            self.ids.image_display.source = self.image_path

        # Get image metadata
        image_meta_path = os.path.join(images_meta_dir, f"{os.path.splitext(image_filename)[0]}.json")
        if not os.path.exists(image_meta_path):
            Logger.warning(f"ImageViewScreen: Image metadata not found: {image_meta_path}")
            # If no metadata, just show image with filename
            self.image_name = os.path.splitext(image_filename)[0]
            self.image_description = "No description available"
            self.image_tags = "No tags"
            self.album_name = "Unknown album"
            self.upload_date = "Unknown"
        else:
            # Load metadata
            try:
                with open(image_meta_path, 'r') as f:
                    metadata = json.load(f)

                # Extract metadata fields
                self.image_name = metadata.get('display_name', os.path.splitext(image_filename)[0])
                self.image_description = metadata.get('description', "No description available")
                tags = metadata.get('tags', [])
                self.image_tags = ", ".join(tags) if tags else "No tags"
                self.album_name = metadata.get('album', "Unknown album")
                self.upload_date = metadata.get('upload_date', "Unknown")

                # Update UI
                self.update_ui_with_metadata()

            except Exception as e:
                Logger.error(f"ImageViewScreen: Error loading image metadata: {str(e)}")
                self._show_error(f"Error loading image metadata: {str(e)}")

    def update_ui_with_metadata(self):
        """Update UI elements with image metadata"""
        if hasattr(self, 'ids'):
            if hasattr(self.ids, 'image_title'):
                self.ids.image_title.text = self.image_name
            if hasattr(self.ids, 'image_description_text'):
                self.ids.image_description_text.text = self.image_description
            if hasattr(self.ids, 'image_tags_text'):
                self.ids.image_tags_text.text = self.image_tags
            if hasattr(self.ids, 'image_album_text'):
                self.ids.image_album_text.text = self.album_name
            if hasattr(self.ids, 'image_date_text'):
                self.ids.image_date_text.text = self.upload_date

    def go_back(self):
        """Return to album view screen"""
        Logger.info("ImageViewScreen: go_back called")
        if self.manager:
            self.manager.current = 'album_view'
        else:
            Logger.error("ImageViewScreen: No screen manager found")

    def _show_error(self, message):
        """Display an error message"""
        box = None
        if hasattr(self, 'ids') and hasattr(self.ids, 'metadata_container'):
            box = self.ids.metadata_container
        elif hasattr(self, 'ids') and hasattr(self.ids, 'main_container'):
            box = self.ids.main_container

        if box:
            box.clear_widgets()
            label = Label(
                text=message,
                font_size='16sp',
                color=(1, 0.3, 0.3, 1)
            )
            box.add_widget(label)