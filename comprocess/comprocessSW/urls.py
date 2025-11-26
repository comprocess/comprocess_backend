from django.urls import path
from .views import TravelScheduleAI

urlpatterns = [
    path('travel-plan/', TravelScheduleAI.as_view()),
]
