결ㅏ 본#!/usr/bin/env python3
import requests
import json
import time

def test_long_response():
    url = "http://127.0.0.1:8001/chat"
    data = {
        "message": "오늘 하루 일정을 자세히 계획해주세요. 아침부터 저녁까지 시간대별로 구체적인 계획을 세워주고, 각 시간대마다 해야 할 일들과 휴식 시간도 포함해서 상세하게 설명해주세요. 그리고 일정 관리 팁과 생산성 향상 방법도 함께 알려주세요."
    }
    
    print("🚀 긴 응답 스트림 테스트 시작...")
    print(f"📝 요청: {data['message'][:50]}...")
    print("-" * 60)
    
    try:
        response = requests.post(url, json=data, stream=True, timeout=30)
        print(f"상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            print("📊 실시간 스트림 수신 중...")
            chunk_count = 0
            start_time = time.time()
            
            for chunk in response.iter_content(chunk_size=1, decode_unicode=True):
                if chunk:
                    chunk_count += 1
                    current_time = time.time()
                    elapsed = current_time - start_time
                    
                    print(f"[{elapsed:.2f}s] 청크 #{chunk_count}: {repr(chunk)}")
                    
                    # 0.1초마다 시간 표시
                    if chunk_count % 10 == 0:
                        print(f"    ⏱️  {elapsed:.2f}초 경과, {chunk_count}개 청크 수신")
        else:
            print(f"오류: {response.text}")
            
    except Exception as e:
        print(f"예외: {e}")

if __name__ == "__main__":
    test_long_response()
