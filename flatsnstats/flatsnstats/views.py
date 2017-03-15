from django.shortcuts import render, redirect
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from stravalib.client import Client
from .models import Users, Relationship
import datetime


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
        'training_partners': calc_top_training_partners(client)
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
    if request.POST.get('button_click'):
        athlete_data = update_top_training_partners()
    else:
        athlete_data = {
            'id': current_athlete.id,
            'first_name': current_athlete.firstname,
            'last_name': current_athlete.lastname,
            'profile_picture': current_athlete.profile,
            'training_partners': calc_top_training_partners(client),
            'last_updated': get_last_updated(current_id)
        }

    return render(request, 'top_training_partners/index.html', athlete_data)


def calc_top_training_partners(c):
    # TODO: Add Progress bar for calc function
    my_dict = {}
    athlete_list = []

    try:
        # TODO: FIGURE OUT WHAT TO SET last_updated TO
        user_object = Users.objects.get(strava_id=current_id)
        last_updated = getattr(user_object, "ttp_last_updated")
    except ObjectDoesNotExist:
        print("ERROR: User doesn't exist. Look into this!!!!!!!!! ")
        return None

    for activity in c.get_activities(after=last_updated):
        for related_activity in activity.related:
            training_partner_id = related_activity.athlete.id

            # Update or create Relationship in db (maybe switch to update_or_create)
            try:
                db_object = Relationship.objects.get(user1=current_id, user2=training_partner_id)
                db_object.ra_count = F("ra_count") + 1
                db_object.save(update_fields=['ra_count'])
            except Relationship.DoesNotExist:
                r = Relationship(user1=current_id, user2=training_partner_id, ra_count=1)
                r.save()
            except Relationship.MultipleObjectsReturned:
                print("ERROR: Marcel, Why are there repeat partner pairs!?!?!? ")

    # Update User.tpp_last_updated
    try:
        db_object = Users.objects.get(strava_id=current_id)
        db_object.ttp_last_updated = str(datetime.datetime.utcnow().isoformat()) + 'Z'
        db_object.save(update_fields=['ttp_last_updated'])
    except Users.DoesNotExist:
        print('ERROR: Well this is awkward, this shouldnt have happened. #1')
    except Relationship.MultipleObjectsReturned:
        print('ERROR: Well this is awkward, this shouldnt have happened. #2')

    ttp_qs = Relationship.objects.filter(user1=current_id).order_by('-ra_count')[:850]

    for relationship in ttp_qs:
        partner = c.get_athlete(relationship.user2)
        athlete_list.append(partner.firstname + ' ' + partner.lastname + ' (' + str(relationship.ra_count) + ')')

    return athlete_list


def update_top_training_partners():
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
        db_object = Users.objects.get(strava_id=user_id)
        last_updated = getattr(db_object, "ttp_last_updated")
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
