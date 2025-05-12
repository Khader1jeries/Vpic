from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.clock import Clock


class HomeScreen(Screen):
    """Home screen of the application"""

    def on_pre_enter(self):
        """Called before the screen is displayed"""
        # Check if a project is selected
        app = App.get_running_app()
        if not app.current_project:
            # No project selected, redirect to project selection
            Clock.schedule_once(lambda dt: self.redirect_to_project_selection(), 0.1)

    def redirect_to_project_selection(self):
        """Redirect to project selection screen if no project is selected"""
        if self.manager:
            self.manager.current = 'project_selection'