from django.shortcuts import render
from . import google_auth
import datetime

# Create your views here.


def index(request):
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    # Retrieve next ten events starting from now from the linked google calendar
    events_result = google_auth.get_service().events().list(calendarId='hv4cl31tra0t7l0ggbfrev6tes@group.calendar.google.com', timeMin=now,
                                                            maxResults=10, singleEvents=True,
                                                            orderBy='startTime').execute()
    events = events_result.get('items', [])
    # Parse the events into a simple printable form
    eventsSimple = []
    for event in events:
        eventsSimple.append(event['start'].get('dateTime', event['start'].get('date')))
    return render(
        request,
        'index.html',
        #passes the contents of the brackets to the template
        context={'eventsSimple':eventsSimple},
    )
