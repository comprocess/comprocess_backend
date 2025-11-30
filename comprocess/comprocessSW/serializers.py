from rest_framework import serializers
from .models import Travel_Schedule, UploadedImage, User

class UserRegisterSerializer(serializers.ModelSerializer):
    """회원가입 Serializer"""
    password = serializers.CharField(write_only=True, min_length=4, help_text="비밀번호 (최소 4자)")
    
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'created_at']
        read_only_fields = ('id', 'created_at')
    
    def create(self, validated_data):
        user = User(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """로그인 Serializer"""
    username = serializers.CharField(help_text="아이디")
    password = serializers.CharField(write_only=True, help_text="비밀번호")


class UserUpdateSerializer(serializers.Serializer):
    """계정 수정 Serializer"""
    current_password = serializers.CharField(write_only=True, help_text="현재 비밀번호")
    new_username = serializers.CharField(required=False, help_text="새 아이디 (선택)")
    new_password = serializers.CharField(write_only=True, required=False, min_length=4, help_text="새 비밀번호 (선택)")


class UserDeleteSerializer(serializers.Serializer):
    """계정 삭제 Serializer"""
    username = serializers.CharField(help_text="아이디")
    password = serializers.CharField(write_only=True, help_text="비밀번호")


class UserDetailSerializer(serializers.ModelSerializer):
    """유저 상세 정보 Serializer (비밀번호 제외)"""
    class Meta:
        model = User
        fields = ['id', 'username', 'created_at', 'updated_at']
        read_only_fields = ('id', 'username', 'created_at', 'updated_at')


class TravelScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Travel_Schedule
        fields = ['id', 'destination', 'budget', 'travel_date', 'preferences', 'extra', 'user']
        read_only_fields = ('id',)


class TravelScheduleCreateSerializer(serializers.ModelSerializer):
    """여행 일정 생성용 Serializer"""
    
    class Meta:
        model = Travel_Schedule
        fields = ['destination', 'budget', 'travel_date', 'preferences', 'extra']


class TravelScheduleDetailSerializer(serializers.ModelSerializer):
    """여행 일정 상세 조회용 Serializer"""
    username = serializers.CharField(source='user.username', read_only=True, allow_null=True)
    
    class Meta:
        model = Travel_Schedule
        fields = ['id', 'user', 'username', 'destination', 'budget', 'travel_date', 
                  'preferences', 'extra', 'ai_result', 'created_at']
        read_only_fields = ('id', 'username', 'created_at')


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
