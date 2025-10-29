"""
유틸리티 함수들

공통으로 사용되는 유틸리티 함수들을 정의합니다.
"""

import os
import hashlib
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


def get_file_hash(file_path: str) -> str:
    """파일의 MD5 해시값을 계산합니다."""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return ""


def get_file_mime_type(file_path: str) -> str:
    """파일의 MIME 타입을 반환합니다."""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or "application/octet-stream"


def get_file_category(file_path: str) -> str:
    """파일 확장자에 따라 카테고리를 반환합니다."""
    extension = Path(file_path).suffix.lower()
    
    document_extensions = {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'}
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv'}
    audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'}
    archive_extensions = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'}
    
    if extension in document_extensions:
        return "document"
    elif extension in image_extensions:
        return "image"
    elif extension in video_extensions:
        return "video"
    elif extension in audio_extensions:
        return "audio"
    elif extension in archive_extensions:
        return "archive"
    else:
        return "other"


def format_file_size(size_bytes: int) -> str:
    """바이트 크기를 읽기 쉬운 형태로 변환합니다."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def safe_filename(filename: str) -> str:
    """파일명에서 안전하지 않은 문자를 제거합니다."""
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    return filename


def create_directory_if_not_exists(directory_path: str) -> bool:
    """디렉토리가 존재하지 않으면 생성합니다."""
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def is_valid_file_path(file_path: str) -> bool:
    """파일 경로가 유효한지 확인합니다."""
    try:
        path = Path(file_path)
        return path.exists() and path.is_file()
    except Exception:
        return False


def get_file_info(file_path: str) -> Optional[Dict[str, Any]]:
    """파일의 기본 정보를 반환합니다."""
    try:
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            return None
        
        stat = path.stat()
        return {
            "file_path": str(path),
            "file_name": path.name,
            "file_size": stat.st_size,
            "file_category": get_file_category(file_path),
            "mime_type": get_file_mime_type(file_path),
            "created_at": datetime.fromtimestamp(stat.st_ctime),
            "modified_at": datetime.fromtimestamp(stat.st_mtime),
            "file_hash": get_file_hash(file_path)
        }
    except Exception:
        return None


def truncate_text(text: str, max_length: int = 100) -> str:
    """텍스트를 지정된 길이로 자릅니다."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def parse_time_string(time_str: str) -> Optional[datetime]:
    """시간 문자열을 datetime 객체로 변환합니다."""
    try:
        # "HH:MM" 형식 파싱
        hour, minute = map(int, time_str.split(':'))
        return datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
    except Exception:
        return None


def is_time_to_run(run_time: str) -> bool:
    """현재 시간이 실행 시간인지 확인합니다."""
    try:
        target_time = parse_time_string(run_time)
        if not target_time:
            return False
        
        now = datetime.now()
        # 현재 시간과 목표 시간의 차이가 1분 이내인지 확인
        time_diff = abs((now - target_time).total_seconds())
        return time_diff <= 60
    except Exception:
        return False
