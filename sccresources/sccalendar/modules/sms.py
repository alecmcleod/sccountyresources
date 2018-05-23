from background_task import background
from .. import models
from .. import google_auth
from datetime import datetime, time, timedelta
from twilio.rest import Client


"""
Purpose:
this class is a singular object that will be created on launch
and shared between all modules. it is used to send sms notifications
and reminders to users and provides a quick list of commands for 
developers.

##TO DO##

#this will not work

make remind reset on recurrence.

Note:

background functions declared like this

@background(schedule=5)
def start_schedule_thread():
"""


client = Client('AC64cd9b460c90133128a027a0321a4d40',\
				'8954f49f28bac7223d76ddf9da56b177')


def add_reminder(event_id,cal_id,date,time,rrule,title,phone_number): 

	'''input: 
		
		many arguments to reduce the api tax

		output: none

		result: adds a phone number to an event in the database
				if it does not already exist. if it does, do nothing.
				if an event does not already exists. one is scheduled

	'''
	iso = datetime.combine(date,time).isoformat()
	py_dt = datetime.combine(date,time)

	try:
		event = models.Event.objects.get(event_id=event_id, calendar_id = cal_id , \
										 iso_date_time=iso)
	except:
		event = None


	try:
		numbers = models.Number.objects.filter(event=event)

	except:
		numbers = None


	if not event:

		event = models.Event(event_id=event_id, calendar_id=cal_id, \
							 iso_date_time=iso)
		event.save()

		new_number = models.Number(event=event,number=phone_number)
		
		new_number.save()

		seconds = one_hour_before(py_dt)

		if seconds:
			__remind(event_id,cal_id,title,duration=seconds)
		else:
			print("would add to next recurrent event but recurrence codes don't exist")

		return

	else:

		new_number = models.Number(event=event,number=phone_number)

	try:
		
		numbers = models.Number.objects.filter(event=event)
		number_set = [i.number for i in numbers]
		
		if new_number.number not in number_set:
			new_number.save()

	except:
		
		print('tried to add new number, failed')


def del_reminder(event,phone_number):

	'''
	removes phone number from one event

	'''
	models.Number.objects.get(event=event,number=phone_number).delete()


def unsubscribe(phone_number):

	'''
	deletes phone number from all events in dict

	'''
	event_numbers = models.Number.objects.filter(number=phone_number)
	for i in event_numbers:
		i.delete()

def one_hour_before(datetime_obj):
	''' input: datetime.datetime object
		output: the number of seconds till one hour before then
		if it is past then return none
	'''
	now = datetime.datetime.now()
	
	seconds = (datetime_obj-now).total_seconds()

	if seconds < 3600:
		return None
	else:
		return seconds 

@background
def __remind(event_id,cal_id,title):
	'''
	- remind the user a default of an hour before the event
	- if the event recurs then call __remind.

	# gonna wait to impliment that one until recurrence returns anything

	'''
	try:
		event = models.Event.objects.get(event_id=event_id)
		print('reminding event:',event)
		numbers_list = models.Number.objects.filter(event=event)
		print('numbers found:', numbers_list)


		description = 'This is a reminder that ' + event.get('summary') \
		 + occur + ',from Santa Cruz County Resource Center. \n \n \
		 if you would like to cancel notifications for this event ,\
		 text back CANCEL . if you would like to cancel all notifications , text back ALL . '

		for i in numbers_list:
			twilio_service.messages.create(to=i.number, from_="+19252394858",body=description)
	except:
		print('no event or no number, no reminder sent')










