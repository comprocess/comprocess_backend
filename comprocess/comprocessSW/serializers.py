from rest_framework import serializers
from .models import Travel_Schedule

class TravelScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Travel_Schedule
        fields = '__all__'
