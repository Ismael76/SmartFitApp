import requests
import json
from kivy.app import App

class Authentication():
    api_key = "AIzaSyAiE0NHSX-n8i-indM7bOwJVFO5LiKvAts"
    def register(self, email, password, name, weight, height):
        #Send registration details to DB
        #Firebase returns, localID(For users to identify them), authToken(Authorization token for users), refreshToken(Used to refresh authToken)
        #The below url is used to register new users to the DB
        register_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key=" + self.api_key
        register_data = {"email": email, "password": password, "name": name, "weight": weight, "height": height, "returnSecureToken": True}
        register_request = requests.post(register_url, data=register_data)
        print(register_request.ok)
        print(register_request.content.decode())
        register_dict = json.loads(register_request.content.decode())


        if register_request.ok == True:
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
            the_data = '{"Avatar": "002-man.png", "Friends": "", "Workouts": "", "Level": "1", "Name": "Ali", "User_Id": %s}' % User_Id
            requests.patch("https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/" + localId + ".json?auth=" + idToken,
                           data=the_data)

            App.get_running_app().change_screen("home_screen")

        #Firebase checks if email & password are correct
        if register_request.ok == False:
            error_data = json.loads(register_request.content.decode())
            error_message = error_data["error"]['message']
            App.get_running_app().root.ids['register_screen'].ids['error_label'].text = error_message

    def login(self, email, password):
        pass

    #Automatic sign in if refresh_token is present
    def exchange_refresh_token(self, refresh_token):
        refresh_url = "https://securetoken.googleapis.com/v1/token?key=" + self.api_key
        refresh_payload = '{"grant_type": "refresh_token", "refresh_token": "%s"}' % refresh_token
        refresh_req = requests.post(refresh_url, data=refresh_payload)
        id_token = refresh_req.json()['id_token']
        local_id = refresh_req.json()['user_id']
        return id_token, local_id