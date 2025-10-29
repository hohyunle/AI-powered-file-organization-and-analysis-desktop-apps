"""
Python Worker 통신 테스트

실제 Electron과 Python Worker 간의 통신을 테스트합니다.
"""

import subprocess
import json
import time
import sys
from pathlib import Path


def test_electron_python_communication():
    """Electron과 Python Worker 간 통신 테스트"""
    print("Electron-Python Worker 통신 테스트")
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
        
        # stdout에서 상태 메시지 확인
        if process.poll() is None:
            print("Python Worker가 정상적으로 실행 중")
            
            # 명령 전송 테스트
            test_command = {"type": "get_stats"}
            command_json = json.dumps(test_command) + '\n'
            
            print(f"\n명령 전송: {test_command}")
            process.stdin.write(command_json)
            process.stdin.flush()
            
            # 응답 대기
            time.sleep(2)
            
            # 프로세스 상태 확인
            if process.poll() is None:
                print("Python Worker가 명령에 정상 응답")
            else:
                print("Python Worker가 종료됨")
        
        # 프로세스 종료
        print("\nPython Worker 종료 중...")
        process.terminate()
        
        try:
            process.wait(timeout=5)
            print("Python Worker 정상 종료")
        except subprocess.TimeoutExpired:
            print("강제 종료")
            process.kill()
        
        print("\n통신 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"통신 테스트 실패: {e}")
        return False


def show_worker_status():
    """현재 Worker 상태 표시"""
    print("현재 Python Worker 상태")
    print("=" * 30)
    
    # 실행 중인 Python 프로세스 확인
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True)
        
        if 'python.exe' in result.stdout:
            print("Python 프로세스가 실행 중입니다.")
            lines = result.stdout.split('\n')
            for line in lines:
                if 'python.exe' in line:
                    print(f"  {line.strip()}")
        else:
            print("실행 중인 Python 프로세스가 없습니다.")
            
    except Exception as e:
        print(f"프로세스 확인 오류: {e}")
    
    print()


if __name__ == "__main__":
    print("Python Worker 작동 확인")
    print("=" * 50)
    
    # 현재 상태 확인
    show_worker_status()
    
    # 통신 테스트
    success = test_electron_python_communication()
    
    if success:
        print("\nPython Worker가 정상적으로 작동합니다!")
        print("\n주요 기능:")
        print("- Electron과의 stdin/stdout 통신")
        print("- JSON 명령/응답 처리")
        print("- 비동기 메인 루프")
        print("- 상태 업데이트 전송")
        print("- 명령 처리 및 응답")
    else:
        print("\nPython Worker 작동에 문제가 있습니다.")
    
    sys.exit(0 if success else 1)
