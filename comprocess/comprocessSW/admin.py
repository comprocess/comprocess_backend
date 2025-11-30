from django.contrib import admin
from .models import Travel_Schedule, UploadedImage, User

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'created_at', 'updated_at']
    search_fields = ['username']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Travel_Schedule)
class TravelScheduleAdmin(admin.ModelAdmin):
    list_display = ['id', 'destination', 'budget', 'travel_date']
    search_fields = ['destination']

@admin.register(UploadedImage)
class UploadedImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'uploaded_at']
    search_fields = ['title']
    readonly_fields = ['uploaded_at']
