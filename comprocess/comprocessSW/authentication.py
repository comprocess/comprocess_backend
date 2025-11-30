from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

def get_tokens_for_user(user):
    """사용자를 위한 JWT 토큰 생성"""
    refresh = RefreshToken()
    refresh['user_id'] = user.id
    refresh['username'] = user.username
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
