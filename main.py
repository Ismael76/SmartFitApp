from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, CardTransition, NoTransition, SlideTransition
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image, AsyncImage
from kivy.core.window import Window
from kivymd.uix.list import OneLineAvatarListItem
from kivymd.uix.snackbar import Snackbar
from kivy.graphics import Color, RoundedRectangle
from datetime import datetime
from workoutgrid import WorkoutGrid
from kivymd.uix.menu import MDDropdownMenu
from kivy.properties import ObjectProperty, StringProperty
from kivy.core.text import LabelBase
from kivy.uix.label import Label
from firebaseauthentication import Authentication
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRectangleFlatButton, MDRoundFlatButton, MDFlatButton
from os import walk
import kivy.utils
from kivy.uix.popup import Popup
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os
from kivy.clock import Clock
from kivy.app import App
from functools import partial
import requests
import json
from friendlist import FriendList
from leaderboard import Leaderboard
from kivymd.uix.dialog import MDDialog
from kivy.network.urlrequest import UrlRequest
import certifi
from plyer import notification

os.environ['SSL_CERT_FILE'] = certifi.where()

Window.size = (400, 700) #Comment This Line Out When Deploying As APK

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

class FriendScreen(Screen):
    pass

class LeaderboardScreen(Screen):
    pass

class FoodSearchScreen(Screen):
    pass

class SocialScreen(Screen):
    pass

class ChangeAvatarScreen(Screen):
    pass

class ProfileScreen(Screen):
    pass

class BadgeScreen(Screen):
    pass

class ImageButton(ButtonBehavior, Image): #Icons will act as 'buttons'
    pass

class LabelButton(ButtonBehavior, Label): #Icons will act as 'buttons'
    pass

class SettingsScreen(Screen):
    pass

class LogScreen(Screen):
    pass

class P(FloatLayout):
    pass

class Item(OneLineAvatarListItem):
    divider = None
    source = StringProperty()

