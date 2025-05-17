from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.app import App
from kivy.logger import Logger
from kivy.clock import Clock
import os


class ProjectSelectionScreen(Screen):
    """Initial screen for selecting or creating a project"""
    projects = ListProperty([])

    def __init__(self, **kwargs):
        super(ProjectSelectionScreen, self).__init__(**kwargs)
        self.projects_dir = os.path.join(os.getcwd(), 'data', 'projects')
        self.create_project_popup = None

        # Schedule loading of projects after the screen is fully initialized
        Clock.schedule_once(self.delayed_init, 0.5)

    def delayed_init(self, dt):
        """Initialize after the screen is fully loaded"""
        # Create projects directory if it doesn't exist
        if not os.path.exists(self.projects_dir):
            os.makedirs(self.projects_dir)

    def on_pre_enter(self):
        """Called before the screen is shown"""
        app = App.get_running_app()
        # Clear current project when entering this screen if coming from another screen
        if self.manager and self.manager.current != 'project_selection' and hasattr(app, 'current_project'):
            # Don't clear if coming from home after selecting (on app start)
            if not (self.manager.current == 'home' and app.current_project):
                Logger.info("ProjectSelectionScreen: Clearing current project on screen entry")

    def on_enter(self):
        """Called when the screen is shown"""
        # Schedule loading projects to ensure UI elements are ready
        Clock.schedule_once(self.load_projects, 0.1)

    def load_projects(self, dt=None):
        """Load existing projects from the projects directory"""
        # Make sure the container widget exists
        if not hasattr(self, 'ids') or not hasattr(self.ids, 'projects_container'):
            Logger.warning("ProjectSelectionScreen: projects_container not ready yet")
            return

        # Get list of projects (directories)
        self.projects = []
        try:
            for item in os.listdir(self.projects_dir):
                item_path = os.path.join(self.projects_dir, item)
                if os.path.isdir(item_path):
                    self.projects.append(item)
        except Exception as e:
            Logger.error(f"ProjectSelectionScreen: Error loading projects: {str(e)}")

        # Update the projects list in the UI
        projects_container = self.ids.projects_container
        projects_container.clear_widgets()

        if self.projects:
            for project in self.projects:
                btn = Button(
                    text=project,
                    size_hint_y=None,
                    height='50dp',
                    background_normal='',
                    background_color=(0.3, 0.5, 0.7, 1)
                )
                btn.bind(on_press=lambda instance, p=project: self.select_project(p))
                projects_container.add_widget(btn)
        else:
            # No projects found
            lbl = Label(
                text="No projects found. Create a new project to get started.",
                size_hint_y=None,
                height='50dp'
            )
            projects_container.add_widget(lbl)

    def select_project(self, project_name):
        """Select an existing project"""
        # Set the current project in the app
        app = App.get_running_app()
        app.current_project = project_name
        app.current_project_path = os.path.join(self.projects_dir, project_name)

        Logger.info(f"ProjectSelectionScreen: Selected project {project_name}")

        # Force a refresh of the UI to reflect the selected project
        app.refresh_ui()

        # Navigate to home screen
        self.manager.current = 'home'

    def show_create_project_popup(self):
        """Show popup for creating a new project"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Project name input
        name_layout = BoxLayout(orientation='vertical', size_hint_y=None, height='80dp')
        name_layout.add_widget(Label(text="Project Name:", size_hint_y=None, height='30dp', halign='left'))

        project_name_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height='40dp'
        )
        name_layout.add_widget(project_name_input)
        content.add_widget(name_layout)

        # Error message label (initially empty)
        error_label = Label(
            text="",
            color=(1, 0, 0, 1),
            size_hint_y=None,
            height='30dp'
        )
        content.add_widget(error_label)

        # Buttons
        buttons = BoxLayout(size_hint_y=None, height='50dp', spacing=10)

        cancel_btn = Button(text="Cancel")
        create_btn = Button(text="Create Project", background_color=(0.2, 0.7, 0.3, 1), background_normal='')

        buttons.add_widget(cancel_btn)
        buttons.add_widget(create_btn)
        content.add_widget(buttons)

        # Create the popup
        popup = Popup(
            title='Create New Project',
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )

        # Button bindings
        cancel_btn.bind(on_press=popup.dismiss)
        create_btn.bind(on_press=lambda x: self.create_project(project_name_input.text, error_label, popup))

        # Show the popup
        self.create_project_popup = popup
        popup.open()

    def create_project(self, project_name, error_label, popup):
        """Create a new project"""
        # Validate project name
        if not project_name or not project_name.strip():
            error_label.text = "Please enter a project name"
            return

        # Clean project name (remove special characters, spaces)
        clean_name = ''.join(e for e in project_name if e.isalnum() or e == '_' or e == '-')

        # Check if project already exists
        project_path = os.path.join(self.projects_dir, clean_name)
        if os.path.exists(project_path):
            error_label.text = f"Project '{clean_name}' already exists"
            return

        try:
            # Create project directory
            os.makedirs(project_path)

            # Set the current project in the app
            app = App.get_running_app()
            app.current_project = clean_name
            app.current_project_path = project_path

            Logger.info(f"ProjectSelectionScreen: Created project {clean_name}")

            # Force a refresh of the UI to reflect the new project
            app.refresh_ui()

            # Close the popup
            popup.dismiss()

            # Navigate to home screen
            self.manager.current = 'home'
        except Exception as e:
            error_label.text = f"Error creating project: {str(e)}"
            Logger.error(f"ProjectSelectionScreen: Error creating project: {str(e)}")