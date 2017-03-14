from django.db import models
import datetime


class Users(models.Model):
    strava_id = models.IntegerField(default=0)
    first_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')
    authorized = models.BooleanField(default=False)
    ttp_last_updated = models.DateTimeField(auto_now=False, default=None)

    def __str__(self):
        return self.first_name + ' ' + self.last_name + ' (' + str(self.strava_id) + "): " + str(self.authorized)


class TopTrainingPartners(models.Model):
    strava_id = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    partner1 = models.CharField(max_length=100)
    partner2 = models.CharField(max_length=100)
    partner3 = models.CharField(max_length=100)
    partner4 = models.CharField(max_length=100)
    partner5 = models.CharField(max_length=100)
    partner6 = models.CharField(max_length=100)
    partner7 = models.CharField(max_length=100)
    partner8 = models.CharField(max_length=100)
    partner9 = models.CharField(max_length=100)
    partner10 = models.CharField(max_length=100)


class Relationship(models.Model):
    user1 = models.IntegerField(default=0)
    user2 = models.IntegerField(default=0)
    ra_count = models.IntegerField(default=0)

    def __str__(self):
        return str(self.user1) + ' - ' + str(self.user2) + ": " + str(self.ra_count)
