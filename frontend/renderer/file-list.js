// 파일 목록 화면 JavaScript
console.log('file-list.js 스크립트가 로드되었습니다!');
console.log('현재 시간:', new Date().toISOString());

// 현재 뷰/파일 상태 보관
let currentView = 'large-icons';
let currentFiles = [];
let currentSort = { column: 'name', direction: 'asc' }; // 현재 정렬 상태

document.addEventListener('DOMContentLoaded', async () => {
    console.log('파일 목록 화면이 로드되었습니다.');
    
    // 파일 목록 로드
    await loadFileList();
    
    // 이벤트 리스너 설정
    setupEventListeners();
});

// 파일 목록 로드
async function loadFileList() {
    try {
        console.log('파일 목록 로드 시작...');
        console.log('window 객체:', window);
        console.log('window.electronAPI:', window.electronAPI);
        
        // electronAPI가 없으면 오류
        if (!window.electronAPI) {
            console.error('window.electronAPI가 없습니다!');
            showNotification('Electron API를 찾을 수 없습니다.', 'error');
            return;
        }
        
        console.log('getFileList 함수:', window.electronAPI.getFileList);
        
        // 테스트용 더미 데이터 먼저 표시
        const testFiles = [
            {
                id: 'test1',
                name: 'test_image.jpg',
                path: '/test/path',
                size: 1024000,
                type: 'image',
                status: 'pending',
                created: '2024-01-15',
                modified: '2024-01-15'
            },
            {
                id: 'test2',
                name: 'test_document.pdf',
                path: '/test/path',
                size: 2048000,
                type: 'document',
                status: 'pending',
                created: '2024-01-14',
                modified: '2024-01-14'
            }
        ];
        
        const testStats = {
            total: 2,
            images: 1,
            documents: 1,
            videos: 0,
            others: 0
        };
        
        console.log('테스트 데이터로 먼저 표시');
        updateStats(testStats);
        currentFiles = testFiles;
        currentSort = { column: 'name', direction: 'asc' };
        const sortedTestFiles = sortFiles(testFiles, currentSort.column, currentSort.direction);
        displayFiles(sortedTestFiles);
        updateSortIcons();
        
        // 실제 API 호출
        console.log('실제 API 호출 시작...');
        const result = await window.electronAPI.getFileList();
        console.log('파일 목록 API 응답:', result);
        
        if (result.success) {
            console.log('파일 목록 로드 성공:', result.files.length, '개 파일');
            console.log('파일 목록:', result.files);
            console.log('통계:', result.stats);
            
            // 통계 업데이트
            updateStats(result.stats);
            
            // 파일 목록 표시 (기본 정렬: 이름순)
            currentFiles = result.files;
            currentSort = { column: 'name', direction: 'asc' };
            const sortedFiles = sortFiles(currentFiles, currentSort.column, currentSort.direction);
            displayFiles(sortedFiles);
            updateSortIcons();
            
            showNotification(`${result.files.length}개 파일을 불러왔습니다.`, 'success');
        } else {
            console.error('파일 목록 로드 실패:', result);
            showNotification('파일 목록을 불러오는데 실패했습니다.', 'error');
        }
    } catch (error) {
        console.error('파일 목록 로드 오류:', error);
        console.error('에러 스택:', error.stack);
        showNotification('파일 목록 로드 중 오류가 발생했습니다.', 'error');
    }
}

// 통계 업데이트
function updateStats(stats) {
    console.log('통계 업데이트 시작:', stats);
    
    // 전체 파일 개수
    const totalElement = document.querySelector('.file-count');
    console.log('전체 파일 개수 요소:', totalElement);
    if (totalElement) {
        totalElement.textContent = `${stats.total}개`;
        console.log('전체 파일 개수 업데이트:', `${stats.total}개`);
    }
    
    // 타입별 통계 업데이트
    const imageCount = document.querySelector('.file-type-stats .image-count');
    const documentCount = document.querySelector('.file-type-stats .document-count');
    const videoCount = document.querySelector('.file-type-stats .video-count');
    const otherCount = document.querySelector('.file-type-stats .other-count');
    
    console.log('타입별 요소들:', { imageCount, documentCount, videoCount, otherCount });
    
    if (imageCount) {
        imageCount.textContent = `${stats.images}개`;
        console.log('이미지 개수 업데이트:', `${stats.images}개`);
    }
    if (documentCount) {
        documentCount.textContent = `${stats.documents}개`;
        console.log('문서 개수 업데이트:', `${stats.documents}개`);
    }
    if (videoCount) {
        videoCount.textContent = `${stats.videos}개`;
        console.log('비디오 개수 업데이트:', `${stats.videos}개`);
    }
    if (otherCount) {
        otherCount.textContent = `${stats.others}개`;
        console.log('기타 개수 업데이트:', `${stats.others}개`);
    }
}

