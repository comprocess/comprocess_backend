import asyncio
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Travel_Schedule, UploadedImage
from .serializers import TravelScheduleSerializer, ImageUploadSerializer
from comprocessSW.ai_module.kjy import generate_travel_plan
from comprocessSW.ai_module.kwy import KoreanImageAnalyzer

# Create your views here.
class TravelScheduleAI(APIView):
    def post(self, request):
        serializer = TravelScheduleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        schedule_obj = serializer.save()

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

        return Response({
            "input": serializer.data,
            "ai_result": ai_result
        }, status=status.HTTP_200_OK)


class ImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    @swagger_auto_schema(
        operation_description="이미지 업로드",
        manual_parameters=[
            openapi.Parameter(
                'image',
                openapi.IN_FORM,
                description="업로드할 이미지 파일",
                type=openapi.TYPE_FILE,
                required=True
            ),
            openapi.Parameter(
                'title',
                openapi.IN_FORM,
                description="이미지 제목",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'description',
                openapi.IN_FORM,
                description="이미지 설명",
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        responses={201: ImageUploadSerializer()}
    )
    def post(self, request, format=None):
        serializer = ImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_image = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="업로드된 이미지 목록 조회",
        responses={200: ImageUploadSerializer(many=True)}
    )
    def get(self, request, format=None):
        images = UploadedImage.objects.all().order_by('-uploaded_at')
        serializer = ImageUploadSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ImageAnalyzeView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_description="이미지 업로드 및 AI 분석 (한국 관광지/음식)",
        manual_parameters=[
            openapi.Parameter(
                'image',
                openapi.IN_FORM,
                description="분석할 이미지 파일",
                type=openapi.TYPE_FILE,
                required=True
            ),
            openapi.Parameter(
                'title',
                openapi.IN_FORM,
                description="이미지 제목 (선택사항)",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'description',
                openapi.IN_FORM,
                description="이미지 설명 (선택사항)",
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        responses={
            201: openapi.Response(
                description="이미지 업로드 및 분석 완료",
                examples={
                    "application/json": {
                        "image_info": {
                            "id": 1,
                            "image": "/media/uploads/image.jpg",
                            "title": "제목",
                            "uploaded_at": "2025-11-26T..."
                        },
                        "ai_analysis": {
                            "success": True,
                            "data": {
                                "type": "음식",
                                "음식명": "김치찌개",
                                "대부분_들어가있는_재료": ["김치", "돼지고기", "두부"]
                            }
                        }
                    }
                }
            )
        }
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