# 환율 예측 API 사용법

## API 엔드포인트
POST http://localhost:8000/api/exchange-rate-predict/

## 요청 예시

### cURL
```bash
curl -X POST http://localhost:8000/api/exchange-rate-predict/ \
  -H "Content-Type: application/json" \
  -d '{
    "year": 2026,
    "month": 3,
    "country": "미국"
  }'
```

### Python requests
```python
import requests

url = "http://localhost:8000/api/exchange-rate-predict/"
data = {
    "year": 2026,
    "month": 3,
    "country": "미국"
}

response = requests.post(url, json=data)
print(response.json())
```

### JavaScript fetch
```javascript
fetch('http://localhost:8000/api/exchange-rate-predict/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    year: 2026,
    month: 3,
    country: '미국'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## 국가 옵션
- "미국" - USD 환율
- "일본" - JPY(100엔당) 환율

## 응답 예시

### 성공
```json
{
  "success": true,
  "year": 2026,
  "month": 3,
  "country": "미국",
  "predicted_rate": 1350.50,
  "currency": "USD",
  "latest_rate": 1320.00,
  "latest_date": "2025년 10월",
  "change_rate": 2.31,
  "change_direction": "상승",
  "months_ahead": 5,
  "is_historical": false,
  "note": "AI 예측 결과 (5개월 후)"
}
```

### 에러
```json
{
  "success": false,
  "error": "월은 1부터 12 사이의 값이어야 합니다."
}
```
