from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
from kivy.core.window import Window
from kivymd.uix.snackbar import Snackbar

from workoutgrid import WorkoutGrid
from kivymd.uix.menu import MDDropdownMenu
from kivy.properties import ObjectProperty
from kivy.core.text import LabelBase
from kivy.uix.label import Label
from firebaseauthentication import Authentication
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRectangleFlatButton
from os import walk
from functools import partial
import requests
import json
from friendlist import FriendList

LabelBase.register(name="Alphakind", fn_regular="Alphakind.ttf")
Window.size = (350, 600) #Remove This Line When App Is Complete

class HomeScreen(Screen):
    pass

class LogInScreen(Screen):
    pass

class AddUserScreen(Screen):
    pass

class RegisterScreen(Screen):
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
    my_user_id = 1
    def build(self):
        self.authentication = Authentication()
        self.theme_cls.primary_palette = 'Orange'
        GUI = Builder.load_file("main.kv")  # Loads 'main.kv' file that holds GUI layout
        return GUI

    def on_start(self):

        #Adding items to drop down menu

        # Avatar change on 'profile_screen'
        avatar_selection = self.root.ids['change_avatar_screen'].ids['avatar_selection']
        for root_dir, folders, files in walk("icons/avatars"):
            for avatar in files:
                img = ImageButton(source="icons/avatars/" + avatar, on_release=partial(self.update_avatar, avatar))
                avatar_selection.add_widget(img)

        try:
            with open("refresh_token.txt", 'r') as f:
                refresh_token = f.read()

            #Getting new idToken
            id_token, local_id = self.authentication.exchange_refresh_token(refresh_token)

            #The firebase ID of individual users
            self.local_id = local_id
            self.id_token = id_token

            #Get DB data
            result = requests.get("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/" + local_id + ".json?auth=" + id_token)
            data = json.loads(result.content.decode()) #Decoding the data into 'string' as it comes in binary format initially, then converting it into JSON format

            #Updates avatar from DB
            avatar_image = self.root.ids['home_screen'].ids['avatar_image']
            avatar_image.source = "icons/avatars/" + data['Avatar']
            avatar_image = self.root.ids['profile_screen'].ids['avatar_image']
            avatar_image.source = "icons/avatars/" + data['Avatar']

            #Get the users friends list
            self.friends_list = data['Friends']
            self.user_name = data['Name']
            self.level = data['Level']

            #Update 'user_id' on 'profile_screen'
            user_id_label = self.root.ids['profile_screen'].ids['user_id_label']
            user_id_label.text = "User ID: " + str(self.my_user_id)

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
                W = WorkoutGrid(Workout_Image=workout['Workout_Image'], Description=workout['Description'],
                                  Unit_Image=workout['Unit_Image'], Number=workout['Number'], Unit=workout['Unit'],
                                  Likes=workout['Likes'])
                banner.add_widget(W)

            #Populate friends list on app
            friends_list_array = self.friends_list.split(",")
            print(friends_list_array)
            for friend in friends_list_array:
                friend = friend.replace(" ", "")
                if friend == "":
                    continue
                else:
                    friend_banner = FriendList(friend_id=friend, name=self.user_name, level=self.level)
                    self.root.ids["social_screen"].ids["friends_list_grid"].add_widget(friend_banner)

            self.change_screen("home_screen")

        except Exception as e:
            pass

    def logout(self,):
        pass

    #Changes avatar on app and also the DB
    def update_avatar(self, image, widget_id):
        avatar_image = self.root.ids['home_screen'].ids['avatar_image']
        avatar_image.source = "icons/avatars/" + image
        avatar_image = self.root.ids['profile_screen'].ids['avatar_image']
        avatar_image.source = "icons/avatars/" + image

        #Patch request to update data (Avatar Image) in DB
        the_data = '{"Avatar": "%s"}' % image
        requests.patch("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/" + str(self.my_user_id) + ".json",
                       data=the_data)

        self.change_screen("profile_screen")

    def change_screen(self, screen_name):
        #Use 'screen_manager' to do this

        screen_manager = self.root.ids['screen_manager']
        screen_manager.current = screen_name #This will make the current screen be on whatever the screen name is

    def navigation_draw(self):
        print("Navigation")


    #Checks DB and ensure the user_id exists, then adds the user if it exists
    def add_friend(self, user_id):
        user_id = user_id.replace("\n", "")
        check_request = requests.get('https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/.json?orderBy="User_Id"&equalTo=' + user_id)
        data = check_request.json()

        try:
            int_user_id = int(user_id)
        except:
            # Friend id had some letters in it when it should just be a number
            self.root.ids['add_user_screen'].ids['add_friend_label'].text = "Please enter a valid user id"
            return
        if user_id == self.my_user_id:
            self.root.ids['add_user_screen'].ids['add_friend_label'].text = "You can't add yourself as a friend"
            return
        if user_id in self.friends_list:
            self.root.ids['add_user_screen'].ids['add_friend_label'].text = "This user is already added to your friend's list"
            return
        if data == {}:
            self.root.ids['add_user_screen'].ids['add_friend_label'].text = "This user does not exist"
        else:
            key = list(data.keys())[0]
            new_friend_id = data[key]['User_Id']
            self.root.ids["add_user_screen"].ids["add_friend_label"].text = "User %s has been successfully added" % user_id
            self.friends_list += ",%s" % user_id
            patch_data = '{"Friends": "%s"}' % self.friends_list
            friend_patch = requests.patch("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/%s.json?auth=%s" % (self.local_id, self.id_token), data=patch_data)
            friend_banner = FriendList(friend_id=user_id, name=self.user_name, level=self.level)
            self.root.ids["social_screen"].ids["friends_list_grid"].add_widget(friend_banner)

SmartFit().run()