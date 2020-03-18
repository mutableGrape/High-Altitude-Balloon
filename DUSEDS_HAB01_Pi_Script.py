import Iridium_Beacon_GMail_Downloader_RockBLOCK as gmail_downloader
import Iridium_Beacon_Sheets_Uploader as sheets_uploader
import random, sys, time, os
from datetime import datetime
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from TwitterAPI import TwitterAPI, TwitterError


TWITTER_KZ = ""                     # Directory to Twitter Key File
CHECK_FREQ = 15                     # How often it checks for new messages in seconds
SBD_DIR = "SBD"                     # Folder name for SBD files
LAST_TWEET_DATE = ""                # "YYYY-MM-DD"
MAP_IMAGE_FILENAME = "MAP_IMAGE.png"# Image file to save map rendering to
TWITTER_ATTEMPTS = 2                # Number of attempts for interacting with twitter API before giving up
TWITTER_WAIT = 15*60                # Time to wait in seconds between attempts
SHEETS_ATTEMPTS = 4                 # Number of attempts for interacting with Google Spreadsheets
LAT_SPACING = 3                     # Parameter for map image
NO_MSGS_MSG = False                 # Determines whether a post will be made if no messages were received before GIVE_UP_TIME
GIVE_UP_TIME = 22                   # Time at which it reports no new messages [hour]
RETRY_LIST = []                     # List for messages which failed to upload to either sheets or twitter (or both)


def ValidCoords(data_entry):
    return data_entry['GPS Long'] != 0 and data_entry['GPS Lat'] != 0


def ValidReadings(data_entry):
    return data_entry['Pressure'] != -1


def GetMOMSN(filename):
    return filename[16:-4]


def ValidSBDFile(filename):
    return filename[-4:] == ".bin" and filename[15:16] == "-"


def GetNewMessages():
    filenames = []
    credentials = gmail_downloader.get_credentials()
    http = credentials.authorize(gmail_downloader.httplib2.Http())
    service = gmail_downloader.discovery.build('gmail', 'v1', http=http, cache_discovery=False)

    messages = gmail_downloader.ListMessagesMatchingQuery(service, 'me', 'is:unread has:attachment')
    if messages:
        for message in messages:
            if gmail_downloader.GetSubject(service, 'me', message["id"]).count("from RockBLOCK") > 0:
                print('Processing: '+gmail_downloader.GetSubject(service, 'me', message["id"]))
                gmail_downloader.SaveAttachments(service, SBD_DIR, 'me', message["id"])
                filenames.append(gmail_downloader.GetAttachmentFilenames(service, 'me', message['id'])[0])
                gmail_downloader.MarkAsRead(service, 'me', message["id"])
                gmail_downloader.MoveToLabel(service, 'me', message["id"], 'SBD')
    return filenames


def LoadData(new_files):        # Takes in a list of filenames and returns a list of dictionaries with each file's data formatted
    data_dict = []
    for filename in new_files:
        entry = []
        with open(SBD_DIR + "/" + filename, 'r') as f:
            entry = f.read().split(",")
            f.close()
        
        new_dict = dict()
        if len(entry[0]) > 13:      
            new_dict["RockBLOCK base Serial"] = None       # Skip Base Serial if not present
            entry = [None] + entry
        else:               
            new_dict["RockBLOCK Base Serial"] = entry[0]    # Base RockBLOCK serial number
               
        new_dict["GPS TX Time"] = [entry[1][:4]] + [entry[1][i:i+2] for i in range(4,14,2)]  # GPS Tx Time (YYYYMMDDHHMMSS)               
        new_dict["GPS Lat"] = float(entry[2])           # GPS Lat             
        new_dict["GPS Long"] = float(entry[3])          # GPS Long         
        new_dict["GPS Alt"] = int(entry[4])             # GPS Alt           
        new_dict["GPS Speed"] = float(entry[5])         # GPS Speed             
        new_dict["GPS Heading"] = int(entry[6])         # GPS Heading             
        new_dict["GPS HDOP"] = float(entry[7])          # GPS HDOP            
        new_dict["GPS Sat"] = int(entry[8])             # GPS Satellites            
        new_dict["Pressure"] = float(entry[9])          # Pressure               
        new_dict["Humidity"] = float(entry[10])         # Humidity               
        new_dict["Temperature"] = float(entry[11])      # Temperature               
        new_dict["Battery"] = float(entry[12])          # Battery           
        new_dict["Iteration"] = int(entry[13])          # Iteration Count   

        if len(entry) > 14:                    
            new_dict["Serial Number"] = entry[14]           # RockBlock Serial No.
        else:
            new_dict["Serial Number"] = None

        new_dict["MOMSN"] = int(GetMOMSN(filename))     # Add the MOMSN number for later checks

        data_dict.append(new_dict)
    return data_dict


