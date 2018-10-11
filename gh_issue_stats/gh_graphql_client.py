import requests
import sys


class GhGraphQlClient:
    def __init__(self, token, api_endpoint):
        self.token = token
        self.api_endpoint = api_endpoint
        self._create_session()

    def _create_session(self):
        self.session = requests.Session()
        self.session.headers['Authorization'] = f'token {self.token}'

    def run_query(self, query):
        res = self.session.post(self.api_endpoint, json={'query': query})
        data = res.json()
        try:
            return data['data']['search']
        except Exception:
            sys.exit('There was a problem retrieving the data. Please ensure that the login information is correct.')
