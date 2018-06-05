import calendar
from datetime import datetime, time, timedelta
from typing import Dict
from user_agents import parse
import googlemaps
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render

from . import google_auth
from .forms import SearchForm
from .google_calendar import GoogleCalendar
from .google_maps import GoogleMaps
from .utils import parse_recurrence, to_sent, to_standard

# Calendar ID variables
FOOD_CAL    = GoogleCalendar(google_auth.get_service(), 'hv4cl31tra0t7l0ggbfrev6tes@group.calendar.google.com')
DRUG_CAL    = GoogleCalendar(google_auth.get_service(), 'nu02uodssn6j0ij4o3l4rqv9dk@group.calendar.google.com')
HEALTH_CAL  = GoogleCalendar(google_auth.get_service(), 'vlqtpo7ig0mbvpmk91j8r736kk@group.calendar.google.com')
SHOWER_CAL  = GoogleCalendar(google_auth.get_service(), 'uk8elskt37v991sbe3k7qasu1k@group.calendar.google.com')
# Maps keywords to Calendar variables
var_map: Dict[str, GoogleCalendar] = {"DRUGS": DRUG_CAL, "FOOD": FOOD_CAL, "HEALTH": HEALTH_CAL, "SHOWER": SHOWER_CAL}

# Google maps variable
gmaps = GoogleMaps('AIzaSyDY3_muYN8O6uGzGGRE35Xj_OPAMVrup4g')

# Create your views here.
def index(request):
    form = SearchForm(request.GET)
    return render(
        request,
        'index.html',
        # Passes the contents of the brackets to the template
        context={'form': form},
    )

def calendars(request):
    client_ua = parse(str(request.META['HTTP_USER_AGENT']))
    return render(
        request,
        'calendars.html',
        context={'is_mobile': client_ua.is_mobile}
    )


def search(request):

    def sort_events(events):
        """
        Sorts events in the event list by distance
        :param events: list to be sorted
        """
        # the key defines what value is used to sort by in the event dictionaries. If it is missing it will return none
        def event_key(event):
            missing_distance = (event.distance is None)
            return missing_distance, event.distance if not missing_distance else None
        list.sort(events, key=event_key)

    # Perform the get request to google api for the appropriate service and location
    now = datetime.combine(datetime.today(), time(0, 0)).isoformat() + '-08:00'
    tomorrow = (datetime.combine(datetime.today(), time(0, 0)) + timedelta(days=1)).isoformat() + '-08:00'
    api_params = {'timeMin': now, 'timeMax': tomorrow, 'singleEvents': True, 'orderBy': "startTime"}

    services = request.GET.get('services')
    if services is None:
        # If there are no search parameters, redirect to home page
        return HttpResponseRedirect('/')
    elif services not in var_map:
        # Requested service doesn't exist
        raise Http404("Service does not exist.")
    else:
        if request.GET.get('locations') is not None:
            # Use Calendar API to get a list of GoogleEvents, then use Distance Matrix to add distances to those events
            events_today = gmaps.convert_events(request.GET.get('locations'), list(var_map[services].get_events(api_params)))
            if events_today is not None:
                sort_events(events_today)

    return render(
        request,
        'search.html',
        context={'events': events_today, 'origin': request.GET.get('locations'), 'service': request.GET.get('services')}
    )


def details(request, service=None, event_id=None):
    """
    Renders the detail page for a given event id
    """

    origin = request.GET.get('locations')

    if service in var_map:
        google_event_params = {
            'default_summary': '',
            'default_reccurence': '',
            'default_location': '1515 Ocean St, Santa Cruz, CA 95060',
            'default_description': ''
        }
        event = var_map[service].get_event(event_id, dict(), google_event_params)
    else:
        raise Http404("Service does not exist.")

    return render(request, 'details.html', context={'title': event.summary,
                                                    'location': event.location,
                                                    'description': event.description,
                                                    'date': event.start_datetime.date,
                                                    'time': event.start_datetime.time,
                                                    'recurrence': event.reccurence,
                                                    'origin': origin
                                                    })

def event_ical_download(request, service=None, event_id=None):
    """
    Returns an ical file for a spefic event.
    """
    if service in var_map:
        google_event_params = {
            'default_summary': '',
            'default_reccurence': '',
            'default_location': '1515 Ocean St, Santa Cruz, CA 95060',
            'default_description': ''
        }
        event = var_map[service].get_event(event_id, dict(), google_event_params)

        response = HttpResponse(event.to_ical(), content_type='text/calendar')
        response['Content-Disposition'] = 'attachment; filename=calendar.ics'
        return response
    else:
        raise Http404("Service does not exist.")

def calendar_ical_download(request, service=None):
    """
    Returns an ical file for a whole calendar
    """
    if service is None:
        # If there are no search parameters, redirect to home page
        return HttpResponseRedirect('/')
    elif service not in var_map:
        # Requested service doesn't exist
        raise Http404("Service does not exist.")
    else:
        response = HttpResponse(var_map[service].to_ical(), content_type='text/calendar')
        response['Content-Disposition'] = 'attachment; filename=calendar.ics'
        return response