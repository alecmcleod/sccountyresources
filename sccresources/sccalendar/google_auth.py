from __future__ import print_function
from google.oauth2 import service_account
from googleapiclient.discovery import build

# maps api key AIzaSyDY3_muYN8O6uGzGGRE35Xj_OPAMVrup4g
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'sccalendar/servicekey.json'

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('calendar', 'v3', credentials=credentials)


def get_service():
    return service


