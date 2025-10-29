"""
데이터 모델 정의

파일 정리 시스템에서 사용하는 데이터 모델들을 정의합니다.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class FileStatus(Enum):
    """파일 상태 열거형"""
    PENDING = "pending"      # 대기 중
    PROCESSING = "processing"  # 처리 중
    COMPLETED = "completed"  # 완료
    FAILED = "failed"        # 실패
    ORGANIZED = "organized"  # 정리됨


class FileType(Enum):
    """파일 타입 열거형"""
    DOCUMENT = "document"    # 문서
    IMAGE = "image"         # 이미지
    VIDEO = "video"         # 비디오
    AUDIO = "audio"         # 오디오
    ARCHIVE = "archive"     # 압축파일
    OTHER = "other"         # 기타


@dataclass
class FileInfo:
    """파일 정보 모델"""
    id: Optional[int] = None
    file_path: str = ""
    file_name: str = ""
    file_size: int = 0
    file_type: FileType = FileType.OTHER
    status: FileStatus = FileStatus.PENDING
    extracted_text: Optional[str] = None
    classification: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class OrganizeJob:
    """정리 작업 모델"""
    id: Optional[int] = None
    job_name: str = ""
    status: str = "pending"
    files_count: int = 0
    processed_count: int = 0
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class Config:
    """설정 모델"""
    monitoring_folder: str = "C:/Downloads"
    moving_folder: str = "C:/Documents/정리된 파일"
    threshold: int = 50
    auto_organize: bool = True
    run_time: str = "09:00"
    active: bool = True
    allowed_extensions: List[str] = None
    mcp_server_url: str = "http://localhost:8000"
    database_url: str = "postgresql://user:password@localhost:5432/file_organizer"
    
    def __post_init__(self):
        if self.allowed_extensions is None:
            self.allowed_extensions = [
                ".pdf", ".pptx", ".docx", ".xlsx", 
                ".jpg", ".jpeg", ".png", ".txt"
            ]


@dataclass
class Stats:
    """통계 정보 모델"""
    total_files: int = 0
    pending_files: int = 0
    processed_files: int = 0
    organized_files: int = 0
    failed_files: int = 0
    last_organized: Optional[datetime] = None
    monitoring_folder: str = ""
    auto_organize_enabled: bool = True