def LoadDataPointsFromSaved(filenames, data_keys):     # SBD files to load from, data wanted as list of key names in order desired
    data = LoadData(filenames)
    specific_data = []
    for entry in data:
        tmp = []
        for key in data_keys:
            tmp.append(entry[key])
        specific_data.append(tuple(tmp))
    return specific_data


def PlotCoordinates(coords):   # coords = [(lat, lon, alt) for i in positions], ordered old to new
    lat, lon, a = coords[-1]
    m = Basemap(width=3600000, height=2700000, projection='lcc', resolution='l', lat_1=lat-LAT_SPACING, lat_2=lat+LAT_SPACING, lat_0=lat, lon_0=lon)
    m.drawcountries(linewidth=1)
    m.drawstates(color='b')
    #m.drawcounties(color='b')      # Throws an error for some reason - beleive it's an error in the shape file
    m.bluemarble()

    coords_filtered = [(lat, lon, alt) for lat, lon, alt in coords if lat != 0.0 and lon != 0.0 and alt != 0.0]

    xys = [m(lon,lat) for lat, lon, alt in coords_filtered]
    xs, ys  = [i[0] for i in xys], [i[1] for i in xys]
    alts = [i[2] for i in coords_filtered]

    m.plot(xs, ys, '.-r', c="r")#alts)
    plt.savefig(MAP_IMAGE_FILENAME, bbox_inches='tight', pad_inches=0)

def GenerateGreeting():     # Randomly chooses a greeting
    morning_greetings = ["Good morning!", "Morning all,", "Good morning everyone,", "Morning everyone,"]
    afternoon_greetings = ["Good Afternoon,", "Afternoon all,", "Good afternoon everyone,", "Afternoon everyone,", "Afternoon all :),"]
    general_greetings = ["Hello!", "Hello,", "Hi everyone,", "Hi everyone!", "Hey peeps,", "Helloooo,"]
    a = random.randint(0,5)
    cur_hour = datetime.now().hour
    if (5 <= cur_hour < 12 or 12 <= cur_hour <= 17) and a < 3: 
        if 5 <= cur_hour < 12:
            return random.choice(morning_greetings)
        else:
            return random.choice(afternoon_greetings)
    else:
        return random.choice(general_greetings)


