from django.urls import path
from .views import TravelScheduleAI
from django.urls import path
from . import views

urlpatterns = [
    path('travel-plan/', TravelScheduleAI.as_view()),
]

urlpatterns = [
    path("predict/", views.exchange_service),
]
