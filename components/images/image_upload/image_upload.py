from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty
from kivy.lang import Builder
from kivy.logger import Logger
import os
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserListView
import subprocess
import threading
import tempfile


class UploadScreen(Screen):
    """Initial screen for uploading an image or a folder of images"""
    # Add property to store images queue for batch processing
    image_queue = ListProperty([])

    def __init__(self, **kwargs):
        super(UploadScreen, self).__init__(**kwargs)
        Logger.info("UploadScreen: Initialized")

        # Create app directories if they don't exist
        self.create_app_directories()

    def create_app_directories(self):
        """Create necessary directories for the app to store images"""
        base_dir = os.path.join(os.path.expanduser('~'), 'vpic_app')
        uploads_dir = os.path.join(base_dir, 'uploads')

        # Create base directory
        if not os.path.exists(base_dir):
            try:
                os.makedirs(base_dir)
                Logger.info(f"UploadScreen: Created directory {base_dir}")
            except Exception as e:
                Logger.error(f"UploadScreen: Error creating directory {base_dir}: {str(e)}")

        # Create uploads directory
        if not os.path.exists(uploads_dir):
            try:
                os.makedirs(uploads_dir)
                Logger.info(f"UploadScreen: Created directory {uploads_dir}")
            except Exception as e:
                Logger.error(f"UploadScreen: Error creating directory {uploads_dir}: {str(e)}")

    def on_enter(self):
        """Called when screen is displayed"""
        Logger.info("UploadScreen: on_enter called")
        # Reset any previous selections and queues
        app = App.get_running_app()
        app.selected_file = ""
        self.image_queue = []

    def show_file_chooser(self):
        """Open native OS file chooser dialog to select an image"""
        Logger.info("UploadScreen: Opening native file chooser")

        try:
            # Use direct OS file dialog (Windows-specific)
            if os.name == 'nt':  # Windows
                self.show_windows_file_dialog()
            elif os.name == 'posix':  # macOS or Linux
                self.show_linux_file_dialog()
            else:
                # Fallback to Kivy's file chooser for unsupported platforms
                self.show_kivy_file_chooser()

        except Exception as e:
            Logger.error(f"UploadScreen: Error using native file chooser: {str(e)}")
            # Fallback to Kivy's file chooser
            self.show_kivy_file_chooser()

    def show_windows_file_dialog(self):
        """Show the Windows native file dialog"""
        try:
            # Create a temporary VBS script to show the file dialog
            vbs_content = '''
            Set objDialog = CreateObject("UserAccounts.CommonDialog")
            objDialog.Filter = "Image Files (*.jpg;*.jpeg;*.png;*.gif)|*.jpg;*.jpeg;*.png;*.gif"
            objDialog.FilterIndex = 1
            objDialog.InitialDir = "%s"
            intResult = objDialog.ShowOpen
            If intResult = 0 Then
                WScript.Echo "CANCELLED"
            Else
                WScript.Echo objDialog.FileName
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
                    self.handle_selected_file([result])
            finally:
                os.unlink(path)  # Delete the temporary file

        except Exception as e:
            Logger.error(f"UploadScreen: Error with Windows file dialog: {str(e)}")
            # Fallback
            self.show_kivy_file_chooser()

    def show_linux_file_dialog(self):
        """Show the Linux/macOS native file dialog using zenity"""
        try:
            # Check if zenity is available
            subprocess.check_call(['which', 'zenity'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Use zenity file dialog
            cmd = [
                'zenity', '--file-selection',
                '--title=Select an Image',
                '--file-filter=Image files (jpg,png,gif) | *.jpg *.jpeg *.png *.gif'
            ]

            # Run in a separate thread to avoid blocking the UI
            def run_dialog():
                try:
                    result = subprocess.check_output(cmd, universal_newlines=True).strip()
                    if result:
                        # Process on the main thread
                        Clock.schedule_once(lambda dt: self.handle_selected_file([result]), 0)
                except subprocess.CalledProcessError:
                    # User cancelled or error occurred
                    pass
                except Exception as e:
                    Logger.error(f"UploadScreen: Error with Linux file dialog: {str(e)}")
                    # Fallback on the main thread
                    Clock.schedule_once(lambda dt: self.show_kivy_file_chooser(), 0)

            threading.Thread(target=run_dialog).start()

        except (subprocess.CalledProcessError, FileNotFoundError):
            # Zenity not available, try kdialog
            try:
                subprocess.check_call(['which', 'kdialog'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                # Use kdialog
                cmd = [
                    'kdialog', '--getopenfilename', os.path.expanduser('~'),
                    'Image Files (*.jpg *.jpeg *.png *.gif)'
                ]

                def run_dialog():
                    try:
                        result = subprocess.check_output(cmd, universal_newlines=True).strip()
                        if result:
                            Clock.schedule_once(lambda dt: self.handle_selected_file([result]), 0)
                    except subprocess.CalledProcessError:
                        # User cancelled or error occurred
                        pass
                    except Exception as e:
                        Logger.error(f"UploadScreen: Error with kdialog: {str(e)}")
                        Clock.schedule_once(lambda dt: self.show_kivy_file_chooser(), 0)

                threading.Thread(target=run_dialog).start()

            except (subprocess.CalledProcessError, FileNotFoundError):
                # Neither zenity nor kdialog is available, fall back to Kivy's file chooser
                self.show_kivy_file_chooser()
        except Exception as e:
            Logger.error(f"UploadScreen: Error with Linux file dialog: {str(e)}")
            self.show_kivy_file_chooser()

    def show_kivy_file_chooser(self):
        """Fall back to Kivy's built-in FileChooserListView"""
        Logger.info("UploadScreen: Falling back to Kivy's file chooser")

        content = BoxLayout(orientation='vertical')

        # File chooser widget
        file_chooser = FileChooserListView(
            filters=['*.png', '*.jpg', '*.jpeg', '*.gif'],
            path=os.path.expanduser('~')  # Start from home directory
        )
        content.add_widget(file_chooser)

        # Buttons layout
        buttons = BoxLayout(size_hint_y=None, height=50, spacing=5)

        # Cancel button
        cancel_btn = Button(text='Cancel')
        select_btn = Button(text='Select')

        buttons.add_widget(cancel_btn)
        buttons.add_widget(select_btn)
        content.add_widget(buttons)

        # Create the popup
        popup = Popup(
            title='Select an Image',
            content=content,
            size_hint=(0.9, 0.9),
            auto_dismiss=False
        )

        # Button bindings
        cancel_btn.bind(on_press=popup.dismiss)
        select_btn.bind(on_press=lambda x: self.handle_selected_file(file_chooser.selection, popup))

        # Show the popup
        popup.open()

    def show_folder_chooser(self):
        """Open a folder chooser dialog to select a folder of images"""
        Logger.info("UploadScreen: Opening folder chooser")

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
            Logger.error(f"UploadScreen: Error using native folder chooser: {str(e)}")
            # Fallback to Kivy's folder chooser
            self.show_kivy_folder_chooser()

    def show_windows_folder_dialog(self):
        """Show the Windows native folder dialog"""
        try:
            # Create a temporary VBS script to show the folder dialog
            vbs_content = '''
            Set objShell = CreateObject("Shell.Application")
            Set objFolder = objShell.BrowseForFolder(0, "Select a folder containing images", 0, "%s")
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
                    self.scan_folder_for_images(result)
            finally:
                os.unlink(path)  # Delete the temporary file

        except Exception as e:
            Logger.error(f"UploadScreen: Error with Windows folder dialog: {str(e)}")
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
                '--title=Select a Folder Containing Images'
            ]

            # Run in a separate thread to avoid blocking the UI
            def run_dialog():
                try:
                    result = subprocess.check_output(cmd, universal_newlines=True).strip()
                    if result:
                        # Process on the main thread
                        Clock.schedule_once(lambda dt: self.scan_folder_for_images(result), 0)
                except subprocess.CalledProcessError:
                    # User cancelled or error occurred
                    pass
                except Exception as e:
                    Logger.error(f"UploadScreen: Error with Linux folder dialog: {str(e)}")
                    # Fallback on the main thread
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
                            Clock.schedule_once(lambda dt: self.scan_folder_for_images(result), 0)
                    except subprocess.CalledProcessError:
                        # User cancelled or error occurred
                        pass
                    except Exception as e:
                        Logger.error(f"UploadScreen: Error with kdialog: {str(e)}")
                        Clock.schedule_once(lambda dt: self.show_kivy_folder_chooser(), 0)

                threading.Thread(target=run_dialog).start()

            except (subprocess.CalledProcessError, FileNotFoundError):
                # Neither zenity nor kdialog is available, fall back to Kivy's file chooser
                self.show_kivy_folder_chooser()
        except Exception as e:
            Logger.error(f"UploadScreen: Error with Linux folder dialog: {str(e)}")
            self.show_kivy_folder_chooser()

    def show_kivy_folder_chooser(self):
        """Fall back to Kivy's built-in FileChooserListView for folder selection"""
        Logger.info("UploadScreen: Falling back to Kivy's folder chooser")

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
            title='Select a Folder Containing Images',
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

        # Scan the folder for images
        self.scan_folder_for_images(folder_path)

    def scan_folder_for_images(self, folder_path):
        """Scan the selected folder for images and queue them for processing"""
        Logger.info(f"UploadScreen: Scanning folder: {folder_path}")

        # List to store found image files
        image_files = []

        # Valid image extensions
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']

        # Scan folder for image files
        try:
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)

                # Check if it's a file (not a subdirectory)
                if os.path.isfile(file_path):
                    # Check if it has a valid image extension
                    ext = os.path.splitext(filename)[1].lower()
                    if ext in valid_extensions:
                        image_files.append(file_path)

            # Log found images
            Logger.info(f"UploadScreen: Found {len(image_files)} images in folder")

            # If images were found, start batch processing
            if image_files:
                # Set the image queue
                self.image_queue = image_files

                # Show confirmation popup
                self.show_batch_confirmation(len(image_files))
            else:
                # Show message if no images found
                self.show_error_message("No image files found in the selected folder.")

        except Exception as e:
            Logger.error(f"UploadScreen: Error scanning folder: {str(e)}")
            self.show_error_message(f"Error scanning folder: {str(e)}")

    def show_batch_confirmation(self, count):
        """Show a confirmation popup before starting batch processing"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Message
        content.add_widget(Label(
            text=f"Found {count} images to process.\nDo you want to start batch processing?",
            halign='center',
            valign='middle',
            text_size=(400, None)
        ))

        # Buttons
        buttons = BoxLayout(size_hint_y=None, height=50, spacing=10)

        cancel_btn = Button(text="Cancel")
        start_btn = Button(
            text="Start Processing",
            background_color=(0.2, 0.7, 0.3, 1),
            background_normal=''
        )

        buttons.add_widget(cancel_btn)
        buttons.add_widget(start_btn)
        content.add_widget(buttons)

        # Create popup
        popup = Popup(
            title="Batch Processing",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )

        # Button bindings
        cancel_btn.bind(on_press=lambda x: self.cancel_batch_processing(popup))
        start_btn.bind(on_press=lambda x: self.start_batch_processing(popup))

        # Show popup
        popup.open()

    def cancel_batch_processing(self, popup):
        """Cancel batch processing and close popup"""
        self.image_queue = []
        popup.dismiss()

    def start_batch_processing(self, popup):
        """Start processing the queued images"""
        if not self.image_queue:
            popup.dismiss()
            return

        # Process the first image in the queue
        app = App.get_running_app()

        # Set batch processing mode
        app.batch_processing = True
        app.batch_current = "1"
        app.batch_total = str(len(self.image_queue))

        # Take the first image from the queue
        app.selected_file = self.image_queue.pop(0)

        # Dismiss popup
        popup.dismiss()

        # Navigate to description screen
        if self.manager:
            self.manager.current = 'img_description'
        else:
            Logger.error("UploadScreen: No screen manager found")

    def handle_selected_file(self, selection, popup=None):
        """Process the selected file"""
        if not selection:
            if popup:
                popup.dismiss()
            return

        try:
            # Get the selected file
            file_path = selection[0]

            # Close the popup if provided
            if popup:
                popup.dismiss()

            # Check if file exists and is an image
            if not os.path.exists(file_path):
                Logger.error(f"UploadScreen: Selected file does not exist: {file_path}")
                return

            # Check file extension
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.gif']:
                Logger.error(f"UploadScreen: Selected file is not a supported image: {file_path}")
                self.show_error_message("Please select a valid image file (jpg, jpeg, png, gif)")
                return

            # Store in app's data
            app = App.get_running_app()
            app.selected_file = file_path
            app.batch_processing = False  # Single file mode

            # Navigate to image description screen
            if self.manager:
                self.manager.current = 'img_description'
            else:
                Logger.error("UploadScreen: No screen manager found")

        except Exception as e:
            Logger.error(f"UploadScreen: Error handling selected file: {str(e)}")
            self.show_error_message(f"Error processing file: {str(e)}")

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