// 파일 목록 표시
function displayFiles(files) {
    console.log('파일 목록 표시 시작:', files);
    const fileListContainer = document.getElementById('file-list-container');
    console.log('파일 목록 컨테이너:', fileListContainer);
    
    if (!fileListContainer) {
        console.error('파일 목록 컨테이너를 찾을 수 없습니다!');
        return;
    }
    
    // 기존 파일 목록 초기화
    fileListContainer.innerHTML = '';
    
    if (files.length === 0) {
        console.log('파일이 없어서 빈 메시지 표시');
        fileListContainer.innerHTML = '<div class="no-files">정리 대기 중인 파일이 없습니다.</div>';
        return;
    }
    
    console.log(`${files.length}개 파일을 표시합니다.`);
    files.forEach((file, index) => {
        console.log(`파일 ${index + 1}:`, file);
        let fileElement;
        if (currentView === 'detailed') {
            fileElement = createDetailedRow(file);
        } else if (currentView === 'simple') {
            fileElement = createSimpleRow(file);
        } else {
            fileElement = createLargeCard(file);
        }
        fileListContainer.appendChild(fileElement);
    });
    
    console.log('파일 목록 표시 완료');

    if (currentView === 'detailed') {
        setupSelectionHandlers();
    }
}

// 상세뷰: 테이블 행
function createDetailedRow(file) {
    const fileDiv = document.createElement('div');
    fileDiv.className = 'file-item';
    fileDiv.dataset.fileId = file.id;
    
    // 파일 확장자를 data 속성으로 추가 (CSS 색상 적용용)
    const extension = file.name.toLowerCase().split('.').pop();
    fileDiv.dataset.fileType = extension;
    
    // 자세히 보기용 데이터 속성 추가
    fileDiv.dataset.fileSize = formatFileSize(file.size);
    fileDiv.dataset.fileType = file.type;
    fileDiv.dataset.fileDate = file.modified;
    fileDiv.dataset.fileStatus = getStatusText(file.status);
    
    // 파일 아이콘
    const icon = getFileIcon(file.type, file.name);
    // 파일 크기 포맷팅
    const sizeText = formatFileSize(file.size);

    fileDiv.innerHTML = `
        <div class="file-checkbox">
            <input type="checkbox" class="file-select-checkbox" data-file-id="${file.id}">
        </div>
        <div class="file-icon-name">
            <div class="file-icon">${icon}</div>
            <div class="file-name">${file.name}</div>
        </div>
        <div class="file-size">${sizeText}</div>
        <div class="file-type">${getFileTypeText(file.type)}</div>
        <div class="file-date">${file.modified}</div>
    `;
    
    return fileDiv;
}

// 간단히 보기: 아이콘 + 파일명만
function createSimpleRow(file) {
    const row = document.createElement('div');
    row.className = 'file-item';
    row.dataset.fileId = file.id;
    const extension = file.name.toLowerCase().split('.').pop();
    row.dataset.fileType = extension;

    const icon = getFileIcon(file.type, file.name);
    row.innerHTML = `
        <div class="file-icon">${icon}</div>
        <div class="file-name">${file.name}</div>
    `;
    return row;
}

// 큰 아이콘 카드
function createLargeCard(file) {
    const card = document.createElement('div');
    card.className = 'file-item';
    card.dataset.fileId = file.id;
    const extension = file.name.toLowerCase().split('.').pop();
    card.dataset.fileType = extension;

    const icon = getFileIcon(file.type, file.name);
    const sizeText = formatFileSize(file.size);
    card.innerHTML = `
        <div class="file-icon">${icon}</div>
        <div class="file-info">
            <div class="file-name">${file.name}</div>
            <div class="file-details">
                <span class="file-size">${sizeText}</span>
                <span class="file-status ${file.status}">${getStatusText(file.status)}</span>
            </div>
        </div>
    `;
    return card;
}

