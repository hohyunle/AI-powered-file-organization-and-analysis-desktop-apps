// 파일 목록 화면 JavaScript
document.addEventListener('DOMContentLoaded', () => {
    console.log('파일 목록 화면이 로드되었습니다.');
    
    // 이벤트 리스너 설정
    setupEventListeners();
});

function setupEventListeners() {
    // 닫기 버튼
    document.getElementById('close-file-list-btn').addEventListener('click', () => {
        window.close();
    });

    // 뷰 옵션 버튼들 (큰 아이콘, 간단히, 자세히)
    document.getElementById('large-icons-btn').addEventListener('click', () => {
        switchView('large-icons');
        showNotification('큰 아이콘 보기로 전환되었습니다.', 'info');
    });

    document.getElementById('simple-view-btn').addEventListener('click', () => {
        switchView('simple');
        showNotification('간단히 보기로 전환되었습니다.', 'info');
    });

    document.getElementById('detailed-view-btn').addEventListener('click', () => {
        switchView('detailed');
        showNotification('자세히 보기로 전환되었습니다.', 'info');
    });

    // 정렬 선택
    document.getElementById('sort-select').addEventListener('change', (event) => {
        const value = event.target.value;
        console.log('정렬 기준 변경:', value);
        showNotification(`${value}순으로 정렬되었습니다.`, 'info');
    });

    // 검색 입력
    document.getElementById('search-input').addEventListener('input', (event) => {
        const query = event.target.value;
        if (query.length > 2) {
            console.log('검색 쿼리:', query);
            // TODO: 실제 검색 로직 구현
        }
    });

    // 필터 버튼
    document.getElementById('filter-btn').addEventListener('click', () => {
        showNotification('필터 기능을 준비 중입니다...', 'info');
    });

    // 파일 삭제 버튼들
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            showNotification('파일 삭제 기능을 준비 중입니다...', 'info');
        });
    });

    // 알림 닫기 버튼
    document.getElementById('notification-close').addEventListener('click', () => {
        hideNotification();
    });
}

// 뷰 전환 함수
function switchView(viewType) {
    // 모든 뷰 버튼 비활성화
    document.querySelectorAll('.view-btn').forEach(btn => btn.classList.remove('active'));
    
    // 모든 뷰 숨기기
    document.getElementById('large-icons-view').classList.add('hidden');
    document.getElementById('simple-view').classList.add('hidden');
    document.getElementById('detailed-view').classList.add('hidden');
    
    // 선택된 뷰 활성화
    switch(viewType) {
        case 'large-icons':
            document.getElementById('large-icons-btn').classList.add('active');
            document.getElementById('large-icons-view').classList.remove('hidden');
            break;
        case 'simple':
            document.getElementById('simple-view-btn').classList.add('active');
            document.getElementById('simple-view').classList.remove('hidden');
            break;
        case 'detailed':
            document.getElementById('detailed-view-btn').classList.add('active');
            document.getElementById('detailed-view').classList.remove('hidden');
            break;
    }
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
