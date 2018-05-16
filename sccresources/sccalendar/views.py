from django.shortcuts import render
from django.http import HttpResponseRedirect
from . import google_auth
from datetime import datetime, time, timedelta
from .google_calendar import GoogleCalendar
from .forms import SearchForm
from .utils import to_sent, parse_recurrence, to_standard

import calendar
import googlemaps


# Calendar ID variables
FOOD_CAL    = GoogleCalendar(google_auth.get_service(), 'hv4cl31tra0t7l0ggbfrev6tes@group.calendar.google.com')
DRUG_CAL    = GoogleCalendar(google_auth.get_service(), 'nu02uodssn6j0ij4o3l4rqv9dk@group.calendar.google.com')
HEALTH_CAL  = GoogleCalendar(google_auth.get_service(), 'vlqtpo7ig0mbvpmk91j8r736kk@group.calendar.google.com')
SHOWER_CAL  = GoogleCalendar(google_auth.get_service(), 'uk8elskt37v991sbe3k7qasu1k@group.calendar.google.com')
# Maps keywords to Calendar variables
var_map = {"DRUGS": DRUG_CAL, "FOOD": FOOD_CAL, "HEALTH": HEALTH_CAL, "SHOWER": SHOWER_CAL}

# Google maps variable
gmaps = googlemaps.Client(key='AIzaSyDY3_muYN8O6uGzGGRE35Xj_OPAMVrup4g')

origins = ['603 Laguna St Santa Cruz']
destinations = ['UCSC']
print(gmaps.distance_matrix(origins, destinations))

print('test')

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
    # Perform the get request to google api for the appropriate service and location
    now = datetime.combine(datetime.today(), time(0, 0)).isoformat() + '-08:00'
    tomorrow = (datetime.combine(datetime.today(), time(0, 0)) + timedelta(days=1)).isoformat() + '-08:00'
    api_params = {'timeMin': now, 'timeMax': tomorrow, 'singleEvents': True, 'orderBy': "startTime"}

    services = request.GET.get('services')
    if services is None:
        # If there are no search parameters, redirect to home page
        return HttpResponseRedirect('/')
    elif services is None:
        # Requested service doesn't exist
        return render(request, '404.html')
    else:
        events_today = list(var_map[services].get_events(**api_params))

    return render(
        request,
        'search.html',
        context={'events': events_today, 'service': request.GET.get('services')}
    )

def details(request, service=None, event_id=None):
    '''Details: returns a response with all event info'''
    '''         pretaining to an event with id 'event_id' '''

    if service in var_map:
        event = var_map[service].get_event(event_id)
    else:
        return render(request, '404.html')

    if not event:
        return render(request, '404.html')

    title = event.get('summary', '')
    try:
        recurrence = parse_recurrence(event['recurrence'])
    except KeyError:
        recurrence = ''

    location = event.get('location', '1515 Ocean St, Santa Cruz, CA 95060')
    text = event.get('description', '')
    event_date = event['start'].get('dateTime', '')
    event_time = event['start'].get('date', '')

    if '-' in event_time:
        ed_list = event_time.split('-')
        ed_list[2] = ed_list[2].split('T')[0] 
        event_time = calendar.month_name[int(ed_list[1])] + ' , ' + ed_list[2] + ' , ' + ed_list[0]
    elif ':' in event_time:
        event_time = to_standard(event_time) 

    # ^ ^ this requires explanation. some people think its fun to enter
    #the time as the date or the date as the time. this is to fix monkey
    #problems.

    if event_date is not '':
        ed_list = event_date.split('-')
        ed_list[2] = ed_list[2].split('T')[0] 
        event_date = calendar.month_name[int(ed_list[1])] + ' , ' + ed_list[2] + ' , ' + ed_list[0]

    return render(request, 'details.html', context={'title': title,
                                                    'location': location,
                                                    'description': text,
                                                    'date': event_date,
                                                    'time': event_time,
                                                    'recurrence':recurrence
                                                    })