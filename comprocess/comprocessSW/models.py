from django.db import models

# Create your models here.
class Travel_Schedule(models.Model):
    destination = models.CharField(max_length=50)
    budget = models.CharField(max_length=100)
    travel_date = models.CharField(max_length=100)
    preferences = models.CharField(max_length=255)
    extra = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.destination} ({self.travel_date})"

