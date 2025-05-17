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
        Logger.info("ImgDescriptionScreen: Initialized")

    def on_pre_enter(self):
        """Called when the screen is about to be shown"""
        Logger.info("ImgDescriptionScreen: on_pre_enter called")
        # Get the selected file from the app
        app = App.get_running_app()

        # Check if we have a file
        if not hasattr(app, 'selected_file') or not app.selected_file:
            Logger.warning("ImgDescriptionScreen: No file selected")
            if self.manager:
                self.manager.current = 'upload'
            return

        # Set the image preview
        self.ids.image_preview.source = app.selected_file

        # Set the initial image name to be the original filename (if not already set)
        if not hasattr(app, 'image_name') or not app.image_name:
            filename = os.path.basename(app.selected_file)
            name_without_ext = os.path.splitext(filename)[0]
            self.ids.image_name_input.text = name_without_ext
        else:
            # If the image name was previously set, use it
            self.ids.image_name_input.text = app.image_name

        # If description was previously entered, show it
        if hasattr(app, 'image_description') and app.image_description:
            self.ids.description_input.text = app.image_description

        # Clear any previous error message
        self.ids.error_message.text = ""

        # If this is batch processing, update the next button text and show batch info
        if hasattr(app, 'batch_processing') and app.batch_processing:
            self.ids.next_button.text = "Next: Add Tags"

            # If we haven't set batch_current yet, initialize it
            if not app.batch_current:
                app.batch_current = "1"

            # Get the upload screen to access the image queue
            upload_screen = self.manager.get_screen('upload')
            total_images = len(upload_screen.image_queue) + int(app.batch_current)

            # Log this for debugging
            Logger.info(f"ImgDescriptionScreen: Batch processing image {app.batch_current} of {total_images}")

    def save_and_continue(self):
        """Save description and move to tags screen"""
        Logger.info("ImgDescriptionScreen: save_and_continue called")
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
        if self.manager:
            self.manager.current = 'img_tags'
        else:
            Logger.error("ImgDescriptionScreen: No screen manager found")

    def go_back(self):
        """Return to upload screen"""
        Logger.info("ImgDescriptionScreen: go_back called")

        app = App.get_running_app()

        # If in batch mode and not the first image, we need to handle "back" differently
        if app.batch_processing and int(app.batch_current) > 1:
            # We should ask if they want to cancel the whole batch or just this image
            self.show_batch_back_options()
        else:
            # Regular back navigation
            if self.manager:
                self.manager.current = 'upload'
            else:
                Logger.error("ImgDescriptionScreen: No screen manager found")

    def show_batch_back_options(self):
        """Show options when going back during batch processing"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        from kivy.uix.label import Label

        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        content.add_widget(Label(
            text="You're in the middle of batch processing. What would you like to do?",
            halign='center',
            valign='middle',
            text_size=(400, None)
        ))

        # Buttons
        buttons = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=150)

        # Skip this image
        skip_btn = Button(
            text="Skip This Image",
            background_color=(0.3, 0.6, 0.9, 1),
            background_normal=''
        )

        # Go back to Upload screen (cancel batch)
        cancel_btn = Button(
            text="Cancel Batch Processing",
            background_color=(0.9, 0.3, 0.3, 1),
            background_normal=''
        )

        # Continue with this image
        continue_btn = Button(
            text="Continue With This Image",
            background_color=(0.3, 0.7, 0.3, 1),
            background_normal=''
        )

        buttons.add_widget(skip_btn)
        buttons.add_widget(cancel_btn)
        buttons.add_widget(continue_btn)

        content.add_widget(buttons)

        popup = Popup(
            title="Batch Processing",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )

        # Button bindings
        skip_btn.bind(on_press=lambda x: self.skip_current_image(popup))
        cancel_btn.bind(on_press=lambda x: self.cancel_batch_processing(popup))
        continue_btn.bind(on_press=popup.dismiss)

        popup.open()

    def skip_current_image(self, popup):
        """Skip the current image and process the next one"""
        app = App.get_running_app()

        # Close popup
        popup.dismiss()

        # Process next image
        app.process_next_batch_image()

    def cancel_batch_processing(self, popup):
        """Cancel the batch processing and return to upload screen"""
        app = App.get_running_app()

        # Reset batch processing
        app.batch_processing = False
        app.batch_current = "0"

        # Clear the image queue in the upload screen
        upload_screen = self.manager.get_screen('upload')
        upload_screen.image_queue = []

        # Close popup
        popup.dismiss()

        # Go back to upload screen
        if self.manager:
            self.manager.current = 'upload'
        else:
            Logger.error("ImgDescriptionScreen: No screen manager found")