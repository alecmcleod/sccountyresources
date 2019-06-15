import os
import httplib2shim
# workaround for connection errors see https://github.com/thefreeguide/sccountyresources/issues/26
httplib2shim.patch()  # NOQA

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_google_service_credentials():
    """Return path to credentials or raise ValueError"""
    try:
        return os.environ['GOOGLE_SERVICE_KEY']
    except KeyError:
        raise ValueError('Set GOOGLE_SERVICE_KEY to allow Google API access')


def get_google_api_key():
    """Return api key or raise ValueError"""
    try:
        return os.environ['GOOGLE_MAPS_KEY']
    except KeyError:
        raise ValueError('Set GOOGLE_MAPS_KEY to allow Google API access')


credentials = service_account.Credentials.from_service_account_file(
    get_google_service_credentials(), scopes=SCOPES)

service = build('calendar', 'v3', credentials=credentials)


def get_service():
    return service
