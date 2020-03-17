import httplib2
import os
import datetime
import time

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient import errors

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
APPLICATION_NAME = "Google Sheets Short Burst Data Uploader"
CLIENT_SECRET_FILE = "credentials.json"
SPREADSHEET_ID = "1f5YmNJC6xdTzdj7TKNBDY7rvzQkGlQaAcQJcLzm0Qz4"


def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'sheets-python-quickstart.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE,SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags: 
            credentials = tools.run_flow(flow, store, flags)
        else:
            raise TypeError("Use a newer version of python plz")
        print("Storing credentials to " + credential_path)
    return credentials

def GetRow(service, range_):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=range_).execute()
    values = result.get('values', [])
    return values

def AppendRow(service, data):
    sheet = service.spreadsheets()
    values = [data]
    body = {'values': values}
    result = sheet.values().append(spreadsheetId=SPREADSHEET_ID, valueInputOption='USER_ENTERED',range='Sheet1',body=body).execute()
    return result

def Clear(service):
    sheet = service.spreadsheets()
    first_col = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='Sheet1!A2:A1000').execute().get('values', [])
    n_rows = len(first_col)
    request = sheet.values().clear(spreadsheetId=SPREADSHEET_ID, range='Sheet1!A2:N' +str(1+n_rows))
    response = request.execute()
    return response



if __name__ == '__main__':
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('sheets', 'v4', http=http)
    print(Clear(service))
    #print(AppendRow(service, ["", "", ""]))
    #print(GetRow(service, 'Sheet1!A1:E'))

    
