from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
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
from functools import partial
import requests
import json
from friendlist import FriendList
from kivymd.uix.dialog import MDDialog
from kivy.network.urlrequest import UrlRequest
import certifi

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

class FriendScreen(Screen):
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

class Item(OneLineAvatarListItem):
    divider = None
    source = StringProperty()

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

        self.root.ids["social_screen"].ids["no_friend_label"].text = "You currently do not have any friends"
        self.root.ids['log_screen'].ids['no_activity_label'].text = "You do not have logged activities"

        #Populate the day, month & year inputs in the 'add workout' screen
        current_date = datetime.now()
        day = current_date.day
        month = current_date.month
        year = current_date.year
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
            with open("refresh_token.txt", 'r') as f:
                refresh_token = f.read()
                #self.change_screen("home_screen") #Remove This Line After Done

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
            nav_avatar_image = self.root.ids['nav_avatar_image']
            nav_avatar_image.source = "icons/avatars/" + data['Avatar']

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

            #User details
            self.user_name = data['Name']
            self.user_email = data['Email']
            self.level = data['Level']
            self.xp = data['Xp']

            #Populate users progress bar based on Xp from the DB
            progress_bar = self.root.ids['home_screen'].ids['progress_bar']
            progress_bar.value = self.xp

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
                workout_keys.sort(key=lambda value: datetime.strptime(workouts[value]['Date'], "%m/%d/%Y"))
                workout_keys = workout_keys[::-1]
                for workout_key in workout_keys:
                    workout = workouts[workout_key]
                    W = WorkoutGrid(Workout_Image=workout['Workout_Image'], Description=workout['Description'],
                                      Unit_Image=workout['Unit_Image'], Amount=workout['Amount'], Units=workout['Units'],
                                      Likes=workout['Likes'], Date=workout['Date'])
                    banner.add_widget(W)

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
        with open("refresh_token.txt", 'w') as f:
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
        self.root.ids['workout_screen'].ids['repetitions_label'].color = 0, 0, 0
        self.root.ids['workout_screen'].ids['distance_label'].color = 0, 0, 0
        self.root.ids['workout_screen'].ids['time_label'].color = 0, 0, 0
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
        requests.patch("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/" + self.local_id + ".json",
                       data=the_data)

        self.change_screen("profile_screen")

    def change_screen(self, screen_name):
        result = requests.get(
            "https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/" + self.local_id + ".json?auth=" + self.id_token)
        data = json.loads(result.content.decode())

        self.level = data['Level']
        self.xp = data['Xp']
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
        self.root.ids['workout_screen'].ids['repetitions_label'].color = 0,0,0
        self.root.ids['workout_screen'].ids['distance_label'].color = 0, 0, 0
        self.root.ids['workout_screen'].ids['time_label'].color = 0, 0, 0
        self.root.ids['login_screen'].ids['user_email'].text = ""
        self.root.ids['login_screen'].ids['user_password'].text = ""
        self.root.ids['login_screen'].ids['error_label'].text = ""
        self.root.ids['register_screen'].ids['register_email'].text = ""
        self.root.ids['register_screen'].ids['register_password'].text = ""
        self.root.ids['register_screen'].ids['register_name'].text = ""
        self.root.ids['register_screen'].ids['register_weight'].text = ""
        self.root.ids['register_screen'].ids['register_height'].text = ""
        self.root.ids['register_screen'].ids['error_label'].text = ""


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
            userdata_request = requests.get('https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/.json?orderBy="User_Id"&equalTo=' + user_id)
            data = userdata_request.json()
            friend_patch = requests.patch("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/%s.json?auth=%s" % (self.local_id, self.id_token), data=patch_data)
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

        #Populate friend screen
        if workouts == "":
            self.root.ids['friend_screen'].ids['no_friend_activity_label'].text = "This user has no logged activities"
            self.change_screen("friend_screen")
            return

        workout_keys = list(workouts.keys())
        workout_keys.sort(key=lambda value: datetime.strptime(workouts[value]['Date'], "%m/%d/%Y"))
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
        self.root.ids['log_screen'].ids['no_activity_label'].text = ""
        W = WorkoutGrid(Workout_Image=self.workout_icon, Description=workout_description,
                          Unit_Image=self.choice, Amount=workout_amount, Units=workout_unit,
                          Likes="0", Date=workout_day_date + "/" + workout_month_date + "/" + workout_year_date)
        banner.add_widget(W, index=len(banner.children))


        self.change_screen("home_screen")

        #Based off how many calories a user burns they gain the relevant xp
        if int(workout_calories_burnt) == 0:
            self.xp_earnt = 0
            self.root.ids['home_screen'].ids['progress_bar'].value = self.xp + self.xp_earnt

        elif int(workout_calories_burnt) > 100 and int(workout_calories_burnt) < 300:
            self.xp_earnt = 5
            #Add xp to progress bar
            self.root.ids['home_screen'].ids['progress_bar'].value = self.xp + self.xp_earnt

        elif int(workout_calories_burnt) > 300 and int(workout_calories_burnt) < 700:
            self.xp_earnt = 10
            self.root.ids['home_screen'].ids['progress_bar'].value = self.xp + self.xp_earnt

        elif int(workout_calories_burnt) > 700 and int(workout_calories_burnt) < 1000:
            self.xp_earnt = 20
            self.root.ids['home_screen'].ids['progress_bar'].value = self.xp + self.xp_earnt

        elif int(workout_calories_burnt) > 1000 and int(workout_calories_burnt) < 2000:
            self.xp_earnt = 30
            self.root.ids['home_screen'].ids['progress_bar'].value = self.xp + self.xp_earnt

        elif int(workout_calories_burnt) > 2000:
            self.xp_earnt = 40
            self.root.ids['home_screen'].ids['progress_bar'].value = self.xp + self.xp_earnt


        #Sends xp to DB
        patch_xp = '{"Xp": %s}' % (self.xp + int(self.xp_earnt))

        #Updates the DB with new XP
        self.update_xp_request = requests.patch("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/%s.json?auth=%s" % (self.local_id, self.id_token), data=patch_xp)


        close_button = MDFlatButton(text="CLOSE", on_release=self.close_dialog, text_color=self.theme_cls.primary_color)
        self.dialog = MDDialog(title="[font=Alphakind.ttf]Workout Logged[/font]",
                               text="[font=Alphakind.ttf]You have logged a workout and have earnt %s xp[/font]" % (self.xp_earnt), size_hint=(0.7, 1),
                               buttons=[close_button])
        self.dialog.open()

        if self.root.ids['home_screen'].ids['progress_bar'].value == 100:
            self.level = int(self.level) + 1
            self.increase_lvl()
            return

        #Clear workout widgets once a workout has been logged
        self.root.ids['workout_screen'].ids['workout_description'].text = ""
        self.root.ids['workout_screen'].ids['workout_description'].text = ""
        self.root.ids['workout_screen'].ids['amount_input'].text = ""
        self.root.ids['workout_screen'].ids['units_input'].text = ""
        self.root.ids['workout_screen'].ids['calories_input'].text = ""
        self.root.ids['workout_screen'].ids['repetitions_label'].color = 0, 0, 0
        self.root.ids['workout_screen'].ids['distance_label'].color = 0, 0, 0
        self.root.ids['workout_screen'].ids['time_label'].color = 0, 0, 0

    #Increases the level of the user when they level up
    def increase_lvl(self):
        self.dialog.dismiss()

        #If user reaches certain levels they earn badges as a reward
        if (self.level) == 2:
            close_button1 = MDFlatButton(text="CLOSE", on_release=self.close_dialog, text_color=self.theme_cls.primary_color)
            self.dialog = MDDialog(title="[font=Alphakind.ttf]Badge Earnt[/font]", type="simple", size_hint=(.85, 1), items=[
            Item(text="[font=Alphakind.ttf]Level 2 badge Unlocked[/font]", source="icons/002-medal.png"),
            ], buttons=[close_button1])

            self.dialog.open()

        close_button = MDFlatButton(text="CLOSE", on_release=self.close_dialog, text_color=self.theme_cls.primary_color)
        self.dialog = MDDialog(title="[font=Alphakind.ttf]Level Gain[/font]",
                               text="[font=Alphakind.ttf]Congratulations! You have levelled up, you are now level %s[/font]" % (
                                   self.level), size_hint=(0.7, 1),
                               buttons=[close_button], )
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

    def close_dialog(self, obj):
        self.dialog.dismiss()

SmartFit().run()