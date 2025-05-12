from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.logger import Logger
import os
import shutil
from kivy.app import App


class UploadScreen(Screen):
    """Initial screen for uploading an image"""

    def __init__(self, **kwargs):
        super(UploadScreen, self).__init__(**kwargs)
        self.file_chooser_popup = None

        # Create app directories if they don't exist
        self.create_app_directories()

    def create_app_directories(self):
        """Create necessary directories for the app to store images"""
        base_dir = os.path.join(os.path.expanduser('~'), 'vpic_app')
        uploads_dir = os.path.join(base_dir, 'uploads')

        # Create base directory
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        # Create uploads directory
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)

    def show_file_chooser(self):
        """Open a popup with a file chooser to select an image"""
        content = BoxLayout(orientation='vertical')

        # Add a search input at the top
        search_box = BoxLayout(size_hint_y=None, height=50, spacing=5, padding=[5, 5])
        from kivy.uix.textinput import TextInput
        search_input = TextInput(hint_text="Search files...", multiline=False, size_hint_x=0.8)
        search_btn = Button(text="Search", size_hint_x=0.2)
        search_box.add_widget(search_input)
        search_box.add_widget(search_btn)
        content.add_widget(search_box)

        # File chooser widget
        file_chooser = FileChooserListView(filters=['*.png', '*.jpg', '*.jpeg', '*.gif'])
        content.add_widget(file_chooser)

        # Bind search functionality
        def perform_search(instance):
            search_term = search_input.text.strip()
            if search_term:
                # Change directory to user's home directory to make it easier to search
                file_chooser.path = os.path.expanduser('~')
                # Filter shown files
                file_chooser.filters = ['*' + search_term + '*']
            else:
                # Reset filters if search is empty
                file_chooser.filters = ['*.png', '*.jpg', '*.jpeg', '*.gif']

        search_btn.bind(on_press=perform_search)
        search_input.bind(on_text_validate=perform_search)  # Search on Enter key

        # Buttons layout
        buttons = BoxLayout(size_hint_y=None, height=50, spacing=5)

        # Cancel button
        cancel_btn = Button(text='Cancel')
        select_btn = Button(text='Select')

        buttons.add_widget(cancel_btn)
        buttons.add_widget(select_btn)
        content.add_widget(buttons)

        # Create the popup
        popup = Popup(title='Select an Image', content=content, size_hint=(0.9, 0.9))

        # Button bindings
        cancel_btn.bind(on_press=popup.dismiss)
        select_btn.bind(on_press=lambda x: self.select_file(file_chooser.selection, popup))

        # Store the popup reference and show it
        self.file_chooser_popup = popup
        popup.open()

    def select_file(self, selection, popup):
        """Handle the file selection"""
        if selection:
            # Get the first selected file
            file_path = selection[0]

            # Store in app's data
            app = App.get_running_app()
            app.selected_file = file_path

            # Navigate to image description screen
            self.manager.current = 'img_description'

            # Close the popup
            popup.dismiss()