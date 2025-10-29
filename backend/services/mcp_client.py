"""
MCP (Model Context Protocol) 클라이언트

LLM과의 표준화된 통신을 담당합니다.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
import httpx
from loguru import logger


class MCPClient:
    """MCP 클라이언트 클래스"""
    
    def __init__(self):
        self.server_url = "http://localhost:8000"  # MCP 서버 URL
        self.client = None
        self.is_initialized = False
    
    async def initialize(self):
        """MCP 클라이언트 초기화"""
        try:
            self.client = httpx.AsyncClient(timeout=30.0)
            
            # MCP 서버 연결 테스트
            response = await self.client.get(f"{self.server_url}/health")
            if response.status_code == 200:
                self.is_initialized = True
                logger.info("MCP 클라이언트 초기화 완료")
            else:
                logger.warning("MCP 서버 연결 실패, 오프라인 모드로 동작")
                
        except Exception as e:
            logger.warning(f"MCP 서버 연결 실패: {e}, 오프라인 모드로 동작")
            self.is_initialized = False
    
    async def close(self):
        """MCP 클라이언트 종료"""
        if self.client:
            await self.client.aclose()
            self.is_initialized = False
    
    async def classify_files(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """파일들을 AI를 통해 분류"""
        try:
            if not self.is_initialized:
                return await self._offline_classify_files(files)
            
            # MCP 서버에 분류 요청
            request_data = {
                "type": "classify_files",
                "files": files,
                "context": {
                    "task": "파일 정리 및 분류",
                    "language": "ko"
                }
            }
            
            response = await self.client.post(
                f"{self.server_url}/classify",
                json=request_data
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"AI 분류 완료: {len(files)}개 파일")
                return result
            else:
                logger.error(f"MCP 서버 오류: {response.status_code}")
                return await self._offline_classify_files(files)
                
        except Exception as e:
            logger.error(f"파일 분류 오류: {e}")
            return await self._offline_classify_files(files)
    
    async def _offline_classify_files(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """오프라인 파일 분류 (규칙 기반)"""
        logger.info("오프라인 모드로 파일 분류 실행")
        
        classification_plan = {
            "job_id": None,
            "items": []
        }
        
        for file_info in files:
            file_path = Path(file_info["path"])
            file_ext = file_info["ext"].lower()
            text_snippet = file_info.get("text_snippet", "")
            
            # 확장자 기반 기본 분류
            category = self._get_category_by_extension(file_ext)
            
            # 텍스트 내용 기반 세부 분류
            subcategory = self._get_subcategory_by_content(text_snippet)
            
            classification_plan["items"].append({
                "file_id": file_info["id"],
                "file_path": file_info["path"],
                "action": "MOVE",
                "from_path": file_info["path"],
                "to_path": f"{category}/{subcategory}/{file_path.name}",
                "category": category,
                "subcategory": subcategory,
                "confidence": 0.8,
                "reason": f"확장자 {file_ext} 및 내용 기반 분류"
            })
        
        return classification_plan
    
    def _get_category_by_extension(self, file_ext: str) -> str:
        """확장자 기반 카테고리 분류"""
        category_map = {
            '.pdf': '문서',
            '.docx': '문서',
            '.doc': '문서',
            '.txt': '문서',
            '.pptx': '프레젠테이션',
            '.ppt': '프레젠테이션',
            '.xlsx': '스프레드시트',
            '.xls': '스프레드시트',
            '.jpg': '이미지',
            '.jpeg': '이미지',
            '.png': '이미지',
            '.bmp': '이미지'
        }
        
        return category_map.get(file_ext, '기타')
    
    def _get_subcategory_by_content(self, text_snippet: str) -> str:
        """텍스트 내용 기반 세부 카테고리 분류"""
        if not text_snippet:
            return '기타'
        
        text_lower = text_snippet.lower()
        
        # 키워드 기반 분류
        if any(keyword in text_lower for keyword in ['과제', 'assignment', 'homework']):
            return '과제'
        elif any(keyword in text_lower for keyword in ['강의', 'lecture', '수업']):
            return '강의자료'
        elif any(keyword in text_lower for keyword in ['회의', 'meeting', '미팅']):
            return '회의자료'
        elif any(keyword in text_lower for keyword in ['보고서', 'report', '리포트']):
            return '보고서'
        elif any(keyword in text_lower for keyword in ['계약', 'contract', '계약서']):
            return '계약서'
        elif any(keyword in text_lower for keyword in ['영수증', 'receipt', '청구서']):
            return '영수증'
        else:
            return '기타'
    
    async def generate_organize_plan(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """정리 계획 생성"""
        try:
            if not self.is_initialized:
                return await self._offline_generate_plan(files)
            
            request_data = {
                "type": "generate_organize_plan",
                "files": files,
                "context": {
                    "task": "파일 정리 계획 수립",
                    "language": "ko"
                }
            }
            
            response = await self.client.post(
                f"{self.server_url}/organize",
                json=request_data
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return await self._offline_generate_plan(files)
                
        except Exception as e:
            logger.error(f"정리 계획 생성 오류: {e}")
            return await self._offline_generate_plan(files)
    
    async def _offline_generate_plan(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """오프라인 정리 계획 생성"""
        plan = {
            "plan_id": f"plan_{asyncio.get_event_loop().time()}",
            "items": [],
            "summary": {
                "total_files": len(files),
                "categories": {},
                "estimated_time": "5분"
            }
        }
        
        for file_info in files:
            item = {
                "file_id": file_info["id"],
                "file_path": file_info["path"],
                "action": "MOVE",
                "from_path": file_info["path"],
                "to_path": f"정리된 파일/{self._get_category_by_extension(file_info['ext'])}/{Path(file_info['path']).name}",
                "reason": "규칙 기반 자동 분류"
            }
            plan["items"].append(item)
        
        return plan
