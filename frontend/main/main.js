const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

// 개발 모드 확인
const isDev = process.argv.includes('--dev');

let mainWindow;
let settingsWindow = null;
let fileListWindow = null;
let pythonWorker = null;

function createWindow() {
  // 메인 윈도우 생성
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, '../preload/preload.js')
    },
    icon: path.join(__dirname, '../assets/icon.png'),
    titleBarStyle: 'default',
    show: false
  });

  // HTML 파일 로드
  mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));

  // 개발 모드에서 DevTools 열기
  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  // 윈도우가 준비되면 표시
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // 윈도우가 닫힐 때
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// 설정 윈도우 생성
function createSettingsWindow() {
  if (settingsWindow) {
    settingsWindow.focus();
    return;
  }

  settingsWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 1000,
    minHeight: 700,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, '../preload/preload.js')
    },
    icon: path.join(__dirname, '../assets/icon.png'),
    titleBarStyle: 'default',
    show: false,
    parent: mainWindow
  });

  // 설정 화면 HTML 로드
  settingsWindow.loadFile(path.join(__dirname, '../renderer/settings.html'));

  if (isDev) {
    settingsWindow.webContents.openDevTools();
  }

  settingsWindow.once('ready-to-show', () => {
    settingsWindow.show();
  });

  settingsWindow.on('closed', () => {
    settingsWindow = null;
  });
}

// 파일 목록 윈도우 생성
function createFileListWindow() {
  if (fileListWindow) {
    fileListWindow.focus();
    return;
  }

  fileListWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, '../preload/preload.js')
    },
    icon: path.join(__dirname, '../assets/icon.png'),
    titleBarStyle: 'default',
    show: false,
    parent: mainWindow
  });

  // 파일 목록 화면 HTML 로드
  fileListWindow.loadFile(path.join(__dirname, '../renderer/file-list.html'));

  if (isDev) {
    fileListWindow.webContents.openDevTools();
  }

  fileListWindow.once('ready-to-show', () => {
    fileListWindow.show();
  });

  fileListWindow.on('closed', () => {
    fileListWindow = null;
  });
}

// 앱이 준비되면 윈도우 생성
app.whenReady().then(createWindow);

