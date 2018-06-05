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

    def test_get_raw_events(self):
        c = GoogleCalendar(self.service, self.calendar_id)

        actual = list(c.get_raw_events(api_params={"singleEvents": True, 'orderBy': "startTime"}))

        self.assertEqual("TEST", actual[0]["summary"])
        self.assertEqual("TEST2", actual[1]["summary"])  
        self.assertEqual("TEST3", actual[2]["summary"])  
        self.assertEqual("Fuck", actual[3]["summary"])   
        self.assertEqual("TEST4", actual[4]["summary"])

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
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response=response, template_name="index.html")
    
    def test_calendars_expecting_200(self):
        """
        Simple test of the static calendars page.
        """
        response = self.client.get("/calendars/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response=response, template_name="calendars.html")
    
    def test_search_given_correct_params_expecting_200(self):
        """
        Test each one of the 4 calendars with the search page. Confirming that the webpage
        returns 200, and the correct template for each one.
        """
        for service in self.services:
            response = self.client.get("/search/", data={"services": service, "locations": "1515 Ocean St, Santa Cruz, CA 95060"})
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response=response, template_name="search.html")
    
    def test_search_given_incorrect_service_expecting_404(self):
        """
        If an invalid service for the search page is given, then we should 404.
        """
        response = self.client.get("/search/", data={"services": "this doesn't exist", "locations": "1515 Ocean St, Santa Cruz, CA 95060"})

        self.assertEqual(response.status_code, 404)

    def test_search_given_no_location_expecing_400(self):
        """
        If no location for the search page is given, then 400.
        """
        for service in self.services:
            response = self.client.get("/search/", data={"services": service, "locations": None})
            self.assertEqual(response.status_code, 400)

    def test_details_expecting_200(self):
        """
        Basic test of the details page. Ensures that urls are configured properly, and that
        given the correct paramters, it returns a 200 and the correct template.
        """
        response = self.client.get("/details/FOOD/5tmc6k935cb5jmmqmnub4lhjjk_20180606T000000Z/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response=response, template_name="details.html")

    def test_details_invalid_service_expecting_404(self):
        """
        Tests to make sure the details view returns a 404 on an invalid service.
        """
        response = self.client.get("/details/this doens't exist/5tmc6k935cb5jmmqmnub4lhjjk_20180606T000000Z/")

        self.assertEqual(response.status_code, 404)

    def test_details_invalid_id_expecting_404(self):
        """
        Tests to make sure the details view returns a 404 on an invalid id.
        """
        response = self.client.get("/details/FOOD/aaaaaaaaaa")

        self.assertEqual(response.status_code, 404)
    
    def test_download_full_calendar_expecting_200(self):
        for service in self.services:
            response = self.client.get(f"/download/calendar/{service}/")

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Content-Disposition", "attachment; filename=calendar.ics")

class UtilsTestCase(TestCase):
    def test_to_sent(self):
        actual = to_sent("MO,TU,WE,TH,FR,SA,SU")
        expected = "Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, and Sunday"

        self.assertEqual(actual, expected)