// 설정 화면 JavaScript
document.addEventListener('DOMContentLoaded', () => {
    console.log('설정 화면이 로드되었습니다.');
    
    // 이벤트 리스너 설정
    setupEventListeners();
});

function setupEventListeners() {
    // 닫기 버튼
    document.getElementById('close-settings-btn').addEventListener('click', () => {
        window.close();
    });

    // 폴더 선택 버튼들
    document.getElementById('select-monitoring-folder-btn').addEventListener('click', () => {
        showNotification('폴더 선택 기능을 준비 중입니다...', 'info');
    });

    document.getElementById('select-moving-folder-btn').addEventListener('click', () => {
        showNotification('폴더 선택 기능을 준비 중입니다...', 'info');
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
