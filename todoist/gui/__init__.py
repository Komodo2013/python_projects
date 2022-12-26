import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout

kivy.require("2.1.0")


class MainWidget(GridLayout):
    pass


class GUIApp(App):
    def build(self):
        return MainWidget()

