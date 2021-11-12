from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (
    ObjectProperty, StringProperty
)
from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')
Config.set('input', 'mouse', 'mouse,disable_multitouch')
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivymd.uix.picker import MDDatePicker
from kivymd.app import MDApp
from plyer import filechooser # Do this during packaging: https://github.com/kivy/plyer/issues/613
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock

from base import Hologram
from datetime import  datetime, timedelta
from requests.exceptions import RequestException
import requests
import threading
import functools
import os
import tempfile
import json
import sys

credentials_path = os.path.join(tempfile.gettempdir(), 'credentials.json')

f = open('timezones.json')
timezones = json.load(f)
tz_offset = {
    tz['text']: tz['offset']
    for tz in timezones
}

args = {n: arg for n, arg in enumerate(sys.argv)}

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
        self.text = list(tz_offset.keys())[0]
        self.values = list(tz_offset.keys())

class ShellCommand(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiline = True
        self.text = ''

about_us_text = '''
[b]Manuel A. Andrade[/b]*
Assistant Professor of Water and Irrigation Management
andradea@unr.edu

[b]Diego A. Quintero[/b]*
Graduate research assistant
dquintero@nevada.unr.edu

[b]Uriel Cholula[/b]*
Graduate research assistant
ucholula@nevada.unr.edu

*University of Nevada, Reno
Dept. of Agriculture, Veterinary and Rangeland Sciences
Water and Irrigation Management Lab

The development of this software is based upon work that is 
supported by the Nevada System of Higher Education (NSHE).
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
        self.title = 'PyHOLA_GUI  Version 0.1.2110'
        self.size = (450, 450)
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
    store = JsonStore(credentials_path)
    try:
        deviceid = store.get('credentials')['deviceid']
        orgid = store.get('credentials')['orgid']
        apikey = store.get('credentials')['apikey']
        timezone = store.get('parameters')['timezone']
    except KeyError:
        deviceid = ''
        orgid = ''
        apikey = ''
        timezone =list(tz_offset.keys())[0]
    download_progress = 0
    Hol = Hologram(
        deviceID=deviceid,
        apiKey=apikey,
        startTime=None,
        endTime=None,
        orgID=orgid,
    )
    date_from = None
    date_to = None
    
    def __init__(self, **kwargs):
        super(Root, self).__init__(orientation='vertical', *kwargs)
        Clock.schedule_interval(self.terminate_download, 0.5)
        '''
        This is ussed during testing to set parameters
        '''
        if args.get(1) == 'test':
            import os
            base_date = datetime(2021, 10, 31)
            self.date_range = [base_date - timedelta(days=x) for x in range(180)]
            self.date_range = self.date_range[::-1]
            self.path = ['C:\\Users\\dandres\\Desktop\\test.csv']
            self.ids.file_label.text = str(self.path[0])
            ddrange = f'Download from {self.date_range[0]} to {self.date_range[-1]}'
            self.ids.date_label.text = f'{ddrange}'
            try:
                os.remove(self.path[0])
            except FileNotFoundError:
                pass
        
    # Save date
    def on_save(self, instance, value, date_range):
        ddrange = f'Download from {date_range[0]} to {date_range[-1]}'
        self.ids.date_label.text = f'{ddrange}'
        self.date_range = date_range
    # Cancel_date
    def on_cancel(self, instance, value):
        self.ids.date_label.text = 'Select a date'

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

    
    def update_progress(self, dt):
        # stuff that must be done on the main thread
        self.ids.progressbar.value += 1
    

    def download_main_thread(self):
        donwload_thread = threading.Thread(target=self.download_trigger)
        donwload_thread.start()

    
    def download_trigger(self):
        if args.get(1) == 'test': 
            try:
                os.remove(self.path[0])
            except FileNotFoundError:
                pass
        if not hasattr(self, 'date_range'):
            self.open_warn('You must define a date range')
            return None 
        try: 
            self.path
        except AttributeError:
            self.open_warn('You must select a file to download the records')
            return None
        if os.path.exists(self.path[0]) and not self.ids.append.active:
            self.open_warn('File already exists, you must create a new one')
            return None
        if not os.path.exists(self.path[0]) and self.ids.append.active:
            self.open_warn('File does not exist, you must select a existing file to append records to')
            return None
        try:
            _ = requests.get('http://www.google.com', timeout=3)
        except (requests.ConnectionError, requests.Timeout):
            self.open_warn('No internet connection')
            return None

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
        self.download_init()
        self.date_from =  datetime.combine(self.date_range[0], datetime.min.time())
        self.date_from -= timedelta(days=1)
        self.date_to = datetime.combine(self.date_range[-1], datetime.min.time()) + timedelta(days=1)
        if self.date_to > datetime.now():
            self.date_to = datetime.now() + timedelta(days=1)

        self.ids.progressbar.max = (self.date_to - self.date_from).days 
        endDate = self.date_to
        self.date_to = self.date_from + timedelta(days=1)
        
        while self.date_from < endDate:
            self.Hol.startTime = self.date_from
            self.Hol.endTime = self.date_to
            self.download()
            self.date_from += timedelta(days=1)
            self.date_to += timedelta(days=1)
        print()
        
    def terminate_download(self, dt):
        if self.ids.progressbar.value == self.ids.progressbar.max:
            if len(self.Hol.records) < 1:
                self.open_warn('No records for the requested period')
                self.Hol = Hologram(
                    deviceID=self.deviceid,
                    apiKey=self.apikey,
                    startTime=None,
                    endTime=None,
                    orgID=self.orgid,
                )
                self.ids.progressbar.max = 1e10
                return
            save_thread = threading.Thread(target=self.save_records)
            save_thread.start()
            
            
            self.ids.progressbar.value = 0
            
            
            

    def download_init(self):
        self.Hol.apiKey = self.ids.APIKey.text.strip()
        self.Hol.orgID = self.ids.OrganizationID.text.strip()
        if self.ids.oneDevice.active:
            self.Hol.deviceID = self.ids.deviceID.text.strip()
        else:
            self.Hol.deviceID = None
        self.ids.download_button.disabled = True
        self.ids.download_button.text = '[b][color=303030]Downloading...[/b][/color]'
            


    def download(self):
        try: 
            self.Hol.startTime = self.date_from
            self.Hol.endTime = self.date_to
            try:
                self.Hol.retrieve()
                Clock.schedule_once(functools.partial(self.update_progress))
            except RequestException:
                self.ids.progressbar.max -= 1
                return None
        except RequestException:
            self.open_warn('Something went wrong with the request')
            self.ids.progressbar.max -= 1


    def save_records(self):
        self.ids.download_button.text = '[b][color=252525]Saving records...[/b][/color]'
        self.Hol.save_records(
            filepath=str(self.path[0]),
            sep='\t',
            append=self.ids.append.active,
            timeDelta=tz_offset[self.ids.timeDelta.text],
            absStartDate=self.date_range[0]
        )
        self.open_warn(f'{len(self.Hol.records)} records written to {self.path[0]}', 'Successful download')
        self.Hol = Hologram(
                deviceID=self.deviceid,
                apiKey=self.apikey,
                startTime=None,
                endTime=None,
                orgID=self.orgid,
            )
        self.ids.download_button.text = '[b]Download[/b]'
        self.ids.download_button.disabled = False
        
        


class PyHOLAApp(MDApp):
    path = ObjectProperty(None)
    out = StringProperty('')
    def build(self):
        
        return Root()
    
if __name__ == '__main__':
    PyHOLAApp().run()