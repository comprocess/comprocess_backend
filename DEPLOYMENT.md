# Comprocess Backend - 배포 가이드

## 🚀 배포 전 체크리스트

### 1. 환경 변수 설정
`.env.example` 파일을 참고하여 `.env` 파일을 생성하세요:

```bash
cp comprocess/.env.example comprocess/.env
```

필수 환경 변수:
- `SECRET_KEY`: Django 시크릿 키
- `DEBUG`: 배포시 `False`로 설정
- `ALLOWED_HOSTS`: 배포 도메인 추가 (예: `yourdomain.com,www.yourdomain.com`)
- `CORS_ALLOWED_ORIGINS`: 프론트엔드 도메인 추가 (예: `https://yourdomain.com`)
- `OPENAI_API_KEY`: OpenAI API 키

### 2. 패키지 설치
```bash
cd comprocess
pip install -r requirements.txt
```

### 3. 데이터베이스 마이그레이션
```bash
python manage.py migrate
```

### 4. 정적 파일 수집
```bash
python manage.py collectstatic --noinput
```

### 5. 서버 실행

#### 개발 환경
```bash
python manage.py runserver
```

#### 프로덕션 환경 (Gunicorn)
```bash
gunicorn comprocess.wsgi:application --bind 0.0.0.0:8000
```

## 📦 배포 플랫폼별 가이드

### Heroku
1. Heroku CLI 설치 및 로그인
2. 앱 생성: `heroku create your-app-name`
3. 환경 변수 설정: `heroku config:set SECRET_KEY=...`
4. 배포: `git push heroku main`

### Railway
1. Railway 계정 연결
2. GitHub 리포지토리 연결
3. 환경 변수 설정
4. 자동 배포

### AWS EC2
1. EC2 인스턴스 생성 및 접속
2. Python 환경 설정
3. Nginx + Gunicorn 설정
4. SSL 인증서 설정 (Let's Encrypt)

## 🔒 보안 설정 (프로덕션)

배포시 `.env` 파일에서 다음 설정을 변경하세요:
```
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

## 📝 API 문서
배포 후 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: `https://yourdomain.com/swagger/`
- ReDoc: `https://yourdomain.com/redoc/`

## 🛠️ 문제 해결

### CORS 에러
프론트엔드 도메인이 `CORS_ALLOWED_ORIGINS`에 포함되어 있는지 확인하세요.

### 정적 파일 404 에러
`python manage.py collectstatic`을 실행했는지 확인하세요.

### 이미지 업로드 에러
`uploads/` 디렉토리에 쓰기 권한이 있는지 확인하세요.
