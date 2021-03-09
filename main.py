from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
from kivy.core.window import Window
from kivymd.uix.snackbar import Snackbar
from kivy.graphics import Color, RoundedRectangle

from workoutgrid import WorkoutGrid
from kivymd.uix.menu import MDDropdownMenu
from kivy.properties import ObjectProperty
from kivy.core.text import LabelBase
from kivy.uix.label import Label
from firebaseauthentication import Authentication
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRectangleFlatButton
from os import walk
import kivy.utils
from functools import partial
import requests
import json
from friendlist import FriendList

LabelBase.register(name="Alphakind", fn_regular="Alphakind.ttf")
Window.size = (350, 600) #Remove This Line When App Is Complete

class HomeScreen(Screen):
    pass

class WorkoutScreen(Screen):
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
    workout_icon = None
    choice = None
    workout_icon_widget = ""
    previous_workout_icon_widget = None

    def build(self):
        self.authentication = Authentication()
        self.theme_cls.primary_palette = 'Orange'
        GUI = Builder.load_file("main.kv")  # Loads 'main.kv' file that holds GUI layout
        return GUI

    #Identifies what icon is selected for the log workout screen
    def update_workout_icon(self, filename, widget_id):
        self.previous_workout_icon_widget = self.workout_icon_widget
        self.workout_icon = filename
        self.workout_icon_widget = widget_id

        if self.previous_workout_icon_widget:
            self.previous_workout_icon_widget.canvas.before.clear()

        #Display what workout icon has been selected
        with self.workout_icon_widget.canvas.before:
            Color(rgb=(kivy.utils.get_color_from_hex("#6C5B7B")))
            RoundedRectangle(size=self.workout_icon_widget.size, pos=self.workout_icon_widget.pos, radius=[5, ])

    def on_start(self):

        # Avatar change on 'profile_screen'
        avatar_selection = self.root.ids['change_avatar_screen'].ids['avatar_selection']
        for root_dir, folders, files in walk("icons/avatars"):
            for avatar in files:
                img = ImageButton(source="icons/avatars/" + avatar, on_release=partial(self.update_avatar, avatar))
                avatar_selection.add_widget(img)

        #Populate workout icons
        workout_selection = self.root.ids['workout_screen'].ids['workout_icons_grid']
        for root_dir, folders, files in walk("icons/workout"):
            for workout_icon in files:
                img = ImageButton(source="icons/workout/" + workout_icon, on_release=partial(self.update_workout_icon, workout_icon))
                workout_selection.add_widget(img)

        try:
            with open("refresh_token.txt", 'r') as f:
                refresh_token = f.read()
                self.change_screen("home_screen") #Remove This Line After Done

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

            #Get the users weight + height & display on homepage
            weight_label = self.root.ids['home_screen'].ids['weight_label']
            weight_label.text = str(data['Weight']) + " KG"

            height_label = self.root.ids['home_screen'].ids['height_label']
            height_label.text = str(data['Height']) + " CM"

            #Calculates the users BMI using their height + weight
            bmi_label = self.root.ids['home_screen'].ids['bmi_label']
            bmi_label.text = str(round((float(data['Weight']) / float(data['Height']) / float(data['Height']))*10000))

            if int(bmi_label.text) >= 18 and int(bmi_label.text) <= 25:
                bmi_label.color = 0, 100, 0

            elif int(bmi_label.text) < 18:
                bmi_label.color = 1, 0.9, 0

            elif int(bmi_label.text) >= 26 and int(bmi_label.text) <= 30:
                bmi_label.color = 1, 0.6, 0

            elif int(bmi_label.text) > 30:
                bmi_label.color = 1, 0, 0
                #Note: To get RGB colours above we get the three rgb colour values from rapidtables.com then we divide each one by 255

            #Get the users friends list
            self.friends_list = data['Friends']
            self.user_name = data['Name']
            self.level = data['Level']

            #Update 'user_id' on 'profile_screen'
            user_id_label = self.root.ids['profile_screen'].ids['user_id_label']
            user_id_label.text = "User ID: " + str(data['User_Id'])

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
            workouts = data['Workouts']
            workout_keys = workouts.keys()
            for workout_key in workout_keys:
                workout = workouts[workout_key]
                W = WorkoutGrid(Workout_Image=workout['Workout_Image'], Description=workout['Description'],
                                  Unit_Image=workout['Unit_Image'], Amount=workout['Amount'], Units=workout['Units'],
                                  Likes=workout['Likes'], Date=workout['Date'])
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
        requests.patch("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/" + self.local_id + ".json",
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

    def log_workout(self):
        #Gets user data (Entries in log screen)
        workout_screen = self.root.ids["workout_screen"]
        workout_description = workout_screen.ids["workout_description"].text
        workout_amount = workout_screen.ids["amount_input"].text
        workout_unit = workout_screen.ids["units_input"].text
        workout_month_date = workout_screen.ids["month_input"].text
        workout_year_date = workout_screen.ids["year_input"].text
        workout_day_date = workout_screen.ids["day_input"].text
        workout_calories_burnt = workout_screen.ids["calories_input"].text

        #Checks if user fields (With data) are appropriate
        if self.workout_icon == None:
            pass
            return
        if self.choice == None:
            workout_screen.ids["time_label"].color = 123, 0, 0
            workout_screen.ids["distance_label"].color = 123, 0, 0
            workout_screen.ids["repetitions_label"].color = 123, 0, 0
            return
        if workout_description == "":
            workout_screen.ids["workout_description"].background_color = 123, 0, 0
            return
        if workout_amount == "":
            workout_screen.ids["amount_input"].background_color = 123, 0, 0
            return
        if workout_unit == "":
            workout_screen.ids["units_input"].background_color = 123, 0, 0
            return
        if workout_calories_burnt == "":
            workout_screen.ids["calories_input"].background_color = 123, 0, 0
            return
        if workout_day_date == "":
            workout_screen.ids["day_input"].background_color = 123, 0, 0
            return
        if workout_month_date == "":
            workout_screen.ids["month_input"].background_color = 123, 0, 0
            return
        if workout_year_date == "":
            workout_screen.ids["year_input"].background_color = 123, 0, 0
            return

        #If fields are ok update the DB
        workout_data = {"Workout_Image": self.workout_icon, "Description": workout_description, "Likes": 0, "Amount": workout_amount,
                        "Units": workout_unit, "Unit_Image": self.choice, "Date": workout_day_date + "/" + workout_month_date + "/" + workout_year_date}

        workout_req = requests.post("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/%s/Workouts.json?auth=%s" %(self.local_id, self.id_token),
                                    data=json.dumps(workout_data))

        banner = self.root.ids['log_screen'].ids['banner_grid']

        W = WorkoutGrid(Workout_Image=self.workout_icon, Description=workout_description,
                          Unit_Image=self.choice, Amount=workout_amount, Units=workout_unit,
                          Likes="0", Date=workout_day_date + "/" + workout_month_date + "/" + workout_year_date)
        banner.add_widget(W, index=len(banner.children))

        self.change_screen("home_screen")

SmartFit().run()