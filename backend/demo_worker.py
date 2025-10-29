"""
Python Worker 데모 스크립트

실제 파일 감시 기능을 시연합니다.
"""

import asyncio
import json
import sys
import os
import signal
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent


class DemoFileHandler(FileSystemEventHandler):
    """데모용 파일 변경 이벤트 핸들러"""
    
    def __init__(self, worker):
        self.worker = worker
        self.processed_files = set()
    
    def on_created(self, event):
        """파일 생성 이벤트"""
        if not event.is_directory:
            file_path = Path(event.src_path)
            if self._is_valid_file(file_path):
                logger.info(f"새 파일 감지: {file_path}")
                self.worker.new_files.append(str(file_path))
    
    def _is_valid_file(self, file_path: Path) -> bool:
        """유효한 파일인지 확인"""
        allowed_extensions = {'.txt', '.pdf', '.docx', '.jpg', '.png'}
        return (
            file_path.exists() and 
            file_path.is_file() and 
            file_path.suffix.lower() in allowed_extensions and
            str(file_path) not in self.processed_files
        )


class DemoPythonWorker:
    """데모용 Python Worker"""
    
    def __init__(self):
        self.is_running = False
        self.observer = None
        self.new_files = []
        self.watch_folder = "C:/Downloads"  # 기본 감시 폴더
        
        # 시그널 핸들러 등록
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """시그널 핸들러"""
        logger.info(f"시그널 {signum} 수신, 워커 종료 중...")
        self.stop()
    
    async def start(self):
        """워커 시작"""
        logger.info("데모 Python Worker 시작 중...")
        
        try:
            # 파일 감시 시작
            await self._start_file_watching()
            
            self.is_running = True
            
            # 메인 루프 시작
            await self._main_loop()
            
        except Exception as e:
            logger.error(f"워커 시작 실패: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """워커 종료"""
        logger.info("데모 Python Worker 종료 중...")
        
        self.is_running = False
        
        # 파일 감시 중지
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        logger.info("데모 Python Worker 종료 완료")
    
    async def _start_file_watching(self):
        """파일 감시 시작"""
        try:
            watch_path = Path(self.watch_folder)
            if not watch_path.exists():
                logger.warning(f"감시 폴더가 존재하지 않습니다: {self.watch_folder}")
                return
            
            self.observer = Observer()
            handler = DemoFileHandler(self)
            
            self.observer.schedule(handler, str(watch_path), recursive=True)
            self.observer.start()
            
            logger.info(f"파일 감시 시작: {self.watch_folder}")
            
        except Exception as e:
            logger.error(f"파일 감시 시작 실패: {e}")
            raise
    
    async def _main_loop(self):
        """메인 실행 루프"""
        logger.info("메인 루프 시작")
        
        while self.is_running:
            try:
                # 새로운 파일 처리
                await self._process_new_files()
                
                # 상태 업데이트
                await self._update_status()
                
                # 2초 대기
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"메인 루프 오류: {e}")
                await asyncio.sleep(5)
    
    async def _process_new_files(self):
        """새로운 파일 처리"""
        try:
            if self.new_files:
                files = self.new_files.copy()
                self.new_files.clear()
                
                for file_path in files:
                    logger.info(f"파일 처리 중: {file_path}")
                    
                    # 간단한 파일 정보 추출
                    file_info = {
                        "path": file_path,
                        "size": Path(file_path).stat().st_size,
                        "extension": Path(file_path).suffix,
                        "processed_at": asyncio.get_event_loop().time()
                    }
                    
                    logger.info(f"파일 정보: {file_info}")
                
        except Exception as e:
            logger.error(f"새 파일 처리 오류: {e}")
    
    async def _update_status(self):
        """상태 업데이트"""
        try:
            stats = {
                "total_files": len(self.new_files),
                "monitoring_folder": self.watch_folder,
                "status": "monitoring",
                "timestamp": asyncio.get_event_loop().time()
            }
            
            # Electron으로 상태 전송
            status_data = {
                "type": "status_update",
                "data": stats
            }
            
            print(f"STATUS:{json.dumps(status_data)}", flush=True)
            
        except Exception as e:
            logger.error(f"상태 업데이트 오류: {e}")
    
    async def handle_command(self, command: Dict[str, Any]):
        """명령 처리"""
        try:
            cmd_type = command.get('type')
            
            if cmd_type == 'get_stats':
                stats = {
                    "total_files": len(self.new_files),
                    "monitoring_folder": self.watch_folder,
                    "status": "monitoring"
                }
                return {"success": True, "data": stats}
            
            elif cmd_type == 'start_cleanup':
                logger.info("정리 작업 시작")
                return {"success": True, "message": "데모 모드: 정리 작업 시작됨"}
            
            elif cmd_type == 'update_config':
                config = command.get('config', {})
                if 'monitoring_folder' in config:
                    self.watch_folder = config['monitoring_folder']
                    logger.info(f"모니터링 폴더 변경: {self.watch_folder}")
                return {"success": True, "message": "설정 업데이트됨"}
            
            else:
                return {"success": False, "error": f"알 수 없는 명령: {cmd_type}"}
                
        except Exception as e:
            logger.error(f"명령 처리 오류: {e}")
            return {"success": False, "error": str(e)}
    
    async def handle_stdin_commands(self):
        """stdin 명령 처리"""
        try:
            while self.is_running:
                loop = asyncio.get_event_loop()
                line = await loop.run_in_executor(None, sys.stdin.readline)
                
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    command = json.loads(line)
                    logger.info(f"명령 수신: {command}")
                    
                    result = await self.handle_command(command)
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
        "worker/logs/demo_worker.log",
        rotation="1 day",
        retention="7 days",
        level="INFO"
    )
    
    worker = DemoPythonWorker()
    
    try:
        # 명령 처리 태스크 시작
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
    asyncio.run(main())
