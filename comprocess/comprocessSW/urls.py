from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    TravelScheduleAI, ImageUploadView, ImageAnalyzeView, ExchangeRatePredictionView,
    UserRegisterView, UserLoginView, UserUpdateView, UserDeleteView,
    UserDetailView, UserListView, UserTravelHistoryView, TravelScheduleDetailView,
    UserMeView, MyTravelHistoryView
)

urlpatterns = [
    # User Management
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('user/me/', UserMeView.as_view(), name='user-me'),
    path('user/me/travel-history/', MyTravelHistoryView.as_view(), name='my-travel-history'),
    path('user/<int:user_id>/', UserUpdateView.as_view(), name='user-update'),
    path('user/<int:user_id>/detail/', UserDetailView.as_view(), name='user-detail'),
    path('user/<int:user_id>/travel-history/', UserTravelHistoryView.as_view(), name='user-travel-history'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('user/delete/', UserDeleteView.as_view(), name='user-delete'),
    
    # Travel & Image
    path('travel-plan/', TravelScheduleAI.as_view()),
    path('travel-plan/<int:schedule_id>/', TravelScheduleDetailView.as_view(), name='travel-schedule-detail'),
    path('image-upload/', ImageUploadView.as_view()),
    path('image-analyze/', ImageAnalyzeView.as_view()),
    path('exchange-rate-predict/', ExchangeRatePredictionView.as_view()),
]
