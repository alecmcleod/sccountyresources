import random
from datetime import time, timedelta, datetime, date
from urllib import parse

import phonenumbers
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from googleapiclient.errors import HttpError as GoogleHttpError
from phonenumbers import NumberParseException
from user_agents import parse as ua_parse

from .google_auth import get_google_api_key
from . import google_auth, models
from .forms import ConfirmForm, SearchForm, SubscribeForm, DistanceFilterForm
from .google_calendar import GoogleCalendar
from .google_maps import GoogleMaps
from .modules import sms
from .modules.sms import (AlreadySubscribed, LessThanHour,
                          NullSubscriptionArgument)

# Calendar ID variables
FOOD_CAL_ID = 'hv4cl31tra0t7l0ggbfrev6tes@group.calendar.google.com'
DRUG_CAL_ID = 'nu02uodssn6j0ij4o3l4rqv9dk@group.calendar.google.com'
HEALTH_CAL_ID = 'vlqtpo7ig0mbvpmk91j8r736kk@group.calendar.google.com'
SHOWER_CAL_ID = 'uk8elskt37v991sbe3k7qasu1k@group.calendar.google.com'
FOOD_CAL = GoogleCalendar(google_auth.get_service(), FOOD_CAL_ID)
DRUG_CAL = GoogleCalendar(google_auth.get_service(), DRUG_CAL_ID)
HEALTH_CAL = GoogleCalendar(google_auth.get_service(), HEALTH_CAL_ID)
SHOWER_CAL = GoogleCalendar(google_auth.get_service(), SHOWER_CAL_ID)
# Maps keywords to Calendar variables
var_map = {
    "DRUGS": DRUG_CAL,
    "FOOD": FOOD_CAL,
    "HEALTH": HEALTH_CAL,
    "SHOWER": SHOWER_CAL}
cal_id_map = {
    "DRUGS": DRUG_CAL_ID,
    "FOOD": FOOD_CAL_ID,
    "HEALTH": HEALTH_CAL_ID,
    "SHOWER": SHOWER_CAL_ID}
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


def search_day(request, year=None, month=None, day=None):
    return search(request, year, month, day, 'day')


def search_week(request):
    now = datetime.now()
    return search(request, now.year, now.month, now.day, 'week')


def search_weekdate(request, year=None, month=None, day=None):
    return search(request, year, month, day, 'week')


def search_month(request, year=None, month=None, day=None):
    return search(request, year, month, day, 'month')


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
            print(request.get_full_path())
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

    distance_form = DistanceFilterForm(request.GET)
    services = request.GET.get('services')
    locations = request.GET.get('locations')

    daily_events = []
    day_names = []

    # Perform the get request to google api for the appropriate service and
    # location
    if timespan == 'day':
        time_min = datetime.combine(date(year, month, day), time(0, 0)).isoformat() + '-08:00'
        time_max = datetime.combine(date(year, month, day + 1), time(0, 0)).isoformat() + '-08:00'
        api_params = {'timeMin': time_min, 'timeMax': time_max, 'singleEvents': True, 'orderBy': "startTime"}

    elif timespan == 'week':
        # Run the api call 7 times, one for each day, adding each to a
        # dictionary of days

        for i in range(7):
            time_min = datetime.combine(date(year, month, day + i), time(0, 0)).isoformat() + '-08:00'
            time_max = datetime.combine(date(year, month, day + i + 1), time(0, 0)).isoformat() + '-08:00'
            api_params = {'timeMin': time_min, 'timeMax': time_max, 'singleEvents': True, 'orderBy': "startTime"}
            # Add that days worth of events to the list, and the name of the day
            # Say today if it is, and tomorrow if it is
            if date(year, month, day + i) == datetime.today().date():
                day_names.append(f"Today, {datetime.strftime(datetime(year, month, day + i, 0, 0), '%B %d')}")
            elif date(year, month, day + i) == (date.today() + timedelta(days=1)):
                day_names.append(f"Tomorrow, {datetime.strftime(datetime(year, month, day + i, 0, 0), '%B %d')}")
            else:
                day_names.append(datetime.strftime(datetime(year, month, day + i, 0, 0), "%A, %B %d"))
            daily_events.append(api_call(services, locations, api_params))

    else:
        # If no parameters, set to display today's events
        timespan = 'day'
        time_min = datetime.combine(datetime.today().date(), time(0, 0)).isoformat() + '-08:00'
        time_max = (datetime.combine(datetime.today().date(), time(0, 0)) + timedelta(days=1)).isoformat() + '-08:00'
        api_params = {'timeMin': time_min, 'timeMax': time_max, 'singleEvents': True, 'orderBy': "startTime"}

    events = api_call(services, locations, api_params)

    return render(
        request,
        'search.html',
        context={'events': events,
                 'origin': request.GET.get('locations'),
                 'service': request.GET.get('services'),
                 'distance_form': distance_form,
                 'daily_events': zip(daily_events, day_names)}
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

    print('the secret code is : ', the_secret_bean)

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

    form = SubscribeForm(request.POST)

    hidden_data = {
        'event_id': event_id,
        'cal_id': cal_id_map[service],
        'title': event.summary,
        'date': str(event.start_datetime.date()),
        'time': str(event.start_datetime.time()),
        'rrule': event.reccurence}

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
            'form': form,
            'hidden_data': hidden_data,
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
