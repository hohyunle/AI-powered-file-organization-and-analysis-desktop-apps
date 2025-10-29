"""
AI 파일 정리 도우미 - Python Worker

이 모듈은 Electron 메인 프로세스에서 child_process로 실행되는
Python 워커 프로세스의 진입점입니다.

주요 기능:
1. 파일 시스템 감시 (watchdog)
2. 파일 내용 추출 (PDF, PPTX, DOCX, 이미지 OCR 등)
3. AI를 통한 파일 분류 및 정리 계획 생성
4. PostgreSQL 데이터베이스 연동
5. Electron과의 IPC 통신
"""

import asyncio
import json
import sys
import os
import signal
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

# 한글 인코딩 설정
import locale
import codecs

# Windows에서 한글 출력을 위한 인코딩 설정
if sys.platform == 'win32':
    # 콘솔 출력 인코딩을 UTF-8로 설정
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
    
    # 로케일 설정
    try:
        locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'Korean_Korea.949')
        except:
            pass

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.services.file_watcher import FileWatcher
from backend.services.text_extractor import TextExtractor
from backend.services.database_manager import DatabaseManager
from backend.services.mcp_client import MCPClient
from backend.services.organizer import FileOrganizer
from backend.config.settings import Settings


class PythonWorker:
    """Python Worker 메인 클래스"""
    
    def __init__(self):
        self.settings = Settings()
        self.db_manager = DatabaseManager()
        self.file_watcher = FileWatcher()
        self.text_extractor = TextExtractor()
        self.mcp_client = MCPClient()
        self.organizer = FileOrganizer()
        
        self.is_running = False
        self.tasks = []
        
        # 시그널 핸들러 등록
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """시그널 핸들러 (Ctrl+C, 종료 신호 등)"""
        logger.info(f"시그널 {signum} 수신, 워커 종료 중...")
        self.stop()
    
    async def start(self):
        """워커 시작"""
        logger.info("Python Worker 시작 중...")
        
        try:
            # 데이터베이스 연결
            await self.db_manager.connect()
            logger.info("데이터베이스 연결 완료")
            
            # 설정 로드
            config = await self.db_manager.get_config()
            if not config:
                logger.warning("설정이 없습니다. 기본 설정을 사용합니다.")
                config = self.settings.get_default_config()
            
            # 파일 감시 시작 (설정이 없으면 기본값 사용)
            monitoring_folder = config.get('monitoring_folder', 'C:/Downloads')
            if not monitoring_folder or monitoring_folder == '':
                monitoring_folder = 'C:/Downloads'
            
            await self.file_watcher.start_watching(monitoring_folder)
            logger.info(f"파일 감시 시작: {monitoring_folder}")
            
            # 상태 출력 (Electron에서 파싱 가능하도록)
            print(f"STATUS:{json.dumps({'watching': True, 'folder': monitoring_folder})}")
            
            # MCP 클라이언트 초기화
            await self.mcp_client.initialize()
            logger.info("MCP 클라이언트 초기화 완료")
            
            self.is_running = True
            
            # 메인 루프 시작
            await self._main_loop()
            
        except Exception as e:
            logger.error(f"워커 시작 실패: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """워커 종료"""
        logger.info("Python Worker 종료 중...")
        
        self.is_running = False
        
        # 모든 태스크 취소
        for task in self.tasks:
            task.cancel()
        
        # 파일 감시 중지
        await self.file_watcher.stop_watching()
        
        # 데이터베이스 연결 종료
        await self.db_manager.disconnect()
        
        # MCP 클라이언트 종료
        await self.mcp_client.close()
        
        logger.info("Python Worker 종료 완료")
    
    async def _main_loop(self):
        """메인 실행 루프"""
        logger.info("메인 루프 시작")
        
        while self.is_running:
            try:
                # 새로운 파일 처리
                await self._process_new_files()
                
                # 임계값 확인 및 자동 정리
                await self._check_auto_organize_threshold()
                
                # 주기적 상태 업데이트
                await self._update_status()
                
                # 1초 대기
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"메인 루프 오류: {e}")
                await asyncio.sleep(5)  # 오류 시 5초 대기
    
    async def _process_new_files(self):
        """새로운 파일 처리"""
        try:
            # 감지된 새 파일들 가져오기
            new_files = await self.file_watcher.get_new_files()
            
            for file_path in new_files:
                # 파일을 데이터베이스에 등록
                file_id = await self.db_manager.add_file(file_path)
                
                # 텍스트 추출
                extraction_result = await self.text_extractor.extract_text(file_path)
                
                # 추출 결과를 데이터베이스에 저장
                await self.db_manager.save_extraction(file_id, extraction_result)
                
                logger.info(f"파일 처리 완료: {file_path}")
                
        except Exception as e:
            logger.error(f"새 파일 처리 오류: {e}")
    
    async def _check_auto_organize_threshold(self):
        """자동 정리 임계값 확인"""
        try:
            config = await self.db_manager.get_config()
            if not config.get('auto_organize', False):
                return
            
            threshold = config.get('threshold', 50)
            pending_count = await self.db_manager.get_pending_files_count()
            
            if pending_count >= threshold:
                logger.info(f"임계값 도달 ({pending_count}/{threshold}), 자동 정리 시작")
                await self._start_organize()
                
        except Exception as e:
            logger.error(f"자동 정리 임계값 확인 오류: {e}")
    
    async def _start_organize(self):
        """정리 작업 시작"""
        try:
            # 미분류 파일들 가져오기
            pending_files = await self.db_manager.get_pending_files()
            
            if not pending_files:
                logger.info("정리할 파일이 없습니다.")
                return
            
            # MCP를 통해 AI에게 분류 요청
            classification_plan = await self.mcp_client.classify_files(pending_files)
            
            # 정리 실행
            job_id = await self.organizer.execute_plan(classification_plan)
            
            logger.info(f"정리 작업 완료: Job ID {job_id}")
            
        except Exception as e:
            logger.error(f"정리 작업 오류: {e}")
    
    async def _update_status(self):
        """상태 업데이트 (Electron으로 전송)"""
        try:
            stats = await self.db_manager.get_stats()
            
            # Electron으로 상태 전송 (stdout을 통해)
            status_data = {
                "type": "status_update",
                "data": stats,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            print(f"STATUS:{json.dumps(status_data)}", flush=True)
            
        except Exception as e:
            logger.error(f"상태 업데이트 오류: {e}")
    
    async def handle_command(self, command: Dict[str, Any]):
        """Electron으로부터 명령 처리"""
        try:
            cmd_type = command.get('type')
            
            if cmd_type == 'start_cleanup':
                await self._start_organize()
                return {"success": True, "message": "정리 작업 시작됨"}
            
            elif cmd_type == 'get_stats':
                stats = await self.db_manager.get_stats()
                return {"success": True, "data": stats}
            
            elif cmd_type == 'update_config':
                config = command.get('config', {})
                await self.db_manager.update_config(config)
                return {"success": True, "message": "설정 업데이트됨"}
            
            else:
                return {"success": False, "error": f"알 수 없는 명령: {cmd_type}"}
                
        except Exception as e:
            logger.error(f"명령 처리 오류: {e}")
            return {"success": False, "error": str(e)}
    
    async def handle_stdin_commands(self):
        """stdin으로부터 명령 수신 및 처리"""
        import sys
        
        try:
            while self.is_running:
                # 비동기적으로 stdin 읽기
                loop = asyncio.get_event_loop()
                line = await loop.run_in_executor(None, sys.stdin.readline)
                
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # JSON 명령 파싱
                    command = json.loads(line)
                    logger.info(f"명령 수신: {command}")
                    
                    # 명령 처리
                    result = await self.handle_command(command)
                    
                    # 결과 출력 (Electron으로 전송)
                    print(f"RESULT:{json.dumps(result)}", flush=True)
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON 파싱 오류: {e}")
                    error_result = {"success": False, "error": f"JSON 파싱 오류: {e}"}
                    print(f"RESULT:{json.dumps(error_result)}", flush=True)
                
        except Exception as e:
            logger.error(f"stdin 명령 처리 오류: {e}")


async def main():
    """메인 함수"""
    # 로깅 설정
    logger.add(
        "backend/logs/worker.log",
        rotation="1 day",
        retention="7 days",
        level="INFO"
    )
    
    worker = PythonWorker()
    
    try:
        # Electron으로부터 명령 수신을 위한 태스크 시작
        command_task = asyncio.create_task(worker.handle_stdin_commands())
        
        await worker.start()
        
        # 명령 처리 태스크도 함께 실행
        await command_task
        
    except KeyboardInterrupt:
        logger.info("사용자에 의한 종료")
    except Exception as e:
        logger.error(f"워커 실행 오류: {e}")
    finally:
        await worker.stop()


if __name__ == "__main__":
    # 비동기 메인 함수 실행
    asyncio.run(main())
