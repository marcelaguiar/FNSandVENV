from django.shortcuts import render
from stravalib.client import Client


client = Client()


def index(request):
    access_token = get_access_token(request)
    client.access_token = access_token
    athlete = client.get_athlete()

    sorted_partner_list = top_training_partners(client)

    athlete_data = {
        'id': athlete.id,
        'first_name': athlete.firstname,
        'last_name': athlete.lastname,
        'profile_picture': athlete.profile,
        'training_partners': sorted_partner_list
    }

    return render(request, 'index.html', athlete_data)


def get_access_token(request):
    client_id = 15675
    client_secret = 'ada13b288862d04f79f6686f84d1ef3127cda3ef'
    access_code = request.GET.get('code')
    access_token = client.exchange_code_for_token(client_id=client_id, client_secret=client_secret, code=access_code)

    return access_token


def top_training_partners(c):
    my_dict = {}

    for activity in c.get_activities():
        for related_activity in activity.related:
            if related_activity.athlete.id in my_dict:
                my_dict[related_activity.athlete.id] += 1
            else:
                my_dict[related_activity.athlete.id] = 1

    ten_sorted = sorted([(k, v) for k, v in my_dict.items()], key=lambda x: x[1], reverse=True)[0:10]

    athlete_list = []
    for person in ten_sorted:
        athlete = c.get_athlete(person[0])
        athlete_list.append(athlete.firstname + ' ' + athlete.lastname + ' (' + str(person[1]) + ')')

    return athlete_list


def handler404(request):
    return render(request, '404.html')


def handler500(request):
    return render(request, '500.html')
