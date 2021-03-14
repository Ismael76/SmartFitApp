from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from buttons import ImageButton
from buttons import LabelButton
from kivy.app import App
from functools import partial
from kivy.graphics import Color, Rectangle
import requests
import kivy.utils


class FriendList(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__()
        with self.canvas.before:
            Color(rgb=(kivy.utils.get_color_from_hex("#d5d5d5"))) #Change Background Colour Of Workout Banner
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect) #Anytime the size of the banner changes then it will call 'update_rect' to update the size and pos of

        check_request = requests.get('https://smartfit-ad8c3-default-rtdb.firebaseio.com/Users/.json?orderBy="User_Id"&equalTo=' + kwargs['friend_id'])

        data = check_request.json()
        unique_id =  list(data.keys())[0]

        friend_avatar = data[unique_id]['Avatar']

        friend_image = ImageButton(source="icons/avatars/" + friend_avatar, size_hint=(.3, .5), pos_hint={"top":.9, "right": 0.3}, on_release=partial(App.get_running_app().friends_screen, kwargs['friend_id']))

        friend_label = LabelButton(text="User ID: " + kwargs['friend_id'], size_hint=(1, .5), pos_hint={"top": .5, "right":.65}, font_name="Alphakind", color= (0,0,0,1), font_size='15dp', on_release=partial(App.get_running_app().friends_screen, kwargs['friend_id']))

        friend_name_label = LabelButton(text="Name: " + kwargs['name'], size_hint=(1, .8), pos_hint={"top": 1, "right":1}, font_name="Alphakind", color= (0,0,0,1), font_size='15dp', on_release=partial(App.get_running_app().friends_screen, kwargs['friend_id']))

        friend_level_label = LabelButton(text="Level: " + kwargs['level'], size_hint=(1, .8),
                                        pos_hint={"top": .7, "right": 1}, font_name="Alphakind", color=(0, 0, 0, 1),
                                        font_size='15dp', on_release=partial(App.get_running_app().friends_screen, kwargs['friend_id']))

        self.add_widget(friend_image)
        self.add_widget(friend_label)
        self.add_widget(friend_name_label)
        self.add_widget(friend_level_label)



    #Updates size of banner when the size changes
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size