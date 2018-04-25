from __future__ import print_function
from google.oauth2 import service_account
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools


SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'sccalendar/servicekey.json'

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('calendar', 'v3', credentials=credentials)

def getService():
    return service


