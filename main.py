from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty
from kivy.clock import Clock
import os

# Load navigation component first
Builder.load_file('components/core/navigation/navigation.kv')
from components.core.navigation.navigation import NavigationComponent

# Import screen classes - these would eventually move to components too
# These import paths would change as you migrate to component structure
from screens.project_selection_screen import ProjectSelectionScreen
from screens.upload_screen import UploadScreen
from screens.img_description_screen import ImgDescriptionScreen
from screens.img_tags_screen import ImgTagsScreen
from screens.upload_complete_screen import UploadCompleteScreen
from screens.albums_screen import AlbumsScreen
from screens.home_screen import HomeScreen
from screens.create_album_screen import CreateAlbumScreen
from screens.album_view_screen import AlbumViewScreen
from screens.image_view_screen import ImageViewScreen
from screens.settings_screen import SettingsScreen


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

        # Load all kv files
        # This will eventually be replaced with loading individual component kv files
        try:
            Builder.load_file("kv/project_selection_screen.kv")
            print("Loaded project_selection_screen.kv")
        except Exception as e:
            print(f"Error loading project_selection_screen.kv: {e}")

        try:
            Builder.load_file("kv/upload_screen.kv")
            print("Loaded upload_screen.kv")
        except Exception as e:
            print(f"Error loading upload_screen.kv: {e}")

        try:
            Builder.load_file("kv/img_description_screen.kv")
            print("Loaded img_description_screen.kv")
        except Exception as e:
            print(f"Error loading img_description_screen.kv: {e}")

        try:
            Builder.load_file("kv/img_tags_screen.kv")
            print("Loaded img_tags_screen.kv")
        except Exception as e:
            print(f"Error loading img_tags_screen.kv: {e}")

        try:
            Builder.load_file("kv/upload_complete_screen.kv")
            print("Loaded upload_complete_screen.kv")
        except Exception as e:
            print(f"Error loading upload_complete_screen.kv: {e}")

        try:
            Builder.load_file("kv/albums_screen.kv")
            print("Loaded albums_screen.kv")
        except Exception as e:
            print(f"Error loading albums_screen.kv: {e}")

        # Load the new screens
        try:
            Builder.load_file("kv/create_album_screen.kv")
            print("Loaded create_album_screen.kv")
        except Exception as e:
            print(f"Error loading create_album_screen.kv: {e}")

        try:
            Builder.load_file("kv/album_view_screen.kv")
            print("Loaded album_view_screen.kv")
        except Exception as e:
            print(f"Error loading album_view_screen.kv: {e}")

        try:
            Builder.load_file("kv/image_view_screen.kv")
            print("Loaded image_view_screen.kv")
        except Exception as e:
            print(f"Error loading image_view_screen.kv: {e}")

        try:
            Builder.load_file("kv/settings_screen.kv")
            print("Loaded settings_screen.kv")
        except Exception as e:
            print(f"Error loading settings_screen.kv: {e}")

        # Load the updated main kv file
        main_widget = Builder.load_file("app.kv")

        # Schedule setting the initial screen after the app is fully initialized
        Clock.schedule_once(lambda dt: self.set_initial_screen(main_widget), 0.1)

        return main_widget

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