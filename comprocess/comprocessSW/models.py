from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_password(self, raw_password):
        """비밀번호를 해시화하여 저장"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """비밀번호 확인"""
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username


class Travel_Schedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='travel_schedules', null=True, blank=True)
    destination = models.CharField(max_length=50)
    budget = models.CharField(max_length=100)
    travel_date = models.CharField(max_length=100)
    preferences = models.CharField(max_length=255)
    extra = models.CharField(max_length=255)
    ai_result = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.destination} ({self.travel_date})"


class UploadedImage(models.Model):
    image = models.ImageField(upload_to='uploads/')
    title = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"Image {self.id}"

