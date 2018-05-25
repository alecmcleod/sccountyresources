"""
Package for working with Google Calendar and iCal
"""
from . import google_auth
from .utils import parse_recurrence
from datetime import datetime
from typing import Generator
from icalendar import Calendar, Event
from googleapiclient.discovery import Resource
from pyrfc3339 import parse

class GoogleEvent():
    """
    Represents an event on a google calendar

    Properties:
    id - String representing the event id
    summary - String containting the summary of the event (title)
    location - A string containing the location of the event
    description - A string containing the description of the event
    start_datetime - A datetime object containing the start date and time of the event
    end_datetime - A datetime object containing the end date and time of the event
    reccurence - A textual representation of the days the event reccurers on.
    """
    def __init__(self, 
                event,
                default_summary = None, 
                default_location = None, 
                default_description = None,
                default_reccurence = None):
        self._event = event

        self.id = event.get("id")
        self.summary = event.get("summary", default_summary)
        self.location = event.get("location", default_location)
        self.description = event.get("description", default_description)

        try:
            # Try to parse the datetime like a normal event
            self.start_datetime = parse(event["start"]["dateTime"])
            self.end_datetime = parse(event["end"]["dateTime"])
        except KeyError:
            # If a datetime doesn't exist, then it's likely an all-day event
            # According to the google api, date is in the format "yyyy-mm-dd"
            self.start_datetime = datetime(*event["start"]["date"].split("-", 2), 0, 0, 0)
            self.end_datetime = datetime(*event["end"]["date"].split("-", 2), 23, 59, 59)
            self._allday = True
            
        try:
            self.reccurence = parse_recurrence(event["reccurence"])
        except KeyError:
            self.reccurence = default_reccurence
    
    def __repr__(self):
        return f"GoogleEvent(id: {self.id} summary:{self.summary} location:{self.location} description:{self.description} start_datetime:{self.start_datetime} end_datetime:{self.end_datetime} reccurence:{self.reccurence})"

    @property
    def is_allday(self) -> bool:
        """
        Returns true if the event is an all-day event
        """
        return self._allday

    def to_ical_event(self) -> Event:
        """
        Returns this event as an iCalendar Event object
        """
        event = Event()
        event.add("uid",            self._event["iCalUID"])
        event.add("summary",        self.summary)
        event.add("location",       self.location)
        event.add("description",    self.description)
        event.add("dtstart",        self.start_datetime)
        event.add("dtend",          self.end_datetime)
        return event

    def to_ical(self) -> Calendar:
        """
        Returns this event as an iCalendar Calendar object
        """
        cal = Calendar()
        cal.add_component(self.to_ical_event())
        return cal

class GoogleCalendar:
    """
    Represents a connection to a Google Calendar.

    Properties:
    service - The service object returned by google_auth.py associated with with this calendar.
    calendar_id - A string representing the Google Calendar ID
    summary - A string represeting the summary for the calendar as returned by the Google Calendar API
    description - A string representing the description for the calendar as returned by the Google Calendar API
    time_zone - A string represeting the timezone of the calendar as returned by the Google Calendar API
    location - A string represeting the location of the calendar as returned by the Google Calendar API
    """
    def __init__(self, service: Resource, calendar_id: str):
        """
        Creates a new GoogleCalendar object.

        Params:
        service - service object returned by google_auth.py
        calendar_id - A string representing the Google Calendar ID
        """
        self.service = service
        self.calendar_id = calendar_id

        meta = service.calendars().get(calendarId=self.calendar_id).execute()
        self.summary = meta.get("summary")
        self.description = meta.get("description")
        self.time_zone = meta.get("timeZome")
        self.location = meta.get("location")

    def __repr__(self):
        return "GoogleCalendar(" + self.service + ", " + self.calendar_id + ")"
    
    def get_event(self, event_id, api_params=dict(), google_event_params=dict()) -> GoogleEvent:
        """
        Returns an event by it's id.

        Params:
        event_id - A string containing the id of the event
        api_params - A dict containing paramters to pass to the Google Calendar API
        google_event_params - Optional paramters to pass to the GoogleEvent object
        """
        event = self.service.events().get(calendarId=self.calendar_id, eventId=event_id, **api_params).execute()
        return GoogleEvent(event, **google_event_params)

    def get_raw_events(self, api_params=dict()) -> Generator[dict, None, None]:
        """
        Returns a generator that can be used to iterate over all the events in the calendar.
        Events are returned as-is from the API.
        """
        resp = self.service.events().list(calendarId=self.calendar_id, **api_params).execute()
        while True:
            for event in resp["items"]:
                yield event

            # Break condition
            if not resp.get("nextPageToken"):
                raise StopIteration()
            else:
                resp = self.service.events().list(calendarId=self.calendar_id, pageToken=resp["nextPageToken"], **api_params).execute()

    def export_ical(self, **api_params) -> Calendar:
        """
        Returns a calendar object from the icalendar package containing the events listed in the Google Calendar.
        """
        cal = Calendar()
        cal["summary"] = self.summary
        cal["description"] = self.description

        for event in self.get_raw_events(**api_params):
            i_event = Event()
            i_event.add("summary",      event["summary"])
            i_event.add("description",  event.get("description"))
            i_event.add("uid",          event["iCalUID"])
            i_event.add("dtstart",      parse(event["start"]["dateTime"]))
            i_event.add("dtend",        parse(event["end"]["dateTime"]))
            
            if event.get("reccurence"):
                i_event.add("sequence", event["sequence"])
                for i in event.get("reccurence"):
                    prop_name, v = i.split(":", max_split=1)
                    i_event[prop_name] = v

            cal.add_component(i_event)
        
        return cal