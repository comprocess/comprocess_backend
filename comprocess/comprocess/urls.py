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
        title="🌍 Comprocess Travel API",
        default_version='v1.0.0',
        description="""
# 환영합니다! 👋

**Comprocess Travel API**는 여행 계획을 도와주는 AI 기반 API입니다.

## 주요 기능 🚀

### 1. 🗺️ 여행 일정 생성 AI
- **엔드포인트**: `/comprocessSW/travel-plan/`
- 목적지, 예산, 날짜, 선호사항을 입력하면 AI가 맞춤형 여행 일정을 생성합니다.

### 2. 📸 이미지 업로드
- **엔드포인트**: `/comprocessSW/image-upload/`
- 여행 사진을 업로드하고 관리할 수 있습니다.

### 3. 🔍 한국 관광지/음식 이미지 분석 AI
- **엔드포인트**: `/comprocessSW/image-analyze/`
- 업로드한 이미지를 AI가 분석하여 한국 관광지나 음식 정보를 제공합니다.

### 4. 💱 환율 예측 AI
- **엔드포인트**: `/comprocessSW/exchange-rate-predict/`
- 년도, 월, 국가를 입력하면 AI가 환율을 예측합니다.
- 지원 국가: 🇺🇸 미국 (USD), 🇯🇵 일본 (JPY)

## 기술 스택 🛠️
- Django REST Framework
- OpenAI GPT-4
- TensorFlow LSTM
- Python 3.x

## 문의 📧
기술 지원이 필요하시면 contact@comprocess.local로 연락주세요.
        """,
        terms_of_service="https://www.comprocess.com/terms/",
        contact=openapi.Contact(
            name="Comprocess Dev Team",
            email="contact@comprocess.local",
            url="https://www.comprocess.com"
        ),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
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
