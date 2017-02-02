from stravalib.client import Client
import requests


TOKEN_EX_URL = "https://www.strava.com/oauth/token"
CLIENT_ID = 15675
CLIENT_SECRET = 'ada13b288862d04f79f6686f84d1ef3127cda3ef'  # ada13b288862d04f79f6686f84d1ef3127cda3ef
ACCESS_CODE = 'a3a8949b2223530ace053f9167ad99304d6f2ff9'  # a3a8949b2223530ace053f9167ad99304d6f2ff9
REDIRECT_URI = 'http://127.0.0.1:8000/'


client = Client()
authorize_url = client.authorization_url(client_id=CLIENT_ID, redirect_uri=REDIRECT_URI)

payload = {'client_id': 'CLIENT_ID', 'client_secret': 'CLIENT_SECRET', 'code': 'ACCESS_CODE'}
re = requests.get(TOKEN_EX_URL, params=payload)
jo = re.json()

first_name = jo['firstname']
last_name = jo['lastname']
profile_picture = jo['profile']

'''
class User:
    first_name = jo['firstname']
    last_name = jo['lastname']
    profile_picture = jo['profile']

    def __str__(self):
        return self.first_name + ' ' + self.last_name
'''