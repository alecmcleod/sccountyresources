import tempfile
import os
from sys import platform

from .google_calendar import GoogleCalendar
from .utils import to_sent

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

        # Sanity Check
        self.assertEqual(len(ical.subcomponents), 5)
        
        # Export the calendar as a file
        directory = tempfile.mkdtemp()
        path = os.path.join(directory, 'artifact.ics')
        f = open(path, 'wb')
        f.write(ical.to_ical())
        f.close()
        print("Created test artifact " + path)


class UtilsTestCase(TestCase):
    def test_to_sent(self):
        actual = to_sent("MO,TU,WE,TH,FR,SA,SU")
        expected = "Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, and Sunday"

        self.assertEqual(actual, expected)