// 파일 아이콘 가져오기
function getFileIcon(type, fileName) {
    const extension = fileName.toLowerCase().split('.').pop();
    
    // 특정 파일 타입별 아이콘
    if (['hwp', 'hwpx'].includes(extension)) {
        return '📝'; // HWP 파일 - 파란색 스타일
    } else if (['xlsx', 'xls'].includes(extension)) {
        return '📊'; // Excel 파일 - 녹색 스타일
    } else if (['pptx', 'ppt'].includes(extension)) {
        return '📈'; // PowerPoint 파일
    } else if (['pdf'].includes(extension)) {
        return '📋'; // PDF 파일
    } else if (['doc', 'docx'].includes(extension)) {
        return '📄'; // Word 파일
    } else if (['txt'].includes(extension)) {
        return '📝'; // 텍스트 파일
    }
    
    // 기본 타입별 아이콘
    const icons = {
        image: '🖼️',
        document: '📄',
        video: '🎥',
        other: '📁'
    };
    return icons[type] || '📁';
}

// 파일 크기 포맷팅
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// 상태 텍스트 가져오기
function getStatusText(status) {
    const statusTexts = {
        pending: '대기 중',
        processing: '처리 중',
        completed: '완료',
        error: '오류'
    };
    return statusTexts[status] || '알 수 없음';
}

// 유형 텍스트 변환
function getFileTypeText(type) {
    const map = {
        image: 'image',
        document: 'document',
        video: 'video',
        other: 'other'
    };
    return map[type] || 'other';
}

// 파일 정렬 함수들
function sortFiles(files, sortBy, direction = 'asc') {
    const sortedFiles = [...files]; // 원본 배열 복사
    
    switch(sortBy) {
        case 'name':
            return sortedFiles.sort((a, b) => {
                const result = a.name.localeCompare(b.name, 'ko');
                return direction === 'asc' ? result : -result;
            });
        case 'size':
            return sortedFiles.sort((a, b) => {
                const result = a.size - b.size; // 작은 것부터 (오름차순)
                return direction === 'asc' ? result : -result;
            });
        case 'date':
            return sortedFiles.sort((a, b) => {
                const result = new Date(b.modified) - new Date(a.modified); // 최신부터
                return direction === 'asc' ? -result : result;
            });
        case 'type':
            return sortedFiles.sort((a, b) => {
                // 먼저 타입별로 정렬, 같은 타입이면 이름순
                if (a.type !== b.type) {
                    const result = a.type.localeCompare(b.type);
                    return direction === 'asc' ? result : -result;
                }
                const result = a.name.localeCompare(b.name, 'ko');
                return direction === 'asc' ? result : -result;
            });
        default:
            return sortedFiles;
    }
}

// 헤더 클릭 정렬
function handleHeaderSort(column) {
    if (!Array.isArray(currentFiles) || currentFiles.length === 0) {
        console.log('정렬할 파일이 없습니다.');
        return;
    }
    
    // 같은 컬럼을 클릭하면 방향 전환, 다른 컬럼이면 오름차순으로 시작
    if (currentSort.column === column) {
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort.column = column;
        currentSort.direction = 'asc';
    }
    
    console.log(`${column} ${currentSort.direction}순으로 정렬 중...`);
    const sortedFiles = sortFiles(currentFiles, currentSort.column, currentSort.direction);
    displayFiles(sortedFiles);
    updateSortIcons();
    showNotification(`${getSortDisplayName(currentSort.column)} ${currentSort.direction === 'asc' ? '오름차순' : '내림차순'}으로 정렬되었습니다.`, 'info');
}

// 정렬 아이콘 업데이트
function updateSortIcons() {
    // 모든 헤더에서 active 클래스와 아이콘 제거
    document.querySelectorAll('.sortable').forEach(header => {
        header.classList.remove('active');
        const icon = header.querySelector('.sort-icon');
        icon.textContent = '';
    });
    
    // 현재 정렬 컬럼에 active 클래스와 아이콘 추가
    const activeHeader = document.querySelector(`[data-sort="${currentSort.column}"]`);
    if (activeHeader) {
        activeHeader.classList.add('active');
        const icon = activeHeader.querySelector('.sort-icon');
        icon.textContent = currentSort.direction === 'asc' ? '▲' : '▼';
    }
}

