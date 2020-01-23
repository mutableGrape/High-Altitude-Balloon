# High-Altitude-Balloon
Code for the High Altitude balloon

##### Writing your Own Code
See <a href="https://github.com/mutableGrape/High-Altitude-Balloon/blob/master/HelpWritingYourOwnCode.md#writing-a-python-script-for-the-balloon">HelpWritingYouOwnCode.md</a> on how to write your own code to interpret the messages. 

## DUSEDS_HAB01_Pi_Script.py
This file uses the Gmail API (__Iridium_Beacon_GMail_Downloader_RockBLOCK.py__ by <a href="https://github.com/PaulZC/Iridium_9603_Beacon/tree/master/Python">Paul Clark</a>) to download Short Burst Data messages received via email. It then reads the file and writes the data to a dictionary (basically a list with placenames). This data is then used to to create a Facebook post. 

### Keys
Two keys are required for this program to run: one for the Gmail API and one for the Facebook app. The former should automatically be downloaded upon executing the program (you'll be directed to a page to sign into the 'softSkies' google account). For the Facebook key, contact me directly. 

### Getting the Program Running
The program was written in Python 3.6 (3.x will be able to run it, probably 2.x too). It requires the packages *random*, *datetime* and *facebook*. The *random* and *datetime* librarys should be included in your Python installation. To install the facebook library, open a command prompt window (press Win Key + R and type cmd, then press enter). Then type `pip install facebook-sdk`. You can install most packages using this method, just replace "facebook-sdk" with whatever package you require. Once you have all the necessary packages installed, download the <a href="https://github.com/PaulZC/Iridium_9603_Beacon/tree/master/Python">__Iridium_Beacon_GMail_Downloader_RockBLOCK.py__</a> file meantioned earlier and place it in the same folder as the __DUSEDS_HAB01_Pi_Script.py__ file. You may also need to create a folder named bin in the same directory. Then just run the program and you should see it checking every 10s or so for new emails. 
