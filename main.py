from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (
    ObjectProperty, StringProperty
)
from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivymd.uix.picker import MDDatePicker
from kivymd.app import MDApp
from plyer import filechooser

from HOLA.base import Hologram
from datetime import datetime
from requests.exceptions import RequestException

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

class ShellCommand(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiline = True
        self.text = ''
        
        
    

# Root widget
class Root(BoxLayout):
    
    def __init__(self, **kwargs):
        super(Root, self).__init__(orientation='vertical', *kwargs)
        # self.button = Button(size_hint=(.5, .5), pos_hint={'x_center': 0.5})
        
    # Save date
    def on_save(self, instance, value, date_range):
        ddrange = f'Download from {date_range[0]} to {date_range[-1]}'
        self.ids.date_label.text = f'{ddrange}'
        self.date_range = date_range
    # Cancel_date
    def on_cancel(self, instance, value):
        self.ids.date_label.text = '[color=000000]Select a date[/color]'

    def print_msg(self, msg='Downloading'):
        self.ids.console_prompt.text += str(msg)+'\n'

    def show_date_picker(self):
        date_dialog = MDDatePicker(mode='range')
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()

    def open_file(self):
        self.path = filechooser.open_file(
            title="Pick a CSV file..", 
                filters=[("Comma-separated Values", "*.csv")]
            )
        try:
            self.ids.file_label.text = str(self.path[0])
        except IndexError:
            pass
    

    def download(self):
        if hasattr(self, 'date_range'):
            self.print_msg('Downloading...')
            deviceID = self.ids.deviceID.text.strip()
            OrganizationID = self.ids.OrganizationID.text.strip()
            APIKey = self.ids.APIKey.text.strip()
            date_from =  datetime.combine(self.date_range[0], datetime.min.time())
            date_to = datetime.combine(self.date_range[-1], datetime.min.time())
            try: 
                Hol = Hologram(
                    deviceID=deviceID,
                    apiKey=APIKey,
                    startTime=date_from,
                    endTime=date_to,
                    orgID=OrganizationID,
                    isLive=self.ids.isLive.active
                )
                Hol.retrieve()
                Hol.save_records(
                    filepath=str(self.path[0]),
                    sep='\t',
                    append=self.ids.append.active,
                    timeDelta=int(self.ids.timeDelta.text)
                )
            except RequestException:
                self.print_msg('Something went wrong with the request')
            
            self.print_msg(f'{len(Hol.records)} records written to {self.path[0]}')
        else:
            self.print_msg('You must define a date range')

class PyHOLAApp(MDApp):
    path = ObjectProperty(None)
    out = StringProperty('')
    def build(self):
        
        return Root()
    
if __name__ == '__main__':
    PyHOLAApp().run()