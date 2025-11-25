from django.db import models

# Create your models here.
class Travel_Schedule(models.Model):
    destination = models.CharField((""), max_length=50)
    budget = models.CharField((""))
    travel_date = models.CharField((""))
    preferences = models.CharField((""))
    extra = models.CharField((""))