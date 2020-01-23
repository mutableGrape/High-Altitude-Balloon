from Iridium_Beacon_GMail_Downloader_RockBLOCK import *
import random
from datetime import datetime
import facebook

CHECK_FREQ = 15   #15*60      # How often it checks for new messages in seconds

ROCKET_EMOJI = 🚀
BALLOON_EMOJI = 🎈 


def get_new_messages():
    print("Looking for new messages...")
    filenames = []
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    messages = ListMessagesMatchingQuery(service, 'me', 'is:unread')#'subject:(Message \"from RockBLOCK\") is:unread has:attachment')
    if messages:
        print("Messages found!")
        for message in messages:
            print('Processing: '+GetSubject(service, 'me', message["id"]))
            #SaveMessageBody(service, 'me', message["id"])
            SaveAttachments(service, 'me', message["id"])
            filenames.append(GetAttachmentFilenames(service, 'me', message['id'])[0])
            MarkAsRead(service, 'me', message["id"])
            MoveToLabel(service, 'me', message["id"], 'SBD')
    print("Filenames: ", filenames)
    return filenames


def load_data(new_files):
    print("Formatting data...")
    data = []
    for filename in new_files:
        with open(bin_dir + "/" + filename, 'r') as f:
            data.append(f.read().split(","))
            f.close()

    data_dict = []
    for entry in data:
        new_dict = dict()
        for index, data_point in enumerate(entry):
            if len(entry[0]) > 13:      # Skip Base Serial if not present
                index += 1
                new_dict["RockBLOCK base Serial"] = "NAN"
            if index == 0:               # Base RockBLOCK serial number
                new_dict["RockBLOCK Base Serial"] = data_point
            elif index == 1:               # GPS Tx Time (YYYYMMDDHHMMSS)
                new_dict["GPS TX Time"] = [data_point[:4]] + [data_point[i:i+2] for i in range(4,14,2)]
            elif index == 2:                 # GPS Lat
                new_dict["GPS Lat"] = float(data_point)
            elif index == 3:                 # GPS Long
                new_dict["GPS Long"] = float(data_point)
            elif index == 4:                 # GPS Alt
                new_dict["GPS Alt"] = int(data_point)
            elif index == 5:                 # GPS Speed
                new_dict["GPS Speed"] = float(data_point)
            elif index == 6:                 # GPS Heading
                new_dict["GPS Heading"] = int(data_point)
            elif index == 7:                 # GPS HDOP
                new_dict["GPS HDOP"] = float(data_point)
            elif index == 8:                 # GPS Satellites
                new_dict["GPS Sat"] = int(data_point)
            elif index == 9:                 # Pressure
                new_dict["Pressure"] = int(data_point)
            elif index == 10:                # Humidity
                new_dict["Humidity"] = float(data_point)
            elif index == 11:                # Temperature
                new_dict["Temperature"] = float(data_point)
            elif index == 12:                # Battery
                new_dict["Battery"] = float(data_point)
            elif index == 13:                # Iteration Count
                new_dict["Iteration"] = int(data_point)
            else:                           # RockBlock Serial No.
                new_dict["Serial Number"] = data_point
        data_dict.append(new_dict)
    print("All Formatted!\n")
    return data_dict


def generate_greeting():
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
    

def valid_coords(data_entry):
    return data_entry['GPS Long'] != 0 and data_entry['GPS Lat'] != 0

def valid_readings(data_entry):
    return data_entry['Pressure'] != -1

