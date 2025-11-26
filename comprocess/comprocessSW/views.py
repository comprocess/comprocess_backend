import asyncio
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Travel_Schedule
from .serializers import TravelScheduleSerializer
from comprocessSW.ai_module.kjy import generate_travel_plan

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