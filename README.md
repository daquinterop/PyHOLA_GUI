# PyHOLA_GUI
A GUI for PyHOLA

PyHOLA is a Python package for sensoring system data downloading. It uses the HOLOGRAM API (https://www.hologram.io/references/http#/introduction/authentication) to retrieve the data. 

PyHOLA GUI is a Graphic User Interface to [PyHOLA](https://pypi.org/project/PyHOLA/). It allows the user to download their sensor data by entering some requests parameters. The downloaded data is saved in a csv file with tabulation separator. PyHOLA also allows the user to append new data to an existing file.

## Install PyHOLA
Last PyHOLA installer is available at the project's Sourceforge. To install PyHOLA you just have to specify the installation path in case you don't want to install it on the default location. Before installing a new PyHOLA version on your computer you must remove the previous PyHOLA installation. You can do that by removing the PyHOLA installation folder.

## Download Data using PyHOLA.
### Insert device and organization info.
To download the data, you need your `Organization ID` and `API Key`. You can find both of those on the Hologram Dashboard under your [Account Settings](https://dashboard.hologram.io/account/api). You must check the `Only download from one device` if you want to download data from only one device, in that case you must provide the `Device ID`. If you want to download data from all devices associated to your `Organization ID` you have to uncheck the `Only download from one device` checkbox. In that case the `Device ID` textbox will be disabled.

### Set download parameters.
Using the `Select date range to download` button you can select the time range to download. You must pick on the first date before picking the last date of the time range. PyHOLA saves the records using a timezone defined by the user. As the device writes the records using the Universal Time Coordinated (UTC), it is necessary to convert the times to the actual time at the device location. You can use the `Select the timezone` dropdown to select the timezone at your device location. That way, if you select ***UTC -5*** as your timezone, then the record with time 18:00 at your device will be saved as the record for 13:00.

You can save your data to a new file by unchecking `Append to existing file` checkbox. If you check the `Append to existing file` checkbox the downloaded records will be appended to an existing file i.e. it will update the existing file with the new records. This is useful since it allows you to have a single file for all your records. You can uncheck the `Only download for live devices` to make your download to include all the devices even if they are not currently available. 

### Select file to save downloaded records
The `Open file` button will open the windows file selector. If `Append to existing file` checkbox is unchecked then you should write the name of the new file with the ***.csv*** extension and click on Open. If `Append to existing file` checkbox is checked then you must select an existing file.

### Download 
You click the `Download` button to start the download. If everything is ok the download will start. If something is wrong a window will popup with a warning message, usually that message will tell you what's wrong. The download progress will be reflected on the progressbar. A popup window will let you know when your download is completed and your records have been saved to the defined file.

## Output file
The output file is a text file with columns separated by tabulations. The file header contains all the columns numerated from 0 to the number of fields on your data. Additionally, the last three columns contain the *record id*, *device name* and *device ID*. The header can be modified manually. Then you can replace the numbers at the header and everything will be ok if the file preserves its structure (columns separated by tabulations). You can use the file with the modified header to keep appending new records.

