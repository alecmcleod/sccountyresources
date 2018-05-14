from django.shortcuts import render
from django.http import HttpResponseRedirect
from . import google_auth
from datetime import datetime, time, timedelta
from .forms import SearchForm
import calendar
import googlemaps


# Calendar ID variables
FOOD_CAL = 'hv4cl31tra0t7l0ggbfrev6tes@group.calendar.google.com'
DRUG_CAL = 'nu02uodssn6j0ij4o3l4rqv9dk@group.calendar.google.com'
HEALTH_CAL = 'vlqtpo7ig0mbvpmk91j8r736kk@group.calendar.google.com'
SHOWER_CAL = 'uk8elskt37v991sbe3k7qasu1k@group.calendar.google.com'

# Google maps variable
gmaps = googlemaps.Client(key='AIzaSyDY3_muYN8O6uGzGGRE35Xj_OPAMVrup4g')

origins = ['603 Laguna St Santa Cruz']
destinations = ['UCSC']
print(gmaps.distance_matrix(origins, destinations))

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
    def get_results():
        now = datetime.combine(datetime.today(), time(0, 0)).isoformat() + '-08:00'
        tomorrow = (datetime.combine(datetime.today(), time(0, 0)) + timedelta(days=1)).isoformat() + '-08:00'
        if request.GET.get('services') == 'DRUGS':
            events_today = google_auth.get_service().events().list(
                calendarId=DRUG_CAL,
                timeMin=now,
                timeMax=tomorrow,
                singleEvents=True,
                orderBy='startTime').execute()
        elif request.GET.get('services') == 'FOOD':
            events_today = google_auth.get_service().events().list(
                calendarId=FOOD_CAL,
                timeMin=now,
                timeMax=tomorrow,
                singleEvents=True,
                orderBy='startTime').execute()
        elif request.GET.get('services') == 'HEALTH':
            events_today = google_auth.get_service().events().list(
                calendarId=HEALTH_CAL,
                timeMin=now,
                timeMax=tomorrow,
                singleEvents=True,
                orderBy='startTime').execute()
        elif request.GET.get('services') == 'SHOWER':
            events_today = google_auth.get_service().events().list(
                calendarId=SHOWER_CAL,
                timeMin=now,
                timeMax=tomorrow,
                singleEvents=True,
                orderBy='startTime').execute()
        else:
            return render(request, '404.html')
        return events_today

    # If there are no search parameters, redirect to home page
    if not request.GET.get('services'):
        return HttpResponseRedirect('/')
    else:
        events = get_results().get('items', [])
        return render(
            request,
            'search.html',
            context={'events': events, 'service': request.GET.get('services')}
        )



def details(request, service=None, event_id=None):
    '''Details: returns a response with all event info'''
    '''         pretaining to an event with id 'event_id' '''

    def parse_recurrance(rec_list):
        '''arguments: standard google calendars list of recurrance strings'''
        '''output : an english string describing when an event recurrs'''
        keys = ['FREQ','COUNT','INTERVAL','BYDAY','UNTIL']
        parse = ''
        out_string = ''
        for rule in rec_list:
            for key in keys:
                if key in rule:
                    parse = rule.split('=')
                    if parse[0] is 'FREQ':
                        parse = parse[1].lower() + ', '
                    elif parse[0]  is 'COUNT':
                        parse = ''
                    elif parse[0]  is 'INTERVAL':
                        parse = ''
                    elif parse[0]  is 'BYDAY':
                        parse = 'on' + to_sent(parse[1])
                    elif parse[0]  is 'UNTIL':
                        parse = 'until' + calendar.month_name(int(parse[1][5:6])) + ',' + parse[1][7:]
                    else:
                        break
            out_string += ("this event occurs " + parse)
        return out_string

    def to_sent(abbrv_string):
        '''to_sent: input: a comma seperate string of day abbreviations
                    output: an english sentence enumerating those days'''
        abbrv_dict = {'MO':'Monday','TU':'Tuesday','WE':'Wednesday'
        ,'TH':'Thursday','FR':'Friday','SA':'Saturday','SU':'Sunday'}
        
        abbrv_list = abbrv_string.split(',')
        
        length = len(abbrv_list)-1
        
        sent = ' '

        for i  in range(length):
           sent += abbrv_dict[abbrv_list[i]]

        sent += ("and " + abbrv_dict[length+1])

        return sent


    def to_standard(military_string):
        '''to_standard: converts military time to standard and adds meridean'''

        military_list = military_string.split(':')
        if int(military_list[0]) > 12:
            return str( int(military_list[0])-12 ) + ':' + military_list[1] + " P.M."
        else:
            return str( int(military_list[0]) ) + ':' + military_list[1] + " A.M."

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
    try:
        recurrence = event[recurrence]
        recurrence = parse_recurrance(recurrence)
        print(recurrence)
    except:
        recurrence = None

    location = event.get('location')
    text = event.get('description')
    event_date = event['start'].get('dateTime')
    event_time = event['start'].get('date')

    #if block which replaces the default values with empty strings

    if text is None:
        text = ''

    if title is None:
        title = ''

    if location is None:
        location = '1515 Ocean St, Santa Cruz, CA 95060'

    if text is None:
        text = ''

    if recurrence is None:
        recurrence = ''

    if event_time is None:
        event_time = ''
    elif '-' in event_time:
        ed_list = event_time.split('-')
        ed_list[2] = ed_list[2].split('T')[0] 
        event_time = calendar.month_name[int(ed_list[1])] + ' , ' + ed_list[2] + ' , ' + ed_list[0]
    elif ':' in event_time:
        event_time = to_standard(event_time) 

    # ^ ^ this requires explanation. some people think its fun to enter
    #the time as the date or the date as the time. this is to fix monkey
    #problems.

    if event_date is None:
        event_date = ''
    else:
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








