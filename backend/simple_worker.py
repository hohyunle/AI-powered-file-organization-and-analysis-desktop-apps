"""
간단한 Python Worker 테스트 버전

데이터베이스나 복잡한 의존성 없이 기본 기능만 테스트합니다.
"""

import asyncio
import json
import sys
import os
import signal
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger


class SimplePythonWorker:
    """간단한 Python Worker 테스트 클래스"""
    
    def __init__(self):
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
        logger.info("간단한 Python Worker 시작 중...")
        
        try:
            self.is_running = True
            
            # 메인 루프 시작
            await self._main_loop()
            
        except Exception as e:
            logger.error(f"워커 시작 실패: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """워커 종료"""
        logger.info("간단한 Python Worker 종료 중...")
        
        self.is_running = False
        
        # 모든 태스크 취소
        for task in self.tasks:
            task.cancel()
        
        logger.info("간단한 Python Worker 종료 완료")
    
    async def _main_loop(self):
        """메인 실행 루프"""
        logger.info("메인 루프 시작")
        
        while self.is_running:
            try:
                # 주기적 상태 업데이트
                await self._update_status()
                
                # 5초 대기
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"메인 루프 오류: {e}")
                await asyncio.sleep(5)  # 오류 시 5초 대기
    
    async def _update_status(self):
        """상태 업데이트 (Electron으로 전송)"""
        try:
            stats = {
                "total_files": 0,
                "extracted_files": 0,
                "labeled_files": 0,
                "moved_files": 0,
                "pending_files": 0,
                "monitoring_folder": "C:/Downloads",
                "last_organized": "테스트 모드"
            }
            
            # Electron으로 상태 전송 (stdout을 통해)
            status_data = {
                "type": "status_update",
                "data": stats,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            print(f"STATUS:{json.dumps(status_data)}", flush=True)
            logger.info("상태 업데이트 전송됨")
            
        except Exception as e:
            logger.error(f"상태 업데이트 오류: {e}")
    
    async def handle_command(self, command: Dict[str, Any]):
        """Electron으로부터 명령 처리"""
        try:
            cmd_type = command.get('type')
            
            if cmd_type == 'start_cleanup':
                logger.info("정리 작업 시작 명령 수신")
                return {"success": True, "message": "테스트 모드: 정리 작업 시작됨"}
            
            elif cmd_type == 'get_stats':
                stats = {
                    "total_files": 0,
                    "extracted_files": 0,
                    "labeled_files": 0,
                    "moved_files": 0,
                    "pending_files": 0,
                    "monitoring_folder": "C:/Downloads",
                    "last_organized": "테스트 모드"
                }
                return {"success": True, "data": stats}
            
            elif cmd_type == 'update_config':
                config = command.get('config', {})
                logger.info(f"설정 업데이트 명령 수신: {config}")
                return {"success": True, "message": "테스트 모드: 설정 업데이트됨"}
            
            else:
                return {"success": False, "error": f"알 수 없는 명령: {cmd_type}"}
                
        except Exception as e:
            logger.error(f"명령 처리 오류: {e}")
            return {"success": False, "error": str(e)}
    
    async def handle_stdin_commands(self):
        """stdin으로부터 명령 수신 및 처리"""
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
        "worker/logs/simple_worker.log",
        rotation="1 day",
        retention="7 days",
        level="INFO"
    )
    
    worker = SimplePythonWorker()
    
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
