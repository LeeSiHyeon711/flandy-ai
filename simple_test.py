#!/usr/bin/env python3
import requests
import json

def test_simple():
    url = "http://127.0.0.1:8001/chat"
    data = {"message": "안녕하세요"}
    
    print("테스트 시작...")
    
    try:
        response = requests.post(url, json=data, stream=True, timeout=10)
        print(f"상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            print("응답 수신 중...")
            for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                if chunk:
                    print(f"청크: {repr(chunk)}")
        else:
            print(f"오류: {response.text}")
            
    except Exception as e:
        print(f"예외: {e}")

if __name__ == "__main__":
    test_simple()