def GeneratePost(data_entry, known_SBDs):
    output_string = GenerateGreeting() + "\n\n"
    GPS_fix_found = False
    is_image = False
    post = dict()
    if len(data_entry) == 0:
        sentence = random.choice(["Unfortunately we haven't received any data from the balloon today so check back tomorrow for more updates", "No data was received today so there's nothing to report :(", "No data today so check back tomorrow :)", "We haven't heard anything from the balloon today so be sure to check back again tomorrow"])
        suffix = "In the meantime though, be sure to check out the Durham SEDS page for updates on upcoming projects and space news: https://www.facebook.com/groups/DurhamSEDS/"
        output_string = sentence + "\n\n" + suffix
    else:
        GPS_fix_found = data_entry['GPS TX Time'][0] != "1970"
        if GPS_fix_found:
            hours, minutes = data_entry['GPS TX Time'][3:5]
            hours = int(hours)
            ampm = "am"*bool(hours<12) + "pm"*bool(hours>=12)
            if hours > 12: 
                hours %= 12
            ping_msg = random.choice(["At {}:{}{} we received a message from the balloon", 
                                        "We received a message at {}:{}{} from the balloon",
                                        "So we received message at {}:{}{}"]).format(hours, minutes,ampm)
        else:
            ping_msg = random.choice(["We've received a message from the balloon", 
                                        "We've just received a message from the balloon", 
                                        "A message has just been received from the balloon"])
        output_string += ping_msg
        # Positions
        if GPS_fix_found:
            lat, lon, speed, heading =  data_entry['GPS Lat'], data_entry['GPS Long'], data_entry['GPS Speed'], data_entry['GPS Heading']
            alt_sentence = random.choice(["which transmitted from {}m up.", 
                                                "from an alitiude of {}m."]).format(data_entry['GPS Alt']) # Shock emoji here would be cool            
            location_sentence = random.choice(["It's current coordinates are: ({}, {}). It reported a speed of {} m/s and heading of {} degrees".format(lat, lon, speed, heading),
                                                "The GPS recorded the ballons coordinates as ({}, {}), its speed as {} m/s and its heading as {} degrees.".format(lat, lon, speed, heading)])
        
            if ValidReadings(data_entry):
                pressure, humidity, temperature = data_entry['Pressure'], data_entry['Humidity'], data_entry['Temperature']
                readings_sentence = random.choice(["It reported a temperature of {} C, {} mbar of pressure and a humidity of {}%.".format(temperature, pressure, humidity),
                                        "The onboard sensors read a temerature of {} C, a pressure of {} mbar, and a humidity of {}%".format(temperature, pressure, humidity),
                                        "The environment sensors read:\n\n Temerature: {} C \n Pressure: {} mbar \n Humidity: {}% \n\n".format(temperature, pressure, humidity)])
            else:
                readings_sentence = random.choice(["The sensor readings (temperature, pressure, humidity) were faulty.", "No envorimental data was transmitted (temperature, pressure, humidity). This could be due to an error starting up the sensors."])
            output_string += " " + " ".join([alt_sentence, location_sentence, readings_sentence])
        else:
            if ValidReadings(data_entry):
                pressure, humidity, temperature = data_entry['Pressure'], data_entry['Humidity'], data_entry['Temperature']
                readings_sentence = "which reported a temperature of {} C, {} mbar of pressure and a humidity of {}%.".format(temperature, pressure, humidity)
                GPS_sentence = random.choice(["Unfortunately, the balloon was unable to acquire a GPS fix so we don't know where exactly it is :/ .", 
                                                "The balloon was unable to get a GPS fix. This can happen if it can't see enough satellites above it to gauge it's position from."])
                output_string += " " + readings_sentence + " " + GPS_sentence
            else:
                no_data = random.choice([". Unfortunately, neither the GPS nor the envirnomental sensors were able to take any measurements so there is nothing to report :(", "No data was recorded so there isn't anything to report - at least we know it's still transmitting though."])
                output_string += no_data
    post = output_string

    
    if GPS_fix_found:   # Produce image, if GPS fix was found
        lat_long_alt = LoadDataPointsFromSaved(known_SBDs, ["GPS Lat", "GPS Long", "GPS Alt"])
        PlotCoordinates(lat_long_alt)
        is_image = True

    return post, is_image


def InstantiateLog():
    filename = str(datetime.now()).replace(" ", "-").replace(":", "")[:15] + ".log"
    with open(filename, 'w+') as f:
        message = "[" +  str(datetime.now()) + "] Log file created.\n"
        f.write(message)
        f.close()
    return filename


def WriteToLog(filename, text):
    with open(filename, "a+") as f:
        message = "[" +  str(datetime.now()) + "] " + text
        print(message)
        f.write(message + "\n")
        f.close()


def LookForKnownSBDs():     # Searches SDB_DIR for SBD files
    known_files = []
    for root, dir, files in os.walk(".\\" + SBD_DIR):
        if root == ".\\" + SBD_DIR:
            for filename in files:
                if ValidSBDFile(filename):
                    known_files.append(filename)
    known_files = sorted(known_files, key=lambda x: int(x[16:-4]))
    return known_files



##### Functions for Google Sheets ##### 

def AppendToSpreadsheet(data):
    attempts = 0
    while attempts < SHEETS_ATTEMPTS:
        try:
            credentials = shts.get_credentials()
            http = credentials.authorize(httplib2.Http())
            service = discovery.build('sheets', 'v4', http=http)

            data[1] = "/".join([str(i) for i in data[1][:3]]) + " " + ":".join([str(i) for i in data[1][3:]])
            shts.AppendRow(service, data)
            return 1
        except:
            e = sys.exc_info()[0]
            print(str(e))
            attempts += 1
    return 0



##### Twitter Functions #####


