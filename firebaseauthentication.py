import requests
import json
from kivy.app import App
from kivy.network.urlrequest import UrlRequest
import certifi
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRectangleFlatButton, MDRoundFlatButton, MDFlatButton

class Authentication():
    api_key = "AIzaSyAiE0NHSX-n8i-indM7bOwJVFO5LiKvAts"
    def register(self, email, password, name, weight, height):
        #Send registration details to DB
        #Firebase returns, localID(For users to identify them), authToken(Authorization token for users), refreshToken(Used to refresh authToken)
        #The below url is used to register new users to the DB
        register_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key=" + self.api_key
        register_data = {"email": email, "password": password, "name": name, "weight": weight, "height": height,
                         "returnSecureToken": True}
        main_app = App.get_running_app()


        height = main_app.root.ids["register_screen"].ids["register_height"]
        self.height_text = height.text

        weight = main_app.root.ids["register_screen"].ids["register_weight"]
        self.weight_text = weight.text

        name = main_app.root.ids["register_screen"].ids["register_name"]
        self.name_text = name.text

        email = main_app.root.ids["register_screen"].ids["register_email"]
        self.email_text = email.text


        if self.weight_text == "" or self.name_text == "" or self.height_text == "" :
            App.get_running_app().root.ids['register_screen'].ids['error_label'].text = "Please fill in all the fields"
            #Firebase checks if email & password are correct
        else:
            self.register_request = requests.post(register_url, data=register_data)
            if self.register_request.ok == False:
                error_data = json.loads(self.register_request.content.decode())
                error_message = error_data["error"]['message']
                App.get_running_app().root.ids['register_screen'].ids['error_label'].text = error_message
            else:
                register_dict = json.loads(self.register_request.content.decode())
                refresh_token = register_dict['refreshToken']
                localId = register_dict['localId']
                idToken = register_dict['idToken']

                #Save refreshToken locally so users can refresh their sessions
                with open("refresh_token.txt", "w") as f:
                    f.write(refresh_token)

                #Save localId & idToken
                App.get_running_app().local_id = localId
                App.get_running_app().id_token = idToken

                friend_req = requests.get("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/Next_User_Id.json?auth=" + idToken)
                User_Id = friend_req.json()
                #Create user_id for new user
                friend_patch_data = '{"Next_User_Id": %s}' % str(User_Id + 1)
                friend_patch_req = requests.patch("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/.json?auth=" + idToken, data=friend_patch_data)

                #Create user with a localID & default information
                the_data = {"Avatar": "002-man.png", "Friends": "", "Workouts": "", "Level": "1", "Name": self.name_text, "Email": self.email_text, "User_Id": User_Id, "Weight": self.weight_text, "Height": self.height_text, "Xp": 5, "Badges": ""}
                requests.patch("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/" + localId + ".json?auth=" + idToken,
                               data=json.dumps(the_data))

                App.get_running_app().on_start()
                App.get_running_app().change_screen("home_screen")

    #Authenticate users when they try to log onto the app
    def login(self, email, password):
        login_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key=" + self.api_key
        login_data = {"email": email, "password": password, "returnSecureToken": True}
        login_req = requests.post(login_url, data=login_data)
        login_dict = json.loads(login_req.content.decode())

        if login_req.ok == True:
            refresh_token = login_dict['refreshToken']
            localId = login_dict['localId']
            idToken = login_dict['idToken']
            with open("refresh_token.txt", "w") as f:
                f.write(refresh_token)

            #Save localId & idToken
            App.get_running_app().local_id = localId
            App.get_running_app().id_token = idToken

            App.get_running_app().on_start()
            App.get_running_app().change_screen("home_screen")

        elif login_req.ok == False:
            error_data = json.loads(login_req.content.decode())
            error_message = error_data["error"]['message']
            App.get_running_app().root.ids['login_screen'].ids['error_label'].text = error_message

    #Automatic sign in if refresh_token is present
    def exchange_refresh_token(self, refresh_token):
        refresh_url = "https://securetoken.googleapis.com/v1/token?key=" + self.api_key
        refresh_payload = '{"grant_type": "refresh_token", "refresh_token": "%s"}' % refresh_token
        refresh_req = requests.post(refresh_url, data=refresh_payload)
        id_token = refresh_req.json()['id_token']
        local_id = refresh_req.json()['user_id']
        return id_token, local_id

    def update_likes(self, friend_id, workout_key, likes, *args):
        app = App.get_running_app()
        patch_data = '{"Likes": %s}' % (likes)
        check_req = requests.get('https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/.json?orderBy="User_Id"&equalTo=' + friend_id)
        data = check_req.json()
        friend_local_id = list(data.keys())[0]

        self.update_likes_request = UrlRequest("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/%s/Workouts/%s.json?auth=" % (friend_local_id, workout_key) + app.id_token,
                                                 req_body=patch_data , ca_file=certifi.where(), method='PATCH',)
        close_button = MDFlatButton(text="CLOSE", on_release=self.close_dialog, text_color=self.theme_cls.primary_color)
        self.dialog = MDDialog(text="[font=Alphakind.ttf]You have liked this workout[/font]", size_hint=(0.7, 1), buttons=[close_button],)
        self.dialog.open()

    def close_dialog(self, obj):
        self.dialog.dismiss()
