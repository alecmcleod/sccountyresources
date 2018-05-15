from .calendar import GoogleCalendar
from .google_auth import get_service

from django.test import TestCase
# Create your tests here.
class GoogleCalendarTestCase(TestCase):
    def setUp(self):
        self.service = get_service()
        self.calendar_id = "ucsc.edu_gn5gb46mq2mt6961h0g3jifakg@group.calendar.google.com"

    def test_export_calendar(self):
        c = GoogleCalendar(self.service, self.calendar_id)
        ical = c.export_ical()

        self.assertEquals(len(ical.subcomponents), 5)