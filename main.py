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
from plyer import filechooser # Do this during packaging: https://github.com/kivy/plyer/issues/613
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.storage.jsonstore import JsonStore

from base import Hologram
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

about_us_text = '''
[i]PyHOLA_GUI 21.9[/i]

[b][color=ffffff]Water and irrigation management lab[/b][/color]
University of Nevada, Reno

Department of Agriculture, Veterinary & Rangeland Science
Knudset Resource Center. 920 Valley Road. Reno, NV. Lab 117
Alejandro Andrade-Rodriguez, Ph.D.
andradea@unr.edu

For support: dquintero@nevada.unr.edu
'''
class AboutUSLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text=about_us_text
        self.size_hint=(1, 0.80)
        self.markup=True
        self.halign='left'

class WarningLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint=(1, 0.75)
        self.markup=True
        self.halign='left'

class WarningPopup(Popup):
    def __init__(self, popup_text, title='Warning', **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.size = (400, 170)
        self.size_hint = (None, None)
        self.content = BoxLayout(orientation = 'vertical')
        warn_text = WarningLabel()
        warn_text.text = popup_text
        self.content.add_widget(warn_text)
        self.content.add_widget(
            Button(
                text='Close', 
                on_release=self.dismiss,
                size_hint=(0.5, 0.25),
                pos_hint={'center_x': 0.5},
                padding_y=50
            )
        )


class AboutUS(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = 'About us'
        self.size = (400, 400)
        self.size_hint = (None, None)
        self.content = BoxLayout(orientation = 'vertical')
        self.content.add_widget(
            AboutUSLabel()
        )
        self.content.add_widget(BlankSpace(size_hint=(1, 0.05)))
        self.content.add_widget(
            Button(
                text='Close', 
                on_release=self.dismiss,
                size_hint=(0.5, 0.10),
                pos_hint={'center_x': 0.5},
                padding_y=50
            )
        )
        self.content.add_widget(BlankSpace(size_hint=(1, 0.05)))
        
        
    

# Root widget
class Root(BoxLayout):
    # Retrieve credentials
    store = JsonStore('credentials.json')
    try:
        deviceid = store.get('credentials')['deviceid']
        orgid = store.get('credentials')['orgid']
        apikey = store.get('credentials')['apikey']
        timezone = store.get('parameters')['timezone']
    except KeyError:
        deviceid = ''
        orgid = ''
        apikey = ''
        timezone = '-7'
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
        self.ids.date_label.text = 'Select a date[/color]'

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

    def open_aboutus(self):
        popup = AboutUS()
        popup.open()
    
    def open_warn(self, message, title='Warning'):
        popup = WarningPopup(message, title)
        popup.open()

    def download(self):
        self.store.put(
            'credentials', 
            deviceid=self.ids.deviceID.text,
            orgid=self.ids.OrganizationID.text,
            apikey=self.ids.APIKey.text
        )
        self.store.put(
            'parameters', 
            timezone=self.ids.timeDelta.text
        )
        if hasattr(self, 'date_range'):
            # self.print_msg('Downloading...')
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
                try:
                    Hol.retrieve()
                except IndexError:
                    self.open_warn('No records for the requested period')
                    return None
                Hol.save_records(
                    filepath=str(self.path[0]),
                    sep='\t',
                    append=self.ids.append.active,
                    timeDelta=int(self.ids.timeDelta.text)
                )
                self.open_warn(f'{len(Hol.records)} records written to {self.path[0]}', 'Successful download')
            except RequestException:
                self.open_warn('Something went wrong with the request')
            
           
        else:
            self.open_warn('You must define a date range')

class PyHOLAApp(MDApp):
    path = ObjectProperty(None)
    out = StringProperty('')
    def build(self):
        
        return Root()
    
if __name__ == '__main__':
    PyHOLAApp().run()