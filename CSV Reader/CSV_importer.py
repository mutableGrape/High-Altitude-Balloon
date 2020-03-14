""" File template for using the balloon data, imported via a *.csv file """


def import_from_csv(filename):
    "Imports the data from a *.csv file stored in the same folder as this program"

    contents = ""
    with open(filename, "r") as f:
        contents = f.read()
        f.close()
    
    split_contents = [entry.split(",") for entry in contents.split("\n") if entry != ""]

    data_dictionarys = []
    for entry in split_contents[1:]:    # Exclude titles
        new_dict = dict()
             
        new_dict["MOMSN"] = entry[0]                    # Message MOMSN       
        new_dict["GPS TX Time"] = entry[1]              # GPS Tx Time "DD/MM/YYY HH:MM:SS"               
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
        data_dictionarys.append(new_dict)

    return data_dictionarys


if __name__ == "__main__":

    my_filename = "test_data_file.csv"
    data = import_from_csv(my_filename)

    ### The data variable above is a list of dictionarys - each dictionary has the data from one transmission

    ### Example code to put all the temperatures into a list:

    my_temperatures = []
    for entry in data:
        temperature = entry["Temperature"]      # Change "Temperature" here for the data you want (see above for names)
        my_temperatures.append(temperature)

    print(my_temperatures)


    ### Put your code below here


