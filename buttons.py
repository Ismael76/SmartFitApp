from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.label import Label

class ImageButton(ButtonBehavior, Image): #Icons will act as 'buttons'
    pass

class LabelButton(ButtonBehavior, Label): #Icons will act as 'buttons'
    pass