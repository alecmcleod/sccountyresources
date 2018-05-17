import googlemaps
import json

"""
Package for interacting with the google maps API and google calendar events
"""
class GoogleMaps:
    """
    Represents a connection to the google calendar API.

    Properties:
    service: Calendar connection object used to request maps data
    """
    def __init__(self, key: str):
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
            return {'distance_value': distance_value, 'distance_text': distance_text, 'Success': 'OK'}
        else:
            return {'distance_value': None, 'distance_text': None, 'Success': None}


