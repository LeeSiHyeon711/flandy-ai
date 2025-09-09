#!/usr/bin/env python3
import asyncio
import websockets
import json
import time

async def test_websocket():
    uri = "ws://127.0.0.1:8001/ws/chat"
    
    print("🚀 WebSocket 실시간 스트림 테스트 시작...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket 연결 성공!")
            
            # 메시지 전송
            message_data = {
                "message": "안녕하세요! 오늘 일정을 확인해주세요.",
                "user_id": 1,
                "session_id": "test_ws_001"
            }
            
            await websocket.send(json.dumps(message_data))
            print(f"📤 메시지 전송: {message_data['message']}")
            print("-" * 60)
            
            # 실시간 응답 수신
            start_time = time.time()
            message_count = 0
            
            async for message in websocket:
                message_count += 1
                current_time = time.time()
                elapsed = current_time - start_time
                
                try:
                    data = json.loads(message)
                    print(f"[{elapsed:.2f}s] 메시지 #{message_count}: {data}")
                    
                    if data.get("type") == "complete":
                        print("🏁 스트림 완료!")
                        break
                        
                except json.JSONDecodeError:
                    print(f"[{elapsed:.2f}s] 메시지 #{message_count}: {message}")
            
            print("-" * 60)
            print(f"✅ 테스트 완료! 총 {message_count}개 메시지 수신, {elapsed:.2f}초 소요")
            
    except Exception as e:
        print(f"❌ 오류: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