def generate_post(data_entry):
    output_string = generate_greeting() + "\n\n"
    post = dict()
    if len(data_entry) == 0:
        sentence = random.choice(["Unfortunately we haven't received any data from the balloon today so check back tomorrow for more updates", "No data was received today so there's nothing to report :(", "No data today so check back tomorrow :)", "We haven't heard anything from the balloon today so be sure to check back again tomorrow"])
        suffix = "In the meantime though, be sure to check out the Durham SEDS page for updates on upcoming projects and space news: https://www.facebook.com/groups/DurhamSEDS/"
        output_string = sentence + "\n\n" + suffix
    else:
        if data_entry['GPS TX Time'][0] != "1970":
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
        if valid_coords(data_entry):
            lat, lon, speed, heading =  data_entry['GPS Lat'], data_entry['GPS Long'], data_entry['GPS Speed'], data_entry['GPS Heading']
            alt_sentence = random.choice(["which transmitted from {}m up.", 
                                                "from an alitiude of {}m."]).format(data_entry['GPS Alt']) # Shock emoji here would be cool            
            location_sentence = random.choice(["It's current coordinates are: ({}, {}). It reported a speed of {} m/s and heading of {} degrees".format(lat, lon, speed, heading),
                                                "The GPS recorded the ballons coordinates as ({}, {}), its speed as {} m/s and its heading as {} degrees.".format(lat, lon, speed, heading)])
        
            if valid_readings(data_entry):
                pressure, humidity, temperature = data_entry['Pressure'], data_entry['Humidity'], data_entry['Temperature']
                readings_sentence = random.choice(["It reported a temperature of {} C, {} mbar of pressure and a humidity of {}%.".format(temperature, pressure, humidity),
                                        "The onboard sensors read a temerature of {} C, a pressure of {} mbar, and a humidity of {}%".format(temperature, pressure, humidity),
                                        "The environment sensors read:\n\n Temerature: {} C \n Pressure: {} mbar \n Humidity: {}% \n\n".format(temperature, pressure, humidity)])
            else:
                readings_sentence = random.choice(["The sensor readings (temperature, pressure, humidity) were faulty.", "No envorimental data was transmitted (temperature, pressure, humidity). This could be due to an error starting up the sensors."])
            output_string += " " + " ".join([alt_sentence, location_sentence, readings_sentence])
        else:
            if valid_readings(data_entry):
                pressure, humidity, temperature = data_entry['Pressure'], data_entry['Humidity'], data_entry['Temperature']
                readings_sentence = "which reported a temperature of {} C, {} mbar of pressure and a humidity of {}%.".format(temperature, pressure, humidity)
                GPS_sentence = random.choice(["Unfortunately, the balloon was unable to acquire a GPS fix so we don't know where exactly it is :/ .", 
                                                "The balloon was unable to get a GPS fix. This can happen if it can't see enough satellites above it to gauge it's position from."])
            else:
                no_data = random.choice([". Unfortunately, neither the GPS nor the envirnomental sensors were able to take any measurements so there is nothing to report :(", "No data was recorded so there isn't anything to report - at least we know it's still transmitting though."])
            output_string += " " + readings_sentence + " " + GPS_sentence
    post['body'] = output_string
    return post

def get_map_image(lat, lon, zoom):
    # Create the url
    path_url = 'https://maps.googleapis.com/maps/api/staticmap?center='
    path_url += ("%.6f"%lat) + ',' + ("%.6f"%lon)
    path_url += '&markers=color:red|' + ("%.6f"%lat) + ',' + ("%.6f"%lon)
    path_url += '&zoom=' + '15'
    path_url += '&size=100x100'
    path_url += '&format=png&key='
    path_url += 'Your google API key goes here' #Maps_Key
    return path_url 

def make_fb_post(text):
    graph = facebook.GraphAPI("Your Facebook API key goes here")
    graph.put_object("110466717164776", "feed", message=text)

if __name__ == "__main__":
    print("HAB01 Script running...\n")
    print("Will check for new messages every {}s".format(CHECK_FREQ))
 

    while(1):
        data = []
        new_message_filenames = get_new_messages()
        if new_message_filenames:
            data = load_data(new_message_filenames)
            post = generate_post(data[len(data)-1]) # generate post from most recent message (we expect only 1 at a time) 
            print("generating post")
            make_fb_post(post['body'])

        print("Sleeping")
        time.sleep(CHECK_FREQ)

    # for i in range(10):
    #     print("Post", i)
    #     print(generate_post(test_data)['body'])
    #     print("\n\n")

    # print(get_map_image(54.768397, -2.208669,0))
