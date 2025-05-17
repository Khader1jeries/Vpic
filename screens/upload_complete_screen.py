from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.lang import Builder
from kivy.logger import Logger


class UploadCompleteScreen(Screen):
    """Screen shown after successful upload"""

    def __init__(self, **kwargs):
        super(UploadCompleteScreen, self).__init__(**kwargs)
        Logger.info("UploadCompleteScreen: Initialized")

    def on_pre_enter(self):
        """Called when the screen is about to be shown"""
        Logger.info("UploadCompleteScreen: on_pre_enter called")
        # Get the app
        app = App.get_running_app()

        # Check if we were in batch processing mode
        if hasattr(app, 'batch_processing') and app.batch_processing:
            # Get the upload screen to access the number of processed images
            total_processed = int(app.batch_current) if app.batch_current else 0

            # Show batch completion message
            self.ids.upload_success_message.text = f"Batch upload complete! {total_processed} images were successfully uploaded."
            self.ids.upload_complete_title.text = "Batch Upload Complete!"

            # Reset batch processing flags
            app.batch_processing = False
            app.batch_current = "0"
        else:
            # Show single image upload message
            if hasattr(app, 'upload_filename') and app.upload_filename:
                self.ids.upload_success_message.text = f"Your image \"{app.upload_filename}\" was successfully uploaded."
            self.ids.upload_complete_title.text = "Upload Complete!"

    def upload_another(self):
        """Start over with a new upload"""
        Logger.info("UploadCompleteScreen: upload_another called")
        # Clear the app's stored data
        app = App.get_running_app()

        # Reset necessary attributes - use safe reset approach
        app.selected_file = ""
        app.image_name = ""
        app.image_description = ""
        app.upload_filename = ""

        # Make sure batch processing is reset
        app.batch_processing = False
        app.batch_current = "0"

        # Clean up the image queue in the upload screen
        upload_screen = self.manager.get_screen('upload')
        upload_screen.image_queue = []

        # Log navigation for debugging
        Logger.info("UploadCompleteScreen: Navigating back to upload screen")

        # Go back to upload screen
        if self.manager:
            self.manager.current = 'upload'
        else:
            Logger.error("UploadCompleteScreen: No screen manager found")