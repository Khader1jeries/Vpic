from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserListView
import os
import shutil
import json
import threading
import subprocess
import tempfile
from datetime import datetime


class SettingsScreen(Screen):
    """Settings screen for the application"""

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        Logger.info("SettingsScreen: Initialized")

    def on_enter(self):
        """Called when the screen is displayed"""
        Logger.info("SettingsScreen: on_enter called")
        # Update project info in UI
        self.update_project_info()

    def update_project_info(self):
        """Update the project information in the UI"""
        app = App.get_running_app()

        if hasattr(self, 'ids') and hasattr(self.ids, 'current_project_label'):
            if app.current_project:
                self.ids.current_project_label.text = f"Current Project: {app.current_project}"
            else:
                self.ids.current_project_label.text = "No project selected"

    def change_project(self):
        """Go to project selection screen"""
        Logger.info("SettingsScreen: change_project called")
        if self.manager:
            self.manager.current = 'project_selection'
        else:
            Logger.error("SettingsScreen: No screen manager found")

    def clear_project(self):
        """Clear all contents of the current project"""
        Logger.info("SettingsScreen: clear_project called")
        app = App.get_running_app()

        if not app.current_project or not app.current_project_path:
            self.show_error_message("No project is selected")
            return

        # Show confirmation dialog
        self.show_clear_confirmation()

    def show_clear_confirmation(self):
        """Show confirmation dialog for clearing project"""
        app = App.get_running_app()

        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Message
        content.add_widget(Label(
            text=f"Are you sure you want to clear all contents from project '{app.current_project}'?\n\nThis will delete all images and album data, but keep the project itself.",
            halign='center',
            valign='middle',
            text_size=(400, None)
        ))

        # Warning
        content.add_widget(Label(
            text="WARNING: This action cannot be undone!",
            halign='center',
            valign='middle',
            color=(1, 0.3, 0.3, 1),
            font_size='16sp',
            bold=True,
            size_hint_y=None,
            height='30dp'
        ))

        # Buttons
        buttons = BoxLayout(size_hint_y=None, height=50, spacing=10)
        cancel_btn = Button(text="Cancel", size_hint_x=0.5)
        confirm_btn = Button(
            text="Clear Project",
            size_hint_x=0.5,
            background_color=(0.9, 0.3, 0.3, 1),
            background_normal=''
        )

        buttons.add_widget(cancel_btn)
        buttons.add_widget(confirm_btn)
        content.add_widget(buttons)

        # Create and show popup
        popup = Popup(
            title="Confirm Project Clear",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )

        # Button bindings
        cancel_btn.bind(on_press=popup.dismiss)
        confirm_btn.bind(on_press=lambda x: self.execute_project_clear(popup))

        popup.open()

    def execute_project_clear(self, popup):
        """Execute project content clearing"""
        Logger.info("SettingsScreen: Executing project clear")
        app = App.get_running_app()

        try:
            # Close popup first
            popup.dismiss()

            # Get project directory paths
            project_path = app.current_project_path
            images_dir = os.path.join(project_path, "images")
            images_meta_dir = os.path.join(project_path, "images_metadata")
            albums_meta_dir = os.path.join(project_path, "albums_metadata")

            # Clear images directory
            if os.path.exists(images_dir):
                for item in os.listdir(images_dir):
                    item_path = os.path.join(images_dir, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                        Logger.info(f"SettingsScreen: Removed image file {item_path}")

            # Clear images metadata directory
            if os.path.exists(images_meta_dir):
                for item in os.listdir(images_meta_dir):
                    item_path = os.path.join(images_meta_dir, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                        Logger.info(f"SettingsScreen: Removed image metadata file {item_path}")

            # Clear albums metadata directory
            if os.path.exists(albums_meta_dir):
                for item in os.listdir(albums_meta_dir):
                    item_path = os.path.join(albums_meta_dir, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                        Logger.info(f"SettingsScreen: Removed album metadata file {item_path}")

            # Recreate Unsigned Images album
            unsigned_album_file = os.path.join(albums_meta_dir, "Unsigned_Images.json")
            if not os.path.exists(albums_meta_dir):
                os.makedirs(albums_meta_dir)

            album_data = {
                "name": "Unsigned Images",
                "description": "Default album for newly uploaded images",
                "created_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "images": []
            }

            with open(unsigned_album_file, 'w') as f:
                json.dump(album_data, f, indent=4)

            # Show success message
            self.show_success_message("Project cleared successfully")

        except Exception as e:
            Logger.error(f"SettingsScreen: Error clearing project: {str(e)}")
            self.show_error_message(f"Error clearing project: {str(e)}")

    def delete_project(self):
        """Delete the entire current project"""
        Logger.info("SettingsScreen: delete_project called")
        app = App.get_running_app()

        if not app.current_project or not app.current_project_path:
            self.show_error_message("No project is selected")
            return

        # Show confirmation dialog
        self.show_delete_confirmation()

    def show_delete_confirmation(self):
        """Show confirmation dialog for deleting project"""
        app = App.get_running_app()

        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Message
        content.add_widget(Label(
            text=f"Are you sure you want to DELETE project '{app.current_project}'?\n\nThis will delete the entire project directory and all its contents.",
            halign='center',
            valign='middle',
            text_size=(400, None)
        ))

        # Warning
        content.add_widget(Label(
            text="WARNING: This action cannot be undone!",
            halign='center',
            valign='middle',
            color=(1, 0.3, 0.3, 1),
            font_size='16sp',
            bold=True,
            size_hint_y=None,
            height='30dp'
        ))

        # Buttons
        buttons = BoxLayout(size_hint_y=None, height=50, spacing=10)
        cancel_btn = Button(text="Cancel", size_hint_x=0.5)
        confirm_btn = Button(
            text="Delete Project",
            size_hint_x=0.5,
            background_color=(0.9, 0.1, 0.1, 1),
            background_normal=''
        )

        buttons.add_widget(cancel_btn)
        buttons.add_widget(confirm_btn)
        content.add_widget(buttons)

        # Create and show popup
        popup = Popup(
            title="Confirm Project Deletion",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )

        # Button bindings
        cancel_btn.bind(on_press=popup.dismiss)
        confirm_btn.bind(on_press=lambda x: self.execute_project_deletion(popup))

        popup.open()

    def execute_project_deletion(self, popup):
        """Execute project deletion"""
        Logger.info("SettingsScreen: Executing project deletion")
        app = App.get_running_app()

        try:
            # Get project path
            project_path = app.current_project_path
            project_name = app.current_project

            # Close popup
            popup.dismiss()

            # Delete project directory
            if os.path.exists(project_path):
                shutil.rmtree(project_path)
                Logger.info(f"SettingsScreen: Deleted project directory {project_path}")

            # Reset app's current project
            app.current_project = ""
            app.current_project_path = ""

            # Show success message
            self.show_success_message(f"Project '{project_name}' has been deleted")

            # Navigate to project selection screen
            if self.manager:
                self.manager.current = 'project_selection'

        except Exception as e:
            Logger.error(f"SettingsScreen: Error deleting project: {str(e)}")
            self.show_error_message(f"Error deleting project: {str(e)}")

    def import_project(self):
        """Import a project from a directory"""
        Logger.info("SettingsScreen: import_project called")

        # Show folder chooser dialog
        self.show_folder_chooser()

    def show_folder_chooser(self):
        """Show folder chooser dialog to select a project directory to import"""
        Logger.info("SettingsScreen: Opening folder chooser for import")

        # Try to use OS-native folder selector
        try:
            if os.name == 'nt':  # Windows
                self.show_windows_folder_dialog()
            elif os.name == 'posix':  # macOS or Linux
                self.show_linux_folder_dialog()
            else:
                # Fallback to Kivy's file chooser for unsupported platforms
                self.show_kivy_folder_chooser()
        except Exception as e:
            Logger.error(f"SettingsScreen: Error using native folder chooser: {str(e)}")
            # Fallback to Kivy's folder chooser
            self.show_kivy_folder_chooser()

    def show_windows_folder_dialog(self):
        """Show the Windows native folder dialog"""
        try:
            # Create a temporary VBS script to show the folder dialog
            vbs_content = '''
            Set objShell = CreateObject("Shell.Application")
            Set objFolder = objShell.BrowseForFolder(0, "Select a project folder to import", 0, "%s")
            If objFolder Is Nothing Then
                WScript.Echo "CANCELLED"
            Else
                WScript.Echo objFolder.Self.Path
            End If
            ''' % os.path.expanduser('~').replace('\\', '\\\\')

            # Save the script to a temp file
            fd, path = tempfile.mkstemp(suffix='.vbs')
            try:
                with os.fdopen(fd, 'w') as f:
                    f.write(vbs_content)

                # Execute the script
                result = subprocess.check_output(['cscript', '//NoLogo', path], universal_newlines=True).strip()

                if result != "CANCELLED":
                    self.process_project_import(result)
            finally:
                os.unlink(path)  # Delete the temporary file

        except Exception as e:
            Logger.error(f"SettingsScreen: Error with Windows folder dialog: {str(e)}")
            # Fallback
            self.show_kivy_folder_chooser()

    def show_linux_folder_dialog(self):
        """Show the Linux/macOS native folder dialog using zenity"""
        try:
            # Check if zenity is available
            subprocess.check_call(['which', 'zenity'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Use zenity directory dialog
            cmd = [
                'zenity', '--file-selection', '--directory',
                '--title=Select a Project Folder to Import'
            ]

            # Run in a separate thread to avoid blocking the UI
            def run_dialog():
                try:
                    result = subprocess.check_output(cmd, universal_newlines=True).strip()
                    if result:
                        # Process on the main thread
                        from kivy.clock import Clock
                        Clock.schedule_once(lambda dt: self.process_project_import(result), 0)
                except subprocess.CalledProcessError:
                    # User cancelled or error occurred
                    pass
                except Exception as e:
                    Logger.error(f"SettingsScreen: Error with Linux folder dialog: {str(e)}")
                    # Fallback on the main thread
                    from kivy.clock import Clock
                    Clock.schedule_once(lambda dt: self.show_kivy_folder_chooser(), 0)

            threading.Thread(target=run_dialog).start()

        except (subprocess.CalledProcessError, FileNotFoundError):
            # Zenity not available, try kdialog
            try:
                subprocess.check_call(['which', 'kdialog'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                # Use kdialog
                cmd = [
                    'kdialog', '--getexistingdirectory', os.path.expanduser('~')
                ]

                def run_dialog():
                    try:
                        result = subprocess.check_output(cmd, universal_newlines=True).strip()
                        if result:
                            from kivy.clock import Clock
                            Clock.schedule_once(lambda dt: self.process_project_import(result), 0)
                    except subprocess.CalledProcessError:
                        # User cancelled or error occurred
                        pass
                    except Exception as e:
                        Logger.error(f"SettingsScreen: Error with kdialog: {str(e)}")
                        from kivy.clock import Clock
                        Clock.schedule_once(lambda dt: self.show_kivy_folder_chooser(), 0)

                threading.Thread(target=run_dialog).start()

            except (subprocess.CalledProcessError, FileNotFoundError):
                # Neither zenity nor kdialog is available, fall back to Kivy's file chooser
                self.show_kivy_folder_chooser()
        except Exception as e:
            Logger.error(f"SettingsScreen: Error with Linux folder dialog: {str(e)}")
            self.show_kivy_folder_chooser()

    def show_kivy_folder_chooser(self):
        """Fall back to Kivy's built-in FileChooserListView for folder selection"""
        Logger.info("SettingsScreen: Falling back to Kivy's folder chooser")

        content = BoxLayout(orientation='vertical')

        # Folder chooser widget
        folder_chooser = FileChooserListView(
            path=os.path.expanduser('~'),  # Start from home directory
            dirselect=True,  # Enable directory selection
            filters=[''],  # No filters for directories
            show_hidden=False
        )
        content.add_widget(folder_chooser)

        # Buttons layout
        buttons = BoxLayout(size_hint_y=None, height=50, spacing=5)

        # Cancel button
        cancel_btn = Button(text='Cancel')
        select_btn = Button(text='Select Folder')

        buttons.add_widget(cancel_btn)
        buttons.add_widget(select_btn)
        content.add_widget(buttons)

        # Create the popup
        popup = Popup(
            title='Select a Project Folder to Import',
            content=content,
            size_hint=(0.9, 0.9),
            auto_dismiss=False
        )

        # Button bindings
        cancel_btn.bind(on_press=popup.dismiss)
        select_btn.bind(on_press=lambda x: self.handle_selected_folder(folder_chooser.selection, popup))

        # Show the popup
        popup.open()

    def handle_selected_folder(self, selection, popup):
        """Process the selected folder"""
        if not selection:
            popup.dismiss()
            return

        folder_path = selection[0]
        popup.dismiss()

        # Check if it's a directory
        if not os.path.isdir(folder_path):
            self.show_error_message(f"Selected path is not a directory: {folder_path}")
            return

        # Process the selected folder for import
        self.process_project_import(folder_path)

    def process_project_import(self, folder_path):
        """Process the selected folder as a project import"""
        Logger.info(f"SettingsScreen: Processing folder for import: {folder_path}")

        # Get project name from folder name
        project_name = os.path.basename(folder_path)

        # Check if project name is valid
        if not project_name or project_name.strip() == "":
            self.show_error_message("Invalid project folder name")
            return

        # Check if project already exists
        app = App.get_running_app()
        projects_dir = os.path.join(os.getcwd(), 'data', 'projects')
        dest_path = os.path.join(projects_dir, project_name)

        if os.path.exists(dest_path):
            self.show_import_conflict_dialog(folder_path, project_name, dest_path)
            return

        # Validate the folder structure (simplified check)
        if not self.validate_project_folder(folder_path):
            # Just create required directories
            self.create_project_structure(folder_path)

        # Copy the project to the projects directory
        try:
            # Make sure projects directory exists
            if not os.path.exists(projects_dir):
                os.makedirs(projects_dir)

            # Copy the directory
            shutil.copytree(folder_path, dest_path)
            Logger.info(f"SettingsScreen: Copied project from {folder_path} to {dest_path}")

            # Show success message
            self.show_success_message(f"Project '{project_name}' imported successfully")

            # Set as current project
            app.current_project = project_name
            app.current_project_path = dest_path

            # Update UI
            self.update_project_info()

        except Exception as e:
            Logger.error(f"SettingsScreen: Error importing project: {str(e)}")
            self.show_error_message(f"Error importing project: {str(e)}")

    def show_import_conflict_dialog(self, source_path, project_name, dest_path):
        """Show dialog for handling project name conflict during import"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Message
        content.add_widget(Label(
            text=f"A project named '{project_name}' already exists.\nWhat would you like to do?",
            halign='center',
            valign='middle',
            text_size=(400, None)
        ))

        # Buttons
        buttons = BoxLayout(orientation='vertical', size_hint_y=None, height=150, spacing=10)

        # Options
        rename_btn = Button(
            text=f"Rename and Import as '{project_name}_copy'",
            background_color=(0.3, 0.6, 0.9, 1),
            background_normal=''
        )

        overwrite_btn = Button(
            text="Overwrite Existing Project",
            background_color=(0.9, 0.3, 0.3, 1),
            background_normal=''
        )

        cancel_btn = Button(
            text="Cancel Import",
            background_color=(0.5, 0.5, 0.5, 1),
            background_normal=''
        )

        buttons.add_widget(rename_btn)
        buttons.add_widget(overwrite_btn)
        buttons.add_widget(cancel_btn)
        content.add_widget(buttons)

        # Create popup
        popup = Popup(
            title="Project Already Exists",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )

        # Button bindings
        new_name = f"{project_name}_copy"
        new_dest = os.path.join(os.path.dirname(dest_path), new_name)

        rename_btn.bind(on_press=lambda x: self.import_with_new_name(popup, source_path, new_dest, new_name))
        overwrite_btn.bind(on_press=lambda x: self.import_with_overwrite(popup, source_path, dest_path, project_name))
        cancel_btn.bind(on_press=popup.dismiss)

        popup.open()

    def import_with_new_name(self, popup, source_path, dest_path, project_name):
        """Import project with a new name to avoid conflict"""
        Logger.info(f"SettingsScreen: Importing project with new name: {project_name}")

        try:
            # Close popup
            popup.dismiss()

            # Check if renamed destination already exists
            if os.path.exists(dest_path):
                # Generate a unique name by appending a number
                base_name = project_name
                counter = 1

                while os.path.exists(dest_path):
                    project_name = f"{base_name}_{counter}"
                    dest_path = os.path.join(os.path.dirname(dest_path), project_name)
                    counter += 1

            # Create project structure if needed
            if not self.validate_project_folder(source_path):
                self.create_project_structure(source_path)

            # Copy the directory
            shutil.copytree(source_path, dest_path)
            Logger.info(f"SettingsScreen: Copied project from {source_path} to {dest_path}")

            # Show success message
            self.show_success_message(f"Project imported successfully as '{project_name}'")

            # Set as current project
            app = App.get_running_app()
            app.current_project = project_name
            app.current_project_path = dest_path

            # Update UI
            self.update_project_info()

        except Exception as e:
            Logger.error(f"SettingsScreen: Error importing project with new name: {str(e)}")
            self.show_error_message(f"Error importing project: {str(e)}")

    def import_with_overwrite(self, popup, source_path, dest_path, project_name):
        """Import project, overwriting existing project"""
        Logger.info(f"SettingsScreen: Overwriting existing project: {project_name}")

        try:
            # Close popup
            popup.dismiss()

            # Delete existing project
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)
                Logger.info(f"SettingsScreen: Deleted existing project directory {dest_path}")

            # Create project structure if needed
            if not self.validate_project_folder(source_path):
                self.create_project_structure(source_path)

            # Copy the directory
            shutil.copytree(source_path, dest_path)
            Logger.info(f"SettingsScreen: Copied project from {source_path} to {dest_path}")

            # Show success message
            self.show_success_message(f"Project '{project_name}' imported successfully")

            # Set as current project
            app = App.get_running_app()
            app.current_project = project_name
            app.current_project_path = dest_path

            # Update UI
            self.update_project_info()

        except Exception as e:
            Logger.error(f"SettingsScreen: Error overwriting project: {str(e)}")
            self.show_error_message(f"Error importing project: {str(e)}")

    def validate_project_folder(self, folder_path):
        """Validate that the folder has proper project structure"""
        # Check if it has the basic required subdirectories
        images_dir = os.path.join(folder_path, "images")
        images_meta_dir = os.path.join(folder_path, "images_metadata")
        albums_meta_dir = os.path.join(folder_path, "albums_metadata")

        return (os.path.exists(images_dir) and
                os.path.exists(images_meta_dir) and
                os.path.exists(albums_meta_dir))

    def create_project_structure(self, folder_path):
        """Create required directory structure for a project"""
        Logger.info(f"SettingsScreen: Creating project structure in {folder_path}")

        # Create directories
        os.makedirs(os.path.join(folder_path, "images"), exist_ok=True)
        os.makedirs(os.path.join(folder_path, "images_metadata"), exist_ok=True)
        os.makedirs(os.path.join(folder_path, "albums_metadata"), exist_ok=True)

        # Create default Unsigned Images album
        unsigned_album_file = os.path.join(folder_path, "albums_metadata", "Unsigned_Images.json")
        if not os.path.exists(unsigned_album_file):
            album_data = {
                "name": "Unsigned Images",
                "description": "Default album for newly uploaded images",
                "created_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "images": []
            }

            with open(unsigned_album_file, 'w') as f:
                json.dump(album_data, f, indent=4)

    def show_error_message(self, message):
        """Display an error message to the user in a popup"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Error message
        content.add_widget(Label(
            text=message,
            color=(1, 0.3, 0.3, 1),
            halign='center',
            valign='middle',
            text_size=(400, None)
        ))

        # OK button
        ok_btn = Button(
            text="OK",
            size_hint_y=None,
            height=50
        )
        content.add_widget(ok_btn)

        # Create popup
        popup = Popup(
            title="Error",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )

        # Bind button
        ok_btn.bind(on_press=popup.dismiss)

        # Show popup
        popup.open()

    def show_success_message(self, message):
        """Display a success message to the user in a popup"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Success message
        content.add_widget(Label(
            text=message,
            color=(0.2, 0.7, 0.2, 1),
            halign='center',
            valign='middle',
            text_size=(400, None)
        ))

        # OK button
        ok_btn = Button(
            text="OK",
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.7, 0.2, 1),
            background_normal=''
        )
        content.add_widget(ok_btn)

        # Create popup
        popup = Popup(
            title="Success",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )

        # Bind button
        ok_btn.bind(on_press=popup.dismiss)

        # Show popup
        popup.open()