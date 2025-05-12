from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.lang import Builder


class UploadCompleteScreen(Screen):
    """Screen shown after successful upload"""

    def __init__(self, **kwargs):
        super(UploadCompleteScreen, self).__init__(**kwargs)

    def on_pre_enter(self):
        """Called when the screen is about to be shown"""
        # Get the app
        app = App.get_running_app()

        # Show the uploaded filename
        if hasattr(app, 'upload_filename') and app.upload_filename:
            self.ids.upload_success_message.text = f"Your image \"{app.upload_filename}\" was successfully uploaded."

    def upload_another(self):
        """Start over with a new upload"""
        # Clear the app's stored data
        app = App.get_running_app()
        if hasattr(app, 'selected_file'):
            app.selected_file = None
        if hasattr(app, 'image_description'):
            app.image_description = ""
        if hasattr(app, 'upload_filename'):
            app.upload_filename = ""

        # Go back to upload screen
        self.manager.current = 'upload'