from django.db import models


class Users(models.Model):
    strava_id = models.IntegerField(default=0)
    first_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')
    authorized = models.BooleanField(default=False)
    ttp_last_updated = models.DateTimeField(auto_now=False, default="2000-01-01T00:00:00Z")
    rs_last_updated = models.DateTimeField(auto_now=False, default="2000-01-01T00:00:00Z")
    total_distance = models.IntegerField(default=0)
    num_races = models.IntegerField(default=0)

    def __str__(self):
        return self.first_name + ' ' + self.last_name + ' (' + str(self.strava_id) + "): " + str(self.authorized)


class Relationship(models.Model):
    user1 = models.IntegerField(default=0)
    user2 = models.IntegerField(default=0)
    first_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')
    ra_count = models.IntegerField(default=0)

    def __str__(self):
        return str(self.user1) + ' - ' + str(self.user2) + ": " + str(self.ra_count)


class Races(models.Model):
    activity_id = models.IntegerField(default=0)
    user_id = models.IntegerField(default=0)
    date = models.DateField(auto_now=False, default="2000-01-01")
    name = models.CharField(max_length=256, default='')

    def __str__(self):
        return str(self.activity_id) + ': ' + str(self.name)

