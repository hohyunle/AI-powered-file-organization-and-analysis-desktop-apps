// 설정 화면 JavaScript
document.addEventListener('DOMContentLoaded', async () => {
    console.log('설정 화면이 로드되었습니다.');
    
    // 현재 설정 로드
    await loadCurrentSettings();
    
    // 이벤트 리스너 설정
    setupEventListeners();
});

// 현재 설정 로드
async function loadCurrentSettings() {
    try {
        console.log('설정 로드 시작...');
        const config = await window.electronAPI.getConfig();
        console.log('현재 설정 로드:', config);
        
        // 모니터링 폴더 설정
        const monitoringInput = document.getElementById('monitoring-folder-input');
        if (monitoringInput && config.monitoringFolder) {
            monitoringInput.value = config.monitoringFolder;
            console.log('모니터링 폴더 설정:', config.monitoringFolder);
        }
        
        // 정리 지정 폴더 설정
        const movingInput = document.getElementById('moving-folder-input');
        if (movingInput && config.movingFolder) {
            movingInput.value = config.movingFolder;
            console.log('정리 지정 폴더 설정:', config.movingFolder);
        }
        
        // 자동 정리 설정
        const autoOrganizeToggle = document.getElementById('auto-organize-toggle-settings');
        if (autoOrganizeToggle && typeof config.autoOrganize !== 'undefined') {
            autoOrganizeToggle.checked = config.autoOrganize;
            console.log('자동 정리 설정:', config.autoOrganize);
        }
        
        // 임계값 설정 (threshold-select로 수정)
        const thresholdSelect = document.getElementById('threshold-select');
        if (thresholdSelect && config.threshold) {
            thresholdSelect.value = config.threshold;
            console.log('임계값 설정:', config.threshold);
        }
        
        console.log('설정 로드 완료');
    } catch (error) {
        console.error('설정 로드 실패:', error);
        console.error('에러 상세:', error.message);
        showNotification(`설정을 불러오는데 실패했습니다: ${error.message}`, 'error');
    }
}

function setupEventListeners() {
    // 닫기 버튼
    document.getElementById('close-settings-btn').addEventListener('click', () => {
        window.close();
    });

    // 폴더 선택 버튼들
    document.getElementById('select-monitoring-folder-btn').addEventListener('click', async () => {
        try {
            const currentConfig = await window.electronAPI.getConfig();
            const result = await window.electronAPI.selectFolder({
                title: '모니터링 폴더 선택',
                defaultPath: currentConfig.monitoringFolder || 'C:/Downloads'
            });
            
            if (result.success) {
                document.getElementById('monitoring-folder-input').value = result.folderPath;
                
                // 설정 업데이트
                const currentConfig = await window.electronAPI.getConfig();
                currentConfig.monitoringFolder = result.folderPath;
                await window.electronAPI.updateConfig(currentConfig);
                
                showNotification(`모니터링 폴더가 설정되었습니다: ${result.folderPath}`, 'success');
            } else {
                showNotification(result.error, 'error');
            }
        } catch (error) {
            console.error('폴더 선택 오류:', error);
            showNotification('폴더 선택 중 오류가 발생했습니다.', 'error');
        }
    });

    document.getElementById('select-moving-folder-btn').addEventListener('click', async () => {
        try {
            const currentConfig = await window.electronAPI.getConfig();
            const result = await window.electronAPI.selectFolder({
                title: '정리 지정 폴더 선택',
                defaultPath: currentConfig.movingFolder || 'C:/Documents'
            });
            
            if (result.success) {
                document.getElementById('moving-folder-input').value = result.folderPath;
                
                // 설정 업데이트
                const currentConfig = await window.electronAPI.getConfig();
                currentConfig.movingFolder = result.folderPath;
                await window.electronAPI.updateConfig(currentConfig);
                
                showNotification(`정리 지정 폴더가 설정되었습니다: ${result.folderPath}`, 'success');
            } else {
                showNotification(result.error, 'error');
            }
        } catch (error) {
            console.error('폴더 선택 오류:', error);
            showNotification('폴더 선택 중 오류가 발생했습니다.', 'error');
        }
    });

    // 자동 정리 설정 토글들
    document.getElementById('auto-organize-toggle-settings').addEventListener('change', (event) => {
        const enabled = event.target.checked;
        console.log('자동 정리 설정 변경:', enabled);
        showNotification(`자동 정리 설정이 ${enabled ? '활성화' : '비활성화'}되었습니다.`, 'success');
    });

    document.getElementById('schedule-toggle').addEventListener('change', (event) => {
        const enabled = event.target.checked;
        console.log('스케줄 설정 변경:', enabled);
        showNotification(`스케줄 정리가 ${enabled ? '활성화' : '비활성화'}되었습니다.`, 'success');
    });

    // 임계값 선택
    document.getElementById('threshold-select').addEventListener('change', (event) => {
        const value = event.target.value;
        console.log('임계값 변경:', value);
        showNotification(`임계값이 ${value}개로 설정되었습니다.`, 'info');
    });

    // 스케줄 선택
    document.getElementById('schedule-select').addEventListener('change', (event) => {
        const value = event.target.value;
        console.log('스케줄 시간 변경:', value);
        showNotification(`스케줄 시간이 ${value}로 설정되었습니다.`, 'info');
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
