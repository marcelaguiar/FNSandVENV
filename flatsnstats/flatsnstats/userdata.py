from stravalib.client import Client
import requests


TOKEN_EX_URL = "https://www.strava.com/oauth/token"
CLIENT_ID = 15675
CLIENT_SECRET = ''  # ada13b288862d04f79f6686f84d1ef3127cda3ef
ACCESS_CODE = ''
REDIRECT_URI = 'http://127.0.0.1:8000/'


client = Client()
authorize_url = client.authorization_url(client_id=CLIENT_ID, redirect_uri=REDIRECT_URI)

payload = {'client_id': 'CLIENT_ID', 'client_secret': 'CLIENT_SECRET', 'code': 'ACCESS_CODE'}
r = requests.get(TOKEN_EX_URL, params=payload)


class User:
    first_name = r.json()
    last_name = "Aguiar"
    profile_picture = "https://dgalywyr863hv.cloudfront.net/pictures/athletes/2176188/1065064/3/large.jpg"

    def __str__(self):
        return self.first_name + ' ' + self.last_name
