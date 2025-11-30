"""
URL configuration for comprocess project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Comprocess Travel API",
        default_version='v1.0.0',
        description="""
# Comprocess Travel API

여행 계획을 도와주는 AI 기반 API입니다.

## 인증 방법
이 API는 **JWT Bearer Token** 인증을 사용합니다.

### Swagger에서 인증하기:
1. `/comprocessSW/login/`에서 로그인하여 **access_token** 획득
2. 우측 상단 **Authorize** 버튼 클릭
3. access_token 값만 입력 (Bearer 접두사 제외)
4. **Authorize** 클릭
5. 인증이 필요한 API 사용 가능

### API에서 사용:
- 요청 헤더에 `Authorization: Bearer {access_token}` 추가
- Access Token 만료 시간: 1시간
- Refresh Token 만료 시간: 7일
- 토큰 만료 시 `/comprocessSW/token/refresh/`로 갱신

## 주요 기능

### 1. 회원 관리
- 회원가입, 로그인, 계정 수정/삭제
- JWT 토큰 기반 인증
- 사용자 정보 조회 및 목록

### 2. 여행 일정 생성 AI
- **엔드포인트**: `/comprocessSW/travel-plan/`
- 목적지, 예산, 날짜, 선호사항을 입력하면 AI가 맞춤형 여행 일정을 생성합니다.
- 로그인 시 여행 내역 자동 저장 및 조회 가능
- 비로그인 시에도 일정 생성 가능 (저장되지 않음)

### 3. 이미지 업로드 및 관리
- **엔드포인트**: `/comprocessSW/image-upload/`
- 여행 사진을 업로드하고 관리할 수 있습니다.

### 4. 한국 관광지/음식 이미지 분석 AI
- **엔드포인트**: `/comprocessSW/image-analyze/`
- 업로드한 이미지를 AI가 분석하여 한국 관광지나 음식 정보를 제공합니다.

### 5. 환율 예측 AI
- **엔드포인트**: `/comprocessSW/exchange-rate-predict/`
- 년도, 월, 국가를 입력하면 AI가 환율을 예측합니다.
- 지원 국가: 미국 (USD), 일본 (JPY)


        """,
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('comprocessSW/', include('comprocessSW.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Media files serving
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Static files serving (for production)
if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
