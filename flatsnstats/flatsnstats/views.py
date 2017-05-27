from dateutil import tz
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from stravalib.client import Client
from .models import Races, Relationship, Users
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
    # ------------------------------------------------------------------------------------
    # POPULATE NEW ACTIVITIES
    total_distance = 0.0
    total_races = 0
    new_total_distance = 0.0
    new_num_races = 0  # off-by-one?

    # Get rs_last_updated
    try:
        user_object = Users.objects.get(strava_id=current_id)  # factor out?
        last_updated = getattr(user_object, "rs_last_updated")
    except ObjectDoesNotExist:
        print("ERROR: User doesn't exist. Look into this!")
        return None

    # Loop through new race activities and add to DB
    # for activity in [x for x in client.get_activities(after=last_updated) if x.workout_type == '11']:
    for activity in client.get_activities(after=last_updated):
        if activity.workout_type == '11':

            # Check if activity already exists in DB table for some reason
            exists = Races.objects.filter(activity_id=activity.id).exists()
            if exists is True:
                print("Race activity already in db...INVESTIGATE")
                continue

            # Add to database
            r = Races(activity_id=activity.id,
                      user_id=current_id,
                      date=activity.start_date_local,
                      name=activity.name)
            r.save()

            new_total_distance += float(activity.distance)
            new_num_races += 1

    # Update total_distance and num_races in User table
    try:
        db_object = Users.objects.get(strava_id=current_id)
        db_object.total_distance = F("total_distance") + new_total_distance
        db_object.num_races = F("num_races") + new_num_races
        db_object.save(update_fields=['total_distance', 'num_races'])
    except Users.DoesNotExist:
        print('ERROR: Well this is awkward, this should not have happened. #1')

    # ------------------------------------------------------------------------------------
    # GET ALL RACE DATA
    try:
        user_object = Users.objects.get(strava_id=current_id) # Delete line? already done above.
        total_distance = getattr(user_object, "total_distance")
        total_races = getattr(user_object, "num_races")
    except ObjectDoesNotExist:
        print("User does not exist for some reason")

    # Convert distance from meters to miles and round
    total_distance = float("{0:.2f}".format(total_distance / 1609.34))

    # Query for all races from this user
    rs_qs = Races.objects.filter(user_id=current_id).order_by('-date')

    race_list = []

    # Loop through Queryset items
    for race in rs_qs:
        name = race.name
        url = 'https://www.strava.com/activities/' + str(race.activity_id)
        date = get_activity_date(race.date)

        race_list.append(Race(name, url, date))

    # Update User.rs_last_updated
    try:
        db_object = Users.objects.get(strava_id=current_id)
        db_object.rs_last_updated = str(datetime.datetime.utcnow().isoformat()) + 'Z'
        db_object.save(update_fields=['rs_last_updated'])
    except Users.DoesNotExist:
        print('ERROR: Well this is awkward, this shouldnt have happened. #1')
    except Relationship.MultipleObjectsReturned:
        print('ERROR: Well this is awkward, this shouldnt have happened. #2')

    races_dict = {
        'total_race_mileage': total_distance,
        'num_races': total_races,
        'race_list': race_list,
    }

    return races_dict


def get_activity_date(d):
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
                  ttp_last_updated="2000-01-01T00:00:00Z",
                  rs_last_updated="2000-01-01T00:00:00Z",
                  total_distance=0,
                  num_races=0)
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
        'last_updated': get_last_updated(current_id, "ttp_last_updated")
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


def get_last_updated(user_id, attribute):
    try:
        db_object = Users.objects.get(strava_id=user_id)
        last_updated = getattr(db_object, attribute)
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
