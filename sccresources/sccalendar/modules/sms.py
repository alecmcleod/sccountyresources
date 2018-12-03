from background_task import background
from pyrfc3339 import parse
from .. import models
from .. import google_credentials_auth
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from twilio.rest import Client


"""
Author: Paul May
Date: June , 4th, 2018

Purpose:
this class is a singular object that will be created on launch
and shared between all modules. it is used to send sms notifications
and reminders to users and provides a quick list of commands for
developers.


Note:

background functions declared like this

@background(schedule=5) #5 seconds
def start_schedule_thread():

process_tasks must be running for them to send actual messages

"""


TWILIO_ACCOUNT = 'AC64cd9b460c90133128a027a0321a4d40'
TWILIO_AUTH = '8954f49f28bac7223d76ddf9da56b177'
TWILIO_SERVICE_NUMBER = "+19252394858"

client = Client(TWILIO_ACCOUNT,
                TWILIO_AUTH)

"""
error classes
"""


class LessThanHour(Exception):
    def __init__(self):
        self.error_text = 'LessThanHour Exception: event occurs in less than an hour.'
        print(self.error_text)

    def __str__(self):
        return repr(self.error_text)


class AlreadySubscribed(Exception):
    def __init__(self):
        self.error_text = 'User is already subscribed.'
        print(self.error_text)

    def __str__(self):
        return repr(self.error_text)


class NullSubscriptionArgument(Exception):
    def __init__(self):
        self.error_text = 'One or more of the the argument in add_reminder is null.'
        print(self.error_text)

    def __str__(self):
        return repr(self.error_text)


def add_reminder(event_id, cal_id, date, time, rrule, title, phone_number):   # noqa: C901
    """
    input:
            many arguments to reduce the api tax

            output: none

            result: adds a phone number to an event in the database
                            if it does not already exist. if it does, do nothing.
                            if an event does not already exists. one is scheduled

    """
    rrule = ' ' if not rrule else rrule
    for i in [event_id, cal_id, date, time, rrule, title, phone_number]:
        if not i:
            raise NullSubscriptionArgument

    date = datetime.strptime(date, '%Y-%m-%d').date()
    time = datetime.strptime(time, '%H:%M:%S').time()
    iso = datetime.combine(date, time).isoformat()
    py_dt = datetime.combine(date, time)

    try:
        event = models.Event.objects.get(event_id=event_id, calendar_id=cal_id,
                                         iso_date_time=iso)
    except ObjectDoesNotExist:
        event = None

    if not event:

        event = models.Event(event_id=event_id, calendar_id=cal_id,
                             iso_date_time=iso)

        seconds = one_hour_before(py_dt)

        if seconds <= 3600:
            seconds = 1

        print('scheduling new event in ', seconds, ' seconds')
        __remind(event_id, cal_id, iso, title, schedule=seconds - 3600)
        event.save()

        if seconds <= 3600:
            return 'LTHE'
        else:
            return 'GOOD'

    else:

        new_number = models.Number(event=event, number=phone_number)

        try:
            numbers = models.Number.objects.filter(event=event)
            number_set = [i.number for i in numbers]
            print(number_set)
            if new_number.number not in number_set:
                seconds = one_hour_before(py_dt)
                if seconds <= 3600:
                    return 'LTHE'
                else:
                    return 'GOOD'
            else:
                raise AlreadySubscribed
        except AlreadySubscribed:  # data base misses.
            raise AlreadySubscribed


# this function is called by the verification page and adds a new
# phone number to an even that is about to be called
def call_remind(event_id, cal_id, iso_date_time, number):

    event = models.Event.objects.get(event_id=event_id, calendar_id=cal_id,
                                     iso_date_time=iso_date_time)

    new_number = models.Number(event=event, number=number)

    new_number.save()


def send_sms(number, body):
    client.messages.create(to=number,
                           from_=TWILIO_SERVICE_NUMBER, body=body)


def del_reminder(event, phone_number):
    """
    removes phone number from one event

    """
    # nums = models.Number.objects.filter(event=event, number=phone_number).delete()


def unsubscribe(phone_number):
    """
    deletes phone number from all events in dict

    """
    event_numbers = models.Number.objects.filter(number=phone_number)
    for i in event_numbers:
        i.delete()


def one_hour_before(datetime_obj):
    """ input: datetime.datetime object
            output: the number of seconds till one hour before then
            if it is past then return none
    """
    now = datetime.now()

    seconds = (datetime_obj - now).total_seconds()

    return int(seconds)


@background
def __remind(event_id, cal_id, iso_date_time, title):
    """
    - remind the user a default of an hour before the event
    - if the event recurs then call __remind.

    # gonna wait to impliment that one until recurrence returns anything

    """
    try:
        event = models.Event.objects.get(
            event_id=event_id,
            calendar_id=cal_id,
            iso_date_time=iso_date_time)
        print('reminding event:', event)
        numbers_list = models.Number.objects.filter(event=event)
        print('numbers found:', numbers_list)

        description = 'This is a reminder that ' + title +\
            ' occurs within the next hour, from Santa Cruz County Resource Center.\n \n \
                   if you would like to cancel all notifications, text back CANCEL .\n '

        for i in numbers_list:
            send_sms(i.number, description)

        now = datetime.now()

        google_now = now.isoformat('T') + 'Z'
        # get next instance
        events = google_credentials_auth.service.events().instances(eventId=event_id, calendarId=cal_id,
                                                                    maxResults=5, timeMin=google_now).execute()

        if len(events['items']) > 1:

            next_event = events['items'][1]
            try:
                time = next_event["start"]["dateTime"]
                time = parse(time)
                time = time.replace(tzinfo=None)
                print(time)
            except KeyError:
                # its all day
                date = datetime.strptime(
                    next_event['start']['date'], '%Y-%m-%d').date()
                time = datetime.strptime('08:00:00', '%H:%M:%S').time()
                time = datetime.combine(date, time)

            seconds = one_hour_before(time)

            print('scheduling new event in ', seconds, ' seconds')

            __remind(event_id, cal_id, iso_date_time, title, schedule=seconds)

        else:
            event.delete()

    except ObjectDoesNotExist:
        print('no event or no number, no reminder sent')
