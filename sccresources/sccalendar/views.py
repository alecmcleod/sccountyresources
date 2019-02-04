import random
from datetime import timedelta, datetime
from urllib import parse

import phonenumbers
import json
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from googleapiclient.errors import HttpError as GoogleHttpError
from phonenumbers import NumberParseException
from user_agents import parse as ua_parse
from urllib.request import urlopen

from .utils import get_tz
from .google_credentials_auth import get_google_api_key
from . import google_credentials_auth, models
from .forms import ConfirmForm, SearchForm
from .google_calendar import GoogleCalendar
from .google_maps import GoogleMaps
from .modules import sms
from .modules.sms import (AlreadySubscribed, LessThanHour,
                          NullSubscriptionArgument)

# Calendar ID variables
ADDICTION_CAL_ID = 'thefreeguide.org_5p1u40696ia4dk5gs9rv6vk2nc@group.calendar.google.com'
FOOD_CAL_ID = 'thefreeguide.org_kvh6uvjr5q6b4ag81d8mn7gv6k@group.calendar.google.com'
GENERAL_CAL_ID = 'thefreeguide.org_o47rok0bn546o1p7nuh7fv4hjc@group.calendar.google.com'
HOUSING_CAL_ID = 'thefreeguide.org_8pt89nk8fjp3fc2hjioc08t9c8@group.calendar.google.com'
HYGIENE_CAL_ID = 'thefreeguide.org_5claugljrihomenrh7g48vm47k@group.calendar.google.com'
MEDICAL_CAL_ID = 'thefreeguide.org_i52aj8otebmkpp4bhg36ignu60@group.calendar.google.com'
PSYCH_CAL_ID = 'thefreeguide.org_8i98m84jrnea246rcufbcm8fok@group.calendar.google.com'
RESTROOM_CAL_ID = 'thefreeguide.org_lgt8qn6t8nsugv9vmfmq0i2474@group.calendar.google.com'
SMARTPATH_CAL_ID = 'thefreeguide.org_dcd6op976eb8jv4710tarj0clk@group.calendar.google.com'
STORAGE_CAL_ID = 'thefreeguide.org_mo1gcbgvc5ecu4g0j20hlgl38c@group.calendar.google.com'
VETERAN_CAL_ID = 'thefreeguide.org_akjd0d7ebfblolmvu24efmaslc@group.calendar.google.com'
VET_CAL_ID = 'thefreeguide.org_81c5ophc7o6efc7cg2us30h3qk@group.calendar.google.com'

ADDICTION_CAL = GoogleCalendar(google_credentials_auth.get_service(), ADDICTION_CAL_ID)
FOOD_CAL = GoogleCalendar(google_credentials_auth.get_service(), FOOD_CAL_ID)
GENERAL_CAL = GoogleCalendar(google_credentials_auth.get_service(), GENERAL_CAL_ID)
HOUSING_CAL = GoogleCalendar(google_credentials_auth.get_service(), HOUSING_CAL_ID)
HYGIENE_CAL = GoogleCalendar(google_credentials_auth.get_service(), HYGIENE_CAL_ID)
MEDICAL_CAL = GoogleCalendar(google_credentials_auth.get_service(), MEDICAL_CAL_ID)
PSYCH_CAL = GoogleCalendar(google_credentials_auth.get_service(), PSYCH_CAL_ID)
RESTROOM_CAL = GoogleCalendar(google_credentials_auth.get_service(), RESTROOM_CAL_ID)
SMARTPATH_CAL = GoogleCalendar(google_credentials_auth.get_service(), SMARTPATH_CAL_ID)
STORAGE_CAL = GoogleCalendar(google_credentials_auth.get_service(), STORAGE_CAL_ID)
VETERAN_CAL = GoogleCalendar(google_credentials_auth.get_service(), VETERAN_CAL_ID)
VET_CAL = GoogleCalendar(google_credentials_auth.get_service(), VET_CAL_ID)

# Maps keywords to Calendar variables
var_map = {
    "ADDICTION": ADDICTION_CAL,
    "FOOD": FOOD_CAL,
    "GENERAL": GENERAL_CAL,
    "HOUSING": HOUSING_CAL,
    "HYGIENE": HYGIENE_CAL,
    "MEDICAL": MEDICAL_CAL,
    "PSYCH": PSYCH_CAL,
    "RESTROOM": RESTROOM_CAL,
    "SMARTPATH": SMARTPATH_CAL,
    "STORAGE": STORAGE_CAL,
    "VETERAN": VETERAN_CAL,
    "VET": VET_CAL
    }
