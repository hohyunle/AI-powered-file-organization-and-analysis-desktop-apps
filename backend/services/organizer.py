"""
파일 정리 실행 모듈

AI가 생성한 분류 계획을 실제로 실행합니다.
"""

import asyncio
import shutil
from pathlib import Path
from typing import Dict, Any, List
from loguru import logger


class FileOrganizer:
    """파일 정리 실행 클래스"""
    
    def __init__(self):
        self.current_job_id = None
        self.is_organizing = False
    
    async def execute_plan(self, classification_plan: Dict[str, Any]) -> str:
        """분류 계획 실행"""
        try:
            self.is_organizing = True
            job_id = f"job_{asyncio.get_event_loop().time()}"
            self.current_job_id = job_id
            
            logger.info(f"정리 작업 시작: {job_id}")
            
            # 작업 로그 생성
            await self._log_job_start(job_id, classification_plan)
            
            # 각 파일 처리
            results = []
            for item in classification_plan.get("items", []):
                result = await self._process_file(item)
                results.append(result)
            
            # 작업 완료 로그
            await self._log_job_complete(job_id, results)
            
            logger.info(f"정리 작업 완료: {job_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"정리 작업 오류: {e}")
            await self._log_job_error(job_id, str(e))
            raise
        finally:
            self.is_organizing = False
            self.current_job_id = None
    
    async def _process_file(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """개별 파일 처리"""
        try:
            file_id = item["file_id"]
            from_path = Path(item["from_path"])
            to_path = Path(item["to_path"])
            action = item.get("action", "MOVE")
            
            # 대상 디렉토리 생성
            to_path.parent.mkdir(parents=True, exist_ok=True)
            
            if action == "MOVE":
                # 파일 이동
                shutil.move(str(from_path), str(to_path))
                logger.info(f"파일 이동: {from_path} → {to_path}")
                
                # 데이터베이스 업데이트
                await self._update_file_status(file_id, "MOVED", str(to_path))
                
                return {
                    "file_id": file_id,
                    "success": True,
                    "action": "MOVE",
                    "from_path": str(from_path),
                    "to_path": str(to_path)
                }
            
            elif action == "COPY":
                # 파일 복사
                shutil.copy2(str(from_path), str(to_path))
                logger.info(f"파일 복사: {from_path} → {to_path}")
                
                return {
                    "file_id": file_id,
                    "success": True,
                    "action": "COPY",
                    "from_path": str(from_path),
                    "to_path": str(to_path)
                }
            
            elif action == "DELETE":
                # 파일 삭제
                from_path.unlink()
                logger.info(f"파일 삭제: {from_path}")
                
                await self._update_file_status(file_id, "DELETED", None)
                
                return {
                    "file_id": file_id,
                    "success": True,
                    "action": "DELETE",
                    "from_path": str(from_path)
                }
            
            else:
                logger.warning(f"알 수 없는 액션: {action}")
                return {
                    "file_id": file_id,
                    "success": False,
                    "error": f"알 수 없는 액션: {action}"
                }
                
        except Exception as e:
            logger.error(f"파일 처리 오류 ({item.get('file_id')}): {e}")
            return {
                "file_id": item.get("file_id"),
                "success": False,
                "error": str(e)
            }
    
    async def _update_file_status(self, file_id: int, status: str, new_path: str = None):
        """파일 상태 업데이트"""
        try:
            # 실제 구현에서는 데이터베이스 매니저를 통해 업데이트
            logger.info(f"파일 상태 업데이트: ID {file_id} → {status}")
            
            # TODO: 데이터베이스 업데이트 구현
            # await self.db_manager.update_file_status(file_id, status, new_path)
            
        except Exception as e:
            logger.error(f"파일 상태 업데이트 오류: {e}")
    
    async def _log_job_start(self, job_id: str, plan: Dict[str, Any]):
        """작업 시작 로그"""
        logger.info(f"작업 시작 로그: {job_id}")
        # TODO: 데이터베이스에 작업 로그 저장
    
    async def _log_job_complete(self, job_id: str, results: List[Dict[str, Any]]):
        """작업 완료 로그"""
        success_count = sum(1 for r in results if r.get("success", False))
        total_count = len(results)
        
        logger.info(f"작업 완료 로그: {job_id} - {success_count}/{total_count} 성공")
        # TODO: 데이터베이스에 작업 결과 저장
    
    async def _log_job_error(self, job_id: str, error: str):
        """작업 오류 로그"""
        logger.error(f"작업 오류 로그: {job_id} - {error}")
        # TODO: 데이터베이스에 오류 로그 저장
    
    def get_status(self) -> Dict[str, Any]:
        """정리 상태 반환"""
        return {
            "is_organizing": self.is_organizing,
            "current_job_id": self.current_job_id
        }
