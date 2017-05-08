from dateutil import tz
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from stravalib.client import Client
from .models import Users, Relationship
import datetime

from .race import Race


client = Client()
current_athlete = None
current_id = None


def strava_site(request):
    return redirect(settings.STRAVA_AUTH_URL)


def home(request):
    athlete_data = {
        'id': current_athlete.id,
        'first_name': current_athlete.firstname,
        'last_name': current_athlete.lastname,
        'profile_picture': current_athlete.profile,
        'training_partners': calc_top_training_partners(client, 9)
    }

    return render(request, 'index.html', athlete_data)


def fastest_segments(request):
    return render(request, 'fastest_segments/index.html')


def most_ridden_segments(request):
    return render(request, 'most_ridden_segments/index.html')


def race_statistics(request):
    race_data = calc_race_data()

    return render(request, 'race_statistics/index.html', race_data)


def calc_race_data():
    base_url = 'https://www.strava.com/activities/'
    total_distance = 0.0
    total_races = 0  # off-by-one?
    race_list = []

    for activity in client.get_activities():
        if activity.workout_type == '11':
            total_distance += float(activity.distance)
            total_races += 1

            name = activity.name
            url = base_url + str(activity.id)
            formatted_date = get_activity_date(activity)

            race_list.append(Race(name, url, formatted_date))

    # Convert distance from meters to miles and round
    total_distance = float("{0:.2f}".format(total_distance / 1609.34))

    return_dict = {
        'total_race_mileage': total_distance,
        'num_races': total_races,
        'race_list': race_list
    }

    return return_dict


def get_activity_date(activity):
    d = activity.start_date_local
    return str(d.month) + '/' + str(d.day) + '/' + str(d.year)


def welcome(request):
    return render(request, 'welcome/index.html')


def get_access_token(request):
    client_id = settings.CLIENT_ID
    client_secret = settings.CLIENT_SECRET
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
                  authorized=True,
                  ttp_last_updated="2000-01-01T00:00:00Z")
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

    athlete_data = {
        'id': current_athlete.id,
        'first_name': current_athlete.firstname,
        'last_name': current_athlete.lastname,
        'profile_picture': current_athlete.profile,
        'training_partners': calc_top_training_partners(client, 1000),
        'last_updated': get_last_updated(current_id)
    }

    return render(request, 'top_training_partners/index.html', athlete_data)


# TODO: Probably shouldn't even have to pass in client (c)
def calc_top_training_partners(c, num_results):

    # TODO: Add Progress bar for calc function
    athlete_list = []

    try:
        user_object = Users.objects.get(strava_id=current_id)
        last_updated = getattr(user_object, "ttp_last_updated")
    except ObjectDoesNotExist:
        print("ERROR: User doesn't exist. Look into this!")
        return None

    for activity in c.get_activities(after=last_updated):
        for related_activity in activity.related:
            partner_id = related_activity.athlete.id
            partner_fn = related_activity.athlete.firstname
            partner_ln = related_activity.athlete.lastname

            # Update or create Relationship in db (maybe switch to update_or_create)
            try:
                db_object = Relationship.objects.get(user1=current_id, user2=partner_id)
                db_object.ra_count = F("ra_count") + 1
                db_object.save(update_fields=['ra_count'])
            except Relationship.DoesNotExist:
                r = Relationship(user1=current_id,
                                 user2=partner_id,
                                 first_name=partner_fn,
                                 last_name=partner_ln,
                                 ra_count=1)
                r.save()
            except Relationship.MultipleObjectsReturned:
                print("ERROR: Marcel, Why are there repeat partner pairs?!")

    # Update User.tpp_last_updated
    try:
        db_object = Users.objects.get(strava_id=current_id)
        db_object.ttp_last_updated = str(datetime.datetime.utcnow().isoformat()) + 'Z'
        db_object.save(update_fields=['ttp_last_updated'])
    except Users.DoesNotExist:
        print('ERROR: Well this is awkward, this shouldnt have happened. #1')
    except Relationship.MultipleObjectsReturned:
        print('ERROR: Well this is awkward, this shouldnt have happened. #2')

    ttp_qs = Relationship.objects.filter(user1=current_id).order_by('-ra_count')[:num_results]

    for partner in ttp_qs:
        athlete_list.append(partner.first_name + ' ' + partner.last_name + ' (' + str(partner.ra_count) + ')')

    return athlete_list


def get_last_updated(user_id):
    try:
        db_object = Users.objects.get(strava_id=user_id)
        last_updated = getattr(db_object, "ttp_last_updated")
    except ObjectDoesNotExist:
        last_updated = 'unknown'
        print('ERROR: Could not find user in database')
    return last_updated


def local_tz_convert(utc_datetime):
    # Auto-detect zones:
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    processed_time = str(utc_datetime).split(".")[0]
    utc = datetime.datetime.strptime(processed_time, '%Y-%m-%d %H:%M:%S')
    utc = utc.replace(tzinfo=from_zone)
    local_time = utc.astimezone(to_zone)

    return local_time


def handler404(request):
    return render(request, '404.html')


def handler500(request):
    return render(request, '500.html')
