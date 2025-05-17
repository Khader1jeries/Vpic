from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty
from kivy.clock import Clock
import os

# Load navigation component first
Builder.load_file('components/core/navigation/navigation.kv')

# These import paths will be used as we migrate to component structure
# For each component we migrate, we'll update these imports
# For now, we're still using the screen classes from the original structure

# Project related components

# Home screen

# Image related components
from components.images.image_upload import image_upload


# Album related components

# Settings


# Placeholder screen classes (for screens you haven't implemented yet)
class VotingScreen(Screen): pass


class StatisticsScreen(Screen): pass


class PictureVotingApp(App):
    # Properties to store data between screens
    selected_file = StringProperty(None)
    image_name = StringProperty("")
    image_description = StringProperty("")
    upload_filename = StringProperty("")

    # Project properties
    current_project = StringProperty("")
    current_project_path = StringProperty("")

    # Album property for passing between screens
    current_album = StringProperty("")

    # Image property for passing between screens
    current_image = StringProperty("")

    # Flag to track if user can navigate freely
    has_project = BooleanProperty(False)

    # Batch processing flags
    batch_processing = BooleanProperty(False)
    batch_current = StringProperty("0")
    batch_total = StringProperty("0")

    # Reference to navigation component
    navigation = ObjectProperty(None)

    def build(self):
        # Create necessary directories
        self.create_app_directories()

        # Load components
        self.load_components()

        # Load screens that haven't been migrated yet
        self.load_kv_files()

        # Load the main kv file
        main_widget = Builder.load_file("app.kv")

        # Schedule setting the initial screen after the app is fully initialized
        Clock.schedule_once(lambda dt: self.set_initial_screen(main_widget), 0.1)

        return main_widget

    def load_components(self):
        """Load KV files for the migrated components"""
        # Core components
        # Already loaded: navigation.kv

        # Project components
        Builder.load_file("components/project/project_selection/project_selection.kv")

        # More components will be added here as they are migrated

    def load_kv_files(self):
        """Load all KV files for screens that haven't been migrated to components yet"""
        kv_files = [
            # project_selection.kv has been migrated to a component
            # "kv/project_selection_screen.kv",
            "kv/upload_screen.kv",
            "kv/img_description_screen.kv",
            "kv/img_tags_screen.kv",
            "kv/upload_complete_screen.kv",
            "kv/albums_screen.kv",
            "kv/create_album_screen.kv",
            "kv/album_view_screen.kv",
            "kv/image_view_screen.kv",
            "kv/settings_screen.kv"
        ]

        for kv_file in kv_files:
            try:
                Builder.load_file(kv_file)
                print(f"Loaded {kv_file}")
            except Exception as e:
                print(f"Error loading {kv_file}: {e}")

    def set_initial_screen(self, main_widget):
        """Set the initial screen after the app is fully loaded"""
        # Switch to project selection screen
        if hasattr(main_widget.ids, 'screen_manager'):
            main_widget.ids.screen_manager.current = 'project_selection'

    def on_current_project(self, instance, value):
        """Called when the current_project property changes"""
        # Update has_project flag
        self.has_project = bool(value)

        # Log the change
        if value:
            print(f"Project selected: {value}")
        else:
            print("No project selected")

    def refresh_ui(self):
        """Force a refresh of the UI when project changes"""
        # This method is mainly called to trigger UI updates based on project selection
        # The KV file already has bindings to app.current_project
        # But this explicit call helps ensure UI updates properly
        if self.current_project:
            self.has_project = True
            # Trigger property binding updates
            self.property('current_project').dispatch(self)
        else:
            self.has_project = False

    def create_app_directories(self):
        """Create necessary app directories"""
        # Create data directory
        data_dir = os.path.join(os.getcwd(), 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # Create projects directory
        projects_dir = os.path.join(data_dir, 'projects')
        if not os.path.exists(projects_dir):
            os.makedirs(projects_dir)

    def process_next_batch_image(self):
        """Process the next image in the batch queue"""
        # Get a reference to the upload screen
        upload_screen = None
        for screen in self.root.ids.screen_manager.screens:
            if isinstance(screen, UploadScreen):
                upload_screen = screen
                break

        if not upload_screen or not upload_screen.image_queue:
            # No more images in queue, go to upload complete
            self.root.ids.screen_manager.current = 'upload_complete'
            return

        # Get the next image
        self.selected_file = upload_screen.image_queue.pop(0)
        self.image_name = ""  # Reset name for the new image
        self.image_description = ""  # Reset description for the new image

        # Update batch count
        self.batch_current = str(int(self.batch_current) + 1)

        # Go to description screen for this image
        self.root.ids.screen_manager.current = 'img_description'


if __name__ == '__main__':
    PictureVotingApp().run()