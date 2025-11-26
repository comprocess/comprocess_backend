from rest_framework import serializers
from .models import Travel_Schedule, UploadedImage

class TravelScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Travel_Schedule
        fields = '__all__'


class ImageUploadSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    title = serializers.CharField(max_length=100, required=False, allow_blank=True, default='')
    description = serializers.CharField(required=False, allow_blank=True, default='')
    
    class Meta:
        model = UploadedImage
        fields = ['id', 'image', 'title', 'description', 'uploaded_at']
        read_only_fields = ('id', 'uploaded_at')
