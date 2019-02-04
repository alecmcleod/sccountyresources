import tempfile
import os
import unittest

from .google_calendar import GoogleCalendar, GoogleEvent
from .utils import to_sent

from .google_credentials_auth import get_service
from django.test import TestCase


# FIXME: make this calendar public so that the tests can run
@unittest.skip("These tests depend on a currently inaccessible calendar")
class GoogleCalendarTestCase(TestCase):
    def setUp(self):
        self.service = get_service()
        self.calendar_id = "ucsc.edu_gn5gb46mq2mt6961h0g3jifakg@group.calendar.google.com"
        self.calendar = GoogleCalendar(self.service, self.calendar_id)
        self.expected = [
            {"summary": "TEST",
             "id": "10jn9doq1n2ckmth1b9ber7nk6",
             "start": {'dateTime': '2018-04-25T14:30:00-07:00'},
             "end": {'dateTime': '2018-04-25T15:30:00-07:00'}},
            {"summary": "TEST2",
             "id": "5tlt87hjb3hh6b7kaka1qv03jl",
             "start": {'dateTime': '2018-04-26T18:00:00-07:00'},
             "end": {'dateTime': '2018-04-26T19:00:00-07:00'}},
            {"summary": "TEST3",
             "id": "0gh0be37tqvganj9bgcudqp2ur",
             "start": {'dateTime': '2018-04-27T14:30:00-07:00'},
             "end": {'dateTime': '2018-04-27T15:30:00-07:00'}},
            {"summary": "TEST4",
             "id": "6eccmdp589r987pgc9c8kpf8kl",
             "start": {'dateTime': '2018-04-28T19:30:00-07:00'},
             "end": {'dateTime': '2018-04-28T20:30:00-07:00'}}
        ]

    def test_get_raw_events(self):
        """
        Tests the get_raw_events function in the GoogleCalendar class.
        """
        actual = list(self.calendar.get_raw_events(api_params={"singleEvents": True, 'orderBy': "startTime"}))

        # Ensure the quantity of items in actual match that of expected
        self.assertEqual(len(actual), len(self.expected))

        for a, e in zip(actual, self.expected):
            # Assert that e is a subset of a
            assert e.items() <= a.items()

    def test_get_events(self):
        """
        Tests the get_events method in the Googleget?authuser=1get?authuser=1get?authuser=1Calendar class.
        """
        actual = list(self.calendar.get_events(api_params={"singleEvents": True, 'orderBy': "startTime"}))
        expected = [GoogleEvent(e) for e in self.expected]

        for a, e in zip(actual, expected):
            self.assertEqual(a.summary, e.summary)
            self.assertEqual(a.id, e.id)
            self.assertEqual(a.start_datetime, e.start_datetime)

    def test_export_calendar(self):
        """
        Tests the export_ical function in the GoogleCalendar class. Since it's hard to test
        if the ical file produced is correct, this test case produces an ical file to open in
        an ical client.
        """
        c = GoogleCalendar(self.service, self.calendar_id)
        ical = c.export_ical()

        # Sanity Check
        assert len(ical.subcomponents) == 4

        # Export the calendar as a file
        directory = tempfile.mkdtemp()
        path = os.path.join(directory, 'artifact.ics')
        f = open(path, 'wb')
        f.write(ical.to_ical())
        f.close()
        print("Created test artifact " + path)


class ViewsTestCase(TestCase):
    def setUp(self):
        # This doesn't need module-level scope.
        from .views import var_map
        self.services = list(var_map.keys())

    """
    Test case for the web views.
    """

    def test_index_expecting_200(self):
        """
        Simple test of the static index page
        """
        response = self.client.get("/calendar/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response=response, template_name="index.html")

    def test_calendars_expecting_200(self):
        """
        Simple test of the static calendars page.
        """
        response = self.client.get("/calendar/calendars/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response=response, template_name="calendars.html")

    def test_search_given_correct_params_expecting_200(self):
        """
        Test each one of the 4 calendars with the search page. Confirming that the webpage
        returns 200, and the correct template for each one.
        """
        for service in self.services:
            response = self.client.get("/calendar/search/day/",
                                       data={"services": service, "locations": "1515 Ocean St, Santa Cruz, CA 95060"})
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(
                response=response,
                template_name="search.html")

    def test_search_given_incorrect_service_expecting_404(self):
        """
        If an invalid service for the search page is given, then we should 404.
        """
        response = self.client.get(
            "/calendar/search/day/",
            data={
                "services": "this doesn't exist",
                "locations": "1515 Ocean St, Santa Cruz, CA 95060"})

        self.assertEqual(response.status_code, 404)

    def test_search_given_no_location_expecting_200(self):
        """
        If no location for the search page is given, search should still work
        """
        for service in self.services:
            response = self.client.get("/calendar/search/day/", data={"services": service})
            self.assertEqual(response.status_code, 200)

    def test_search_given_empty_location_expecting_200(self):
        """
        Similar to  `test_search_given_no_location_expecting_200` except with the
        empty string.
        """
        for service in self.services:
            response = self.client.get("/calendar/search/day/", data={"services": service, "locations": ""})
            self.assertEqual(response.status_code, 200)

    def test_search_given_invalid_location_expecting_200(self):
        for service in self.services:
            response = self.client.get("/calendar/search/day/", data={"services": service, "locations": "Invalid"})
            self.assertEqual(response.status_code, 200)

    def test_details_expecting_200(self):
        """
        Basic test of the details page. Ensures that urls are configured properly, and that
        given the correct paramters, it returns a 200 and the correct template.
        """
        response = self.client.get(
            "/calendar/details/FOOD/1ga6tvbtov1uqeikpol7qal2ni_20190203T183000Z/?locations=")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response=response, template_name="details.html")

    def test_details_invalid_service_expecting_404(self):
        """
        Tests to make sure the details view returns a 404 on an invalid service.
        """
        response = self.client.get(
            "/calendar/details/this doens't exist/5tmc6k935cb5jmmqmnub4lhjjk_20180606T000000Z/")

        self.assertEqual(response.status_code, 404)

    def test_details_invalid_id_expecting_404(self):
        """
        Tests to make sure the details view returns a 404 on an invalid id.
        """
        response = self.client.get("/calendar/details/FOOD/aaaaaaaaaa/")

        self.assertEqual(response.status_code, 404)

    def test_download_full_calendar_expecting_200(self):
        for service in self.services:
            response = self.client.get(f"/calendar/download/calendar/{service}/")

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["Content-Disposition"], "attachment; filename=calendar.ics")

class UtilsTestCase(TestCase):
    def test_to_sent(self):
        actual = to_sent("MO,TU,WE,TH,FR,SA,SU")
        expected = "Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, and Sunday"

        self.assertEqual(actual, expected)
