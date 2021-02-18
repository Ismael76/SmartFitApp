from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
from kivy.core.window import Window
from workoutbanner import WorkoutBanner
from kivy.core.text import LabelBase
from kivy.uix.label import Label
from os import walk
from functools import partial
import requests
import json

LabelBase.register(name="Alphakind", fn_regular="Alphakind.ttf")
Window.size = (350, 600) #Remove This Line When App Is Complete

class HomeScreen(Screen):
    pass

class SocialScreen(Screen):
    pass

class ChangeAvatarScreen(Screen):
    pass

class ProfileScreen(Screen):
    pass

class ImageButton(ButtonBehavior, Image): #Icons will act as 'buttons'
    pass

class LabelButton(ButtonBehavior, Label): #Icons will act as 'buttons'
    pass

class SettingsScreen(Screen):
    pass

class LogScreen(Screen):
    pass

class SmartFit(MDApp):
    user_id = 1
    def build(self):
        self.theme_cls.primary_palette = 'Orange'
        GUI = Builder.load_file("main.kv")  # Loads 'main.kv' file that holds GUI layout
        return GUI

    def on_start(self):

        #Get DB data
        result = requests.get("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/" + str(self.user_id) + ".json")
        data = json.loads(result.content.decode()) #Decoding the data into 'string' as it comes in binary format initially, then converting it into JSON format

        #Updates avatar from DB
        avatar_image = self.root.ids['home_screen'].ids['avatar_image']
        avatar_image.source = "icons/avatars/" + data['Avatar']
        avatar_image = self.root.ids['profile_screen'].ids['avatar_image']
        avatar_image.source = "icons/avatars/" + data['Avatar']

        #Avatar change on 'profile_screen'
        avatar_selection = self.root.ids['change_avatar_screen'].ids['avatar_selection']
        for root_dir, folders, files in walk("icons/avatars"):
            for avatar in files:
                img = ImageButton(source="icons/avatars/" + avatar, on_release=partial(self.update_avatar, avatar))
                avatar_selection.add_widget(img)

        #Update 'user_id' on 'profile_screen'
        user_id_label = self.root.ids['profile_screen'].ids['user_id_label']
        user_id_label.text = "User ID: " + str(self.user_id)

        #Updates level from DB
        level = self.root.ids['home_screen'].ids['level_label']
        level.text = "Level " + str(data['Level'])
        level = self.root.ids['profile_screen'].ids['level_label']
        level.text = "Level " + str(data['Level'])

        #Updates name from DB
        name = self.root.ids['home_screen'].ids['name_label']
        name.text = data['Name']
        name = self.root.ids['profile_screen'].ids['name_label']
        name.text = data['Name']

        #Adds to workout banner on the 'log_screen'
        banner = self.root.ids['log_screen'].ids['banner_grid']
        workouts = data['Workouts'][1:]

        for workout in workouts:
            W = WorkoutBanner(Workout_Image=workout['Workout_Image'], Description=workout['Description'],
                              Unit_Image=workout['Unit_Image'], Number=workout['Number'], Unit=workout['Unit'],
                              Likes=workout['Likes'])
            banner.add_widget(W)

    #Changes avatar on app and also the DB
    def update_avatar(self, image, widget_id):
        avatar_image = self.root.ids['home_screen'].ids['avatar_image']
        avatar_image.source = "icons/avatars/" + image
        avatar_image = self.root.ids['profile_screen'].ids['avatar_image']
        avatar_image.source = "icons/avatars/" + image

        #Patch request to update data (Avatar Image) in DB
        the_data = '{"Avatar": "%s"}' % image
        requests.patch("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/" + str(self.user_id) + ".json",
                       data=the_data)

        self.change_screen("profile_screen")
        
    def change_screen(self, screen_name):
        #Use 'screen_manager' to do this

        screen_manager = self.root.ids['screen_manager']
        screen_manager.current = screen_name #This will make the current screen be on whatever the screen name is

    def navigation_draw(self):
        print("Navigation")


SmartFit().run()