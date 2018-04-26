"""
Package for working with Google Calendar and iCal
"""
from . import google_auth
from typing import Generator
from icalendar import Calendar, Event
from googleapiclient.discovery import Resource

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
    
    def get_events(self, **api_params) -> Generator[dict, None, None]:
        """
        Returns a generator that can be used to iterate over all the events in the calendar.
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

        for event in self.get_events(**api_params):
            i_event = Event()
            i_event.add("summary",      event["summary"])
            i_event.add("description",  event.get("description"))
            i_event.add("uid",          event["iCalUID"])
            i_event.add("dtstart",      event["start"]["dateTime"])
            i_event.add("dtend",        event["end"]["dateTime"])
            
            if event.get("reccurence"):
                i_event.add("sequence", event["sequence"])
                for i in event.get("reccurence"):
                    prop_name, v = i.split(":", max_split=1)
                    i_event[prop_name] = v

            cal.add_component(event)
        
        return cal