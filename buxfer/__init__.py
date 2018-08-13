import requests


API_BASE_URL='https://www.buxfer.com/api'


class Client:
    def __init__(self, api_base_url=API_BASE_URL, username=None, password=None):
        self._api_base_url = api_base_url
        self._username = username
        self._password = password
        self._token = None

    def login(self):
        response = requests.get('{}/login'.format(self._api_base_url),
                                params={'userid': self._username,
                                        'password': self._password})
        response.raise_for_status()
        response_json = response.json()
        self._token = response_json['response']['token']

    def upload_statement(self, account_id, statement):
        response = requests.post('{}/upload_statement'.format(self._api_base_url, self._token),
                                 data={
                                     'token': self._token,
                                     'accountId': account_id,
                                     'statement': statement,
                                 })
        response.raise_for_status()
        response_json = response.json()
        return response_json['response']
