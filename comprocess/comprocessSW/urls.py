from django.urls import path
from .views import TravelScheduleAI, ImageUploadView, ImageAnalyzeView

urlpatterns = [
    path('travel-plan/', TravelScheduleAI.as_view()),
    path('image-upload/', ImageUploadView.as_view()),
    path('image-analyze/', ImageAnalyzeView.as_view()),
]
