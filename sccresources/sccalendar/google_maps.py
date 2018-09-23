from .google_calendar import GoogleEvent
import googlemaps
import json

"""
Package for interacting with the google maps API and google calendar events
"""


class GoogleDistanceEvent(GoogleEvent):
    """
    Extention of a GoogleEvent that includes a distance.
    """

    def __init__(self, event, distance, distance_text, defaults=dict()):
        super().__init__(event, **defaults)
        self.distance = distance
        self.distance_text = distance_text

    @classmethod
    def from_google_event(cls, google_event, distance, distance_text):
        """
        Constructs a new instance of GoogleDistanceEvent given a GoogleEvent and distance paramters
        """
        return cls(google_event._event, distance, distance_text,
                   defaults=google_event._defaults)

    @classmethod
    def from_event_and_api(cls, google_event, element):
        """
        Constructs a new instance of GoogleDistanceEvent given a GoogleEvent
        and an element from the Distance Matrix API
        """
        return cls.from_google_event(
            google_event,
            element['distance']['value'],
            element['distance']['text'])


class GoogleMaps:
    """
    Represents a connection to the google calendar API.

    Properties:
    service: Calendar connection object used to request maps data
    """

    def __init__(self, key: str) -> None:
        """
        Creates new GoogleMaps object
        :param key: The google maps API key that provides access to the full suite of APIs
        """
        self.service = googlemaps.Client(key=key)

    def get_distance(self, **api_params):
        """
        Returns a dict with an int value, a text value, and a success code - 'OK' or None
        :param api_params: a list of parameters to be passed to the gmaps API
        :return {'distance_value': int, 'distance_text': string, 'Success': string}
        """
        # Make the request with the given parameters and convert it to JSON
        resp = json.loads(json.dumps(self.service.distance_matrix(**api_params)))
        # Ensure that the distance request was successful
        if resp['rows'][0]['elements'][0]['status'] == 'OK':
            distance_value = resp['rows'][0]['elements'][0]['distance']['value']
            distance_text = resp['rows'][0]['elements'][0]['distance']['text']
            return {'distance_value': distance_value,
                    'distance_text': distance_text, 'Success': 'OK'}
        else:
            return {'distance_value': None,
                    'distance_text': None, 'Success': None}

    def convert_events(self, origin, events_list):
        """
        Converts a list of GoogleEvents to GoogleDistanceEvents, given a single origin.

        Raises an IOError when the API returns a non-OK status
        """
        if not events_list:
            return None
        if not origin:
            return events_list
        resp = json.loads(json.dumps(self.service.distance_matrix(
            origins=[origin], destinations=[str(e.location) for e in events_list], units='imperial'
        )))

        # TODO: Might be a good idea to add a little bit more specific error
        # handling
        if not resp['status'] == "OK":
            print('Recieved error from Google Distance Matrix API: ' + resp['status'])
            raise IOError('Recieved error from Goole Distance Matrix API: ' + resp['status'])

        elements = resp['rows'][0]['elements']

        # Error-checking
        for index, element in enumerate(elements):
            if element['status'] == "NOT_FOUND":
                elements[index] = {'distance': {'value': None, 'text': None}}
            elif element['status'] != "OK":
                raise IOError('Recieved elements error from Googe Distance Matrix API: ' + elements['status'])

        # First, combine the list of events and list of elements into a single list of ordered pairs
        # Then, map over this list with GoogleDistanceEvent.from_event_and_api
        # This creates a new list of GoogleDistanceEvents that we return
        return [GoogleDistanceEvent.from_event_and_api(*e) for e in zip(events_list, elements)]
