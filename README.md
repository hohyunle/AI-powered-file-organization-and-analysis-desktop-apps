# AI 파일 정리 도우미

피그마 디자인을 기반으로 구현한 AI 기반 파일 정리 데스크톱 애플리케이션입니다.

## 🏗️ 프로젝트 구조

```
progect_chang/
├── frontend/                    # Electron 프론트엔드
│   ├── main/                   # 메인 프로세스
│   │   └── main.js            # Electron 메인 프로세스
│   ├── preload/                # 보안 브릿지
│   │   └── preload.js         # IPC 보안 브릿지
│   ├── renderer/              # UI 렌더러
│   │   ├── index.html         # 메인 대시보드
│   │   ├── settings.html      # 설정 화면
│   │   ├── file-list.html     # 파일 목록 화면
│   │   ├── styles.css         # 스타일시트
│   │   ├── renderer.js        # 메인 UI 로직
│   │   ├── settings.js        # 설정 화면 로직
│   │   └── file-list.js       # 파일 목록 로직
│   └── assets/                 # 아이콘, 이미지 등
├── backend/                     # Python 백엔드
│   ├── main.py                 # Worker 메인 진입점
│   ├── requirements.txt        # Python 의존성
│   ├── config/                 # 설정 관리
│   │   ├── settings.py        # 설정 클래스
│   │   └── worker_config.json # 설정 파일
│   ├── services/               # 서비스 모듈들
│   │   ├── file_watcher.py    # 파일 시스템 감시
│   │   ├── text_extractor.py  # 텍스트 추출
│   │   ├── database_manager.py # DB 연동
│   │   ├── mcp_client.py      # MCP 통신
│   │   └── organizer.py       # 파일 정리
│   ├── models/                 # 데이터 모델
│   ├── utils/                  # 유틸리티
│   └── logs/                   # 로그 파일
├── docs/                        # 문서
│   └── API_CONTRACT.md        # API 계약서
├── solution/                    # 기존 솔루션 파일들
├── package.json                # 프로젝트 설정
└── README.md                   # 프로젝트 문서
```

## 🚀 시작하기

### 설치

```bash
# Node.js 의존성 설치
npm install

# Python 의존성 설치
cd backend
pip install -r requirements.txt
```

### 개발 모드 실행

```bash
# Electron 앱 실행
npm run dev

# Python Worker 별도 실행 (선택사항)
cd backend
python main.py
```

### 프로덕션 빌드

```bash
npm run build
```

## 🐍 백엔드 (Python Worker)

Python Worker는 Electron 메인 프로세스에서 `child_process`로 실행되는 별도의 Python 프로세스입니다.

### **주요 기능:**
- **파일 시스템 감시**: `watchdog` 라이브러리로 실시간 파일 변경 감지
- **텍스트 추출**: PDF, PPTX, DOCX, Excel, 이미지(OCR) 등에서 텍스트 추출
- **AI 분류**: MCP를 통해 LLM과 연동하여 파일 자동 분류
- **데이터베이스 연동**: PostgreSQL과 연결하여 파일 정보 저장
- **실시간 통신**: Electron과 stdin/stdout을 통한 양방향 통신

### **통신 방식:**
```
Electron Main Process (Node.js)
    ↓ child_process.spawn('python', ['backend/main.py'])
Python Worker Process
    ↓ stdin/stdout JSON 통신
실시간 명령/응답 처리
```

### **실행 방법:**
```bash
# 의존성 설치
cd backend
pip install -r requirements.txt

# 직접 실행
python main.py

# 또는 배치 파일 사용 (Windows)
start_worker.bat
```

## 🎨 프론트엔드 (Electron)

### 피그마 디자인 기반 구현
- **메인 대시보드**: 모니터링 상태, 빠른 액션, 자동 정리 설정
- **반응형 디자인**: 다양한 화면 크기 지원
- **Inter 폰트**: 깔끔한 타이포그래피
- **색상 팔레트**: 피그마와 동일한 색상 시스템

### 주요 컴포넌트
1. **헤더**: 앱 제목 + 설정 버튼
2. **상태 카드**: 모니터링 폴더, 대기 파일, 마지막 정리
3. **빠른 액션**: 지금 정리하기, 정리 기준 불러오기, 파일 목록 보기
4. **자동 정리 설정**: 토글 스위치로 ON/OFF

