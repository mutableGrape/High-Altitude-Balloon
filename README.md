# High-Altitude-Balloon

##### Writing your Own Code
See <a href="https://github.com/mutableGrape/High-Altitude-Balloon/blob/master/HelpWritingYourOwnCode.md#writing-a-python-script-for-the-balloon">HelpWritingYouOwnCode.md</a> on how to write your own code to interpret the messages. 

## DUSEDS_HAB01_Pi_Script.py
This file uses the Gmail API and __Iridium_Beacon_GMail_Downloader_RockBLOCK.py__ script written by Paul Clark (Github: <a href="https://github.com/PaulZC/Iridium_9603_Beacon/tree/master/Python">PaulZC</a>) to download Short Burst Data messages received via email. It then reads the attachment and copies the data to a dictionary (basically a list with placenames). This data is then used uploaded to a Google Spreadsheet and to create a Twitter post. 

### Keys
Two keys are required for this program to run: one for the Gmail/Sheets API and one for the Twitter API. The former should automatically be downloaded upon executing the program (you'll be directed to a page to sign into the relevant google account). For the Twitter key, store it in the same directory. 

### Getting the Program Running
The program was written in Python 2.7 (2.x is required for the *Basemap* package used for plotting the coordinates). It requires the packages *random*, *datetime* and *TwitterAPI*. The *random* and *datetime* librarys should be included in your Python installation. To install the TwitterAPI library, open a command prompt window (press Win Key + R and type cmd, then press enter). Then type `pip install TwitterAPI`. You can install most packages using this method, just replace "TwitterAPI" with whatever package you require.

This program also uses the *Basemap* packages, which is an extension of the *matplotlib* package. To get this package, you will need to install some form of [Conda](https://docs.conda.io/en/latest/) for installing and using the Basemap package. Once installed, open a command prompt window and type `conda install Basemap` to install the package. 

Once you have all the necessary packages installed, download the <a href="https://github.com/PaulZC/Iridium_9603_Beacon/tree/master/Python">__Iridium_Beacon_GMail_Downloader_RockBLOCK.py__</a> file meantioned earlier and place it in the same folder as the __DUSEDS_HAB01_Pi_Script.py__ file. You may also need to create a folder named "bin" in the same directory.

To run the program, open a command prompt window. Navigate to the directory of the python script. Then type `conda activate base` (you may need to ensure Conda is included in PATH). This creates a working envorniment in which the Basemap package will work (because it requires non-python code to run). Once you have done this, type `python DUSEDS_HAB01_Pi_Script.py` and the program should run. Use Ctrl+C to stop it and `conda deactivate` to end the environment. 
