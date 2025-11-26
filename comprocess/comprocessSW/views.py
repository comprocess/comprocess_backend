import asyncio
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Travel_Schedule
from .serializers import TravelScheduleSerializer
from comprocessSW.ai_module.kjy import generate_travel_plan

# AI 모델 관련 import
import os
import numpy as np
import pandas as pd
import pickle
from datetime import datetime, timedelta
from tensorflow.keras.models import load_model
from django.http import JsonResponse

# 모델 & 스케일러 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_DIR = os.path.join(BASE_DIR, "ljm", "save")

MODEL_PATH = os.path.join(SAVE_DIR, "model.h5")  # 실제 파일명에 맞춰 변경해!
SCALER_PATH = os.path.join(SAVE_DIR, "scaler.pkl")

# 모델 불러오기
model = load_model(MODEL_PATH)

# 스케일러 불러오기
with open(SCALER_PATH, "rb") as f:
    scaler = pickle.load(f)

def predict_rate(target_date: datetime):
    """
    특정 날짜(target_date)의 환율을 예측한다.
    """

    # 예: 데이터를 30일치 입력으로 예측한 경우
    look_back = 30

    # 과거 30일의 실제 환율 데이터를 로드하는 로직이 필요함
    # 여기에서는 예시로 dummy 데이터를 사용 (나중에 DB나 CSV로 교체 가능)
    # shape = (30, 1)
    past_rates = np.random.uniform(1200, 1500, size=(look_back, 1))

    # 스케일러 적용
    scaled = scaler.transform(past_rates)

    # LSTM 입력 형태 맞추기
    X = np.array(scaled).reshape(1, look_back, 1)

    pred_scaled = model.predict(X)
    pred = scaler.inverse_transform(pred_scaled)[0][0]

    return float(pred)

def exchange_service(request):
    """
    파라미터:
    - current_year, current_month, current_day
    - travel_year, travel_month, travel_day
    - country (미국, 일본 등)
    - budget_krw (예산 원화)
    """

    try:
        current_date = datetime(
            int(request.GET.get("current_year")),
            int(request.GET.get("current_month")),
            int(request.GET.get("current_day"))
        )

        travel_date = datetime(
            int(request.GET.get("travel_year")),
            int(request.GET.get("travel_month")),
            int(request.GET.get("travel_day"))
        )

        budget_krw = int(request.GET.get("budget_krw"))
        country = request.GET.get("country")

    except:
        return JsonResponse({"error": "파라미터 오류"}, status=400)

    # 1) 여행 날짜 환율 예측
    travel_rate = predict_rate(travel_date)

    # 예산을 환전하면 얼마? (예: USD 기준)
    travel_money = budget_krw / travel_rate

    # 2) 현재~여행 날짜 사이에서 가장 좋은 환율 찾기
    best_day = None
    best_rate = 999999
    day = current_date

    while day <= travel_date:
        r = predict_rate(day)
        if r < best_rate:
            best_rate = r
            best_day = day
        day += timedelta(days=1)

    best_money = budget_krw / best_rate

    result = {
        "travel_date_rate": round(travel_rate, 2),
        "travel_date_money": round(travel_money, 2),

        "best_day": best_day.strftime("%Y-%m-%d"),
        "best_rate": round(best_rate, 2),
        "best_day_money": round(best_money, 2),

        "unit": "USD"  # 나중에 country별로 자동 변경 가능
    }

    return JsonResponse(result, safe=False)

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
    
