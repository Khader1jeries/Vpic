from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.app import App
from kivy.logger import Logger
from kivy.lang import Builder
import os
import json
from datetime import datetime


class CreateAlbumScreen(Screen):
    """Screen for creating a new album"""

    def __init__(self, **kwargs):
        super(CreateAlbumScreen, self).__init__(**kwargs)
        Logger.info("CreateAlbumScreen: Initialized")

    def on_enter(self):
        """Called when the screen is displayed"""
        Logger.info("CreateAlbumScreen: on_enter called")
        # Clear any previous inputs and error messages
        self.ids.album_name_input.text = ""
        self.ids.album_description_input.text = ""
        self.ids.error_message.text = ""

    def create_album(self):
        """Create a new album with the given name and description"""
        Logger.info("CreateAlbumScreen: create_album called")

        # Get album name and description
        album_name = self.ids.album_name_input.text.strip()
        album_description = self.ids.album_description_input.text.strip()

        # Validate album name
        if not album_name:
            self.ids.error_message.text = "Album name is required"
            return

        # Clean the album name for filename
        filename = album_name.replace(' ', '_') + '.json'

        # Get app reference and check project
        app = App.get_running_app()
        if not hasattr(app, 'current_project_path') or not app.current_project_path:
            self.ids.error_message.text = "No project selected"
            return

        # Path to albums metadata directory
        albums_meta_dir = os.path.join(app.current_project_path, "albums_metadata")
        if not os.path.exists(albums_meta_dir):
            try:
                os.makedirs(albums_meta_dir)
                Logger.info(f"CreateAlbumScreen: Created albums directory: {albums_meta_dir}")
            except Exception as e:
                self.ids.error_message.text = f"Error creating albums directory: {str(e)}"
                Logger.error(f"CreateAlbumScreen: Error creating albums directory: {str(e)}")
                return

        # Check if album already exists
        album_path = os.path.join(albums_meta_dir, filename)
        if os.path.exists(album_path):
            self.ids.error_message.text = f"Album '{album_name}' already exists"
            return

        # Create the album metadata
        try:
            album_data = {
                "name": album_name,
                "description": album_description,
                "created_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "images": []
            }

            with open(album_path, 'w') as f:
                json.dump(album_data, f, indent=4)

            Logger.info(f"CreateAlbumScreen: Created new album: {album_name}")

            # Navigate back to albums screen
            if self.manager:
                # Get the albums screen to refresh data
                albums_screen = self.manager.get_screen('albums')
                albums_screen.load_albums()
                albums_screen.current_album = album_name
                albums_screen.load_album_images(album_name)

                # Go back to albums screen
                self.manager.current = 'albums'
            else:
                Logger.error("CreateAlbumScreen: No screen manager found")

        except Exception as e:
            self.ids.error_message.text = f"Error creating album: {str(e)}"
            Logger.error(f"CreateAlbumScreen: Error creating album: {str(e)}")

    def cancel(self):
        """Cancel album creation and return to albums screen"""
        Logger.info("CreateAlbumScreen: cancel called")
        if self.manager:
            self.manager.current = 'albums'
        else:
            Logger.error("CreateAlbumScreen: No screen manager found")