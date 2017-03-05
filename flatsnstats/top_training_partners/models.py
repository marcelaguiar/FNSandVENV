from django.db import models


class TopTrainingPartners(models.Model):
    strava_id = models.IntegerField()
    authorized = models.BooleanField()
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
