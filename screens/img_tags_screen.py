from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.app import App
from kivy.logger import Logger
from kivy.lang import Builder
import os
import shutil
import time
from datetime import datetime
import json


class ImgTagsScreen(Screen):
    """Screen for adding tags to an uploaded image"""

    def __init__(self, **kwargs):
        super(ImgTagsScreen, self).__init__(**kwargs)
        Logger.info("ImgTagsScreen: Initialized")

    def on_pre_enter(self):
        """Called when the screen is about to be shown"""
        Logger.info("ImgTagsScreen: on_pre_enter called")
        # Get the selected file from the app
        app = App.get_running_app()

        # Make sure we have a file
        if not hasattr(app, 'selected_file') or not app.selected_file:
            Logger.warning("ImgTagsScreen: No file selected")
            if self.manager:
                self.manager.current = 'upload'
            return

        # Check that the ids dictionary exists and has the expected widgets
        if not hasattr(self, 'ids'):
            Logger.error("ImgTagsScreen: 'ids' dictionary not found. KV file might not be properly loaded.")
            return

        if 'image_preview' not in self.ids:
            Logger.error("ImgTagsScreen: 'image_preview' widget not found in ids dictionary")
            return

        # Set the image preview
        self.ids.image_preview.source = app.selected_file

        # Show the custom image name
        if 'image_name' in self.ids and hasattr(app, 'image_name') and app.image_name:
            self.ids.image_name.text = app.image_name

        # Display the description
        if 'description_display' in self.ids and hasattr(app, 'image_description'):
            self.ids.description_display.text = app.image_description

        # If in batch mode, update the button text
        if 'upload_button' in self.ids and hasattr(app, 'batch_processing') and app.batch_processing:
            self.ids.upload_button.text = "Save & Continue"

    def upload_image(self):
        """Process and upload the image"""
        Logger.info("ImgTagsScreen: Starting image upload")
        app = App.get_running_app()

        # Check if we have a file
        if not hasattr(app, 'selected_file') or not app.selected_file:
            Logger.warning("ImgTagsScreen: No file selected for upload")
            return

        # Get the image name, description and tags
        image_name = ""
        if hasattr(app, 'image_name') and app.image_name:
            image_name = app.image_name
        else:
            Logger.warning("ImgTagsScreen: No image name provided")
            if hasattr(self, 'ids') and 'description_display' in self.ids:
                self.ids.description_display.text = "Please go back and provide an image name"
            return

        description = ""
        if hasattr(app, 'image_description'):
            description = app.image_description

        tags = ""
        if hasattr(self, 'ids') and 'tags_input' in self.ids:
            tags = self.ids.tags_input.text

        # Get the current project directory
        if hasattr(app, 'current_project_path') and app.current_project_path:
            base_dir = app.current_project_path
            Logger.info(f"ImgTagsScreen: Using project path: {base_dir}")
        else:
            # Use default uploads directory if no project is selected
            base_dir = os.path.join(os.path.expanduser('~'), 'vpic_app', 'uploads')
            Logger.warning(f"ImgTagsScreen: No project selected, using default path: {base_dir}")

            # Ensure directory exists
            if not os.path.exists(base_dir):
                try:
                    os.makedirs(base_dir)
                    Logger.info(f"ImgTagsScreen: Created directory: {base_dir}")
                except Exception as e:
                    Logger.error(f"ImgTagsScreen: Error creating directory {base_dir}: {str(e)}")
                    return

        # Create necessary folder structure
        try:
            # Images directory - where all original images are stored
            images_dir = os.path.join(base_dir, "images")
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
                Logger.info(f"ImgTagsScreen: Created images directory: {images_dir}")

            # Images metadata directory
            images_meta_dir = os.path.join(base_dir, "images_metadata")
            if not os.path.exists(images_meta_dir):
                os.makedirs(images_meta_dir)
                Logger.info(f"ImgTagsScreen: Created images metadata directory: {images_meta_dir}")

            # Albums metadata directory
            albums_meta_dir = os.path.join(base_dir, "albums_metadata")
            if not os.path.exists(albums_meta_dir):
                os.makedirs(albums_meta_dir)
                Logger.info(f"ImgTagsScreen: Created albums metadata directory: {albums_meta_dir}")

            # Ensure we have an Unsigned Images album metadata
            unsigned_album_file = os.path.join(albums_meta_dir, "Unsigned_Images.json")
            if not os.path.exists(unsigned_album_file):
                # Create the initial album metadata
                album_data = {
                    "name": "Unsigned Images",
                    "description": "Default album for newly uploaded images",
                    "created_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "images": []
                }
                with open(unsigned_album_file, 'w') as f:
                    json.dump(album_data, f, indent=4)
                Logger.info(f"ImgTagsScreen: Created Unsigned Images album metadata: {unsigned_album_file}")

        except Exception as e:
            Logger.error(f"ImgTagsScreen: Error creating directory structure: {str(e)}")
            return

        # Using timestamp for unique filename
        timestamp = int(time.time())
        orig_filename = os.path.basename(app.selected_file)
        file_ext = os.path.splitext(orig_filename)[1]
        new_filename = f"{image_name}_{timestamp}{file_ext}"

        # Path to the destination image file
        dest_path = os.path.join(images_dir, new_filename)

        try:
            # Copy the file to the images directory
            shutil.copy2(app.selected_file, dest_path)
            Logger.info(f"ImgTagsScreen: Copied file to {dest_path}")

            # Create image metadata
            image_metadata = {
                "filename": new_filename,
                "display_name": image_name,
                "original_filename": orig_filename,
                "upload_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "description": description,
                "tags": tags.split(',') if tags else [],
                "album": "Unsigned Images"  # Initial album
            }

            # Save image metadata
            image_meta_file = os.path.join(images_meta_dir, f"{os.path.splitext(new_filename)[0]}.json")
            with open(image_meta_file, 'w') as f:
                json.dump(image_metadata, f, indent=4)
            Logger.info(f"ImgTagsScreen: Saved image metadata to {image_meta_file}")

            # Update album metadata to include this image
            try:
                with open(unsigned_album_file, 'r') as f:
                    album_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                # If file doesn't exist or is invalid, create new album data
                album_data = {
                    "name": "Unsigned Images",
                    "description": "Default album for newly uploaded images",
                    "created_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "images": []
                }

            # Add the image to the album
            album_data["images"].append(new_filename)

            # Save the updated album data
            with open(unsigned_album_file, 'w') as f:
                json.dump(album_data, f, indent=4)
            Logger.info(f"ImgTagsScreen: Updated album metadata in {unsigned_album_file}")

            # Store the filename for showing on complete screen
            app.upload_filename = image_name

            # Check if we're in batch processing mode
            if hasattr(app, 'batch_processing') and app.batch_processing:
                # Go to the next image or complete screen if done
                if self.manager:
                    app.process_next_batch_image()
                else:
                    Logger.error("ImgTagsScreen: No screen manager found")
            else:
                # Single image mode - go to upload complete
                if self.manager:
                    self.manager.current = 'upload_complete'
                else:
                    Logger.error("ImgTagsScreen: No screen manager found")

            Logger.info(f"ImgTagsScreen: Image uploaded successfully to {dest_path}")
        except Exception as e:
            Logger.error(f"ImgTagsScreen: Error uploading image: {str(e)}")

    def go_back(self):
        """Return to description screen"""
        if self.manager:
            self.manager.current = 'img_description'
        else:
            Logger.error("ImgTagsScreen: No screen manager found")