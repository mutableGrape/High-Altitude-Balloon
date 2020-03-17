# Writing a Python Script for the Balloon

This guide is for creating a program that directly interacts with the GMail API. To simply use the .csv file from the Google Sheets page, see [HelpWritingYourOwnCode(CSV).md](../HelpWritingYourOwnCode(CSV).md). 

### Getting Started

Firstly, make a clear plan of what you want your code to do. Python runs line-by-line, so it can only do one thing at a time so bare this in mind. For example, if you wanted the code to create a plot of the temperature for the previous week's data your code would take the general form:

1. Open Last 30 messages
2. Check which ones are from the previous week
3. For those messages save the temperature reading and date/time in two lists
4. Create a plot of the time vs temerature
5. Save the plot as an image file

This sort of plan will make coding easier because you can create a function (block of code) for each of those steps. Refer to other Python files in the repo for guidance. 

### Creating the file

Create a new file in Python (make sure it has a useful name). The first few lines of any script will need to import the library's you want. For downloading emails you'll need the Iridium_Beacon_GMail_Downloader_RockBLOCK.py file in the same folder as your python file (and a folder named 'bin' (see GitHub page for link to file). If you are plotting (graphs), you'll probably want to use `matplotlib` (see <https://matplotlib.org/gallery/lines_bars_and_markers/simple_plot.html#sphx-glr-gallery-lines-bars-and-markers-simple-plot-py> for examples). You may need to install the package. 

### Downloading emails

For downloading emails, you'll want a function that looks something like

```python
def download_SBDs(n):
  filenames = []
  credentials = get_credentials()
  http = credentials.authorize(httplib2.Http())
  service = discovery.build('gmail', 'v1', http=http)

  messages = ListMessagesMatchingQuery(service, 'me', 'label:sbd') # Label says it's in the SBD folder in GMail (my python file puts them there)
  if messages:
      print("Messages found!")
      for message in messages:
          print('Processing: '+GetSubject(service, 'me', message["id"]))
          SaveAttachments(service, 'me', message["id"])
          filenames.append(GetAttachmentFilenames(service, 'me', message['id'])[0])
          
  return filenames
```
This also returns the names of the files so your next function can go and open them. If you don't want to download them, you can look in the Iridium_Beacon_GMail_Downloader_RockBLOCK file for the function `SaveAttachments()` and use the code to make a new function that just returns the file contents for use immediatey in Python. 

### Opening the files

There is loads of documentation for how to open files in Python so I'll let you figure that out for yourself. (just dont forget to `.close()` the file when you're finished!) You might be able to copy my `load_data()` function to do this and also format the contents.

### Using the data

If you're opening the file from scratch, when you read the contents it'll give you a string (text). You'll want integers, floats, etc to work with so some conversions will be required. For plots use `matplotlib` for whih there are thousands of online examples. 

### Testing your Code

If you want to test everything, feel free to delete my test emails from the Gmail account, then create some fake versions of what the Iridium beacon will send and send them to the account (if you want an actual email from the beacon msg me and I'll send you one I received earlier). Make sure the emails are in the 'SBD' folder, then run your code. 

Feel free to consult me about any errors - Happy coding :)
          
          
