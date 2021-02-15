from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
import requests
import json

class HomeScreen(Screen):
    pass

class ImageButton(ButtonBehavior, Image): #Icons will act as 'buttons'
    pass

class SettingsScreen(Screen):
    pass

GUI = Builder.load_file("main.kv") #Loads 'main.kv' file that holds GUI layout
class SmartFit(App):
    def build(self):
        return GUI

    def on_start(self):
        #Get DB data
        result = requests.get("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/1.json")
        data = json.loads(result.content.decode()) #Decoding the data into 'string' as it comes in binary format initially, then converting it into JSON format
        print(data)

    def change_screen(self, screen_name):
        #Use 'screen_manager' to do this

        screen_manager = self.root.ids['screen_manager']
        screen_manager.current = screen_name #This will make the current screen be on whatever the screen name is


SmartFit().run()