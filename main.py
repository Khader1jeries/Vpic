from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

# Define your screen classes
class HomeScreen(Screen): pass
class VotingScreen(Screen): pass
class AlbumsScreen(Screen): pass
class StatisticsScreen(Screen): pass
class UploadScreen(Screen): pass
class SettingsScreen(Screen): pass

# Load your .kv layout
Builder.load_file("kv/main.kv")

class PictureVotingApp(App):
    def build(self):
        # Return the root widget defined in .kv
        return Builder.load_file("kv/main.kv")

if __name__ == '__main__':
    PictureVotingApp().run()
