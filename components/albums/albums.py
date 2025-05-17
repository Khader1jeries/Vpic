from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, StringProperty
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.app import App
from kivy.logger import Logger
import os
import json
from datetime import datetime


class AlbumsScreen(Screen):
    """Screen for viewing albums and images"""
    current_album = StringProperty("")
    albums = ListProperty([])

    def __init__(self, **kwargs):
        super(AlbumsScreen, self).__init__(**kwargs)
        Logger.info("AlbumsScreen: Initialized")
        # Set default album
        self.current_album = "Unsigned Images"

    def on_enter(self):
        """Called when the screen is displayed - use this instead of on_pre_enter"""
        Logger.info("AlbumsScreen: on_enter called")
        self.load_albums()

    def load_albums(self):
        """Load all available albums"""
        Logger.info("AlbumsScreen: Loading albums")
        app = App.get_running_app()

        if not hasattr(app, 'current_project_path') or not app.current_project_path:
            Logger.warning("AlbumsScreen: No project selected")
            self._show_error("Please select a project first")
            return

        # Path to albums metadata directory
        albums_meta_dir = os.path.join(app.current_project_path, "albums_metadata")
        Logger.info(f"AlbumsScreen: Looking for albums in {albums_meta_dir}")

        # Ensure the albums metadata directory exists
        if not os.path.exists(albums_meta_dir):
            Logger.info(f"AlbumsScreen: Creating albums metadata directory at {albums_meta_dir}")
            try:
                os.makedirs(albums_meta_dir)
            except Exception as e:
                Logger.error(f"AlbumsScreen: Error creating albums metadata directory: {str(e)}")
                self._show_error(f"Error creating albums metadata directory: {str(e)}")
                return

        # Ensure Unsigned Images album exists
        unsigned_album_file = os.path.join(albums_meta_dir, "Unsigned_Images.json")
        if not os.path.exists(unsigned_album_file):
            Logger.info(f"AlbumsScreen: Creating Unsigned Images album metadata")
            try:
                # Create the initial album metadata
                album_data = {
                    "name": "Unsigned Images",
                    "description": "Default album for newly uploaded images",
                    "created_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "images": []
                }
                with open(unsigned_album_file, 'w') as f:
                    json.dump(album_data, f, indent=4)
            except Exception as e:
                Logger.error(f"AlbumsScreen: Error creating Unsigned Images album metadata: {str(e)}")

        # Load all album metadata files
        self.albums = []
        try:
            for filename in os.listdir(albums_meta_dir):
                if filename.lower().endswith('.json'):
                    # Extract album name from filename
                    album_name = os.path.splitext(filename)[0].replace('_', ' ')
                    self.albums.append(album_name)
            Logger.info(f"AlbumsScreen: Found albums: {self.albums}")
        except Exception as e:
            Logger.error(f"AlbumsScreen: Error loading albums: {str(e)}")
            self._show_error(f"Error loading albums: {str(e)}")
            return

        # Check if we found any albums
        if not self.albums:
            Logger.warning("AlbumsScreen: No albums found")
            self._show_error("No albums found. Create an album or upload images to see them in 'Unsigned Images'.")
            return

        # Update UI
        self.update_albums_ui()

        # Load current album
        if self.current_album in self.albums:
            self.load_album_images(self.current_album)
        elif self.albums:
            self.current_album = self.albums[0]
            self.load_album_images(self.current_album)

    def update_albums_ui(self):
        """Update the albums list in the UI"""
        Logger.info("AlbumsScreen: Updating albums UI")

        # Check if widget exists
        if not hasattr(self, 'ids') or not hasattr(self.ids, 'albums_container'):
            Logger.error("AlbumsScreen: albums_container not found in UI")
            return

        albums_container = self.ids.albums_container
        albums_container.clear_widgets()

        for album in self.albums:
            btn = Button(
                text=album,
                size_hint_x=None,  # Fixed width for horizontal layout
                width='150dp',  # Set fixed width for buttons
                height='50dp',  # Set fixed height for buttons
                background_normal='',
                background_color=(0.3, 0.5, 0.7, 1) if album == self.current_album else (0.5, 0.5, 0.5, 1)
            )
            # Modify the button binding to open the album view screen
            btn.bind(on_press=lambda instance, a=album: self.view_album(a))
            albums_container.add_widget(btn)

    def select_album(self, album_name):
        """Select an album to display its images in the current screen"""
        Logger.info(f"AlbumsScreen: Selected album {album_name}")
        self.current_album = album_name
        self.update_albums_ui()  # Update highlighting
        self.load_album_images(album_name)

    def view_album(self, album_name):
        """Open the album view screen for the selected album"""
        Logger.info(f"AlbumsScreen: Opening album view for {album_name}")

        # Store the selected album name in the app for access from album view screen
        app = App.get_running_app()
        app.current_album = album_name

        # Navigate to album view screen
        if self.manager:
            self.manager.current = 'album_view'
        else:
            Logger.error("AlbumsScreen: No screen manager found")

    def load_album_images(self, album_name):
        """Load and display images from the selected album"""
        Logger.info(f"AlbumsScreen: Loading images for album {album_name}")

        # Check if widget exists
        if not hasattr(self, 'ids') or not hasattr(self.ids, 'images_grid'):
            Logger.error("AlbumsScreen: images_grid not found in UI")
            return

        app = App.get_running_app()
        if not hasattr(app, 'current_project_path') or not app.current_project_path:
            Logger.warning("AlbumsScreen: No project path available")
            return

        # Get paths to necessary directories
        images_dir = os.path.join(app.current_project_path, "images")
        albums_meta_dir = os.path.join(app.current_project_path, "albums_metadata")

        # Album metadata filename (convert spaces to underscores)
        album_filename = album_name.replace(' ', '_') + '.json'
        album_file_path = os.path.join(albums_meta_dir, album_filename)

        # Check if album metadata exists
        if not os.path.exists(album_file_path):
            Logger.warning(f"AlbumsScreen: Album metadata not found: {album_file_path}")
            self._show_error(f"Album metadata not found for '{album_name}'")
            return

        # Load album metadata
        try:
            with open(album_file_path, 'r') as f:
                album_data = json.load(f)

            # Get the images list
            images_list = album_data.get('images', [])
            Logger.info(f"AlbumsScreen: Album {album_name} contains {len(images_list)} images")

            # Clear current images
            images_grid = self.ids.images_grid
            images_grid.clear_widgets()

            # If no images found
            if not images_list:
                Logger.warning(f"AlbumsScreen: No images found in album {album_name}")
                label = Label(text=f"No images in this album yet", font_size='18sp')
                images_grid.add_widget(label)
                return

            # Add each image to the grid
            for image_filename in images_list:
                img_path = os.path.join(images_dir, image_filename)

                # Check if image file exists
                if not os.path.exists(img_path):
                    Logger.warning(f"AlbumsScreen: Image file not found: {img_path}")
                    continue

                # Create image widget
                from kivy.uix.boxlayout import BoxLayout
                from kivy.uix.image import AsyncImage

                box = BoxLayout(orientation='vertical', size_hint_y=None, height='180dp',
                                size_hint_x=None, width='150dp')

                # Image thumbnail
                img = AsyncImage(
                    source=img_path,
                    allow_stretch=True,
                    keep_ratio=True,
                    size_hint_y=0.8
                )

                # Try to get image metadata for display name
                display_name = os.path.basename(image_filename)
                try:
                    meta_path = os.path.join(app.current_project_path, "images_metadata",
                                             f"{os.path.splitext(image_filename)[0]}.json")
                    if os.path.exists(meta_path):
                        with open(meta_path, 'r') as f:
                            img_meta = json.load(f)
                            display_name = img_meta.get('display_name', display_name)
                except Exception as e:
                    Logger.error(f"AlbumsScreen: Error loading image metadata: {str(e)}")

                # Image name label
                lbl = Label(
                    text=display_name,
                    size_hint_y=0.2,
                    text_size=(140, None),
                    halign='center',
                    shorten=True,
                    shorten_from='right'
                )

                box.add_widget(img)
                box.add_widget(lbl)
                images_grid.add_widget(box)

        except Exception as e:
            Logger.error(f"AlbumsScreen: Error loading album data: {str(e)}")
            self._show_error(f"Error loading album data: {str(e)}")

    def _show_error(self, message):
        """Display an error message in the images grid area"""
        if not hasattr(self, 'ids') or not hasattr(self.ids, 'images_grid'):
            Logger.error(f"AlbumsScreen: Cannot show error, images_grid not found: {message}")
            return

        images_grid = self.ids.images_grid
        images_grid.clear_widgets()

        label = Label(
            text=message,
            font_size='16sp',
            color=(1, 0.3, 0.3, 1)
        )
        images_grid.add_widget(label)

    def create_new_album(self):
        """Navigate to the create album screen"""
        Logger.info("AlbumsScreen: create_new_album called")
        if self.manager:
            self.manager.current = 'create_album'
        else:
            Logger.error("AlbumsScreen: No screen manager found")