cal_id_map = {
    "ADDICTION": ADDICTION_CAL_ID,
    "FOOD": FOOD_CAL_ID,
    "GENERAL": GENERAL_CAL_ID,
    "HOUSING": HOUSING_CAL_ID,
    "HYGIENE": HYGIENE_CAL_ID,
    "MEDICAL": MEDICAL_CAL_ID,
    "PSYCH": PSYCH_CAL_ID,
    "RESTROOM": RESTROOM_CAL_ID,
    "SMARTPATH": SMARTPATH_CAL_ID,
    "STORAGE": STORAGE_CAL_ID,
    "VETERAN": VETERAN_CAL_ID,
    "VET": VET_CAL_ID
    }

# Google maps variable
gmaps = GoogleMaps()


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
    try:
        is_mobile = ua_parse(str(request.META['HTTP_USER_AGENT'])).is_mobile
    except BaseException:
        is_mobile = False

    return render(
        request,
        'calendars.html',
        context={'is_mobile': is_mobile}
    )

def search_day_noncomplete(request):
    now = datetime.now()
    return search(request, now.year, now.month, now.day, 'day')


def search_day(request, year=None, month=None, day=None):
    return search(request, year, month, day, 'day')


def search(request, year=None, month=None, day=None, timespan=None):  # noqa: C901
    def sort_events(events):
        """
        Sorts events in the event list by distance
        :param events: list to be sorted
        """

        # the key defines what value is used to sort by in the event
        # dictionaries. If it is missing it will return none
        def event_key(event):
            missing_distance = (event.distance is None)
            return missing_distance, event.distance if not missing_distance else None

        list.sort(events, key=event_key)

    def api_call(services, locations, api_params):  # noqa: C901
        """
        Makes google maps api call for the specified service and location with the api_params given.
        :param services: service to be returned
        :param locations: location to distance from
        :api_params: parameters for the api call
        """
        if services is None:
            # If there are no search parameters, redirect to home page
            # print(request.get_full_path())
            return HttpResponseRedirect('/')
        elif services not in var_map:
            # Requested service doesn't exist
            raise Http404('Service does not exist.')
        elif locations is None or len(locations) == 0:
            # If no location is provided, don't apply distance to the event
            events = list(var_map[services].get_events(api_params))
        else:
            # Use Calendar API to get a list of GoogleEvents, then use Distance
            # Matrix to add distances to those events
            events = gmaps.convert_events(locations, list(
                var_map[services].get_events(api_params)))
            if events is not None:
                sort_events(events)
        return events

    services = request.GET.get('services')
    locations = request.GET.get('locations')

    addresses = []

    # Perform the get request to google api for the appropriate service and
    # location
    time_min = get_tz().localize(datetime(year, month, day))
    time_max = time_min + timedelta(days=1)
    day_name = time_min.strftime("%A, %B %d")
    api_params = {'timeMin': time_min.isoformat(),
                  'timeMax': time_max.isoformat(),
                  'singleEvents': True,
                  'orderBy': "startTime"}
    day_events = api_call(services, locations, api_params)
    key = get_google_api_key()
    if day_events:
        for event in day_events:
            # Geocode event location and check to make sure it gets a correct result. If not, pass to array as if it did not have address
            if event.location != None:
                url="https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s" % (event.location, key)
                url = url.replace(" ", "+")
                response = urlopen(url)
                jsongeocode = response.read()
                jsongeocode = json.loads(jsongeocode)
                if(jsongeocode['status'] == "OK"):
                    event.latlng = [jsongeocode['results'][0]['geometry']['location']['lat'], jsongeocode['results'][0]['geometry']['location']['lng']]
                else:
                    event.location = None
                    event.latlng = "NO_ADDRESS"
            else:
                event.latlng = "NO_ADDRESS"


    # Create variables defining the next day and previous day
    time_next = time_min + timedelta(days=1)
    time_prev = time_min + timedelta(days=-1)
    time_next_date = [time_next.year, time_next.month, time_next.day]
    time_prev_date = [time_prev.year, time_prev.month, time_prev.day]

    return render(
        request,
        'search.html',
        context={'origin': request.GET.get('locations'),
                 'service': request.GET.get('services'),
                 'day_events': day_events,
                 'day_name': day_name,
                 'next_date': time_next_date,
                 'prev_date': time_prev_date}
    )