### 인터랙션
- **버튼 클릭**: 각 액션에 대한 피드백
- **토글 스위치**: 자동 정리 설정 변경
- **키보드 단축키**: Ctrl+S (설정), Ctrl+Enter (정리 시작), F5 (새로고침)
- **알림 시스템**: 성공/실패 메시지 표시

## 🛠️ 기술 스택

### **프론트엔드 (Electron)**
- **Electron**: 크로스플랫폼 데스크톱 앱
- **HTML/CSS/JavaScript**: 순수 웹 기술
- **IPC**: 메인-렌더러 프로세스 간 안전한 통신
- **Context Isolation**: 보안 강화

### **백엔드 (Python Worker)**
- **Python 3.8+**: 메인 워커 언어
- **watchdog**: 파일 시스템 감시
- **PyMuPDF**: PDF 텍스트 추출
- **python-pptx/docx**: Office 문서 처리
- **pytesseract**: 이미지 OCR
- **SQLAlchemy**: PostgreSQL ORM
- **httpx**: MCP 통신

## 📱 화면 구성

### 메인 대시보드
```
┌─────────────────────────────────────────────────────────┐
│ 📂 파일 정리 도우미                    ⚙️ 설정          │
├─────────────────────────────────────────────────────────┤
│ 📊 모니터링 상태                                        │
│ ┌─────────────┬─────────────┬─────────────┐            │
│ │ 📁 모니터링 │ 📄 대기중인 │ ⏰ 마지막    │            │
│ │ C:/Downloads │ 47개        │ 2시간 전     │            │
│ └─────────────┴─────────────┴─────────────┘            │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────┬─────────────┬─────────────┐            │
│ │ 🚀 지금     │ 📋 정리기준 │ 📋 파일목록 │            │
│ │ 정리하기    │ 불러오기    │ 보기        │            │
│ └─────────────┴─────────────┴─────────────┘            │
├─────────────────────────────────────────────────────────┤
│ ⚡ 자동 정리 조건                    [토글 스위치]        │
│ 파일이 50개 이상 쌓이면 자동으로 정리 제안              │
└─────────────────────────────────────────────────────────┘
```

## 🔧 개발 가이드

### 프론트엔드 구조
- **main.js**: Electron 앱 초기화, 윈도우 생성 및 관리, IPC 핸들러 등록
- **preload.js**: 보안 브릿지 역할, 렌더러 프로세스에 안전한 API 노출
- **renderer/**: UI 렌더링 및 사용자 인터랙션, Electron API를 통한 메인 프로세스와 통신

### 백엔드 구조
- **main.py**: Python Worker 메인 진입점, 비동기 메인 루프
- **services/**: 각종 서비스 모듈 (파일 감시, 텍스트 추출, DB 관리 등)
- **config/**: 설정 관리 및 환경 변수 처리
- **models/**: 데이터 모델 정의
- **utils/**: 공통 유틸리티 함수들

## 📋 다음 단계

1. **PostgreSQL 설정**: 로컬 데이터베이스 구성
2. **MCP 서버**: LLM 연동 서버 구축
3. **파일 감시 테스트**: 실제 파일 시스템 감시 동작 확인
4. **텍스트 추출 테스트**: 다양한 파일 형식에서 텍스트 추출 테스트
5. **AI 분류 테스트**: MCP를 통한 파일 자동 분류 테스트

## 🎯 현재 상태

- ✅ **프로젝트 구조 재구성**: 프론트엔드/백엔드 분리 완료
- ✅ **UI 구현 완료**: 피그마 디자인 기반
- ✅ **기본 인터랙션**: 버튼 클릭, 토글 등
- ✅ **IPC 통신**: 메인-렌더러 간 안전한 통신
- ✅ **Python Worker 구조**: 완전한 모듈화된 워커 시스템
- ✅ **Electron-Python 통신**: stdin/stdout 기반 양방향 통신
- ⏳ **데이터베이스 연동**: PostgreSQL 설정 및 테스트
- ⏳ **MCP 서버**: LLM 연동 서버 구축
- ⏳ **실제 파일 처리**: 파일 감시 및 텍스트 추출 테스트

## 📞 지원

프로젝트에 대한 문의사항이나 버그 리포트는 이슈를 통해 제출해주세요.