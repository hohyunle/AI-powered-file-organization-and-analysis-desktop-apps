// DOM이 로드되면 실행
document.addEventListener('DOMContentLoaded', async () => {
    console.log('파일 정리 도우미 앱이 시작되었습니다.');
    
    // 대시보드 데이터 로드
    await loadDashboardData();
    
    // 이벤트 리스너 등록
    setupEventListeners();
    
    // 설정 변경 이벤트 리스너 등록
    setupConfigUpdateListener();
    
    // 파일 개수 주기적 업데이트 (30초마다)
    setInterval(updateFileCount, 30000);
    
    // 파일 감지 이벤트 리스너 등록
    setupFileDetectionListener();
});

// 대시보드 데이터 로드
async function loadDashboardData() {
    try {
        const stats = await window.electronAPI.getDashboardStats();
        
        // 상태 정보 업데이트
        document.getElementById('monitoring-folder').textContent = stats.monitoringFolder;
        document.getElementById('pending-files').textContent = `${stats.pendingFiles}개`;
        document.getElementById('last-organized').textContent = stats.lastOrganized;
        
        // 자동 정리 토글 상태 설정
        const toggle = document.getElementById('auto-organize-toggle');
        toggle.checked = stats.autoOrganizeEnabled;
        
        console.log('대시보드 데이터 로드 완료:', stats);
    } catch (error) {
        console.error('대시보드 데이터 로드 실패:', error);
    }
}

// 이벤트 리스너 설정
function setupEventListeners() {
    console.log('이벤트 리스너 설정 시작');
    
    // 설정 버튼
    const settingsBtn = document.getElementById('settings-btn');
    if (settingsBtn) {
        settingsBtn.addEventListener('click', async () => {
            console.log('설정 버튼 클릭');
            try {
                await window.electronAPI.openSettings();
            } catch (error) {
                console.error('설정 창 열기 실패:', error);
                showNotification('설정 창 열기에 실패했습니다.', 'error');
            }
        });
        console.log('설정 버튼 이벤트 리스너 등록 완료');
    } else {
        console.error('설정 버튼을 찾을 수 없습니다');
    }
    
    // 지금 정리하기 버튼
    const startCleanupBtn = document.getElementById('start-cleanup-btn');
    if (startCleanupBtn) {
        startCleanupBtn.addEventListener('click', async () => {
            console.log('지금 정리하기 버튼 클릭');
            const button = document.getElementById('start-cleanup-btn');
            const originalText = button.querySelector('.btn-text').textContent;
            
            // 버튼 상태 변경
            button.disabled = true;
            button.querySelector('.btn-text').textContent = '정리 중...';
            button.style.opacity = '0.7';
            
            try {
                const result = await window.electronAPI.startCleanup();
                if (result.success) {
                    console.log('정리 시작 성공');
                    showNotification('정리 작업이 시작되었습니다.', 'success');
                }
            } catch (error) {
                console.error('정리 시작 실패:', error);
                showNotification('정리 작업 시작에 실패했습니다.', 'error');
            } finally {
                // 버튼 상태 복원
                button.disabled = false;
                button.querySelector('.btn-text').textContent = originalText;
                button.style.opacity = '1';
            }
        });
        console.log('지금 정리하기 버튼 이벤트 리스너 등록 완료');
    } else {
        console.error('지금 정리하기 버튼을 찾을 수 없습니다');
    }
    
    // 정리 기준 불러오기 버튼
    document.getElementById('load-rules-btn').addEventListener('click', async () => {
        console.log('정리 기준 불러오기 버튼 클릭');
        showNotification('정리 기준을 불러오는 중...', 'info');
        try {
            await window.electronAPI.loadCleanupRules();
            showNotification('정리 기준을 불러왔습니다.', 'success');
        } catch (error) {
            console.error('정리 기준 불러오기 실패:', error);
            showNotification('정리 기준 불러오기에 실패했습니다.', 'error');
        }
    });
    
    // 파일 목록 보기 버튼
    document.getElementById('view-files-btn').addEventListener('click', async () => {
        console.log('파일 목록 보기 버튼 클릭');
        try {
            await window.electronAPI.viewFileList();
        } catch (error) {
            console.error('파일 목록 창 열기 실패:', error);
            showNotification('파일 목록 창 열기에 실패했습니다.', 'error');
        }
    });
    
    // 자동 정리 토글
    document.getElementById('auto-organize-toggle').addEventListener('change', async (event) => {
        const enabled = event.target.checked;
        console.log('자동 정리 설정 변경:', enabled);
        
        try {
            const result = await window.electronAPI.toggleAutoOrganize(enabled);
            if (result.success) {
                const status = enabled ? '활성화' : '비활성화';
                showNotification(`자동 정리가 ${status}되었습니다.`, 'success');
            } else {
                showNotification('자동 정리 설정 변경에 실패했습니다.', 'error');
            }
        } catch (error) {
            console.error('자동 정리 설정 변경 실패:', error);
            showNotification('자동 정리 설정 변경 중 오류가 발생했습니다.', 'error');
        }
    });
    
    // 알림 닫기 버튼
    document.getElementById('notification-close').addEventListener('click', () => {
        hideNotification();
    });
}