def subscribe(request):
    number = parse.unquote(request.POST.get('phone_number'))

    number = ''.join(filter(str.isdigit, number))

    if len(number) == 10:
        number = '+1' + number
    else:
        number = '+' + number

    try:
        test_case = phonenumbers.parse(number, None)

    except NumberParseException:
        return render(request, 'confirm.html',
                      context={'message': 'you entered an invalid number',
                               'action': ' ',
                               'title': 'back',
                               'unseen_data': 'none'})

    date = datetime.strptime(request.POST.get('date'), '%Y-%m-%d').date()
    time = datetime.strptime(request.POST.get('time'), '%H:%M:%S').time()

    iso_date_time = datetime.combine(date, time).isoformat()

    unseen_data = {'event_id': request.POST.get('event_id'),
                   'cal_id': request.POST.get('cal_id'),
                   'iso_date_time': iso_date_time,
                   'number': number,
                   }

    if not phonenumbers.is_valid_number(test_case):
        return render(request, 'confirm.html',
                      context={'message': 'you entered an invalid number',
                               'action': ' ',
                               'title': 'back',
                               'unseen_data': ''})

    try:
        resp = sms.add_reminder(
            request.POST.get('event_id'),
            request.POST.get('cal_id'),
            request.POST.get('date'),
            request.POST.get('time'),
            request.POST.get('rrule'),
            request.POST.get('title'),
            number)

    except LessThanHour:
        return render(request, 'confirm.html',
                      context={'message':
                               'That event, it occurs in less than an hour. You are\
                                   signed up for future instances of this event.\
                                   You may enter your phone number again to unsubscibe.',
                               'title': 'back',
                               'action': ' ',
                               'unseen_data': unseen_data})

    except AlreadySubscribed:
        return render(
            request,
            'confirm.html',
            context={
                'message': 'You are already subscribed to this event,\
                    would you like us to unsubscibe you from this\
                    event?',
                'action': ' ',
                'title': 'Keep Subsciption',
                'sec_action': '/calendar/cancel/',
                'title2': 'Cancel Subscription',
                'unseen_data': unseen_data})

    except NullSubscriptionArgument:
        return render(
            request,
            'confirm.html',
            context={
                'message': 'there was an error processing your request',
                'action': ' ',
                'title': 'back',
                'unseen_data': unseen_data})

    the_secret_bean = random.randrange(1000, 9999)

    # print('the secret code is : ', the_secret_bean)

    request.session['verification_code'] = the_secret_bean

    sms.send_sms(number, ('your code is ' + str(the_secret_bean) + ' in the\
future you can text this number CANCEL to unsubscribe from all notifications'))

    form = ConfirmForm(request.POST)

    return render(request, 'confirm.html',
                  context={
                      'form': form,

                      'message': 'You will receive a text with a 4 digit code\
                    to confirm your phone number, when you receive it please\
                    enter it into the text box below',

                      'unseen_data': unseen_data,
                      'resp': resp,
                  })


def confirm(request):
    entered_key = request.POST.get('code')

    if int(request.session['verification_code']) == int(entered_key):

        sms.call_remind(request.POST.get('event_id'),
                        request.POST.get('cal_id'),
                        request.POST.get('iso_date_time'),
                        request.POST.get('number'))

        if request.POST.get('resp') == 'LTHE':
            return render(request, 'confirm.html',
                          context={'message': 'reminder confirmed. unfortunately\
                        the event occurs in less than an hour.\
                        you will notified at the next occurrance of this event',
                                   'action': ' ',
                                   'title': 'back'})

        else:
            return render(request, 'confirm.html',
                          context={'message': 'reminder confirmed. you will receive\
                        notification one hour before the event.',
                                   'action': ' ',
                                   'title': 'back'})
    else:

        return render(request, 'confirm.html',
                      context={'message': 'you entered the wrong code,\
                    reenter your number if you wish to try again.',
                               'action': ' ', 'title': 'back'})


def unsubscribe(request):
    event_id = request.POST.get('event_id')
    cal_id = request.POST.get('cal_id')
    iso_date_time = request.POST.get('iso_date_time')
    num = request.POST.get('number')

    event = models.Event.objects.get(event_id=event_id,
                                     calendar_id=cal_id,
                                     iso_date_time=iso_date_time)
    # args : event_id , phone number
    sms.del_reminder(event, num)
    return render(request,
                  'confirm.html',
                  context={'message': 'you have been unsubscribed'})


def unsub_all(request):
    # args : phonenumber
    sms.unsubscribe()
    return render(
        request, 'confirm.html', context={
            'message': 'you have been unsubscribed from all events'})


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

        try:
            event = var_map[service].get_event(event_id, dict(), google_event_params)
        except GoogleHttpError as e:
            if e.resp['status'] == '404':
                raise Http404('Event not found.')
    else:
        raise Http404('Service does not exist.')

    return render(
        request,
        'details.html',
        context={
            'title': event.summary,
            'location': event.location,
            'description': event.description,
            'date': event.start_datetime.date,
            'time': event.start_datetime.time,
            'recurrence': event.reccurence,
            'id': event_id,
            'service': service,
            'origin': origin,
            'api_key': get_google_api_key()
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
        event = var_map[service].get_event(
            event_id, dict(), google_event_params)

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
        response = HttpResponse(
            var_map[service].export_ical(),
            content_type='text/calendar')
        response['Content-Disposition'] = 'attachment; filename=calendar.ics'
        return response