def LoadTwitterKey(filename):
    a = []
    with open(filename, 'r') as f:
        a = f.read().strip().split("\n")
        f.close()
    return a


def PostToTwitter(api, text, is_image):
    if is_image:
        data = ""
        with open(MAP_IMAGE_FILENAME, 'rb') as f:
            data = f.read()
            f.close()
        
        attempts = 0
        while attempts < TWITTER_ATTEMPTS:
            try:
                r = api.request('statuses/update_with_media',{'status':text}, {'media[]':data})
                if r.status_code == 200: 
                    return 1
                elif r.status_code == 403:
                    print("Too many requests, waiting 10 minutes")
                    time.sleep(10*60)
                    pass
                else:
                    print(r.status_code)
            except TwitterError.TwitterConnectionError as e:
                print(e)
                pass
            attempts += 1 
            time.sleep(3)
    else:
        attempts = 0
        while attempts < TWITTER_ATTEMPTS:
            try:
                r = api.request('statuses/update', {'status':text})
                if r.status_code == 200: 
                    return 1
                elif r.status_code == 403:
                    print("Too many requests, waiting 10 minutes")
                    time.sleep(10*60)
                else:
                    print(r.status_code)
            except TwitterError.TwitterConnectionError as e:
                print(e)
            attempts += 1
            time.sleep(3)
    return 0


def TwitterTimeToDate(text):    # Formats twitter time into date string required for LAST_TWEET_DATE
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    year = text[-4:]
    month = months.index(text[4:7]) + 1
    date = text[8:10]
    return year + "-" + "0"*bool(month < 10) + str(month) + "-" + date


def LastTweetDate(api):     # Fetches the date of the last tweet 
    attempts = 0
    while attempts < TWITTER_ATTEMPTS:
        try:
            r = api.request('statuses/user_timeline', {'count': 1})
            if r.status_code == 200:
                tweet = r.json()
                date_string = tweet[0]['created_at']
                return TwitterTimeToDate(date_string)
        except TwitterError.TwitterConnectionError:
            pass
        attempts += 1
    return None 



