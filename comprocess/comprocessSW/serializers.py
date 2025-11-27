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


class ExchangeRatePredictionSerializer(serializers.Serializer):
    """환율 예측 요청 Serializer"""
    year = serializers.IntegerField(
        min_value=2000,
        max_value=2100,
        help_text="📅 예측할 년도 (예: 2026)"
    )
    month = serializers.IntegerField(
        min_value=1,
        max_value=12,
        help_text="📅 예측할 월 (1-12)"
    )
    country = serializers.ChoiceField(
        choices=["미국", "일본"],
        help_text="🌍 국가 선택: '미국' (USD) 또는 '일본' (JPY 100엔당)"
    )
