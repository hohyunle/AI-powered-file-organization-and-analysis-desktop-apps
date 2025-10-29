"""
설정 관리 모듈

워커의 설정을 관리하는 클래스입니다.
"""

from typing import Dict, Any
from pathlib import Path
import json


class Settings:
    """설정 관리 클래스"""
    
    def __init__(self):
        self.config_file = Path(__file__).parent / "worker_config.json"
        self.config_file.parent.mkdir(exist_ok=True)
    
    def get_default_config(self) -> Dict[str, Any]:
        """기본 설정 반환"""
        return {
            "monitoring_folder": "C:/Downloads",
            "moving_folder": "C:/Documents/정리된 파일",
            "threshold": 50,
            "auto_organize": True,
            "run_time": "09:00",  # 매일 9시에 자동 실행
            "active": True,
            "allowed_extensions": [
                ".pdf", ".pptx", ".docx", ".xlsx", 
                ".jpg", ".jpeg", ".png", ".txt"
            ],
            "mcp_server_url": "http://localhost:8000",
            "database_url": "postgresql://user:password@localhost:5432/file_organizer"
        }
    
    def load_config(self) -> Dict[str, Any]:
        """설정 파일에서 설정 로드"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 기본 설정으로 파일 생성
                default_config = self.get_default_config()
                self.save_config(default_config)
                return default_config
        except Exception as e:
            print(f"설정 로드 오류: {e}")
            return self.get_default_config()
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """설정을 파일에 저장"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"설정 저장 오류: {e}")
            return False
