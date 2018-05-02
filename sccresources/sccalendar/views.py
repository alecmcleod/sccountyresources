from django.shortcuts import render
from . import google_auth
import datetime
from .forms import SearchForm

# Create your views here.


def index(request):

    if request.method == 'GET':
        form = SearchForm(request.GET)
        if form.is_valid():
            output_text = request.GET.get('your_name')
        else:
            output_text = 'Invalid input'

    else:
        form = SearchForm()
        output_text = ''

    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    # Retrieve next ten events starting from now from the linked google calendar
    events_result = google_auth.get_service().events().list(calendarId='hv4cl31tra0t7l0ggbfrev6tes@group.calendar.google.com', timeMin=now,
                                                            maxResults=10, singleEvents=True,
                                                            orderBy='startTime').execute()
    events = events_result.get('items', [])
    # Parse the events into a simple printable form
    eventsSimple = []

    for event in events:
        eventsSimple.append((event['start'].get('dateTime'), event['start'].get('date'), event.get('id')))
    return render(
        request,
        'index.html',
        #passes the contents of the brackets to the template
        context={'eventsSimple': eventsSimple, 'form': form, 'output_text': output_text},
    )

def details(request , event_id=None):
    
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    # Retrieve next ten events starting from now from the linked google calendar
    events_result = google_auth.get_service().events().list(calendarId='hv4cl31tra0t7l0ggbfrev6tes@group.calendar.google.com', timeMin=now,
                                                            maxResults=10, singleEvents=True,
                                                            orderBy='startTime').execute()
    events = events_result.get('items', [])
    # Parse the events into a simple printable form

    title = None

    location = None

    text = None

    found = False

    if event_id == None:
        return render(request,'404.html')

    for event in events:
        print(event.get('id'))
        if event.get('id') == event_id:
            found = True
            title = event.get('summary')
            location = event.get('location')
            text = event.get('description')
            date = event['start'].get('dateTime')
            time = event['start'].get('date')
            if text == None:
                text = 'no description'
            if title == None:
                title = 'no title'
            if location == None:
                location ='1515 Ocean St, Santa Cruz, CA 95060'
            break


    tags = ['tag1','tag2','tag3','tag4']

    ##in future add a method to auto generate tags from location
    ## wait for alec to add etags in events

    if not found:
        return render(request,'404.html')


    return render(request,'details.html',context={'title':title,
        'location':location,'description':text,'date':date,'time':time,'tags': tags})