// 모든 윈도우가 닫히면 앱 종료 (macOS 제외)
app.on('window-all-closed', () => {
  // Python Worker 종료
  if (pythonWorker) {
    pythonWorker.kill('SIGTERM');
  }
  
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// macOS에서 독 아이콘 클릭 시 윈도우 재생성
app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// IPC 핸들러들 - 완전한 API 계약 정의

// === 앱 정보 ===
ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

// === 대시보드 데이터 ===
ipcMain.handle('get-dashboard-stats', async () => {
  // TODO: 실제 데이터베이스에서 통계 가져오기
  return {
    monitoringFolder: 'C:/Downloads',
    pendingFiles: 47,
    lastOrganized: '2시간 전',
    autoOrganizeEnabled: true
  };
});

// === 파일 정리 관련 ===
ipcMain.handle('start-cleanup', async () => {
  // TODO: Python Worker에게 정리 시작 신호 보내기
  console.log('정리 시작 요청');
  return { success: true };
});

ipcMain.handle('load-cleanup-rules', async () => {
  // TODO: 정리 기준 불러오기
  console.log('정리 기준 불러오기 요청');
  return { success: true, rules: [] };
});

ipcMain.handle('view-file-list', async () => {
  console.log('파일 목록 보기 요청');
  createFileListWindow();
  return { success: true };
});

// === 설정 관련 ===
ipcMain.handle('toggle-auto-organize', async (event, enabled) => {
  // TODO: 설정 업데이트
  console.log('자동 정리 설정 변경:', enabled);
  return { success: true };
});

ipcMain.handle('open-settings', async () => {
  console.log('설정 창 열기 요청');
  createSettingsWindow();
  return { success: true };
});

// === 파일 관리 관련 ===
ipcMain.handle('get-file-list', async (event, filters = {}) => {
  // TODO: 파일 목록 가져오기 (필터 적용)
  console.log('파일 목록 가져오기:', filters);
  return { success: true, files: [] };
});

ipcMain.handle('get-file-analysis', async (event, fileId) => {
  // TODO: 특정 파일의 분석 결과 가져오기
  console.log('파일 분석 결과 가져오기:', fileId);
  return { success: true, analysis: null };
});

// === 작업 이력 관련 ===
ipcMain.handle('get-job-history', async (event, limit = 50) => {
  // TODO: 작업 이력 가져오기
  console.log('작업 이력 가져오기:', limit);
  return { success: true, jobs: [] };
});

ipcMain.handle('undo-job', async (event, jobId) => {
  // TODO: 작업 되돌리기
  console.log('작업 되돌리기:', jobId);
  return { success: true };
});

// === 설정 관리 ===
ipcMain.handle('get-config', async () => {
  // TODO: 현재 설정 가져오기
  console.log('설정 가져오기');
  return {
    monitoringFolder: 'C:/Downloads',
    movingFolder: 'C:/Documents/정리된 파일',
    threshold: 50,
    autoOrganize: true
  };
});

ipcMain.handle('update-config', async (event, config) => {
  // TODO: 설정 업데이트
  console.log('설정 업데이트:', config);
  return { success: true };
});

// === Python Worker 통신 ===

// Python Worker 시작
ipcMain.handle('start-python-worker', async () => {
  try {
    if (pythonWorker) {
      console.log('Python Worker가 이미 실행 중입니다.');
      return { success: true, pid: pythonWorker.pid };
    }

    // Python Worker 프로세스 시작
    const workerPath = path.join(__dirname, '../../backend/main.py');
    pythonWorker = spawn('python', [workerPath], {
      cwd: path.join(__dirname, '../../backend'),
      stdio: ['pipe', 'pipe', 'pipe']
    });

    // Python Worker 출력 처리
    pythonWorker.stdout.on('data', (data) => {
      const output = data.toString();
      console.log('Python Worker:', output);
      
      // 상태 업데이트 메시지 처리
      if (output.startsWith('STATUS:')) {
        try {
          const statusData = JSON.parse(output.substring(7));
          if (mainWindow) {
            mainWindow.webContents.send('worker-status-update', statusData);
          }
        } catch (e) {
          console.error('상태 데이터 파싱 오류:', e);
        }
      }
    });

    pythonWorker.stderr.on('data', (data) => {
      console.error('Python Worker 오류:', data.toString());
    });

    pythonWorker.on('close', (code) => {
      console.log(`Python Worker 종료됨 (코드: ${code})`);
      pythonWorker = null;
      if (mainWindow) {
        mainWindow.webContents.send('worker-stopped', { code });
      }
    });

    pythonWorker.on('error', (error) => {
      console.error('Python Worker 시작 오류:', error);
      pythonWorker = null;
    });

    console.log(`Python Worker 시작됨 (PID: ${pythonWorker.pid})`);
    return { success: true, pid: pythonWorker.pid };

  } catch (error) {
    console.error('Python Worker 시작 실패:', error);
    return { success: false, error: error.message };
  }
});

// Python Worker 종료
ipcMain.handle('stop-python-worker', async () => {
  try {
    if (pythonWorker) {
      pythonWorker.kill('SIGTERM');
      
      // 5초 후 강제 종료
      setTimeout(() => {
        if (pythonWorker && !pythonWorker.killed) {
          pythonWorker.kill('SIGKILL');
        }
      }, 5000);
      
      console.log('Python Worker 종료 요청됨');
      return { success: true };
    } else {
      console.log('실행 중인 Python Worker가 없습니다.');
      return { success: true };
    }
  } catch (error) {
    console.error('Python Worker 종료 실패:', error);
    return { success: false, error: error.message };
  }
});

// Python Worker 상태 확인
ipcMain.handle('get-worker-status', async () => {
  if (pythonWorker && !pythonWorker.killed) {
    return { 
      success: true, 
      status: 'running', 
      pid: pythonWorker.pid 
    };
  } else {
    return { 
      success: true, 
      status: 'stopped', 
      pid: null 
    };
  }
});

// Python Worker에게 명령 전송
ipcMain.handle('send-worker-command', async (event, command) => {
  try {
    if (!pythonWorker || pythonWorker.killed) {
      return { success: false, error: 'Python Worker가 실행되지 않았습니다.' };
    }

    // 명령을 JSON으로 직렬화하여 전송
    const commandJson = JSON.stringify(command);
    pythonWorker.stdin.write(commandJson + '\n');
    
    console.log('Python Worker에게 명령 전송:', command);
    return { success: true };

  } catch (error) {
    console.error('명령 전송 실패:', error);
    return { success: false, error: error.message };
  }
});
