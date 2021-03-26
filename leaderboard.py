from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from buttons import ImageButton
from buttons import LabelButton
from kivy.app import App
from functools import partial
from kivy.graphics import Color, Rectangle
import requests
import kivy.utils


class Leaderboard(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__()
        with self.canvas.before:
            Color(rgb=(kivy.utils.get_color_from_hex("#d5d5d5"))) #Change Background Colour Of Leaderboard
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect) #Anytime the size of the banner changes then it will call 'update_rect' to update the size and pos of

        check_request = requests.get('https://smartfit-ad8c3-default-rtdb.firebaseio.com/Leaderboard/.json')

        data = check_request.json()
        unique_id =  list(data.keys())[0]
        avatar = data[unique_id]['Avatar']


        pos_image = ImageButton(source="" + kwargs['image_pos'], size_hint=(.3, .5), pos_hint={"top":.8, "right": 0.2})

        pos_label = Label(text=""  + kwargs['pos'], size_hint=(.3, .8), pos_hint={"top": .9, "right":.2}, font_name="Alphakind", color= (0,0,0,1), font_size='15dp')

        avatar_image = ImageButton(source="icons/avatars/" + kwargs['avatar'], size_hint=(.3, .8), pos_hint={"top":.9, "right": 0.35})

        name_label = LabelButton(text="Name: " + kwargs['name'], size_hint=(1, .8), pos_hint={"top": 1, "right":1}, font_name="Alphakind", color= (0,0,0,1), font_size='15dp')

        points_label = LabelButton(text="Points: " + kwargs['points'], size_hint=(1, .8),
                                  pos_hint={"top": .65, "right": 1}, font_name="Alphakind", color=(0, 0, 0, 1),
                                  font_size='15dp')

        self.add_widget((pos_image))
        self.add_widget(pos_label)
        self.add_widget(avatar_image)
        self.add_widget(name_label)
        self.add_widget(points_label)


    #Updates size of banner when the size changes
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size