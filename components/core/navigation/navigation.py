from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.app import App
from kivy.logger import Logger


class NavigationComponent(BoxLayout):
    """
    Navigation sidebar component for the application.

    This component provides the main navigation menu that appears on the left side
    of the application. It dynamically adjusts based on whether a project is selected.
    """
    current_project = StringProperty("")
    has_project = BooleanProperty(False)
    screen_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(NavigationComponent, self).__init__(**kwargs)
        Logger.info("NavigationComponent: Initialized")

        # Listen for app property changes
        app = App.get_running_app()
        app.bind(current_project=self.on_project_changed)

        # Initialize with current project state
        self.current_project = app.current_project
        self.has_project = bool(app.current_project)

    def on_project_changed(self, instance, value):
        """Called when the app's current_project property changes"""
        Logger.info(f"NavigationComponent: Project changed to {value}")
        self.current_project = value
        self.has_project = bool(value)

    def navigate_to(self, screen_name):
        """
        Navigate to the specified screen

        Args:
            screen_name (str): The name of the screen to navigate to
        """
        Logger.info(f"NavigationComponent: Navigating to {screen_name}")
        if self.screen_manager:
            self.screen_manager.current = screen_name
        else:
            Logger.error("NavigationComponent: No screen_manager available")
            # Try to get screen manager from app
            app = App.get_running_app()
            if hasattr(app.root, 'ids') and hasattr(app.root.ids, 'screen_manager'):
                app.root.ids.screen_manager.current = screen_name
            else:
                Logger.error("NavigationComponent: Unable to access screen_manager from app")

    def change_project(self):
        """Navigate to project selection screen"""
        self.navigate_to('project_selection')