// 알림 메시지 표시
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    const messageElement = document.getElementById('notification-message');
    
    messageElement.textContent = message;
    notification.className = `notification ${type} show`;
    
    // 3초 후 자동 숨김
    setTimeout(() => {
        hideNotification();
    }, 3000);
}

// 알림 메시지 숨김
function hideNotification() {
    const notification = document.getElementById('notification');
    notification.className = 'notification hidden';
}

// 설정 변경 이벤트 리스너 설정
function setupConfigUpdateListener() {
    window.electronAPI.onConfigUpdated(async (event, config) => {
        console.log('설정 변경 감지:', config);
        
        // 모니터링 폴더 업데이트
        if (config.monitoringFolder) {
            document.getElementById('monitoring-folder').textContent = config.monitoringFolder;
            
            // 모니터링 폴더의 파일 개수도 다시 계산
            await updateFileCount();
        }
        
        // 자동 정리 설정 업데이트
        if (typeof config.autoOrganize !== 'undefined') {
            const toggle = document.getElementById('auto-organize-toggle');
            toggle.checked = config.autoOrganize;
        }
        
        showNotification('설정이 업데이트되었습니다.', 'success');
    });
}

// 파일 개수 업데이트 함수
async function updateFileCount() {
    try {
        const stats = await window.electronAPI.getDashboardStats();
        const currentCount = document.getElementById('pending-files').textContent;
        const newCount = `${stats.pendingFiles}개`;
        
        // 파일 개수가 변경된 경우에만 업데이트
        if (currentCount !== newCount) {
            document.getElementById('pending-files').textContent = newCount;
            console.log(`파일 개수 업데이트: ${currentCount} → ${newCount}`);
        }
    } catch (error) {
        console.error('파일 개수 업데이트 실패:', error);
    }
}

// 파일 감지 이벤트 리스너 설정
function setupFileDetectionListener() {
    // Electron IPC 이벤트 리스너 (preload API 사용)
    if (window.electronAPI) {
        // onFileDetected 이벤트 리스너 추가
        window.electronAPI.onFileDetected((event, data) => {
            console.log('새 파일이 감지되었습니다:', data.path);
            
            // 대시보드 파일 개수 즉시 업데이트
            updateFileCount();
            
            // 알림 표시
            const fileName = data.path.split(/[/\\]/).pop(); // 파일명만 추출
            showNotification(`새 파일이 감지되었습니다: ${fileName}`, 'info');
            
            // 파일 개수 애니메이션 효과
            const pendingFilesElement = document.getElementById('pending-files');
            pendingFilesElement.style.transform = 'scale(1.1)';
            pendingFilesElement.style.transition = 'transform 0.3s ease';
            setTimeout(() => {
                pendingFilesElement.style.transform = 'scale(1)';
            }, 300);
        });
    }
}