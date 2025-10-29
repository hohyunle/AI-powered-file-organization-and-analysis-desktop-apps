"""
파일 시스템 감시 모듈

watchdog 라이브러리를 사용하여 파일 시스템 변경을 감시합니다.
"""

import asyncio
from pathlib import Path
from typing import List, Set, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent
from loguru import logger


class FileChangeHandler(FileSystemEventHandler):
    """파일 변경 이벤트 핸들러"""
    
    def __init__(self, worker):
        self.worker = worker
        self.processed_files: Set[str] = set()
    
    def on_created(self, event):
        """파일 생성 이벤트"""
        if not event.is_directory:
            file_path = Path(event.src_path)
            if self._is_valid_file(file_path):
                logger.info(f"새 파일 감지: {file_path}")
                self.worker.new_files.append(str(file_path))
    
    def on_modified(self, event):
        """파일 수정 이벤트"""
        if not event.is_directory:
            file_path = Path(event.src_path)
            if self._is_valid_file(file_path):
                logger.info(f"파일 수정 감지: {file_path}")
                self.worker.new_files.append(str(file_path))
    
    def _is_valid_file(self, file_path: Path) -> bool:
        """유효한 파일인지 확인"""
        # 허용된 확장자만 처리
        allowed_extensions = {
            '.pdf', '.pptx', '.docx', '.xlsx', 
            '.jpg', '.jpeg', '.png', '.txt'
        }
        
        return (
            file_path.exists() and 
            file_path.is_file() and 
            file_path.suffix.lower() in allowed_extensions and
            str(file_path) not in self.processed_files
        )


class FileWatcher:
    """파일 시스템 감시 클래스"""
    
    def __init__(self):
        self.observer: Optional[Observer] = None
        self.new_files: List[str] = []
        self.is_watching = False
        self.watch_folder: Optional[str] = None
    
    async def start_watching(self, folder_path: str):
        """파일 감시 시작"""
        try:
            watch_path = Path(folder_path)
            if not watch_path.exists():
                logger.error(f"감시 폴더가 존재하지 않습니다: {folder_path}")
                return
            
            self.watch_folder = folder_path
            self.observer = Observer()
            
            # 이벤트 핸들러 생성
            handler = FileChangeHandler(self)
            
            # 감시 시작
            self.observer.schedule(handler, str(watch_path), recursive=True)
            self.observer.start()
            
            self.is_watching = True
            logger.info(f"파일 감시 시작: {folder_path}")
            
        except Exception as e:
            logger.error(f"파일 감시 시작 실패: {e}")
            raise
    
    async def stop_watching(self):
        """파일 감시 중지"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.is_watching = False
            logger.info("파일 감시 중지")
    
    async def get_new_files(self) -> List[str]:
        """새로 감지된 파일 목록 반환"""
        if self.new_files:
            files = self.new_files.copy()
            self.new_files.clear()
            return files
        return []
    
    def get_status(self) -> dict:
        """감시 상태 반환"""
        return {
            "is_watching": self.is_watching,
            "watch_folder": self.watch_folder,
            "pending_files": len(self.new_files)
        }