if __name__ == "__main__":

    print("HAB01 Script running...\n")
    print("Will check for new messages every {}s".format(CHECK_FREQ))

    print("\nInstantiating log file")
    log_file = InstantiateLog()

    WriteToLog(log_file, "Looking for known SBDs...")
    known_SBDs = LookForKnownSBDs()
    WriteToLog(log_file, "Found: " + ",".join(known_SBDs))

    #try:

    WriteToLog(log_file, "Loading Twitter API Key from " + TWITTER_KZ)

    TAPI_KEY = LoadTwitterKey(TWITTER_KZ)
    TWTR_API = TwitterAPI(TAPI_KEY[0], TAPI_KEY[1], TAPI_KEY[2], TAPI_KEY[3])
    LAST_TWEET_DATE = LastTweetDate(TWTR_API)
    
    if LAST_TWEET_DATE == None:
        WriteToLog(log_file, "Failed to retrieve time of last Twitter post.")
        LAST_TWEET_DATE = str(datetime.now().date())            # If last tweet time not known, will asssume there was one today
    
    WriteToLog(log_file, "Updated LAST_TWEET_DATE to: " + LAST_TWEET_DATE)
    WriteToLog(log_file, "Beginning main loop")

    while(1):

        RETRY_LIST_ = []
        
        if RETRY_LIST:      # If there exists messages that failed to upload last time, try and upload them again
            WriteToLog(log_file, "Found items to retry uploading")

            for data, sheets_upload_success, twitter_upload_success in RETRY_LIST:
                WriteToLog(log_file, "Re-Processing MOMSN: " + str(data["MOMSN"]))
                
                if not sheets_upload_success:
                    sheets_entry = [data["MOMSN"], data["GPS TX Time"],data["GPS Lat"],data["GPS Long"],data["GPS Alt"],data["GPS Speed"],       
                        data["GPS Heading"],data["GPS HDOP"],data["GPS Sat"],data["Pressure"],data["Humidity"],data["Temperature"],          
                        data["Battery"],data["Iteration"]]
                
                    WriteToLog(log_file, "Uploading Data: " + ",".join([str(i) for i in sheets_entry]) + " to google sheets.")
                        
                    sheets_upload_success = AppendToSpreadsheet(sheets_entry)
                
                if not twitter_upload_success:
                    post, load_img = GeneratePost(data, [sbd for sbd in known_SBDs if int(sbd[16:-4]) <= data["MOMSN"]])   # Generate post from data
                    WriteToLog(log_file, "Made post: " + post)

                    if load_img: WriteToLog(log_file, "Will also load image.")

                    twitter_upload_success = PostToTwitter(TWTR_API, post, load_img)
                
                if not twitter_upload_success or not sheets_upload_success:
                    RETRY_LIST_.append([data, sheets_upload_success, twitter_upload_success])
                    WriteToLog(log_file, "One of the uploads failed (" + "twitter"*bool(twitter_upload_success) + ","*bool(twitter_upload_success and sheets_upload_success) + "sheets"*bool(sheets_upload_success) + ". Adding it to RETRY_LIST, MOMSN: " + str(data["MOMSN"]))

        RETRY_LIST = RETRY_LIST_[:]

        WriteToLog(log_file, "Looking for new messages on GMAIL")
        new_message_filenames = GetNewMessages()



        if new_message_filenames:       # If new messages found, format and upload them

            WriteToLog(log_file, "Messages Found!")

            for message_filename in new_message_filenames:

                sheets_upload_success = False
                twitter_upload_success = False

                known_SBDs.append(message_filename)     # Add SDB file to list of known SBDs
                known_SBDs = sorted(known_SBDs, key=lambda x: int(x[16:-4]))

                data = LoadData([message_filename])[0]     # Load data into dictionaries

                sheets_entry = [data["MOMSN"], data["GPS TX Time"],data["GPS Lat"],data["GPS Long"],data["GPS Alt"],data["GPS Speed"],       
                        data["GPS Heading"],data["GPS HDOP"],data["GPS Sat"],data["Pressure"],data["Humidity"],data["Temperature"],          
                        data["Battery"],data["Iteration"]]          # Select data for spreadsheet
                
                WriteToLog(log_file, "Read Data: " + ",".join([str(i) for i in sheets_entry]))
                
                sheets_upload_success = AppendToSpreadsheet(sheets_entry)       # Append to spreadsheet

                if sheets_upload_success:
                    WriteToLog(log_file, "Appended data to Google Spreadsheet")
                else:
                    WriteToLog(log_file, "Failed to append data to Spreadsheet")

                post, load_img = GeneratePost(data, known_SBDs)          # Generate a twitter post from the data
                WriteToLog(log_file, "Made post: " + post)

                if load_img: WriteToLog(log_file, "Will also load image.")

                twitter_upload_success = PostToTwitter(TWTR_API, post, load_img)             # Post it to twitter

                if not twitter_upload_success:
                    WriteToLog(log_file, "Failed to post to twitter. Appended filename to FAILED_FILES")
                else:
                    WriteToLog(log_file, "Posted to twitter")
                    LAST_TWEET_DATE = str(datetime.now().date())
                    WriteToLog(log_file, "Updated LAST_POST_DATE: " + str(LAST_TWEET_DATE))

                if not twitter_upload_success or not sheets_upload_success:     # If either upload failed, append to a retry list
                    RETRY_LIST.append((data, sheets_upload_success, twitter_upload_success))
                    WriteToLog(log_file, "One of the uploads failed (" + "twitter"*bool(twitter_upload_success) + ","*bool(twitter_upload_success and sheets_upload_success) + "sheets"*bool(sheets_upload_success) + ". Adding it to RETRY_LIST, MOMSN: " + str(data["MOMSN"]))

        else:
            WriteToLog(log_file, "No new messages")

        if NO_MSGS_MSG and GIVE_UP_TIME == datetime.now().hour and LAST_TWEET_DATE != str(datetime.now().date()):

            WriteToLog(log_file, "No data received today - making sad post")
            post, load_image = GeneratePost([],[])
            WriteToLog(log_file, "Generated post: " + post['body'])

            PostToTwitter(TWTR_API, post, load_img)
            WriteToLog(log_file, "Posted to twitter")

        WriteToLog(log_file, "Going back to sleep...")
        time.sleep(CHECK_FREQ)

    # except:
    #     e = sys.exc_info()[0]
    #     print(str(e))
    #     WriteToLog(log_file, str(e))
    #     raise e

