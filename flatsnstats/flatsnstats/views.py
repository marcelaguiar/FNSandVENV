from django.shortcuts import render
from stravalib.client import Client

client = Client()


def index(request):

    access_token = get_access_token(request)
    client.access_token = access_token
    athlete = client.get_athlete()
    athlete_data = {
        'first_name': athlete.firstname,
        'last_name': athlete.lastname,
        'profile_picture': athlete.profile
    }

    return render(request, 'index.html', athlete_data)


def get_access_token(request):
    client_id = 15675
    client_secret = 'ada13b288862d04f79f6686f84d1ef3127cda3ef'
    access_code = request.GET.get('code')
    access_token = client.exchange_code_for_token(client_id=client_id, client_secret=client_secret, code=access_code)

    return access_token


def handler404(request):
    return render(request, '404.html')


def handler500(request):
    return render(request, '500.html')
