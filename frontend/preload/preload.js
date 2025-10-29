const { contextBridge, ipcRenderer } = require('electron');

// 완전한 API 계약 정의 - UI ↔ Main ↔ Worker
contextBridge.exposeInMainWorld('electronAPI', {
  
  // === 앱 정보 ===
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  
  // === 대시보드 데이터 ===
  getDashboardStats: () => ipcRenderer.invoke('get-dashboard-stats'),
  
  // === 파일 정리 관련 ===
  startCleanup: () => ipcRenderer.invoke('start-cleanup'),
  loadCleanupRules: () => ipcRenderer.invoke('load-cleanup-rules'),
  viewFileList: () => ipcRenderer.invoke('view-file-list'),
  
  // === 설정 관련 ===
  toggleAutoOrganize: (enabled) => ipcRenderer.invoke('toggle-auto-organize', enabled),
  openSettings: () => ipcRenderer.invoke('open-settings'),
  
  // === 파일 관리 관련 ===
  getFileList: (filters = {}) => ipcRenderer.invoke('get-file-list', filters),
  getFileAnalysis: (fileId) => ipcRenderer.invoke('get-file-analysis', fileId),
  
  // === 작업 이력 관련 ===
  getJobHistory: (limit = 50) => ipcRenderer.invoke('get-job-history', limit),
  undoJob: (jobId) => ipcRenderer.invoke('undo-job', jobId),
  
  // === 설정 관리 ===
  getConfig: () => ipcRenderer.invoke('get-config'),
  updateConfig: (config) => ipcRenderer.invoke('update-config', config),
  
  // === Python Worker 통신 ===
  startPythonWorker: () => ipcRenderer.invoke('start-python-worker'),
  stopPythonWorker: () => ipcRenderer.invoke('stop-python-worker'),
  getWorkerStatus: () => ipcRenderer.invoke('get-worker-status'),
  
  // === 이벤트 리스너 (향후 실시간 업데이트용) ===
  onWorkerStatusChange: (callback) => {
    ipcRenderer.on('worker-status-change', callback);
  },
  
  onFileUpdate: (callback) => {
    ipcRenderer.on('file-update', callback);
  },
  
  onJobProgress: (callback) => {
    ipcRenderer.on('job-progress', callback);
  },
  
  // 이벤트 리스너 제거
  removeAllListeners: (channel) => {
    ipcRenderer.removeAllListeners(channel);
  }
});
