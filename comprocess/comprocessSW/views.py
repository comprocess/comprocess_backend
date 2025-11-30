import asyncio
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Travel_Schedule, UploadedImage, User
from .serializers import (
    TravelScheduleSerializer, ImageUploadSerializer, ExchangeRatePredictionSerializer,
    UserRegisterSerializer, UserLoginSerializer, UserUpdateSerializer, UserDeleteSerializer,
    UserDetailSerializer, TravelScheduleCreateSerializer, TravelScheduleDetailSerializer
)
from comprocessSW.ai_module.kjy import generate_travel_plan
from comprocessSW.ai_module.kwy import KoreanImageAnalyzer
from comprocessSW.ai_module.exchange_rate_predictor import ExchangeRatePredictor
from comprocessSW.authentication import get_tokens_for_user
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.authentication import JWTAuthentication

# Create your views here.
class UserRegisterView(APIView):
    @swagger_auto_schema(
        operation_summary="회원가입",
        operation_description="""
        새로운 계정을 생성합니다.
        
        **입력 정보:**
        - username: 아이디 (고유값)
        - password: 비밀번호 (최소 4자)
        
        **예시:**
        ```json
        {
          "username": "testuser",
          "password": "1234"
        }
        ```
        """,
        request_body=UserRegisterSerializer,
        responses={
            201: openapi.Response(
                description="회원가입 완료",
                examples={
                    "application/json": {
                        "id": 1,
                        "username": "testuser",
                        "created_at": "2025-11-30T10:00:00Z",
                        "message": "회원가입이 완료되었습니다."
                    }
                }
            ),
            400: "잘못된 요청 (아이디 중복 또는 필수 필드 누락)"
        },
        tags=["User Management"]
    )
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "id": user.id,
                "username": user.username,
                "created_at": user.created_at,
                "message": "회원가입이 완료되었습니다."
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    @swagger_auto_schema(
        operation_summary="로그인",
        operation_description="""
        로그인을 진행합니다.
        
        **입력 정보:**
        - username: 아이디
        - password: 비밀번호
        
        **예시:**
        ```json
        {
          "username": "testuser",
          "password": "1234"
        }
        ```
        """,
        request_body=UserLoginSerializer,
        responses={
            200: openapi.Response(
                description="로그인 성공",
                examples={
                    "application/json": {
                        "id": 1,
                        "username": "testuser",
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "message": "로그인 성공"
                    }
                }
            ),
            401: "아이디 또는 비밀번호가 올바르지 않습니다."
        },
        tags=["User Management"]
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                tokens = get_tokens_for_user(user)
                return Response({
                    "id": user.id,
                    "username": user.username,
                    "access": tokens['access'],
                    "refresh": tokens['refresh'],
                    "message": "로그인 성공"
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "error": "아이디 또는 비밀번호가 올바르지 않습니다."
                }, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({
                "error": "아이디 또는 비밀번호가 올바르지 않습니다."
            }, status=status.HTTP_401_UNAUTHORIZED)


class UserUpdateView(APIView):
    @swagger_auto_schema(
        operation_summary="계정 수정",
        operation_description="""
        아이디 또는 비밀번호를 변경합니다.
        
        **입력 정보:**
        - user_id: 사용자 ID (URL 파라미터)
        - current_password: 현재 비밀번호 (필수)
        - new_username: 새 아이디 (선택)
        - new_password: 새 비밀번호 (선택)
        
        **예시:**
        ```json
        {
          "current_password": "1234",
          "new_username": "newuser",
          "new_password": "5678"
        }
        ```
        """,
        request_body=UserUpdateSerializer,
        responses={
            200: openapi.Response(
                description="계정 수정 완료",
                examples={
                    "application/json": {
                        "id": 1,
                        "username": "newuser",
                        "message": "계정 정보가 수정되었습니다."
                    }
                }
            ),
            400: "잘못된 요청",
            401: "현재 비밀번호가 올바르지 않습니다.",
            404: "사용자를 찾을 수 없습니다."
        },
        tags=["User Management"]
    )
    def put(self, request, user_id):
        serializer = UserUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                "error": "사용자를 찾을 수 없습니다."
            }, status=status.HTTP_404_NOT_FOUND)
        
        current_password = serializer.validated_data['current_password']
        if not user.check_password(current_password):
            return Response({
                "error": "현재 비밀번호가 올바르지 않습니다."
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 아이디 변경
        new_username = serializer.validated_data.get('new_username')
        if new_username:
            if User.objects.filter(username=new_username).exclude(id=user_id).exists():
                return Response({
                    "error": "이미 사용 중인 아이디입니다."
                }, status=status.HTTP_400_BAD_REQUEST)
            user.username = new_username
        
        # 비밀번호 변경
        new_password = serializer.validated_data.get('new_password')
        if new_password:
            user.set_password(new_password)
        
        user.save()
        
        return Response({
            "id": user.id,
            "username": user.username,
            "message": "계정 정보가 수정되었습니다."
        }, status=status.HTTP_200_OK)


class UserDeleteView(APIView):
    @swagger_auto_schema(
        operation_summary="계정 삭제",
        operation_description="""
        계정을 영구적으로 삭제합니다.
        
        **입력 정보:**
        - username: 아이디
        - password: 비밀번호
        
        **예시:**
        ```json
        {
          "username": "testuser",
          "password": "1234"
        }
        ```
        """,
        request_body=UserDeleteSerializer,
        responses={
            200: openapi.Response(
                description="계정 삭제 완료",
                examples={
                    "application/json": {
                        "message": "계정이 삭제되었습니다."
                    }
                }
            ),
            401: "아이디 또는 비밀번호가 올바르지 않습니다.",
            404: "사용자를 찾을 수 없습니다."
        },
        tags=["User Management"]
    )
    def delete(self, request):
        serializer = UserDeleteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                user.delete()
                return Response({
                    "message": "계정이 삭제되었습니다."
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "error": "아이디 또는 비밀번호가 올바르지 않습니다."
                }, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({
                "error": "아이디 또는 비밀번호가 올바르지 않습니다."
            }, status=status.HTTP_401_UNAUTHORIZED)


class UserMeView(APIView):
    @swagger_auto_schema(
        operation_summary="현재 로그인한 유저 정보 조회",
        operation_description="""
        현재 로그인한 유저의 정보를 조회합니다.
        
        **인증 필요:**
        - Authorization 헤더 필요
        - Swagger에서 우측 상단 Authorize 버튼 클릭 후 토큰 입력
        
        **반환 정보:**
        - 현재 로그인한 사용자의 ID, 아이디, 생성일, 수정일
        """,
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description="현재 유저 정보 조회 성공",
                examples={
                    "application/json": {
                        "id": 1,
                        "username": "testuser",
                        "created_at": "2025-11-30T10:00:00Z",
                        "updated_at": "2025-11-30T10:00:00Z"
                    }
                }
            ),
            401: "인증 정보가 없거나 유효하지 않습니다."
        },
        tags=["User Management"]
    )
    def get(self, request):
        # JWT 토큰에서 user_id 추출
        user = request.user
        
        # 디버그 정보 수집
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        print(f"[DEBUG] Authorization header: {auth_header[:50] if auth_header else 'None'}...")
        print(f"[DEBUG] request.user: {user}")
        print(f"[DEBUG] request.auth: {request.auth}")

        if user is None or not getattr(user, "is_authenticated", False):
            return Response(
                {
                    "error": "인증 정보가 없거나 유효하지 않습니다.",
                    "debug_user": str(user),
                    "debug_user_type": str(type(user)),
                    "debug_is_authenticated": str(getattr(user, "is_authenticated", "N/A")),
                    "debug_auth": str(request.auth),
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDetailView(APIView):
    @swagger_auto_schema(
        operation_summary="특정 유저 정보 조회",
        operation_description="""
        특정 유저의 상세 정보를 조회합니다.
        
        **URL 파라미터:**
        - user_id: 조회할 사용자 ID
        
        **반환 정보:**
        - 사용자 ID
        - 아이디 (username)
        - 계정 생성일
        - 최근 수정일
        """,
        responses={
            200: openapi.Response(
                description="유저 정보 조회 성공",
                examples={
                    "application/json": {
                        "id": 1,
                        "username": "testuser",
                        "created_at": "2025-11-30T10:00:00Z",
                        "updated_at": "2025-11-30T10:00:00Z"
                    }
                }
            ),
            404: "❌ 사용자를 찾을 수 없습니다."
        },
        tags=["User Management"]
    )
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            serializer = UserDetailSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                "error": "사용자를 찾을 수 없습니다."
            }, status=status.HTTP_404_NOT_FOUND)


class UserListView(APIView):
    @swagger_auto_schema(
        operation_summary="모든 유저 목록 조회",
        operation_description="""
        등록된 모든 유저의 목록을 조회합니다.
        
        **반환 정보:**
        - 전체 유저 수
        - 각 유저의 ID, 아이디, 생성일, 수정일 목록
        
        **참고:**
        - 비밀번호는 반환되지 않습니다
        - 최신 가입 순으로 정렬됩니다
        """,
        responses={
            200: openapi.Response(
                description="유저 목록 조회 성공",
                examples={
                    "application/json": {
                        "count": 2,
                        "users": [
                            {
                                "id": 2,
                                "username": "user2",
                                "created_at": "2025-11-30T11:00:00Z",
                                "updated_at": "2025-11-30T11:00:00Z"
                            },
                            {
                                "id": 1,
                                "username": "user1",
                                "created_at": "2025-11-30T10:00:00Z",
                                "updated_at": "2025-11-30T10:00:00Z"
                            }
                        ]
                    }
                }
            )
        },
        tags=["User Management"]
    )
    def get(self, request):
        users = User.objects.all().order_by('-created_at')
        serializer = UserDetailSerializer(users, many=True)
        return Response({
            "count": users.count(),
            "users": serializer.data
        }, status=status.HTTP_200_OK)


class TravelScheduleAI(APIView):
    @swagger_auto_schema(
        operation_summary="AI 여행 일정 생성",
        operation_description="""
        ## 맞춤형 여행 일정을 AI가 자동으로 생성해드립니다!
        
        ### 입력 정보
        - **destination**: 여행 목적지 (예: 서울, 부산, 제주도)
        - **budget**: 예산 (예: 100만원, 50만원)
        - **travel_date**: 여행 날짜 (예: 2026-01-01 ~ 2026-01-03)
        - **preferences**: 선호사항 (예: 맛집, 카페, 쇼핑, 역사)
        - **extra**: 추가 요청사항 (예: 호텔 추천 필요, 대중교통 이용)
        
        ### 인증 (선택)
        - **Authorization 헤더**: `Bearer {access_token}` 포함 시 여행 내역 자동 저장
        - 비로그인 상태에서도 사용 가능
        
        ### 반환 정보
        - 입력한 정보
        - AI가 생성한 상세 여행 일정
        - 저장된 일정 ID
        
        ### 예시
        ```json
        {
          "destination": "제주도",
          "budget": "150만원",
          "travel_date": "2026-02-01 ~ 2026-02-03",
          "preferences": "자연경관, 맛집",
          "extra": "렌터카 이용 예정"
        }
        ```
        """,
        request_body=TravelScheduleCreateSerializer,
        responses={
            200: openapi.Response(
                description="✅ 여행 일정 생성 완료",
                examples={
                    "application/json": {
                        "input": {
                            "id": 1,
                            "destination": "서울",
                            "budget": "100만원",
                            "travel_date": "2026-01-01 ~ 2026-01-03",
                            "preferences": "맛집, 카페",
                            "extra": "호텔 추천 필요"
                        },
                        "ai_result": {
                            "여행_일정": {
                                "목적지": "서울",
                                "예산": "100만원",
                                "기간": "2026-01-01 ~ 2026-01-03",
                                "일정": [
                                    {
                                        "날짜": "2026-01-01 (첫째 날)",
                                        "활동": [
                                            {
                                                "시간": "09:00-12:00",
                                                "장소": "경복궁",
                                                "설명": "조선시대 궁궐 관람",
                                                "예상비용": "3,000원"
                                            },
                                            {
                                                "시간": "12:00-14:00",
                                                "장소": "광장시장",
                                                "설명": "전통 먹거리 체험",
                                                "예상비용": "15,000원"
                                            }
                                        ]
                                    },
                                    {
                                        "날짜": "2026-01-02 (둘째 날)",
                                        "활동": "..."
                                    }
                                ],
                                "추가_정보": {
                                    "총_예상비용": "약 950,000원",
                                    "교통": "대중교통 이용 권장",
                                    "숙박": "명동 인근 호텔 추천"
                                }
                            }
                        }
                    }
                }
            ),
            400: "❌ 잘못된 요청 (필수 필드 누락)"
        },
        tags=["Travel Planning"]
    )
    def post(self, request):
        serializer = TravelScheduleCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # 인증된 사용자라면 해당 사용자와 일정 연결
        user = request.user if getattr(request.user, "is_authenticated", False) else None

        schedule_obj = serializer.save(user=user)
        
        schedule_obj = serializer.save(user=user)

        destination = schedule_obj.destination
        budget = schedule_obj.budget
        travel_date = schedule_obj.travel_date
        preferences = schedule_obj.preferences
        extra = schedule_obj.extra

        ai_raw = asyncio.run(
            generate_travel_plan(destination, budget, travel_date, preferences, extra)
        )

        try:
            ai_result = json.loads(ai_raw)
        except json.JSONDecodeError:
            ai_result = {"error": "Invalid JSON returned from AI", "raw": ai_raw}
        
        # AI 결과 저장
        schedule_obj.ai_result = ai_result
        schedule_obj.save()
        
        detail_serializer = TravelScheduleDetailSerializer(schedule_obj)

        return Response({
            "schedule_id": schedule_obj.id,
            "input": {
                "destination": schedule_obj.destination,
                "budget": schedule_obj.budget,
                "travel_date": schedule_obj.travel_date,
                "preferences": schedule_obj.preferences,
                "extra": schedule_obj.extra,
                "user_id": schedule_obj.user.id if schedule_obj.user else None
            },
            "ai_result": ai_result
        }, status=status.HTTP_200_OK)


class UserTravelHistoryView(APIView):
    @swagger_auto_schema(
        operation_summary="사용자 여행 일정 내역 조회",
        operation_description="""
        ## 특정 사용자가 생성한 모든 여행 일정을 조회합니다!
        
        ### URL 파라미터
        - **user_id**: 조회할 사용자 ID
        
        ### 반환 정보
        - 해당 사용자의 모든 여행 일정 목록
        - 각 일정의 상세 정보 및 AI 생성 결과
        - 최신 순으로 정렬
        """,
        responses={
            200: openapi.Response(
                description="✅ 여행 일정 내역 조회 성공",
                examples={
                    "application/json": {
                        "user_id": 1,
                        "username": "testuser",
                        "count": 2,
                        "schedules": [
                            {
                                "id": 2,
                                "destination": "부산",
                                "budget": "80만원",
                                "travel_date": "2026-02-01 ~ 2026-02-03",
                                "preferences": "해변, 맛집",
                                "extra": "숙소 추천",
                                "ai_result": {"여행_일정": "..."},
                                "created_at": "2025-11-30T12:00:00Z"
                            },
                            {
                                "id": 1,
                                "destination": "서울",
                                "budget": "100만원",
                                "travel_date": "2026-01-01 ~ 2026-01-03",
                                "preferences": "맛집, 카페",
                                "extra": "호텔 추천",
                                "ai_result": {"여행_일정": "..."},
                                "created_at": "2025-11-30T10:00:00Z"
                            }
                        ]
                    }
                }
            ),
            404: "❌ 사용자를 찾을 수 없습니다."
        },
        tags=["Travel Planning"]
    )
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                "error": "사용자를 찾을 수 없습니다."
            }, status=status.HTTP_404_NOT_FOUND)
        
        schedules = Travel_Schedule.objects.filter(user=user).order_by('-created_at')
        serializer = TravelScheduleDetailSerializer(schedules, many=True)
        
        return Response({
            "user_id": user.id,
            "username": user.username,
            "count": schedules.count(),
            "schedules": serializer.data
        }, status=status.HTTP_200_OK)


