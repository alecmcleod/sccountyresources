import calendar
from datetime import datetime, time, timedelta
from typing import Dict
from user_agents import parse as ua_parse
import googlemaps
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render
from . import models
from . import google_auth
from .forms import SearchForm
from .google_calendar import GoogleCalendar
from .google_maps import GoogleMaps
from .forms import SearchForm, SubscribeForm , ConfirmForm
from .modules import sms
from .modules.sms import LessThanHour , AlreadySubscribed ,NullSubscriptionArgument
from .utils import to_sent, parse_recurrence, to_standard
from urllib import parse
import random
import phonenumbers
from phonenumbers import NumberParseException
import calendar
import googlemaps


# Calendar ID variables
FOOD_CAL_ID = 'hv4cl31tra0t7l0ggbfrev6tes@group.calendar.google.com'
DRUG_CAL_ID = 'nu02uodssn6j0ij4o3l4rqv9dk@group.calendar.google.com'
HEALTH_CAL_ID = 'vlqtpo7ig0mbvpmk91j8r736kk@group.calendar.google.com'
SHOWER_CAL_ID = 'uk8elskt37v991sbe3k7qasu1k@group.calendar.google.com'
FOOD_CAL    = GoogleCalendar(google_auth.get_service(), FOOD_CAL_ID)
DRUG_CAL    = GoogleCalendar(google_auth.get_service(), DRUG_CAL_ID)
HEALTH_CAL  = GoogleCalendar(google_auth.get_service(), HEALTH_CAL_ID)
SHOWER_CAL  = GoogleCalendar(google_auth.get_service(), SHOWER_CAL_ID)
# Maps keywords to Calendar variables
var_map = {"DRUGS": DRUG_CAL, "FOOD": FOOD_CAL, "HEALTH": HEALTH_CAL, "SHOWER": SHOWER_CAL}
cal_id_map = {"DRUGS": DRUG_CAL_ID, "FOOD": FOOD_CAL_ID, "HEALTH": HEALTH_CAL_ID, "SHOWER": SHOWER_CAL_ID}
# Google maps variable
gmaps = GoogleMaps('AIzaSyDY3_muYN8O6uGzGGRE35Xj_OPAMVrup4g')

# Create your views here.
def index(request):
    form = SearchForm(request.GET)
    str(form)
    return render(
        request,
        'index.html',
        # Passes the contents of the brackets to the template
        context={'form': form},
    )

def calendars(request):
    client_ua = ua_parse(str(request.META['HTTP_USER_AGENT']))
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

def subscribe(request):

    number = parse.unquote(request.POST.get('phone_number'))

    number = ''.join(filter(str.isdigit, number))

    if len(number) == 10:
        number = '+1' + number
    else:
        number = '+' + number

    try:
        test_case = phonenumbers.parse(number,None)
    except NumberParseException:
        return render(request, 'confirm.html',\
        context = {'message': 'you entered an invalid number',
                    'action': ' ',
                    'title':'back',
                    'unseen_data':'none'})


    date = datetime.strptime(request.POST.get('date'), '%Y-%m-%d').date()
    time = datetime.strptime(request.POST.get('time'), '%H:%M:%S').time()

    iso_date_time = datetime.combine(date ,time).isoformat()

    unseen_data = { 'event_id' : request.POST.get('event_id') ,
                    'cal_id':request.POST.get('cal_id') ,
                    'iso_date_time' : iso_date_time,
                    'number' : number ,
                    }

    if not phonenumbers.is_valid_number(test_case):
        return render(request, 'confirm.html',\
        context = {'message': 'you entered an invalid number',
                    'action': ' ',
                    'title':'back',
                    'unseen_data':''})

    try:
        sms.add_reminder(request.POST.get('event_id'),request.POST.get('cal_id'),\
                    request.POST.get('date'),request.POST.get('time'),\
                    request.POST.get('rrule'),request.POST.get('title'),\
                    number)

    except LessThanHour:
        return render(request, 'confirm.html',\
         context = {'message': 'Unable to register for\
                    that event, it occurs in less than an hour',
                    'title':'back',
                    'action':' ',
                    'unseen_data':unseen_data})

    except AlreadySubscribed:
        return render(request, 'confirm.html' ,\
         context = {'message': 'You are already subscribed to this event,\
                    would you like us to unsubscibe you from this\
                    event?',
                    'action':' ','title':'Keep Subsciption',
                    'sec_action':'/calendar/cancel/','title2':'Cancel Subscription',
                    'unseen_data':unseen_data})

    except NullSubscriptionArgument:
        return render(request,'confirm.html' ,\
         context = {'message': 'there was an error processing your request',
         'action':' ','title':'back',
         'unseen_data':unseen_data})


    the_secret_bean = random.randrange(1000,9999)

    print('the secret code is : ', the_secret_bean)
    
    request.session['verification_code'] = the_secret_bean

    sms.send_sms(number,('your code is '+str(the_secret_bean)+' in the\
    future you can text this number CANCEL to unsubscribe from all notifications'))


    form = ConfirmForm(request.POST)

    return render(request, 'confirm.html',\
        context = {
        'form':form,
        
        'message':'You will receive a text with a 4 digit code\
                    to confirm your phone number, when you receive it please\
                    enter it into the text box below',
        
        'unseen_data': unseen_data,

        })


def confirm(request):
    
    entered_key = request.POST.get('code')

    if int(request.session['verification_code']) == int(entered_key):

        sms.call_remind(request.POST.get('event_id'),\
                        request.POST.get('cal_id'),\
                        request.POST.get('iso_date_time'),\
                        request.POST.get('number'))


        return render(request,'confirm.html' ,\
        context = {'message': 'reminder confirmed. you will receive\
                    notification one hour before the event.',
                    'action':'',
                    'title':'back'})
    else:
        
        return render(request,'confirm.html' ,\
        context = {'message': 'you entered the wrong code,\
                    reenter your number if you wish to try again.',
                    'action':' '
                    ,'title':'back'})



def unsubscribe(request):
    event_id = request.POST.get('event_id')
    cal_id = request.POST.get('cal_id')
    iso_date_time = request.POST.get('iso_date_time')
    num = request.POST.get('number')

    event = models.Event.objects.get(event_id=event_id, calendar_id = cal_id , \
                                    iso_date_time=iso_date_time)
    #args : event_id , phone number
    sms.del_reminder(event, num)
    return render(request,'confirm.html' ,\
        context = {'message': 'you have been unsubscribed'})

def unsub_all(request):
    #args : phonenumber
    sms.unsubscribe()
    return render(request,'confirm.html' ,\
        context = {'message': 'you have been unsubscribed from all events'})


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

    form = SubscribeForm(request.POST)

    print(event.reccurence)
    
    hidden_data = {'event_id':event_id, 'cal_id':cal_id_map[service],\
    'title':event.summary,'date':str(event.start_datetime.date()),\
    'time':str(event.start_datetime.time()), 'rrule': event.reccurence}
    

    return render(request, 'details.html', context={'title': event.summary,
                                                    'location': event.location,
                                                    'description': event.description,
                                                    'date': event.start_datetime.date,
                                                    'time': event.start_datetime.time,
                                                    'recurrence': event.reccurence,
                                                    'origin': origin,
                                                    'form':form,
                                                    'hidden_data':hidden_data,
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