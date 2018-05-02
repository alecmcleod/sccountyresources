from django.shortcuts import render
from django.http import HttpResponseRedirect
from . import google_auth
from datetime import datetime, time, timedelta
from .forms import SearchForm


# Calendar ID variables
FOOD_CAL = 'hv4cl31tra0t7l0ggbfrev6tes@group.calendar.google.com'
DRUG_CAL = 'nu02uodssn6j0ij4o3l4rqv9dk@group.calendar.google.com'
HEALTH_CAL = 'vlqtpo7ig0mbvpmk91j8r736kk@group.calendar.google.com'
SHOWER_CAL = 'uk8elskt37v991sbe3k7qasu1k@group.calendar.google.com'


# Create your views here.
def index(request):

    form = SearchForm(request.GET)

    return render(
        request,
        'index.html',
        # Passes the contents of the brackets to the template
        context={'form': form},
    )


def search(request):

    # If there are no search parameters, redirect to home page
    if not request.GET.get('services'):
        return HttpResponseRedirect('/')
    else:
        now = datetime.combine(datetime.today(), time(0, 0)).isoformat() + '-08:00'
        tomorrow = (datetime.combine(datetime.today(), time(0, 0)) + timedelta(days=1)).isoformat() + '-08:00'
        print(now)
        print(tomorrow)
        if request.GET.get('services') == 'DRUGS':
            service = 'DRUGS'
            events_today = google_auth.get_service().events().list(
                calendarId=DRUG_CAL,
                timeMin=now,
                timeMax=tomorrow,
                singleEvents=True,
                orderBy='startTime').execute()
        elif request.GET.get('services') == 'FOOD':
            service = 'FOOD'
            events_today = google_auth.get_service().events().list(
                calendarId=FOOD_CAL,
                timeMin=now,
                timeMax=tomorrow,
                singleEvents=True,
                orderBy='startTime').execute()
        elif request.GET.get('services') == 'HEALTH':
            service = 'HEALTH'
            events_today = google_auth.get_service().events().list(
                calendarId=HEALTH_CAL,
                timeMin=now,
                timeMax=tomorrow,
                singleEvents=True,
                orderBy='startTime').execute()
        elif request.GET.get('services') == 'SHOWER':
            service = 'SHOWER'
            events_today = google_auth.get_service().events().list(
                calendarId=SHOWER_CAL,
                timeMin=now,
                timeMax=tomorrow,
                singleEvents=True,
                orderBy='startTime').execute()
        else:
            return render(request, '404.html')

        events = events_today.get('items', [])
        return render(
            request,
            'search.html',
            context={'events': events, 'service': service}
        )


def details(request, service=None, event_id=None):

    if service == 'DRUGS':
        event = google_auth.get_service().events().get(calendarId=DRUG_CAL, eventId=event_id).execute()
    elif service == 'FOOD':
        event = google_auth.get_service().events().get(calendarId=FOOD_CAL, eventId=event_id).execute()
    elif service == 'HEALTH':
        event = google_auth.get_service().events().get(calendarId=HEALTH_CAL, eventId=event_id).execute()
    elif service == 'SHOWER':
        event = google_auth.get_service().events().get(calendarId=DRUG_CAL, eventId=event_id).execute()
    else:
        return render(request, '404.html')

    if not event:
        return render(request, '404.html')

    title = event.get('summary')
    location = event.get('location')
    text = event.get('description')
    event_date = event['start'].get('dateTime')
    event_time = event['start'].get('date')
    if text is None:
        text = 'no description'
    if title is None:
        title = 'no title'
    if location is None:
        location = '1515 Ocean St, Santa Cruz, CA 95060'

    tags = ['tag1', 'tag2', 'tag3', 'tag4']

    # in future add a method to auto generate tags from location
    # wait for alec to add etags in events

    return render(request, 'details.html', context={'title': title,
                                                    'location': location,
                                                    'description': text,
                                                    'date': event_date,
                                                    'time': event_time,
                                                    'tags': tags})








