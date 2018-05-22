
import twilio
from .. import models
from .. import google_auth
from datetime import datetime, time, timedelta

"""
Purpose:
this class is a singular object that will be created on launch
and shared between all modules. it is used to send sms notifications
and reminders to users and provides a quick list of commands for 
developers.


##TO DO##

sleep time calculations for schedule

make remind reset on recurrence.

put the phone numbers in a db refference 

test

"""
##FOR FUTURE: make it check for the existence of a pickle
##in modules before building event dict such that there is
##some kind of memory.

# google time format 2018-05-16T10:30:00-07:00
# need to convert to military

'''
sms_service.event_dict:

	- a dictionary object containing phone numbers (sensitive) in a list
	for each person who rsvp'd for a particular event ID.

	-the event dict is saved as a pickle on shut down. 
'''

'''
sms_service.auth:

	- a tuple which contains the authorization in (account,token) order
'''



def add_reminder(event_id,cal_id,date,time,rrule,phone_number): 

	'''input: 
		
		many arguments to reduce the api tax

		output: none

		result: adds a phone number to an event in the database
				if it does not already exist. if it does, do nothing.
				if an event does not already exists. one is scheduled

	'''

	if date and time:
		iso = datetime.combine(date,time).isoformat()
	else:
		iso = datetime.combine(date, datetime.datetime.time(8) ).isoformat()

		#iso = tomorrow at 8am and set some flag for the twilio message

	try:
		event = models.Event.objects.get(event_id=event_id, calendar_id = cal_id , \
										 iso_date_time=iso)
		print('event:',event)
	except:
		event = None
		print('no event returned, adding new')

	try:
		numbers = models.Number.objects.filter(event=event)
		print(numbers)
	except:
		print('no number list returned')

	if not event:

		event = models.Event(event_id=event_id, calendar_id=cal_id, \
							 iso_date_time=iso)
		event.save()

		new_number = models.Number(event=event,number=phone_number)
		new_number.save()

		#schedule event in chron

		return
	else:
		new_number = models.Number(event=event,number=phone_number)

	try:
		numbers = models.Number.objects.filter(event=event)
		number_set = [i.number for i in numbers]
		print('event:',event)
		if new_number.number not in number_set:
			new_number.save()
			print('added new number')
		else:
			print('redundant number')
	except:
		print('tried to add new number, failed')


	#example call

	#sms.add_reminder(event_id, service , event.start_datetime.date() \
                    #,event.start_datetime.time(), event.reccurence, '+15104576818')




def schedule(event_id,recurrence):
	'''
	edits the  scheduler object and adds event at the date and time

	if the time has already passed it does nothing.
	'''


	if event_dict[event]['event time'] is None:
		#did this event have no date listed (then it had to be today. with current view)
		# not time means schedule at 8am
		if event_dict[event_dict]['try'] is None:
			print('this event has no labeled time no, reminding people at 8am anyways , jesus.')
		else:
			time = event_dict[event_dict]['try']
			now = datetime.datetime.now().time
			# is it past 8 am?
			if now.hour >= 8:
				#compute difference in seconds
				#TO DO:
				time_to_launch = ((360)+(60)+(1))

				t = Timer(time_to_launch, __remind , event)
				t.start()
			else:
				__remind(event)
			# no: schedule for 8, yes: remind now

	else:
		l = 0
		#split into time date
		#sleep time = 360 * hours dif + 60 * minutes dif + secs dif
		#if sleep time is negative do nothing.
		#otherwise remind schedule a remind at sleep time. 


		
		# if it is past 8am do

	#sleep time in seconds

	t = Timer(sleep_time, __remind , event)
	t.start()

	#schedule the event with a threaded timer


def del_reminder(event,phone_number):

	'''
	removes phone number from one event

	'''
	event_dict[event]['contact list'].remove(phone_number)

def unsubscribe(phone_number):

	'''
	deletes phone number from all events in dict

	'''
	for i in event_dict.items:
		i['contact list'].remove(phone_number)



def __remind(event_id):
	'''
	- if the event has no time default 8am
	- if the event has a time remind the user a default of an hour before

	'''

	occur = ' occurs today' if this.event_dict[event_id]['start time'] is None else ' occurs in an hour'

	description = 'This is a reminder that ' + event.get('summary') + occur + ',from Santa Cruz County Resource Center \n \
				 \n if you would like to cancel notifications for this event , text back CANCEL . if you would like to cancel \
				 	 all notifications , text back ALL . '

	recurrence = this.event_dictp[event_id]['recurrence']

	for i in this.event_dict[event]['contact list']:
		twilio_service.messages.create(to="+15104576818"+i, from_="+19252394858",body=description)

def test():
	'''
	test function for  development
	'''