class MyTravelHistoryView(APIView):
    @swagger_auto_schema(
        operation_summary="내 여행 일정 내역 조회 (JWT)",
        operation_description="""
        ## 현재 로그인한 사용자의 모든 여행 일정을 조회합니다!
        
        ### 인증 필요
        - **Authorization 헤더 필요**: `Bearer {access_token}` 또는 `{access_token}`
        - Swagger에서 우측 상단 🔓 Authorize 버튼 클릭 후 토큰 입력
        
        ### 반환 정보
        - 현재 사용자의 모든 여행 일정 목록
        - 각 일정의 상세 정보 및 AI 생성 결과
        - 최신 순으로 정렬
        """,
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description="✅ 여행 일정 내역 조회 성공",
                examples={
                    "application/json": {
                        "user_id": 1,
                        "username": "testuser",
                        "count": 2,
                        "schedules": [
                            {
                                "id": 2,
                                "destination": "부산",
                                "budget": "80만원",
                                "travel_date": "2026-02-01 ~ 2026-02-03",
                                "preferences": "해변, 맛집",
                                "extra": "숙소 추천",
                                "ai_result": {"여행_일정": "..."},
                                "created_at": "2025-11-30T12:00:00Z"
                            }
                        ]
                    }
                }
            ),
            401: "❌ 인증 정보가 없거나 유효하지 않습니다."
        },
        tags=["Travel Planning"]
    )
    def get(self, request):
        user = request.user

        if user is None or not getattr(user, "is_authenticated", False):
            return Response(
                {"error": "인증 정보가 없거나 유효하지 않습니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        schedules = Travel_Schedule.objects.filter(user=user).order_by('-created_at')
        serializer = TravelScheduleDetailSerializer(schedules, many=True)
        
        return Response({
            "user_id": user.id,
            "username": user.username,
            "count": schedules.count(),
            "schedules": serializer.data
        }, status=status.HTTP_200_OK)


class TravelScheduleDetailView(APIView):
    @swagger_auto_schema(
        operation_summary="특정 여행 일정 상세 조회",
        operation_description="""
        ## 특정 여행 일정의 상세 정보를 조회합니다!
        
        ### URL 파라미터
        - **schedule_id**: 조회할 여행 일정 ID
        
        ### 반환 정보
        - 여행 일정의 모든 정보
        - AI가 생성한 상세 일정
        """,
        responses={
            200: openapi.Response(
                description="✅ 여행 일정 조회 성공",
                examples={
                    "application/json": {
                        "id": 1,
                        "user": 1,
                        "username": "testuser",
                        "destination": "서울",
                        "budget": "100만원",
                        "travel_date": "2026-01-01 ~ 2026-01-03",
                        "preferences": "맛집, 카페",
                        "extra": "호텔 추천",
                        "ai_result": {"여행_일정": "..."},
                        "created_at": "2025-11-30T10:00:00Z"
                    }
                }
            ),
            404: "❌ 여행 일정을 찾을 수 없습니다."
        },
        tags=["Travel Planning"]
    )
    def get(self, request, schedule_id):
        try:
            schedule = Travel_Schedule.objects.get(id=schedule_id)
            serializer = TravelScheduleDetailSerializer(schedule)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Travel_Schedule.DoesNotExist:
            return Response({
                "error": "여행 일정을 찾을 수 없습니다."
            }, status=status.HTTP_404_NOT_FOUND)


class ImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    @swagger_auto_schema(
        operation_summary="이미지 업로드",
        operation_description="""
        ## 여행 사진을 업로드하고 관리하세요!
        
        ### 업로드 방법
        - **image**: 이미지 파일 선택 (JPG, PNG 등)
        - **title**: 이미지 제목 (선택사항)
        - **description**: 이미지 설명 (선택사항)
        
        ### 반환 정보
        - 업로드된 이미지 ID
        - 이미지 URL
        - 제목 및 설명
        - 업로드 시간
        """,
        manual_parameters=[
            openapi.Parameter(
                'image',
                openapi.IN_FORM,
                description="📁 업로드할 이미지 파일",
                type=openapi.TYPE_FILE,
                required=True
            ),
            openapi.Parameter(
                'title',
                openapi.IN_FORM,
                description="🏷️ 이미지 제목 (예: 제주도 한라산)",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'description',
                openapi.IN_FORM,
                description="📝 이미지 설명 (예: 일출 사진)",
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        responses={
            201: openapi.Response(
                description="✅ 이미지 업로드 완료",
                examples={
                    "application/json": {
                        "id": 1,
                        "image": "/media/uploads/image_2024_01_01.jpg",
                        "title": "제주도 한라산",
                        "description": "일출 사진",
                        "uploaded_at": "2025-11-28T10:30:00Z"
                    }
                }
            ),
            400: "❌ 잘못된 요청 (이미지 파일 필수)"
        },
        tags=["Image Management"]
    )
    def post(self, request, format=None):
        serializer = ImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_image = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="업로드된 이미지 목록 조회",
        operation_description="""
        ## 업로드된 모든 이미지를 확인하세요!
        
        ### 반환 정보
        - 모든 이미지 목록 (최신순)
        - 각 이미지의 ID, URL, 제목, 설명, 업로드 시간
        """,
        responses={200: ImageUploadSerializer(many=True)},
        tags=["Image Management"]
    )
    def get(self, request, format=None):
        images = UploadedImage.objects.all().order_by('-uploaded_at')
        serializer = ImageUploadSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ImageAnalyzeView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_summary="한국 관광지/음식 이미지 AI 분석",
        operation_description="""
        ## 사진 속 한국 관광지나 음식을 AI가 분석해드립니다!
        
        ### 업로드 방법
        - **image**: 분석할 이미지 파일
        - **title**: 제목 (선택사항)
        - **description**: 설명 (선택사항)
        
        ### AI 분석 내용
        
        **음식인 경우:**
        - 음식명
        - 주요 재료
        - 음식 설명
        - 맛의 특징
        
        **관광지인 경우:**
        - 장소 이름
        - 장소 설명
        - 역사적 의미
        
        ### 예시
        김치찌개 사진 → AI가 재료, 맛, 특징 분석
        경복궁 사진 → AI가 역사, 특징 설명
        """,
        manual_parameters=[
            openapi.Parameter(
                'image',
                openapi.IN_FORM,
                description="🖼️ 분석할 이미지 파일 (한국 관광지 또는 음식)",
                type=openapi.TYPE_FILE,
                required=True
            ),
            openapi.Parameter(
                'title',
                openapi.IN_FORM,
                description="🏷️ 이미지 제목 (선택사항)",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'description',
                openapi.IN_FORM,
                description="📝 이미지 설명 (선택사항)",
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        responses={
            201: openapi.Response(
                description="✅ 이미지 분석 완료",
                examples={
                    "application/json": {
                        "image_info": {
                            "id": 1,
                            "image": "/media/uploads/image.jpg",
                            "title": "맛있는 음식"
                        },
                        "ai_analysis": {
                            "success": True,
                            "data": {
                                "type": "음식",
                                "음식명": "김치찌개",
                                "대부분_들어가있는_재료": ["김치", "돼지고기", "두부"],
                                "음식에_대한_설명": "한국의 대표적인 찌개 요리...",
                                "음식_특징": "매콤하고 개운한 맛..."
                            }
                        }
                    }
                }
            )
        },
        tags=["AI Analysis"]
    )
    def post(self, request, format=None):
        # 이미지 저장
        serializer = ImageUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_image = serializer.save()
        
        # 저장된 이미지 경로로 AI 분석
        try:
            analyzer = KoreanImageAnalyzer()
            image_path = uploaded_image.image.path
            ai_result = analyzer.analyze_image(image_path)
            
            return Response({
                "image_info": serializer.data,
                "ai_analysis": ai_result
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                "image_info": serializer.data,
                "ai_analysis": {
                    "success": False,
                    "error": f"AI 분석 중 오류 발생: {str(e)}"
                }
            }, status=status.HTTP_201_CREATED)


class ExchangeRatePredictionView(APIView):
    """환율 예측 API"""
    
    @swagger_auto_schema(
        operation_summary="AI 환율 예측",
        operation_description="""
        ## 미래의 환율을 AI가 예측해드립니다!
        
        ### 입력 정보
        - **year**: 예측할 년도 (예: 2026)
        - **month**: 예측할 월 (1~12)
        - **country**: 국가 선택
          - 🇺🇸 "미국" - USD 달러 환율
          - 🇯🇵 "일본" - JPY 100엔당 환율
        
        ### 예측 범위
        - 현재(2025년 10월) 기준 **최대 12개월 후**까지 예측 가능
        - 과거 데이터는 실제 환율 반환
        
        ### 반환 정보
        - 예측 환율
        - 현재 환율
        - 변화율 (상승/하락 %)
        - 예측 개월 수
        
        ### 예시 요청
        ```json
        {
          "year": 2026,
          "month": 3,
          "country": "미국"
        }
        ```
        
        ### 예시 응답
        ```json
        {
          "success": true,
          "year": 2026,
          "month": 3,
          "country": "미국",
          "predicted_rate": 1445.50,
          "currency": "USD",
          "change_rate": 1.76,
          "change_direction": "상승"
        }
        ```
        """,
        request_body=ExchangeRatePredictionSerializer,
        responses={
            200: openapi.Response(
                description="✅ 환율 예측 성공",
                examples={
                    "application/json": {
                        "success": True,
                        "year": 2026,
                        "month": 1,
                        "country": "미국",
                        "predicted_rate": 1445.03,
                        "currency": "USD",
                        "latest_rate": 1420.00,
                        "latest_date": "2025년 10월",
                        "change_rate": 1.76,
                        "change_direction": "상승",
                        "months_ahead": 3,
                        "note": "AI 예측 결과 (3개월 후)"
                    }
                }
            ),
            400: "❌ 잘못된 요청 (유효하지 않은 날짜 또는 국가)"
        },
        tags=["Exchange Rate"]
    )
    def post(self, request, format=None):
        serializer = ExchangeRatePredictionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        year = serializer.validated_data['year']
        month = serializer.validated_data['month']
        country = serializer.validated_data['country']
        
        try:
            # 예측 모델 초기화 및 예측
            predictor = ExchangeRatePredictor()
            result = predictor.predict_exchange_rate(year, month, country)
            
            if result["success"]:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
        except FileNotFoundError as e:
            return Response({
                "success": False,
                "error": f"모델 파일을 찾을 수 없습니다: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({
                "success": False,
                "error": f"서버 오류: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)