class SmartFit(MDApp):
    my_user_id = 1
    workout_icon = None
    choice = None
    workout_icon_widget = ""
    refresh_file = "refresh_token.txt"
    previous_workout_icon_widget = None
    LabelBase.register(name="Alphakind", fn_regular="Alphakind.ttf")

    def build(self):
        self.authentication = Authentication()
        self.theme_cls.primary_palette = 'Orange'
        GUI = Builder.load_file("main.kv")  # Loads 'main.kv' file that holds GUI layout
        self.refresh_file = App.get_running_app().user_data_dir + self.refresh_file
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
        user_data = pd.read_csv('userdata.csv')
        X = user_data.drop(columns=['Index'])
        y = user_data['Index']
        #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)  # Allocate 20% of data for testing
        model = DecisionTreeClassifier()

        self.root.ids["social_screen"].ids["no_friend_label"].text = "You currently do not have any friends"
        self.root.ids['log_screen'].ids['no_activity_label'].text = "You do not have logged activities"
        #Populate the day, month & year inputs in the 'add workout' screen
        current_date = datetime.now()
        day = current_date.day
        month = current_date.month
        year = current_date.year
        self.current_time = current_date.strftime("%S")
        self.root.ids['workout_screen'].ids['day_input'].text = str(day)
        self.root.ids['workout_screen'].ids['month_input'].text = str(month)
        self.root.ids['workout_screen'].ids['year_input'].text = str(year)

        #Avatar change on 'profile_screen'
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
            with open(self.refresh_file, 'r') as f:
                refresh_token = f.read()

            #Getting new idToken
            id_token, local_id = self.authentication.exchange_refresh_token(refresh_token)

            #The firebase ID of individual users
            self.local_id = local_id
            self.id_token = id_token

            #Get DB data
            result = requests.get("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/" + local_id + ".json?auth=" + id_token)
            data = json.loads(result.content.decode()) #Decoding the data into 'string' as it comes in binary format initially, then converting it into JSON format

            result2 = requests.get("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Leaderboard/.json" )
            data2 = json.loads(result2.content.decode())

            #Updates avatar from DB
            avatar_image = self.root.ids['home_screen'].ids['avatar_image']
            avatar_image.source = "icons/avatars/" + data['Avatar']
            avatar_image = self.root.ids['profile_screen'].ids['avatar_image']
            avatar_image.source = "icons/avatars/" + data['Avatar']
            nav_avatar_image = self.root.ids['nav_avatar_image']
            nav_avatar_image.source = "icons/avatars/" + data['Avatar']

            #Get the users weight + height & display on homepage
            weight_label = self.root.ids['home_screen'].ids['weight_label']
            weight_label.text = str(data['Weight']) + " KG"

            height_label = self.root.ids['home_screen'].ids['height_label']
            height_label.text = str(data['Height']) + " CM"

            #Uses ML to predict and categorize a user in a BMI
            model.fit(X, y)
            self.predictions = model.predict([[data['Gender'], float(data['Height']), float(data['Weight'])]])

            #Accurary of decision tree algorithm
            #model.fit(X_train, y_train)
            #self.predictions = model.predict(X_test)
            #print(accuracy_score(y_test, self.predictions))

            if self.predictions[0] == 5:
                Clock.schedule_interval(self.notifications, 28800)
            elif self.predictions[0] == 4:
                Clock.schedule_interval(self.notifications, 28800)
            elif self.predictions[0] == 3:
                Clock.schedule_interval(self.notifications, 43200)
            elif self.predictions[0] == 2:
                Clock.schedule_interval(self.notifications, 80000)
            elif self.predictions[0] == 1:
                Clock.schedule_interval(self.notifications, 80000)
            elif self.predictions[0] == 0:
                Clock.schedule_interval(self.notifications, 80000)

            bmi_label = self.root.ids['home_screen'].ids['bmi_label']
            bmi_label.text = str(round((float(data['Weight']) / float(data['Height']) / float(data['Height']))*10000))

            if int(bmi_label.text) >= 18 and int(bmi_label.text) <= 25:
                bmi_label.color = 0, 100, 0, 1

            elif int(bmi_label.text) < 18:
                bmi_label.color = 1, 0.9, 0, 1

            elif int(bmi_label.text) >= 26 and int(bmi_label.text) <= 30:
                bmi_label.color = 1, 0.6, 0, 1

            elif int(bmi_label.text) > 30:
                bmi_label.color = 1, 0, 0, 1
                #Note: To get RGB colours above we get the three rgb colour values from rapidtables.com then we divide each one by 255

            #Get the users friends list
            self.friends_list = data['Friends']

            #User details
            self.user_name = data['Name']
            self.user_email = data['Email']
            self.level = data['Level']
            self.xp = data['Xp']
            self.user_id = data['User_Id']
            self.max = data['Max']

            #Populate users progress bar based on Xp from the DB
            self.root.ids['home_screen'].ids['progress_bar'].max = self.max
            progress_bar = self.root.ids['home_screen'].ids['progress_bar']
            progress_bar.value = self.xp

            self.xp_label = self.root.ids['home_screen'].ids['xp_label']
            self.xp_label.text = str(self.xp) + "/" + str(self.max) + " XP"

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
            if workouts != "":
                self.root.ids['log_screen'].ids['no_activity_label'].text = ""
                workout_keys = list(workouts.keys())
                #Sort workouts in order of date
                workout_keys.sort(key=lambda value: datetime.strptime(workouts[value]['Date'], "%d/%m/%Y"))
                workout_keys = workout_keys[::-1]
                for workout_key in workout_keys:
                    workout = workouts[workout_key]
                    W = WorkoutGrid(Workout_Image=workout['Workout_Image'], Description=workout['Description'],
                                      Unit_Image=workout['Unit_Image'], Amount=workout['Amount'], Units=workout['Units'],
                                      Likes=workout['Likes'], Date=workout['Date'])
                    banner.add_widget(W)

            leaderboard_grid = self.root.ids['leaderboard_screen'].ids['leaderboard_grid']
            #Remove widgets from leaderboards screen so it doesn't duplicate widgets
            for x in leaderboard_grid.walk():
                if x.__class__ == Leaderboard:
                    leaderboard_grid.remove_widget(x)

            #Populate Leaderboards screen
            leaderboard_keys = list(data2)
            leaderboard_keys.sort(key=lambda value: data2[value]['Points'])
            leaderboard_keys = leaderboard_keys[::-1]
            self.pos = 0
            for leaderboard_key in leaderboard_keys:
                pos = data2[leaderboard_key]
                self.pos += 1
                if self.pos > 3:
                    leaderboard_banner = Leaderboard(image_pos='icons/grey.png', pos=str(self.pos), avatar=pos['Avatar'],
                                                     name=str(pos['Name']), points=str(pos['Points']))
                    self.root.ids['leaderboard_screen'].ids['leaderboard_grid'].add_widget(leaderboard_banner)
                else:
                    self.img_pos = "icons/medal %s.png" %self.pos
                    leaderboard_banner = Leaderboard(image_pos=self.img_pos, pos=str(""), avatar=pos['Avatar'], name=str(pos['Name']), points=str(pos['Points']))
                    self.root.ids['leaderboard_screen'].ids['leaderboard_grid'].add_widget(leaderboard_banner)

            #Populate users badge collection
            badge_collection = self.root.ids['badge_screen'].ids['badge_collection']
            self.badge_tier = 0
            self.badges = data['Badges']
            if self.badges != "":
                badge_keys = list(self.badges.keys())
                for badge_key in badge_keys:
                    self.badge_tier += 1
                    badge = self.badges[badge_key]
                    img = Image(source=badge['Badges'])
                    lbl = Label(text="Tier %s Badge" % self.badge_tier, font_name= "Alphakind", color= (0,0,0,1))
                    badge_collection.add_widget(img)
                    badge_collection.add_widget(lbl)

            #Populate friends list on app
            friends_list_array = self.friends_list.split(",")
            for friend in friends_list_array:
                friend = friend.replace(" ", "")
                if friend == "":
                    continue
                else:
                    self.root.ids["social_screen"].ids["no_friend_label"].text = ""
                    userdata_request = requests.get('https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/.json?orderBy="User_Id"&equalTo=' + friend)
                    data = userdata_request.json()
                    friend_banner = FriendList(friend_id=friend, name=str(list(data.values())[0]['Name']), level=str(list(data.values())[0]['Level']))
                    self.root.ids["social_screen"].ids["friends_list_grid"].add_widget(friend_banner)


            self.change_screen("home_screen")
        except Exception as e:
            pass

    def logout(self,):
        with open(self.refresh_file, 'w') as f:
            f.write("")
        self.change_screen("login_screen")

        #Setting all avatar images to default
        avatar_image = self.root.ids['home_screen'].ids['avatar_image']
        avatar_image.source = 'icons/avatars/002-man.png'
        profile_avatar_image = self.root.ids['profile_screen'].ids['avatar_image']
        profile_avatar_image.source = 'icons/avatars/002-man.png'
        nav_avatar_image = self.root.ids['nav_avatar_image']
        nav_avatar_image.source = 'icons/avatars/002-man.png'

        #Clearing all widgets
        self.root.ids['add_user_screen'].ids['add_friend_input'].text = ""
        self.root.ids['add_user_screen'].ids['add_friend_label'].text = ""
        self.root.ids['workout_screen'].ids['workout_description'].text = ""
        self.root.ids['workout_screen'].ids['workout_description'].text = ""
        self.root.ids['workout_screen'].ids['amount_input'].text = ""
        self.root.ids['workout_screen'].ids['units_input'].text = ""
        self.root.ids['workout_screen'].ids['calories_input'].text = ""
        self.root.ids['workout_screen'].ids['repetitions_label'].color = 0, 0, 0, 1
        self.root.ids['workout_screen'].ids['distance_label'].color = 0, 0, 0, 1
        self.root.ids['workout_screen'].ids['time_label'].color = 0, 0, 0, 1
        self.root.ids['login_screen'].ids['user_email'].text = ""
        self.root.ids['login_screen'].ids['user_password'].text = ""
        self.root.ids['register_screen'].ids['register_email'].text = ""
        self.root.ids['register_screen'].ids['register_password'].text = ""
        self.root.ids['register_screen'].ids['register_name'].text = ""
        self.root.ids['register_screen'].ids['register_weight'].text = ""
        self.root.ids['register_screen'].ids['register_height'].text = ""


        #Clearing previous user friend list
        friend_list = self.root.ids['social_screen'].ids['friends_list_grid']
        for w in friend_list.walk():
            if w.__class__ == FriendList:
                friend_list.remove_widget(w)

        #Clearing previous users workout log
        workout_log = self.root.ids['log_screen'].ids['banner_grid']
        for w in workout_log.walk():
            if w.__class__ == WorkoutGrid:
                workout_log.remove_widget(w)

        #Clearing previous users friends workout logs
        friend_workout_log = self.root.ids['friend_screen'].ids['friend_banner_grid']
        for w in friend_workout_log.walk():
            if w.__class__ == WorkoutGrid:
                friend_workout_log.remove_widget(w)

        #Clearing previous users badges
        badge_collection = self.root.ids['badge_screen'].ids['badge_collection']
        for w in badge_collection.walk():
            badge_collection.remove_widget(w)


    #Changes avatar on app and also the DB
    def update_avatar(self, image, widget_id):
        avatar_image = self.root.ids['home_screen'].ids['avatar_image']
        avatar_image.source = "icons/avatars/" + image
        avatar_image = self.root.ids['profile_screen'].ids['avatar_image']
        avatar_image.source = "icons/avatars/" + image
        nav_avatar_image = self.root.ids['nav_avatar_image']
        nav_avatar_image.source = "icons/avatars/" + image

        #Patch request to update data (Avatar Image) in DB
        the_data = '{"Avatar": "%s"}' % image
        the_data2 = '{"Avatar": "%s"}' % image
        UrlRequest("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/%s.json" % (self.local_id), req_body=the_data, ca_file=certifi.where(), method='PATCH', )
        UrlRequest("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Leaderboard/%s.json" % (self.local_id), req_body=the_data2, ca_file=certifi.where(), method='PATCH', )

        result3 = requests.get("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Leaderboard/.json")
        data3 = json.loads(result3.content.decode())

        leaderboard_grid = self.root.ids['leaderboard_screen'].ids['leaderboard_grid']

        # Remove widgets from leaderboards screen so it doesn't duplicate widgets
        for x in leaderboard_grid.walk():
            if x.__class__ == Leaderboard:
                leaderboard_grid.remove_widget(x)

        # Populate Leaderboards screen
        leaderboard_keys = list(data3)
        leaderboard_keys.sort(key=lambda value: data3[value]['Points'])
        leaderboard_keys = leaderboard_keys[::-1]
        self.pos1 = 0
        for leaderboard_key in leaderboard_keys:
            pos = data3[leaderboard_key]
            self.pos1 += 1
            if self.pos1 > 3:
                leaderboard_banner = Leaderboard(image_pos='icons/grey.png', pos=str(self.pos1), avatar=pos['Avatar'],
                                                 name=str(pos['Name']), points=str(pos['Points']))
                self.root.ids['leaderboard_screen'].ids['leaderboard_grid'].add_widget(leaderboard_banner)
            else:
                self.img_pos1 = "icons/medal %s.png" % self.pos1
                leaderboard_banner = Leaderboard(image_pos=self.img_pos1, pos=str(""), avatar=pos['Avatar'],
                                                 name=str(pos['Name']), points=str(pos['Points']))
                self.root.ids['leaderboard_screen'].ids['leaderboard_grid'].add_widget(leaderboard_banner)

        self.change_screen("profile_screen")

    def change_screen(self, screen_name):
        #Use 'screen_manager' to do this
        screen_manager = self.root.ids['screen_manager']
        screen_manager.current = screen_name #This will make the current screen be on whatever the screen name is

        #Clear all widgets when a new screen is loaded
        self.root.ids['add_user_screen'].ids['add_friend_input'].text = ""
        self.root.ids['add_user_screen'].ids['add_friend_label'].text = ""
        self.root.ids['workout_screen'].ids['workout_description'].text = ""
        self.root.ids['workout_screen'].ids['workout_description'].text = ""
        self.root.ids['workout_screen'].ids['amount_input'].text = ""
        self.root.ids['workout_screen'].ids['units_input'].text = ""
        self.root.ids['workout_screen'].ids['calories_input'].text = ""
        self.root.ids['workout_screen'].ids['repetitions_label'].color = 0, 0, 0, 1
        self.root.ids['workout_screen'].ids['distance_label'].color = 0, 0, 0, 1
        self.root.ids['workout_screen'].ids['time_label'].color = 0, 0, 0, 1
        self.root.ids['login_screen'].ids['user_email'].text = ""
        self.root.ids['login_screen'].ids['user_password'].text = ""
        self.root.ids['login_screen'].ids['error_label'].text = ""
        self.root.ids['register_screen'].ids['register_email'].text = ""
        self.root.ids['register_screen'].ids['register_password'].text = ""
        self.root.ids['register_screen'].ids['register_name'].text = ""
        self.root.ids['register_screen'].ids['register_weight'].text = ""
        self.root.ids['register_screen'].ids['register_height'].text = ""
        self.root.ids['register_screen'].ids['error_label'].text = ""
        self.root.ids['food_search_screen'].ids['carb_label'].text = ""
        self.root.ids['food_search_screen'].ids['prot_label'].text = ""
        self.root.ids['food_search_screen'].ids['fat_label'].text = ""
        self.root.ids['food_search_screen'].ids['calories_label'].text = ""
        self.root.ids['food_search_screen'].ids['food_search'].text = ""
        self.root.ids['food_search_screen'].ids['food_img'].source = ""


    def nav_drawer(self):
        nav_drawer = self.root.ids['nav_drawer']
        nav_user_name = self.root.ids['nav_user_name']
        nav_user_name.text = self.user_name
        nav_user_email = self.root.ids['nav_user_email']
        nav_user_email.text = self.user_email

        nav_drawer.set_state()

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
        if user_id == str(self.user_id):
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
            userdata_request = requests.get('https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/.json?orderBy="User_Id"&equalTo=' + user_id)
            data = userdata_request.json()
            friend_patch = UrlRequest("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/%s.json?auth=%s" % (self.local_id, self.id_token), req_body=patch_data, ca_file=certifi.where(), method='PATCH', )
            friend_banner = FriendList(friend_id=user_id, name=str(list(data.values())[0]['Name']), level=str(list(data.values())[0]['Level']))
            self.root.ids["social_screen"].ids["friends_list_grid"].add_widget(friend_banner)
            self.root.ids["social_screen"].ids["no_friend_label"].text = ""
            self.root.ids['add_user_screen'].ids['add_friend_input'].text = ""

    def friends_screen(self, user_id, widget):
        #Gets friends workout using their 'user_id'
        userdata_request = requests.get('https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/.json?orderBy="User_Id"&equalTo=' + user_id)
        data = userdata_request.json()

        self.friends_id = user_id

        workouts = list(data.values())[0]['Workouts']
        banner = self.root.ids['friend_screen'].ids['friend_banner_grid']

        #Remove the widget if it is a workout banner so it doesn't keep duplicating when viewing a friend's workout
        for W in banner.walk():
            if W.__class__ == WorkoutGrid:
                banner.remove_widget(W)

        #Populate friend's avatar image
        friend_avatar_image = self.root.ids['friend_screen'].ids['friend_avatar']
        friend_avatar_image.source = "icons/avatars/" + list(data.values())[0]['Avatar']

        #Populate friend's id
        friends_id = self.root.ids['friend_screen'].ids['friend_id_num']
        friends_id.text = "ID: " + str(self.friends_id)

        #Populate friend's level
        friend_level = self.root.ids['friend_screen'].ids['friend_level']
        friend_level.text = "Level:  " + str(list(data.values())[0]['Level'])

        #Populate friend's name
        friend_name = self.root.ids['friend_screen'].ids['friend_name']
        friend_name.text = "Name:  " + list(data.values())[0]['Name']

        #Populate friend screen
        if workouts == "":
            self.root.ids['friend_screen'].ids['no_friend_activity_label'].text = "This user has no logged activities"
            self.change_screen("friend_screen")
            return

        workout_keys = list(workouts.keys())
        workout_keys.sort(key=lambda value: datetime.strptime(workouts[value]['Date'], "%d/%m/%Y"))
        workout_keys = workout_keys[::-1]
        self.root.ids['friend_screen'].ids['no_friend_activity_label'].text = ""
        for key in workout_keys:
            workout = workouts[key]
            W = WorkoutGrid(Workout_Image=workout['Workout_Image'], Description=workout['Description'],
                            Unit_Image=workout['Unit_Image'], Amount=workout['Amount'], Units=workout['Units'],
                            Likes=workout['Likes'], can_like=True, Date=workout['Date'], workout_key=key)
            banner.add_widget(W)

        self.change_screen("friend_screen")

    def log_workout(self):
        result = requests.get("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/" + self.local_id + ".json?auth=" + self.id_token)
        data = json.loads(result.content.decode())

        result2 = requests.get("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Leaderboard/" + self.local_id + ".json?auth=" + self.id_token)
        data2 = json.loads(result2.content.decode())

        self.level = data['Level']
        self.xp = data['Xp']
        self.points = data2['Points']

        #Gets user data (Entries in log screen)
        workout_screen = self.root.ids["workout_screen"]
        workout_description = workout_screen.ids["workout_description"].text
        workout_amount = workout_screen.ids["amount_input"].text
        workout_unit = workout_screen.ids["units_input"].text
        workout_month_date = workout_screen.ids["month_input"].text
        workout_year_date = workout_screen.ids["year_input"].text
        workout_day_date = workout_screen.ids["day_input"].text
        workout_calories_burnt = workout_screen.ids["calories_input"].text

        self.xp_earnt = 0

        #Checks if user fields (With data) are appropriate
        if self.workout_icon == None:
            pass
            return
        if self.choice == None:
            workout_screen.ids["time_label"].color = 1, 0, 0, 1
            workout_screen.ids["distance_label"].color = 1, 0, 0, 1
            workout_screen.ids["repetitions_label"].color = 1, 0, 0, 1
            return
        if workout_description == "":
            workout_screen.ids["workout_description"].background_color = 1, 0, 0, 1
            return
        if workout_amount == "":
            workout_screen.ids["amount_input"].background_color = 1, 0, 0, 1
            return
        if workout_unit == "":
            workout_screen.ids["units_input"].background_color = 1, 0, 0, 1
            return
        if workout_calories_burnt == "":
            workout_screen.ids["calories_input"].background_color = 1, 0, 0, 1
            return
        if workout_day_date == "":
            workout_screen.ids["day_input"].background_color = 1, 0, 0, 1
            return
        if workout_month_date == "":
            workout_screen.ids["month_input"].background_color = 1, 0, 0, 1
            return
        if workout_year_date == "":
            workout_screen.ids["year_input"].background_color = 1, 0, 0, 1
            return

        #If fields are ok update the DB
        workout_data = {"Workout_Image": self.workout_icon, "Description": workout_description, "Likes": 0, "Amount": workout_amount,
                        "Units": workout_unit, "Unit_Image": self.choice, "Date": workout_day_date + "/" + workout_month_date + "/" + workout_year_date}

        workout_req = UrlRequest("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/%s/Workouts.json?auth=%s" % (
                self.local_id, self.id_token), req_body=json.dumps(workout_data), ca_file=certifi.where(),)

        banner = self.root.ids['log_screen'].ids['banner_grid']
        self.root.ids['log_screen'].ids['no_activity_label'].text = ""
        W = WorkoutGrid(Workout_Image=self.workout_icon, Description=workout_description,
                          Unit_Image=self.choice, Amount=workout_amount, Units=workout_unit,
                          Likes="0", Date=workout_day_date + "/" + workout_month_date + "/" + workout_year_date)
        banner.add_widget(W, index=len(banner.children))

        self.change_screen("home_screen")

        #Based off how many calories a user burns they gain the relevant xp
        if int(workout_calories_burnt) == 0:
            self.xp_earnt = 0
            self.points +=0
            self.root.ids['home_screen'].ids['progress_bar'].value = self.xp + self.xp_earnt

        elif int(workout_calories_burnt) > 0 and int(workout_calories_burnt) <= 100:
            self.xp_earnt = 5
            self.points += 10
            #Add xp to progress bar
            self.root.ids['home_screen'].ids['progress_bar'].value = self.xp + self.xp_earnt

        elif int(workout_calories_burnt) > 100 and int(workout_calories_burnt) <= 200:
            self.xp_earnt = 10
            self.points += 20
            self.root.ids['home_screen'].ids['progress_bar'].value = self.xp + self.xp_earnt

        elif int(workout_calories_burnt) > 200 and int(workout_calories_burnt) <= 400:
            self.xp_earnt = 20
            self.points += 30
            self.root.ids['home_screen'].ids['progress_bar'].value = self.xp + self.xp_earnt

        elif int(workout_calories_burnt) > 400 and int(workout_calories_burnt) <= 600:
            self.xp_earnt = 30
            self.points += 40
            self.root.ids['home_screen'].ids['progress_bar'].value = self.xp + self.xp_earnt

        elif int(workout_calories_burnt) > 600:
            self.xp_earnt = 40
            self.points += 50
            self.root.ids['home_screen'].ids['progress_bar'].value = self.xp + self.xp_earnt


        #Sends xp to DB
        patch_xp = '{"Xp": %s}' % ((self.xp + int(self.xp_earnt)))

        patch_points = '{"Points": %s}' % (self.points)

        #Updates the DB with new XP

        self.update_xp_request = UrlRequest("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/%s/.json?auth=%s" % (
            self.local_id, self.id_token), req_body=patch_xp, ca_file=certifi.where(), method='PATCH', )

        self.update_points_request = UrlRequest("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/%s/.json?auth=%s" % (
                self.local_id, self.id_token), req_body=patch_points, ca_file=certifi.where(), method='PATCH', )

        self.update_points_request = UrlRequest("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Leaderboard/%s/.json?auth=%s" % (
                self.local_id, self.id_token), req_body=patch_points, ca_file=certifi.where(), method='PATCH', )

        self.xp_label = self.root.ids['home_screen'].ids['xp_label']
        self.xp_label.text = str((self.xp + int(self.xp_earnt))) + "/" + str(data['Max']) + " XP"

        close_button = MDFlatButton(text="CLOSE", on_release=self.close_dialog, text_color=self.theme_cls.primary_color)
        self.dialog = MDDialog(title="[font=Alphakind.ttf]Workout Logged[/font]",
                               text="[font=Alphakind.ttf]You have logged a workout and have earnt %s xp[/font]" % (self.xp_earnt), size_hint=(0.7, 1),
                               buttons=[close_button])

        self.dialog.open()

        if self.root.ids['home_screen'].ids['progress_bar'].value == self.root.ids['home_screen'].ids['progress_bar'].max:
            self.level = int(self.level) + 1
            self.increase_lvl()

        #Clear workout widgets once a workout has been logged
        self.root.ids['workout_screen'].ids['workout_description'].text = ""
        self.root.ids['workout_screen'].ids['workout_description'].text = ""
        self.root.ids['workout_screen'].ids['amount_input'].text = ""
        self.root.ids['workout_screen'].ids['units_input'].text = ""
        self.root.ids['workout_screen'].ids['calories_input'].text = ""
        self.root.ids['workout_screen'].ids['repetitions_label'].color = 0, 0, 0, 1
        self.root.ids['workout_screen'].ids['distance_label'].color = 0, 0, 0, 1
        self.root.ids['workout_screen'].ids['time_label'].color = 0, 0, 0, 1

        result3 = requests.get("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Leaderboard/.json")
        data3 = json.loads(result3.content.decode())

        leaderboard_grid = self.root.ids['leaderboard_screen'].ids['leaderboard_grid']
        # Remove widgets from leaderboards screen so it doesn't duplicate widgets
        for x in leaderboard_grid.walk():
            if x.__class__ == Leaderboard:
                leaderboard_grid.remove_widget(x)

        #Populate Leaderboards screen
        leaderboard_keys = list(data3)
        leaderboard_keys.sort(key=lambda value: data3[value]['Points'])
        leaderboard_keys = leaderboard_keys[::-1]
        self.pos1 = 0
        for leaderboard_key in leaderboard_keys:
            pos = data3[leaderboard_key]
            self.pos1+=1
            if self.pos1 > 3:
                leaderboard_banner = Leaderboard(image_pos='icons/grey.png', pos=str(self.pos1), avatar=pos['Avatar'],
                                                 name=str(pos['Name']), points=str(pos['Points']))
                self.root.ids['leaderboard_screen'].ids['leaderboard_grid'].add_widget(leaderboard_banner)
            else:
                self.img_pos1 = "icons/medal %s.png" % self.pos1
                leaderboard_banner = Leaderboard(image_pos=self.img_pos1, pos=str(""), avatar=pos['Avatar'],
                                                 name=str(pos['Name']), points=str(pos['Points']))
                self.root.ids['leaderboard_screen'].ids['leaderboard_grid'].add_widget(leaderboard_banner)

    #Increases the level of the user when they level up
    def increase_lvl(self):
        self.dialog.dismiss()

        result = requests.get("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/" + self.local_id + ".json?auth=" + self.id_token)
        data = json.loads(result.content.decode())

        #Scales up the progress bar after each level
        self.new_max = data['Max'] * 1.5
        self.root.ids['home_screen'].ids['progress_bar'].max = int(self.new_max)
        patch_max = '{"Max": %s}' % int(self.new_max)
        self.update_max_request = UrlRequest(
            "https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/%s/.json?auth=%s" % (
                self.local_id, self.id_token), req_body=patch_max, ca_file=certifi.where(), method='PATCH', )

        self.badge = ""
        self.badge_tier = 0

        #If user reaches certain levels they earn badges as a reward
        if (self.level) == 2:
            self.badge = "icons/badges/002-medal.png"
            close_button2 = MDFlatButton(text="CLOSE", on_release=self.close_dialog2, text_color=self.theme_cls.primary_color)
            self.dialog2 = MDDialog(title="[font=Alphakind.ttf]Badge Earnt[/font]", type="simple", size_hint=(.85, 1), items=[Item(text="[font=Alphakind.ttf]Tier 1 badge Unlocked[/font]",
            source=self.badge), ], buttons=[close_button2])
            self.dialog2.open()
            #post_badges = "{'Badges': 'Hello'}"
            #Updates DB with new user badge
            self.update_badge_request = UrlRequest("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/%s/Badges.json?auth=%s" % (
                self.local_id, self.id_token), req_body=json.dumps({'Badges': self.badge}), ca_file=certifi.where(),)

        elif (self.level) == 5:
            self.badge = "icons/badges/005-award.png"
            close_button2 = MDFlatButton(text="CLOSE", on_release=self.close_dialog2, text_color=self.theme_cls.primary_color)
            self.dialog2 = MDDialog(title="[font=Alphakind.ttf]Badge Earnt[/font]", type="simple", size_hint=(.85, 1), items=[Item(text="[font=Alphakind.ttf]Tier 2 badge Unlocked[/font]",
            source=self.badge), ], buttons=[close_button2])
            self.dialog2.open()
            self.update_badge_request = UrlRequest("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/%s/Badges.json?auth=%s" % (
                    self.local_id, self.id_token), req_body=json.dumps({'Badges': self.badge}), ca_file=certifi.where(),)

        elif (self.level) == 10:
            self.badge = "icons/badges/007-badge.png"
            close_button2 = MDFlatButton(text="CLOSE", on_release=self.close_dialog2, text_color=self.theme_cls.primary_color)
            self.dialog2 = MDDialog(title="[font=Alphakind.ttf]Badge Earnt[/font]", type="simple", size_hint=(.85, 1), items=[Item(text="[font=Alphakind.ttf]Tier 3 badge Unlocked[/font]",
            source=self.badge), ], buttons=[close_button2])
            self.dialog2.open()
            self.update_badge_request = UrlRequest("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/%s/Badges.json?auth=%s" % (
                    self.local_id, self.id_token), req_body=json.dumps({'Badges': self.badge}), ca_file=certifi.where(),)

        elif (self.level) == 15:
            self.badge = "icons/badges/012-trophy.png"
            close_button2 = MDFlatButton(text="CLOSE", on_release=self.close_dialog2, text_color=self.theme_cls.primary_color)
            self.dialog2 = MDDialog(title="[font=Alphakind.ttf]Badge Earnt[/font]", type="simple", size_hint=(.85, 1), items=[Item(text="[font=Alphakind.ttf]Tier 4 badge Unlocked[/font]",
            source=self.badge), ], buttons=[close_button2])
            self.dialog2.open()
            self.update_badge_request = UrlRequest("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/%s/Badges.json?auth=%s" % (
                    self.local_id, self.id_token), req_body=json.dumps({'Badges': self.badge}), ca_file=certifi.where(),)

        elif (self.level) == 25:
            self.badge = "icons/badges/036-award.png"
            close_button2 = MDFlatButton(text="CLOSE", on_release=self.close_dialog2, text_color=self.theme_cls.primary_color)
            self.dialog2 = MDDialog(title="[font=Alphakind.ttf]Badge Earnt[/font]", type="simple", size_hint=(.85, 1), items=[Item(text="[font=Alphakind.ttf]Tier 5 badge Unlocked[/font]",
            source=self.badge), ], buttons=[close_button2])
            self.dialog2.open()
            self.update_badge_request = UrlRequest("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/%s/Badges.json?auth=%s" % (
                    self.local_id, self.id_token), req_body=json.dumps({'Badges': self.badge}), ca_file=certifi.where(),)

        elif (self.level) == 50:
            self.badge = "icons/badges/042-trophy.png"
            close_button2 = MDFlatButton(text="CLOSE", on_release=self.close_dialog2, text_color=self.theme_cls.primary_color)
            self.dialog2 = MDDialog(title="[font=Alphakind.ttf]Badge Earnt[/font]", type="simple", size_hint=(.85, 1), items=[Item(text="[font=Alphakind.ttf]Tier 6 badge Unlocked[/font]",
            source=self.badge), ], buttons=[close_button2])
            self.dialog2.open()
            self.update_badge_request = UrlRequest("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/%s/Badges.json?auth=%s" % (
                    self.local_id, self.id_token), req_body=json.dumps({'Badges': self.badge}), ca_file=certifi.where(),)

        close_button1 = MDFlatButton(text="CLOSE", on_release=self.close_dialog, text_color=self.theme_cls.primary_color)
        self.dialog = MDDialog(title="[font=Alphakind.ttf]Level Gain[/font]",
                               text="[font=Alphakind.ttf]Congratulations! You have levelled up, you are now level %s[/font]" % (
                                   self.level), size_hint=(0.7, 1),
                               buttons=[close_button1],)
        self.dialog.open()

        #Updates DB with new user lvl
        patch_lvl = '{"Level": %s}' % (self.level)
        patch_xp = '{"Xp": 0}'

        #Updates the DB with new XP
        self.update_xp_request = UrlRequest(
            "https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/%s/.json?auth=%s" % (
                self.local_id, self.id_token), req_body=patch_xp, ca_file=certifi.where(), method='PATCH', )

        #Updates DB with new user lvl
        self.update_lvl_request = UrlRequest(
            "https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/%s/.json?auth=%s" % (
                self.local_id, self.id_token), req_body=patch_lvl, ca_file=certifi.where(), method='PATCH', )

        self.root.ids['home_screen'].ids['progress_bar'].value = 0

        #Updates level from DB
        level = self.root.ids['home_screen'].ids['level_label']
        level.text = "Level " + str(self.level)
        level = self.root.ids['profile_screen'].ids['level_label']
        level.text = "Level " + str(self.level)

        #Populate users badge collection
        if self.badge != "":
            self.badge_tier +=1
            badge_collection = self.root.ids['badge_screen'].ids['badge_collection']
            img = Image(source=self.badge)
            lbl = Label(text="New Badge Unlocked!", font_name="Alphakind", color=(0, 0, 0, 1))
            badge_collection.add_widget(img)
            badge_collection.add_widget(lbl)

        self.xp_label = self.root.ids['home_screen'].ids['xp_label']
        self.xp_label.text = "0" + "/" + str(self.new_max) + " XP"

    def new_user_info(self):
        show = P()

        self.popup_window = Popup(title="Update", content=show, size_hint=(1, .5))

        self.popup_window.open()

    def update_new_user_info(self, new_height, new_weight, error_label):
        if new_height == "" or new_weight == "":
            error_label.text = "Please fill in all fields"

        else:
            patch_new_info = '{"Weight": %s, "Height": %s}' %(new_weight, new_height)

            self.update_newinfo_request = UrlRequest(
                "https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/%s/.json?auth=%s" % (
                    self.local_id, self.id_token), req_body=patch_new_info, ca_file=certifi.where(), method='PATCH',)

            bmi_label = self.root.ids['home_screen'].ids['bmi_label']
            bmi_label.text = str(round((float(new_weight) / float(new_height) / float(new_height)) * 10000))

            home_weight_label = self.root.ids['home_screen'].ids['weight_label']
            home_weight_label.text = str(new_weight) + " KG"

            home_height_label = self.root.ids['home_screen'].ids['height_label']
            home_height_label.text = str(new_height) + " CM"

            if int(bmi_label.text) >= 18 and int(bmi_label.text) <= 25:
                bmi_label.color = 0, 100, 0, 1

            elif int(bmi_label.text) < 18:
                bmi_label.color = 1, 0.9, 0, 1

            elif int(bmi_label.text) >= 26 and int(bmi_label.text) <= 30:
                bmi_label.color = 1, 0.6, 0, 1

            elif int(bmi_label.text) > 30:
                bmi_label.color = 1, 0, 0, 1

            self.popup_window.dismiss()

    def close_dialog(self, obj):
        self.dialog.dismiss(force=True)

    def close_dialog2(self, obj):
        self.dialog2.dismiss(force=True)

    def get_food_info(self):

        carb_label = self.root.ids['food_search_screen'].ids['carb_label']
        prot_label = self.root.ids['food_search_screen'].ids['prot_label']
        fat_label = self.root.ids['food_search_screen'].ids['fat_label']
        calories_label = self.root.ids['food_search_screen'].ids['calories_label']
        food_input = self.root.ids['food_search_screen'].ids['food_search'].text
        food_img = self.root.ids['food_search_screen'].ids['food_img']

        self.get_food = requests.get('https://api.edamam.com/api/food-database/v2/parser?ingr={0}%20&app_id=c649c398&app_key=9d0b2632cb6aff689dffad7080d73fb9'.format(food_input))
        self.food_data = json.loads(self.get_food.content.decode())

        try:
            if food_input == "":
                self.root.ids['food_search_screen'].ids['food_error_label'].text = "Please enter a food item to search"
                self.root.ids['food_search_screen'].ids['carb_label'].text = ""
                self.root.ids['food_search_screen'].ids['prot_label'].text = ""
                self.root.ids['food_search_screen'].ids['fat_label'].text = ""
                self.root.ids['food_search_screen'].ids['calories_label'].text = ""
                self.root.ids['food_search_screen'].ids['food_search'].text = ""
                self.root.ids['food_search_screen'].ids['food_img'].source = ""
            else:
                self.get_food = requests.get('https://api.edamam.com/api/food-database/v2/parser?ingr={0}%20&app_id=c649c398&app_key=9d0b2632cb6aff689dffad7080d73fb9'.format(food_input))
                self.food_data = json.loads(self.get_food.content.decode())

                calories_label.text = "Calories:      " + str(self.food_data['parsed'][0]['food']['nutrients']['ENERC_KCAL']) + " Kcals"
                carb_label.text = "Carbohydrates:     " + str(self.food_data['parsed'][0]['food']['nutrients']['CHOCDF']) + " G"
                prot_label.text = "Protein:         " + str(self.food_data['parsed'][0]['food']['nutrients']['PROCNT']) + " G"
                fat_label.text = "Fat:         " + str(self.food_data['parsed'][0]['food']['nutrients']['FAT']) + " G"
                food_img.source = str(self.food_data['parsed'][0]['food']['image'])

                #print(str(food_data['parsed'][0]['food']['image']))
                self.root.ids['food_search_screen'].ids['food_search'].text = ""
                self.root.ids['food_search_screen'].ids['food_error_label'].text = ""
        except:
            self.root.ids['food_search_screen'].ids['food_error_label'].text = "Unable to get information of food item"
            self.root.ids['food_search_screen'].ids['carb_label'].text = ""
            self.root.ids['food_search_screen'].ids['prot_label'].text = ""
            self.root.ids['food_search_screen'].ids['fat_label'].text = ""
            self.root.ids['food_search_screen'].ids['calories_label'].text = ""
            self.root.ids['food_search_screen'].ids['food_search'].text = ""
            self.root.ids['food_search_screen'].ids['food_img'].source = ""


    def notifications(self, kwargs):
      notification.notify("SmartFit", "Make Sure To Workout & Use SmartFit To Log Activities!")


SmartFit().run()