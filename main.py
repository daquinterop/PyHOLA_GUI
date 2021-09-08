from typing import Text
from kivy.app import App 
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
)
from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivymd.uix.picker import MDDatePicker
from kivymd.app import MDApp
from plyer import filechooser


# Holds the label of every section
class SectionLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# Holds as blank empty space
class BlankSpace(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 0.01)

# Date picker
class PickHour(Spinner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = '0'
        self.values = (str(i) for i in range(-24, 24))


class Root(BoxLayout):
    def __init__(self, **kwargs):
        super(Root, self).__init__(orientation='vertical', *kwargs)
        # self.button = Button(size_hint=(.5, .5), pos_hint={'x_center': 0.5})


class PyHOLAApp(MDApp):
    def build(self):
        return Root()
    # Save date
    def on_save(self, instance, value, date_range):
        ddrange = f'Download from {date_range[0]} to {date_range[-1]}'
        self.root.ids.date_label.text = f'[color=000000]{ddrange}[/color]'
    # Cancel_date
    def on_cancel(self, instance, value):
        self.root.ids.date_label.text = '[color=000000]Select a date[/color]'
    def show_date_picker(self):
        date_dialog = MDDatePicker(mode='range')
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()

    def open_file(self):
        path = filechooser.open_file(
            title="Pick a CSV file..", 
                filters=[("Comma-separated Values", "*.csv")]
            )
        print(path)

if __name__ == '__main__':
    PyHOLAApp().run()