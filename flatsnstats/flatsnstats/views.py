from django.shortcuts import render, redirect
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from stravalib.client import Client
from .models import TopTrainingPartners, Users
import time


client = Client()
current_athlete = None
current_id = None


def strava_site(request):
    return redirect(settings.STRAVA_AUTH_URL)


def home(request):
    sorted_partner_list = compile_top_training_partners(client)

    athlete_data = {
        'id': current_athlete.id,
        'first_name': current_athlete.firstname,
        'last_name': current_athlete.lastname,
        'profile_picture': current_athlete.profile,
        'training_partners': sorted_partner_list
    }

    return render(request, 'index.html', athlete_data)


def fastest_segments(request):
    return render(request, 'fastest_segments/index.html')


def most_ridden_segments(request):
    return render(request, 'most_ridden_segments/index.html')


def welcome(request):
    return render(request, 'welcome/index.html')


def get_access_token(request):
    client_id = 15675
    client_secret = 'ada13b288862d04f79f6686f84d1ef3127cda3ef'
    access_code = request.GET.get('code')
    access_token = client.exchange_code_for_token(client_id=client_id, client_secret=client_secret, code=access_code)

    return access_token


def set_global_athlete(request):
    global current_athlete
    global current_id
    client.access_token = get_access_token(request)
    current_athlete = client.get_athlete()
    current_id = current_athlete.id

    try:
        user_object = Users.objects.get(strava_id=current_id)
        user_authorized = getattr(user_object, "authorized")
    except ObjectDoesNotExist:
        # Add to database
        u = Users(strava_id=current_id,
                  first_name=current_athlete.firstname,
                  last_name=current_athlete.lastname,
                  authorized=True)
        u.save()

        user_authorized = True

    settings.AUTHORIZED = True

    if user_authorized is False:
        # Update authorized field in database
        u = Users.objects.filter(strava_id=current_id)
        u.authorized = True
        u.save()


def temporary_redirect(request):
    set_global_athlete(request)
    return redirect('/')


def top_training_partners(request):
    if request.POST.get('button_click'):
        print("LLLLLLMAO")
        athlete_data = update_top_training_partners(request)
    else:
        athlete_data = {
            'id': current_athlete.id,
            'first_name': current_athlete.firstname,
            'last_name': current_athlete.lastname,
            'profile_picture': current_athlete.profile,
            'training_partners': compile_top_training_partners(client),
            'last_updated': get_last_updated(current_id)
        }

    return render(request, 'top_training_partners/index.html', athlete_data)


def compile_top_training_partners(c):
    athlete_list = []

    try:
        athlete_object = TopTrainingPartners.objects.get(strava_id=current_id)
        for i in range(1, 11):
            field = 'partner' + str(i)
            athlete_list.append(getattr(athlete_object, field))
    except ObjectDoesNotExist:
        athlete_list = calc_top_training_partners(c)
    return athlete_list


def calc_top_training_partners(c):
    # TODO: Add Progress bar for calc function
    my_dict = {}
    athlete_list = []

    for activity in c.get_activities():
        for related_activity in activity.related:
            if related_activity.athlete.id in my_dict:
                my_dict[related_activity.athlete.id] += 1
            else:
                my_dict[related_activity.athlete.id] = 1

    ten_sorted = sorted([(k, v) for k, v in my_dict.items()], key=lambda x: x[1], reverse=True)[0:10]

    for person in ten_sorted:
        partner = c.get_athlete(person[0])
        athlete_list.append(partner.firstname + ' ' + partner.lastname + ' (' + str(person[1]) + ')')

    t = TopTrainingPartners(strava_id=current_id, last_updated=time.time(),
                            partner1=list_access_helper(athlete_list, 0),
                            partner2=list_access_helper(athlete_list, 1),
                            partner3=list_access_helper(athlete_list, 2),
                            partner4=list_access_helper(athlete_list, 3),
                            partner5=list_access_helper(athlete_list, 4),
                            partner6=list_access_helper(athlete_list, 5),
                            partner7=list_access_helper(athlete_list, 6),
                            partner8=list_access_helper(athlete_list, 7),
                            partner9=list_access_helper(athlete_list, 8),
                            partner10=list_access_helper(athlete_list, 9))
    t.save()

    return athlete_list


def update_top_training_partners(request):
    # TODO: Calculate activities after certain date
    # 1. Get current top 10 as {strava_id:number_of_related_activities}
    # 2. Get last_updated
    # 3. Calculate activities after last_updated, and add to

    # Recalculate from scratch
    sorted_partner_list = calc_top_training_partners(client)

    athlete_data = {
        'id': current_athlete.id,
        'first_name': current_athlete.firstname,
        'last_name': current_athlete.lastname,
        'profile_picture': current_athlete.profile,
        'training_partners': sorted_partner_list,
        'last_updated': get_last_updated(current_id)
    }

    return athlete_data


def get_last_updated(user_id):
    try:
        db_object = TopTrainingPartners.objects.get(strava_id=user_id)
        last_updated = getattr(db_object, "last_updated")
    except ObjectDoesNotExist:
        last_updated = 'unknown'
        print('Could not find user in database')
    return last_updated


def list_access_helper(my_list, my_index):
    try:
        b = my_list[my_index]
    except IndexError:
        b = None
    return b


def handler404(request):
    return render(request, '404.html')


def handler500(request):
    return render(request, '500.html')
