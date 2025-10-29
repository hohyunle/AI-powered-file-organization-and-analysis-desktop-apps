@echo off
echo AI 파일 정리 도우미 - Python Worker 시작
echo.

REM Python 가상환경 활성화 (선택사항)
REM call venv\Scripts\activate

REM 의존성 설치 확인
echo 의존성 설치 중...
pip install -r requirements.txt

REM Python Worker 시작
echo Python Worker 시작 중...
python main.py

pause
