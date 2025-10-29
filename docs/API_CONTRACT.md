# IPC API 계약 정의

UI ↔ Main Process ↔ Python Worker 간의 완전한 통신 계약입니다.

## 📋 API 카테고리

### 1. 앱 정보
```javascript
// 앱 버전 정보
getAppVersion() → string
```

### 2. 대시보드 데이터
```javascript
// 대시보드 통계 정보
getDashboardStats() → {
  monitoringFolder: string,
  pendingFiles: number,
  lastOrganized: string,
  autoOrganizeEnabled: boolean
}
```

### 3. 파일 정리 관련
```javascript
// 정리 작업 시작
startCleanup() → { success: boolean }

// 정리 기준 불러오기
loadCleanupRules() → { success: boolean, rules: Array }

// 파일 목록 보기
viewFileList() → { success: boolean, files: Array }
```

### 4. 설정 관련
```javascript
// 자동 정리 설정 토글
toggleAutoOrganize(enabled: boolean) → { success: boolean }

// 설정 창 열기
openSettings() → { success: boolean }
```

### 5. 파일 관리 관련
```javascript
// 파일 목록 가져오기 (필터 적용)
getFileList(filters: object) → { success: boolean, files: Array }

// 특정 파일의 분석 결과 가져오기
getFileAnalysis(fileId: number) → { success: boolean, analysis: object }
```

### 6. 작업 이력 관련
```javascript
// 작업 이력 가져오기
getJobHistory(limit: number) → { success: boolean, jobs: Array }

// 작업 되돌리기
undoJob(jobId: number) → { success: boolean }
```

### 7. 설정 관리
```javascript
// 현재 설정 가져오기
getConfig() → {
  monitoringFolder: string,
  movingFolder: string,
  threshold: number,
  autoOrganize: boolean
}

// 설정 업데이트
updateConfig(config: object) → { success: boolean }
```

### 8. Python Worker 통신
```javascript
// Python Worker 프로세스 시작
startPythonWorker() → { success: boolean, pid: number }

// Python Worker 프로세스 종료
stopPythonWorker() → { success: boolean }

// Python Worker 상태 확인
getWorkerStatus() → { success: boolean, status: string, pid: number }
```

### 9. 실시간 이벤트 (향후 구현)
```javascript
// Worker 상태 변경 이벤트
onWorkerStatusChange(callback: function) → void

// 파일 업데이트 이벤트
onFileUpdate(callback: function) → void

// 작업 진행률 이벤트
onJobProgress(callback: function) → void

// 이벤트 리스너 제거
removeAllListeners(channel: string) → void
```

## 🔄 데이터 흐름

### UI → Main Process
```
UI (renderer.js) 
  ↓ window.electronAPI.functionName()
Preload (preload.js) 
  ↓ ipcRenderer.invoke()
Main Process (main.js) 
  ↓ ipcMain.handle()
```

### Main Process → Python Worker (향후)
```
Main Process (main.js)
  ↓ child_process.spawn()
Python Worker (worker/main.py)
  ↓ subprocess communication
```

### Python Worker → Main Process (향후)
```
Python Worker (worker/main.py)
  ↓ stdout/stderr 또는 named pipe
Main Process (main.js)
  ↓ ipcMain.emit()
UI (renderer.js)
  ↓ event listeners
```

## 📝 사용 예시

### UI에서 API 호출
```javascript
// 대시보드 데이터 로드
const stats = await window.electronAPI.getDashboardStats();
console.log('모니터링 폴더:', stats.monitoringFolder);

// 정리 시작
const result = await window.electronAPI.startCleanup();
if (result.success) {
  console.log('정리 작업이 시작되었습니다.');
}

// 설정 변경
await window.electronAPI.toggleAutoOrganize(true);
```

### 이벤트 리스너 등록 (향후)
```javascript
// Worker 상태 변경 감지
window.electronAPI.onWorkerStatusChange((event, status) => {
  console.log('Worker 상태 변경:', status);
});

// 파일 업데이트 감지
window.electronAPI.onFileUpdate((event, fileData) => {
  console.log('새 파일 감지:', fileData);
});
```

## 🛡️ 보안 고려사항

1. **Context Isolation**: 렌더러 프로세스에서 Node.js API 직접 접근 불가
2. **API 제한**: 필요한 기능만 preload를 통해 노출
3. **입력 검증**: 모든 입력값에 대한 검증 필요
4. **에러 처리**: 모든 API 호출에 대한 적절한 에러 처리

## 🔧 확장 계획

1. **Python Worker 연동**: child_process를 통한 프로세스 통신
2. **실시간 업데이트**: WebSocket 또는 named pipe를 통한 실시간 데이터
3. **파일 시스템 감시**: watchdog을 통한 파일 변경 감지
4. **데이터베이스 연동**: PostgreSQL과의 연결
5. **MCP 서버**: LLM과의 표준화된 통신
