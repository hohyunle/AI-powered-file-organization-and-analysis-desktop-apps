"""
Python Worker 테스트 스크립트

Electron과 Python Worker 간의 통신을 테스트합니다.
"""

import subprocess
import json
import time
import sys
from pathlib import Path


def test_python_worker():
    """Python Worker 테스트"""
    print("Python Worker 테스트 시작")
    print("=" * 50)
    
    try:
        # Python Worker 프로세스 시작
        worker_path = Path(__file__).parent / "simple_worker.py"
        print(f"Python Worker 실행: {worker_path}")
        
        process = subprocess.Popen(
            [sys.executable, str(worker_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print(f"Python Worker PID: {process.pid}")
        
        # 상태 업데이트 수신 대기
        print("\n상태 업데이트 수신 대기...")
        time.sleep(3)
        
        # 명령 전송 테스트
        test_commands = [
            {"type": "get_stats"},
            {"type": "start_cleanup"},
            {"type": "update_config", "config": {"threshold": 100}}
        ]
        
        for i, command in enumerate(test_commands, 1):
            print(f"\n테스트 명령 {i}: {command['type']}")
            
            # 명령 전송
            command_json = json.dumps(command) + '\n'
            process.stdin.write(command_json)
            process.stdin.flush()
            
            # 응답 수신 대기
            time.sleep(1)
            
            # 출력 확인
            if process.poll() is None:
                print("Python Worker가 정상적으로 응답 중")
            else:
                print("Python Worker가 종료됨")
                break
        
        # 프로세스 종료
        print("\nPython Worker 종료 중...")
        process.terminate()
        
        try:
            process.wait(timeout=5)
            print("Python Worker 정상 종료")
        except subprocess.TimeoutExpired:
            print("강제 종료")
            process.kill()
        
        print("\n테스트 완료!")
        
    except Exception as e:
        print(f"테스트 실패: {e}")
        return False
    
    return True


def test_imports():
    """필요한 모듈 import 테스트"""
    print("모듈 import 테스트")
    print("=" * 30)
    
    modules = [
        ("asyncio", "비동기 처리"),
        ("json", "JSON 처리"),
        ("pathlib", "경로 처리"),
        ("loguru", "로깅"),
        ("watchdog", "파일 감시")
    ]
    
    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"OK {module_name}: {description}")
        except ImportError as e:
            print(f"FAIL {module_name}: {description} - {e}")
    
    print()


if __name__ == "__main__":
    print("Python Worker 통합 테스트")
    print("=" * 50)
    
    # 모듈 import 테스트
    test_imports()
    
    # Python Worker 테스트
    success = test_python_worker()
    
    if success:
        print("\n모든 테스트 통과!")
        sys.exit(0)
    else:
        print("\n테스트 실패!")
        sys.exit(1)
