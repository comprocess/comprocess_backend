#!/usr/bin/env python
"""환율 예측 API 테스트 스크립트"""

import sys
from pathlib import Path

# Django 설정
sys.path.insert(0, str(Path(__file__).parent))
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comprocess.settings')

import django
django.setup()

from comprocessSW.ai_module.exchange_rate_predictor import ExchangeRatePredictor


def test_predictor():
    """예측기 테스트"""
    print("=" * 60)
    print("환율 예측 테스트")
    print("=" * 60)
    
    try:
        predictor = ExchangeRatePredictor()
        print("✅ 모델 로드 성공!\n")
        
        # 테스트 케이스들
        test_cases = [
            (2026, 1, "미국"),
            (2026, 1, "일본"),
            (2025, 12, "미국"),
        ]
        
        for year, month, country in test_cases:
            print(f"\n📅 {year}년 {month}월 {country} 환율 예측:")
            print("-" * 60)
            
            result = predictor.predict_exchange_rate(year, month, country)
            
            if result["success"]:
                print(f"✅ 예측 환율: {result['predicted_rate']:.2f} 원 ({result['currency']})")
                if not result.get("is_historical"):
                    print(f"   현재 환율: {result['latest_rate']:.2f} 원 ({result['latest_date']})")
                    print(f"   예상 변화: {result['change_rate']:.2f}% {result['change_direction']}")
                print(f"   참고: {result['note']}")
            else:
                print(f"❌ 오류: {result['error']}")
        
        print("\n" + "=" * 60)
        print("테스트 완료!")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_predictor()
