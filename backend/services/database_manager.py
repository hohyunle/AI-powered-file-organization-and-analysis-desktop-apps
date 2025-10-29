"""
데이터베이스 관리 모듈

PostgreSQL과의 연결 및 데이터 관리를 담당합니다.
"""

import asyncio
from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from loguru import logger


class DatabaseManager:
    """데이터베이스 관리 클래스"""
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self.is_connected = False
    
    async def connect(self):
        """데이터베이스 연결"""
        try:
            # PostgreSQL 연결 문자열 (향후 설정에서 가져오기)
            database_url = "postgresql+asyncpg://user:password@localhost:5432/file_organizer"
            
            self.engine = create_async_engine(database_url)
            self.session_factory = sessionmaker(
                self.engine, 
                class_=AsyncSession, 
                expire_on_commit=False
            )
            
            # 연결 테스트
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            
            self.is_connected = True
            logger.info("데이터베이스 연결 성공")
            
        except Exception as e:
            logger.error(f"데이터베이스 연결 실패: {e}")
            raise
    
    async def disconnect(self):
        """데이터베이스 연결 종료"""
        if self.engine:
            await self.engine.dispose()
            self.is_connected = False
            logger.info("데이터베이스 연결 종료")
    
    async def add_file(self, file_path: str) -> int:
        """새 파일을 데이터베이스에 추가"""
        try:
            async with self.session_factory() as session:
                # 파일 정보 추출
                file_path_obj = Path(file_path)
                
                query = text("""
                    INSERT INTO files (path, ext, size, hash, ctime, mtime, status)
                    VALUES (:path, :ext, :size, :hash, :ctime, :mtime, :status)
                    ON CONFLICT (path) DO UPDATE SET
                        size = EXCLUDED.size,
                        hash = EXCLUDED.hash,
                        mtime = EXCLUDED.mtime,
                        updated_at = NOW()
                    RETURNING id
                """)
                
                result = await session.execute(query, {
                    "path": str(file_path),
                    "ext": file_path_obj.suffix,
                    "size": file_path_obj.stat().st_size,
                    "hash": self._calculate_hash(file_path),
                    "ctime": file_path_obj.stat().st_ctime,
                    "mtime": file_path_obj.stat().st_mtime,
                    "status": "NEW"
                })
                
                file_id = result.scalar()
                await session.commit()
                
                logger.info(f"파일 추가됨: {file_path} (ID: {file_id})")
                return file_id
                
        except Exception as e:
            logger.error(f"파일 추가 오류: {e}")
            raise
    
    async def save_extraction(self, file_id: int, extraction_result: Dict[str, Any]):
        """텍스트 추출 결과 저장"""
        try:
            async with self.session_factory() as session:
                query = text("""
                    INSERT INTO extractions (file_id, text_snippet, ocr_used, lang, meta_json, extracted_at)
                    VALUES (:file_id, :text_snippet, :ocr_used, :lang, :meta_json, NOW())
                    ON CONFLICT (file_id) DO UPDATE SET
                        text_snippet = EXCLUDED.text_snippet,
                        ocr_used = EXCLUDED.ocr_used,
                        lang = EXCLUDED.lang,
                        meta_json = EXCLUDED.meta_json,
                        extracted_at = NOW()
                """)
                
                await session.execute(query, {
                    "file_id": file_id,
                    "text_snippet": extraction_result.get("text_snippet", ""),
                    "ocr_used": extraction_result.get("ocr_used", False),
                    "lang": extraction_result.get("lang", "ko"),
                    "meta_json": extraction_result.get("meta_json", {})
                })
                
                # 파일 상태 업데이트
                await session.execute(text("""
                    UPDATE files SET status = 'EXTRACTED' WHERE id = :file_id
                """), {"file_id": file_id})
                
                await session.commit()
                logger.info(f"추출 결과 저장됨: File ID {file_id}")
                
        except Exception as e:
            logger.error(f"추출 결과 저장 오류: {e}")
            raise
    
    async def get_pending_files(self) -> List[Dict[str, Any]]:
        """정리 대기 중인 파일 목록 가져오기"""
        try:
            async with self.session_factory() as session:
                query = text("""
                    SELECT f.id, f.path, f.ext, f.size, e.text_snippet, e.meta_json
                    FROM files f
                    LEFT JOIN extractions e ON f.id = e.file_id
                    WHERE f.status = 'EXTRACTED'
                    AND NOT EXISTS (
                        SELECT 1 FROM label_events le WHERE le.file_id = f.id
                    )
                    ORDER BY f.created_at DESC
                """)
                
                result = await session.execute(query)
                files = []
                
                for row in result:
                    files.append({
                        "id": row.id,
                        "path": row.path,
                        "ext": row.ext,
                        "size": row.size,
                        "text_snippet": row.text_snippet,
                        "meta_json": row.meta_json
                    })
                
                return files
                
        except Exception as e:
            logger.error(f"대기 파일 목록 가져오기 오류: {e}")
            return []
    
    async def get_pending_files_count(self) -> int:
        """정리 대기 중인 파일 개수"""
        try:
            async with self.session_factory() as session:
                query = text("""
                    SELECT COUNT(*)
                    FROM files f
                    WHERE f.status = 'EXTRACTED'
                    AND NOT EXISTS (
                        SELECT 1 FROM label_events le WHERE le.file_id = f.id
                    )
                """)
                
                result = await session.execute(query)
                count = result.scalar()
                return count or 0
                
        except Exception as e:
            logger.error(f"대기 파일 개수 조회 오류: {e}")
            return 0
    
    async def get_config(self) -> Optional[Dict[str, Any]]:
        """현재 설정 가져오기"""
        try:
            async with self.session_factory() as session:
                query = text("""
                    SELECT monitoring_folder, moving_folder, threshold, auto_organize, run_time, active
                    FROM config
                    WHERE active = true
                    ORDER BY created_at DESC
                    LIMIT 1
                """)
                
                result = await session.execute(query)
                row = result.fetchone()
                
                if row:
                    return {
                        "monitoring_folder": row.monitoring_folder,
                        "moving_folder": row.moving_folder,
                        "threshold": row.threshold,
                        "auto_organize": row.auto_organize,
                        "run_time": row.run_time,
                        "active": row.active
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"설정 조회 오류: {e}")
            return None
    
    async def update_config(self, config: Dict[str, Any]):
        """설정 업데이트"""
        try:
            async with self.session_factory() as session:
                query = text("""
                    INSERT INTO config (monitoring_folder, moving_folder, threshold, auto_organize, run_time, active, created_at)
                    VALUES (:monitoring_folder, :moving_folder, :threshold, :auto_organize, :run_time, :active, NOW())
                    ON CONFLICT (id) DO UPDATE SET
                        monitoring_folder = EXCLUDED.monitoring_folder,
                        moving_folder = EXCLUDED.moving_folder,
                        threshold = EXCLUDED.threshold,
                        auto_organize = EXCLUDED.auto_organize,
                        run_time = EXCLUDED.run_time,
                        active = EXCLUDED.active,
                        updated_at = NOW()
                """)
                
                await session.execute(query, config)
                await session.commit()
                
                logger.info("설정 업데이트됨")
                
        except Exception as e:
            logger.error(f"설정 업데이트 오류: {e}")
            raise
    
    async def get_stats(self) -> Dict[str, Any]:
        """통계 정보 가져오기"""
        try:
            async with self.session_factory() as session:
                # 기본 통계 쿼리
                stats_query = text("""
                    SELECT 
                        COUNT(*) as total_files,
                        COUNT(CASE WHEN status = 'EXTRACTED' THEN 1 END) as extracted_files,
                        COUNT(CASE WHEN status = 'LABELED' THEN 1 END) as labeled_files,
                        COUNT(CASE WHEN status = 'MOVED' THEN 1 END) as moved_files
                    FROM files
                """)
                
                result = await session.execute(stats_query)
                row = result.fetchone()
                
                # 설정 정보
                config = await self.get_config()
                
                return {
                    "total_files": row.total_files or 0,
                    "extracted_files": row.extracted_files or 0,
                    "labeled_files": row.labeled_files or 0,
                    "moved_files": row.moved_files or 0,
                    "pending_files": await self.get_pending_files_count(),
                    "monitoring_folder": config.get("monitoring_folder", "") if config else "",
                    "last_organized": "2시간 전"  # 향후 실제 데이터로 교체
                }
                
        except Exception as e:
            logger.error(f"통계 조회 오류: {e}")
            return {}
    
    def _calculate_hash(self, file_path: str) -> str:
        """파일 해시 계산"""
        import hashlib
        
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""
