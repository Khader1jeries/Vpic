from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty
from kivy.app import App
from kivy.logger import Logger
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.uix.boxlayout import BoxLayout
import os
import json


class AlbumViewScreen(Screen):
    """Screen for viewing images within a specific album"""
    album_name = StringProperty("")
    album_description = StringProperty("")
    images = ListProperty([])

    def __init__(self, **kwargs):
        super(AlbumViewScreen, self).__init__(**kwargs)
        Logger.info("AlbumViewScreen: Initialized")

    def on_pre_enter(self):
        """Called before the screen is shown"""
        Logger.info("AlbumViewScreen: on_pre_enter called")
        # Get the album name from app if available
        app = App.get_running_app()
        if hasattr(app, 'current_album') and app.current_album:
            self.album_name = app.current_album
            Logger.info(f"AlbumViewScreen: Loading album {self.album_name}")
            self.load_album()

    def load_album(self):
        """Load album data and images"""
        Logger.info(f"AlbumViewScreen: Loading album data for {self.album_name}")
        app = App.get_running_app()

        if not hasattr(app, 'current_project_path') or not app.current_project_path:
            Logger.warning("AlbumViewScreen: No project selected")
            self._show_error("Please select a project first")
            return

        # Get paths to necessary directories
        albums_meta_dir = os.path.join(app.current_project_path, "albums_metadata")
        images_dir = os.path.join(app.current_project_path, "images")

        # Album metadata filename (convert spaces to underscores for filename)
        album_filename = self.album_name.replace(' ', '_') + '.json'
        album_file_path = os.path.join(albums_meta_dir, album_filename)

        # Check if album metadata exists
        if not os.path.exists(album_file_path):
            Logger.warning(f"AlbumViewScreen: Album metadata not found: {album_file_path}")
            self._show_error(f"Album metadata not found for '{self.album_name}'")
            return

        # Load album metadata
        try:
            with open(album_file_path, 'r') as f:
                album_data = json.load(f)

            # Update album information
            self.album_name = album_data.get('name', self.album_name)
            self.album_description = album_data.get('description', "")

            # Update UI elements with album info
            self.ids.album_title.text = self.album_name
            self.ids.album_description.text = self.album_description

            # Get the images list
            self.images = album_data.get('images', [])
            Logger.info(f"AlbumViewScreen: Album {self.album_name} contains {len(self.images)} images")

            # Update the images display
            self.update_images_display(images_dir)

        except Exception as e:
            Logger.error(f"AlbumViewScreen: Error loading album data: {str(e)}")
            self._show_error(f"Error loading album data: {str(e)}")

    def update_images_display(self, images_dir):
        """Update the images grid with album images"""
        Logger.info(f"AlbumViewScreen: Updating images display for {self.album_name}")

        # Check if widget exists
        if not hasattr(self, 'ids') or not hasattr(self.ids, 'images_grid'):
            Logger.error("AlbumViewScreen: images_grid not found in UI")
            return

        images_grid = self.ids.images_grid
        images_grid.clear_widgets()

        # If no images found
        if not self.images:
            Logger.warning(f"AlbumViewScreen: No images found in album {self.album_name}")
            label = Label(
                text=f"No images in this album yet",
                font_size='18sp'
            )
            images_grid.add_widget(label)
            return

        app = App.get_running_app()

        # Add each image to the grid
        for image_filename in self.images:
            img_path = os.path.join(images_dir, image_filename)

            # Check if image file exists
            if not os.path.exists(img_path):
                Logger.warning(f"AlbumViewScreen: Image file not found: {img_path}")
                continue

            # Create image widget
            box = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height='180dp',
                size_hint_x=None,
                width='150dp'
            )

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
                Logger.error(f"AlbumViewScreen: Error loading image metadata: {str(e)}")

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

            # Bind to image selection event - updated to navigate to image view screen
            box.bind(on_touch_down=lambda instance, touch, img_file=image_filename:
            self.on_image_selected(instance, touch, img_file))

            images_grid.add_widget(box)

    def on_image_selected(self, instance, touch, image_filename):
        """Handle image selection - navigate to image view screen"""
        if instance.collide_point(*touch.pos):
            Logger.info(f"AlbumViewScreen: Image selected: {image_filename}")

            # Store the selected image in the app for the image view screen
            app = App.get_running_app()
            app.current_image = image_filename

            # Navigate to image view screen
            if self.manager:
                self.manager.current = 'image_view'
            else:
                Logger.error("AlbumViewScreen: No screen manager found")

    def go_back(self):
        """Return to albums screen"""
        Logger.info("AlbumViewScreen: go_back called")
        if self.manager:
            self.manager.current = 'albums'
        else:
            Logger.error("AlbumViewScreen: No screen manager found")

    def _show_error(self, message):
        """Display an error message in the images grid area"""
        if not hasattr(self, 'ids') or not hasattr(self.ids, 'images_grid'):
            Logger.error(f"AlbumViewScreen: Cannot show error, images_grid not found: {message}")
            return

        images_grid = self.ids.images_grid
        images_grid.clear_widgets()

        label = Label(
            text=message,
            font_size='16sp',
            color=(1, 0.3, 0.3, 1)
        )
        images_grid.add_widget(label)