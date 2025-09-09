#!/usr/bin/env python3
"""
스트림 응답 테스트 스크립트
/chat 엔드포인트의 SSE 스트림이 제대로 작동하는지 테스트합니다.
"""

import requests
import json
import time
from typing import Iterator

def test_stream_response():
    """스트림 응답 테스트"""
    url = "http://127.0.0.1:8001/chat"
    
    # 테스트 데이터
    test_data = {
        "message": "안녕하세요! 오늘 일정을 확인해주세요.",
        "user_id": 1,
        "session_id": "test_session_001"
    }
    
    print("🚀 스트림 응답 테스트 시작...")
    print(f"📡 요청 URL: {url}")
    print(f"📝 요청 데이터: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    print("-" * 60)
    
    try:
        # 스트림 요청
        response = requests.post(
            url,
            json=test_data,
            headers={
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache"
            },
            stream=True,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ HTTP 오류: {response.status_code}")
            print(f"응답 내용: {response.text}")
            return
        
        print("✅ 스트림 연결 성공!")
        print("📊 실시간 응답 데이터:")
        print("-" * 60)
        
        # SSE 데이터 파싱 및 출력
        buffer = ""
        event_count = 0
        
        for chunk in response.iter_content(chunk_size=1, decode_unicode=True):
            if chunk:
                buffer += chunk
                
                # 완전한 이벤트가 수신되었는지 확인
                while "\n\n" in buffer:
                    event, buffer = buffer.split("\n\n", 1)
                    event_count += 1
                    
                    if event.strip():
                        print(f"📨 이벤트 #{event_count}:")
                        print(f"   {event}")
                        
                        # JSON 데이터 파싱 시도
                        try:
                            lines = event.split('\n')
                            data_line = None
                            event_type = None
                            event_id = None
                            
                            for line in lines:
                                if line.startswith('data: '):
                                    data_line = line[6:]  # 'data: ' 제거
                                elif line.startswith('event: '):
                                    event_type = line[7:]  # 'event: ' 제거
                                elif line.startswith('id: '):
                                    event_id = line[4:]  # 'id: ' 제거
                            
                            if data_line and data_line != "[DONE]":
                                try:
                                    data = json.loads(data_line)
                                    print(f"   📋 파싱된 데이터:")
                                    print(f"      - 이벤트 ID: {event_id}")
                                    print(f"      - 이벤트 타입: {event_type}")
                                    print(f"      - 상태: {data.get('status', 'N/A')}")
                                    print(f"      - 메시지: {data.get('message', 'N/A')}")
                                    
                                    if 'ai_response' in data and data['ai_response']:
                                        print(f"      - AI 응답: {data['ai_response'][:100]}...")
                                    
                                except json.JSONDecodeError:
                                    print(f"   ⚠️  JSON 파싱 실패: {data_line}")
                            
                            elif data_line == "[DONE]":
                                print("   🏁 스트림 종료 신호 수신")
                                break
                                
                        except Exception as e:
                            print(f"   ❌ 이벤트 처리 오류: {e}")
                        
                        print()
        
        print("-" * 60)
        print(f"✅ 테스트 완료! 총 {event_count}개 이벤트 수신")
        
    except requests.exceptions.Timeout:
        print("⏰ 요청 시간 초과 (30초)")
    except requests.exceptions.ConnectionError:
        print("🔌 연결 오류: 서버가 실행 중인지 확인하세요")
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")

def test_health_check():
    """헬스 체크 테스트"""
    url = "http://127.0.0.1:8001/health"
    
    print("🏥 헬스 체크 테스트...")
    
    try:
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 헬스 체크 성공!")
            print(f"   상태: {data.get('status')}")
            print(f"   메시지: {data.get('message')}")
            print(f"   시스템 정보: {data.get('system_info')}")
        else:
            print(f"❌ 헬스 체크 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 헬스 체크 오류: {e}")

if __name__ == "__main__":
    print("🧪 Plandy AI 스트림 응답 테스트")
    print("=" * 60)
    
    # 헬스 체크 먼저 실행
    test_health_check()
    print()
    
    # 스트림 응답 테스트
    test_stream_response()