// 정렬된 파일 목록 표시 (기존 드롭다운용)
function displaySortedFiles(sortBy) {
    if (!Array.isArray(currentFiles) || currentFiles.length === 0) {
        console.log('정렬할 파일이 없습니다.');
        return;
    }
    
    console.log(`${sortBy}순으로 정렬 중...`);
    const sortedFiles = sortFiles(currentFiles, sortBy, 'asc');
    displayFiles(sortedFiles);
    showNotification(`${getSortDisplayName(sortBy)}순으로 정렬되었습니다.`, 'info');
}

// 정렬 기준 표시명
function getSortDisplayName(sortBy) {
    const names = {
        name: '이름',
        size: '크기',
        date: '날짜',
        type: '유형'
    };
    return names[sortBy] || '이름';
}

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

    // 정렬 선택 (드롭다운)
    document.getElementById('sort-select').addEventListener('change', (event) => {
        const value = event.target.value;
        console.log('정렬 기준 변경:', value);
        currentSort.column = value;
        currentSort.direction = 'asc';
        displaySortedFiles(value);
        updateSortIcons();
    });

    // 헤더 클릭 정렬 (자세히 보기에서만)
    document.querySelectorAll('.sortable').forEach(header => {
        header.addEventListener('click', () => {
            const column = header.dataset.sort;
            handleHeaderSort(column);
        });
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
    console.log('뷰 전환:', viewType);
    
    // 모든 뷰 버튼 비활성화
    document.querySelectorAll('.view-btn').forEach(btn => btn.classList.remove('active'));
    
    // 파일 목록 컨테이너 가져오기
    const fileListContainer = document.getElementById('file-list-container');
    const fileListHeader = document.getElementById('file-list-header');
    if (!fileListContainer) {
        console.error('파일 목록 컨테이너를 찾을 수 없습니다!');
        return;
    }
    
    // 기존 뷰 클래스 제거
    fileListContainer.classList.remove('large-icons-view', 'simple-view', 'detailed-view');
    
    // 선택된 뷰 활성화
    switch(viewType) {
        case 'large-icons':
            document.getElementById('large-icons-btn').classList.add('active');
            fileListContainer.classList.add('large-icons-view');
            currentView = 'large-icons';
            if (fileListHeader) fileListHeader.classList.add('hidden');
            console.log('큰 아이콘 보기로 전환');
            break;
        case 'simple':
            document.getElementById('simple-view-btn').classList.add('active');
            fileListContainer.classList.add('simple-view');
            currentView = 'simple';
            if (fileListHeader) fileListHeader.classList.add('hidden');
            console.log('간단히 보기로 전환');
            break;
        case 'detailed':
            document.getElementById('detailed-view-btn').classList.add('active');
            fileListContainer.classList.add('detailed-view');
            currentView = 'detailed';
            if (fileListHeader) fileListHeader.classList.remove('hidden');
            console.log('자세히 보기로 전환');
            break;
    }

    // 현재 파일로 재렌더링 (현재 정렬 기준 유지)
    if (Array.isArray(currentFiles) && currentFiles.length) {
        const sortedFiles = sortFiles(currentFiles, currentSort.column, currentSort.direction);
        displayFiles(sortedFiles);
        updateSortIcons();
    }
}

// 자세히 보기 선택 기능
function setupSelectionHandlers() {
    const selectAll = document.getElementById('select-all-checkbox');
    const rows = Array.from(document.querySelectorAll('.file-select-checkbox'));
    if (selectAll) {
        selectAll.onchange = () => {
            rows.forEach(cb => {
                cb.checked = selectAll.checked;
                const row = cb.closest('.file-item');
                if (row) row.classList.toggle('selected', cb.checked);
            });
        };
    }
    rows.forEach(cb => {
        cb.onchange = () => {
            const row = cb.closest('.file-item');
            if (row) row.classList.toggle('selected', cb.checked);
            if (selectAll) {
                const allChecked = rows.length > 0 && rows.every(x => x.checked);
                const anyChecked = rows.some(x => x.checked);
                // 반선택 상태 표현은 생략, 전체선택 동기화만
                selectAll.checked = allChecked;
                selectAll.indeterminate = !allChecked && anyChecked;
            }
        };
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
