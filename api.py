from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
import uvicorn
from main import PlandyAISystem
import logging
import json
import time

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Plandy AI API",
    description="AI 에이전트 기반 일정 관리 시스템",
    version="1.0.0"
)

# CORS 설정 (프론트엔드에서 접근 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서는 모든 오리진 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Plandy AI 시스템 인스턴스
plandy_ai = None

async def flush_stream():
    """스트림 플러시를 위한 유틸리티 함수"""
    await asyncio.sleep(0.1)  # 더 긴 지연으로 실제 스트림 플러시 보장

async def yield_sse_event(event_id: str, event_type: str, data: dict, retry: int = None):
    """SSE 이벤트를 개별적으로 yield"""
    yield f"id: {event_id}\n"
    yield f"event: {event_type}\n"
    if retry:
        yield f"retry: {retry}\n"
    
    # JSON 데이터를 안전하게 인코딩
    json_data = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    yield f"data: {json_data}\n"
    yield "\n"  # 빈 줄로 이벤트 종료

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 Plandy AI 시스템 초기화"""
    global plandy_ai
    try:
        plandy_ai = PlandyAISystem()
        logger.info("Plandy AI 시스템이 초기화되었습니다.")
    except Exception as e:
        logger.error(f"Plandy AI 시스템 초기화 실패: {e}")
        raise

class ChatRequest(BaseModel):
    """채팅 요청 모델"""
    message: str
    user_id: Optional[int] = 1
    session_id: Optional[str] = None
    chat_room_id: Optional[int] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    success: bool
    message: str
    ai_response: str
    session_id: Optional[str] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    """헬스 체크 응답 모델"""
    status: str
    message: str
    system_info: Dict[str, Any]

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """시스템 상태 확인"""
    try:
        if plandy_ai is None:
            return HealthResponse(
                status="error",
                message="Plandy AI 시스템이 초기화되지 않았습니다.",
                system_info={}
            )
        
        system_info = {
            "graph_type": plandy_ai.graph_type,
            "node_count": plandy_ai.node_count,
            "edge_count": plandy_ai.edge_count,
            "available_tools": plandy_ai.available_tools_count,
            "prompt_templates": plandy_ai.prompt_templates_count
        }
        
        return HealthResponse(
            status="success",
            message="시스템이 정상적으로 작동 중입니다.",
            system_info=system_info
        )
    except Exception as e:
        logger.error(f"헬스 체크 실패: {e}")
        return HealthResponse(
            status="error",
            message=f"시스템 오류: {str(e)}",
            system_info={}
        )

async def generate_stream_response(request: ChatRequest):
    """스트림 응답 생성"""
    try:
        if plandy_ai is None:
            error_data = {'error': 'Plandy AI 시스템이 초기화되지 않았습니다.'}
            async for chunk in yield_sse_event("error", "error", error_data):
                yield chunk
            return
        
        logger.info(f"채팅 요청 수신: {request.message}")
        
        # 초기 응답 전송 (SSE 표준 형식)
        initial_data = {
            'status': 'processing', 
            'message': 'AI가 응답을 생성하고 있습니다...'
        }
        async for chunk in yield_sse_event("init", "status", initial_data, 3000):
            yield chunk
        
        # Plandy AI 시스템으로 실시간 스트림 처리
        from agents.nodes.supervisor_node import supervisor_node
        from agents.nodes.plan_node import plan_node
        from agents.nodes.worklife_node import worklife_node
        from agents.nodes.communication_node import communication_node
        
        # 사용자 입력 강화
        enhanced_input = f"""
        [시스템 지시사항]
        - 사용자 언어: 한국어
        - 사용자 시간대: Asia/Seoul
        - 사용자가 쓰는 언어로 응답해야 합니다
        - 해당 지역의 시간을 조회해야 합니다
        
        [사용자 입력]
        {request.message}
        """
        
        # 초기 상태 생성
        initial_state = plandy_ai.create_initial_state(enhanced_input, request.user_id)
        
        # 실시간 스트림 처리
        final_ai_response = ""
        current_state = initial_state
        
        # 1. Supervisor 노드 처리
        supervisor_start_data = {
            'status': 'processing', 
            'message': 'supervisor 처리 중...', 
            'node': 'supervisor'
        }
        async for chunk in yield_sse_event("supervisor_start", "node_status", supervisor_start_data, 3000):
            yield chunk
        
        supervisor_result = supervisor_node(current_state)
        current_state.update(supervisor_result)
        
        # Supervisor 결과 즉시 전송
        supervisor_complete_data = {
            'status': 'completed', 
            'message': 'supervisor 완료', 
            'node': 'supervisor'
        }
        async for chunk in yield_sse_event("supervisor_complete", "node_status", supervisor_complete_data):
            yield chunk
        
        # 2. Plan 노드 처리 (실시간)
        plan_start_data = {
            'status': 'processing', 
            'message': 'plan_agent 처리 중...', 
            'node': 'plan_agent'
        }
        async for chunk in yield_sse_event("plan_start", "node_status", plan_start_data):
            yield chunk
        
        plan_result = await plan_node(current_state)
        current_state.update(plan_result)
        
        if "ai_response" in plan_result and plan_result["ai_response"]:
            ai_response = plan_result["ai_response"]
            final_ai_response = ai_response
            
            # 즉시 응답 전송
            response_data = {
                "success": True,
                "message": "plan_agent 완료",
                "ai_response": ai_response,
                "session_id": request.session_id,
                "node": "plan_agent",
                "data": {
                    "user_message": {
                        "content": request.message,
                        "user_id": request.user_id
                    },
                    "ai_message": {
                        "content": ai_response,
                        "metadata": plan_result.get("recommendations", [])
                    }
                }
            }
            async for chunk in yield_sse_event("plan_response", "ai_response", response_data):
                yield chunk
        else:
            # Plan 노드에서 응답이 없는 경우에도 상태 전송
            plan_complete_data = {
                'status': 'completed', 
                'message': 'plan_agent 완료 (응답 없음)', 
                'node': 'plan_agent'
            }
            async for chunk in yield_sse_event("plan_complete", "node_status", plan_complete_data):
                yield chunk
        
        # 3. WorkLife 노드 처리 (실시간)
        worklife_start_data = {
            'status': 'processing', 
            'message': 'worklife_balance_agent 처리 중...', 
            'node': 'worklife_balance_agent'
        }
        async for chunk in yield_sse_event("worklife_start", "node_status", worklife_start_data):
            yield chunk
        
        worklife_result = await worklife_node(current_state)
        current_state.update(worklife_result)
        
        if "ai_response" in worklife_result and worklife_result["ai_response"]:
            ai_response = worklife_result["ai_response"]
            # WorkLife 응답을 누적
            if final_ai_response:
                final_ai_response += "\n\n" + ai_response
            else:
                final_ai_response = ai_response
            
            # 즉시 응답 전송
            response_data = {
                "success": True,
                "message": "worklife_balance_agent 완료",
                "ai_response": ai_response,
                "session_id": request.session_id,
                "node": "worklife_balance_agent",
                "data": {
                    "user_message": {
                        "content": request.message,
                        "user_id": request.user_id
                    },
                    "ai_message": {
                        "content": ai_response,
                        "metadata": worklife_result.get("recommendations", [])
                    }
                }
            }
            async for chunk in yield_sse_event("worklife_response", "ai_response", response_data):
                yield chunk
        else:
            # WorkLife 노드에서 응답이 없는 경우에도 상태 전송
            worklife_complete_data = {
                'status': 'completed', 
                'message': 'worklife_balance_agent 완료 (응답 없음)', 
                'node': 'worklife_balance_agent'
            }
            async for chunk in yield_sse_event("worklife_complete", "node_status", worklife_complete_data):
                yield chunk
        
        # 4. Communication 노드 처리 (실시간)
        communication_start_data = {
            'status': 'processing', 
            'message': 'communication_agent 처리 중...', 
            'node': 'communication_agent'
        }
        async for chunk in yield_sse_event("communication_start", "node_status", communication_start_data):
            yield chunk
        
        # Communication 노드 처리
        communication_result = await communication_node(current_state)
        current_state.update(communication_result)
        
        if "ai_response" in communication_result and communication_result["ai_response"]:
            ai_response = communication_result["ai_response"]
            # Communication 응답을 누적
            if final_ai_response:
                final_ai_response += "\n\n" + ai_response
            else:
                final_ai_response = ai_response
            
            # 즉시 응답 전송
            response_data = {
                "success": True,
                "message": "communication_agent 완료",
                "ai_response": ai_response,
                "session_id": request.session_id,
                "node": "communication_agent",
                "data": {
                    "user_message": {
                        "content": request.message,
                        "user_id": request.user_id
                    },
                    "ai_message": {
                        "content": ai_response,
                        "metadata": communication_result.get("recommendations", [])
                    }
                }
            }
            async for chunk in yield_sse_event("communication_response", "ai_response", response_data):
                yield chunk
        else:
            # Communication 노드에서 응답이 없는 경우에도 상태 전송
            communication_complete_data = {
                'status': 'completed', 
                'message': 'communication_agent 완료 (응답 없음)', 
                'node': 'communication_agent'
            }
            async for chunk in yield_sse_event("communication_complete", "node_status", communication_complete_data):
                yield chunk
        
        # 최종 완료 응답
        final_response_data = {
            "success": True,
            "message": "요청이 성공적으로 처리되었습니다.",
            "ai_response": final_ai_response,
            "session_id": request.session_id,
            "data": {
                "user_message": {
                    "content": request.message,
                    "user_id": request.user_id
                },
                "ai_message": {
                    "content": final_ai_response,
                    "metadata": []
                }
            }
        }
        async for chunk in yield_sse_event("final_response", "complete", final_response_data):
            yield chunk
        
        # 스트림 종료 신호
        async for chunk in yield_sse_event("stream_end", "end", {"message": "[DONE]"}):
            yield chunk
        
    except Exception as e:
        logger.error(f"채팅 처리 실패: {e}")
        error_response = {
            "success": False,
            "message": "서버 오류가 발생했습니다.",
            "ai_response": "",
            "session_id": request.session_id,
            "error": str(e),
            "data": {
                "user_message": {
                    "content": request.message,
                    "user_id": request.user_id
                }
            }
        }
        async for chunk in yield_sse_event("error_response", "error", error_response):
            yield chunk
        
        # 에러 시에도 스트림 종료 신호
        async for chunk in yield_sse_event("stream_end_error", "end", {"message": "[DONE]"}):
            yield chunk

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket을 통한 실시간 채팅"""
    await websocket.accept()
    
    try:
        while True:
            # 클라이언트로부터 메시지 수신
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message = message_data.get("message", "")
            user_id = message_data.get("user_id", 1)
            session_id = message_data.get("session_id", None)
            
            # 실시간 스트림 처리
            async for chunk in generate_websocket_stream(message, user_id, session_id):
                await websocket.send_text(chunk)
                
    except WebSocketDisconnect:
        logger.info("WebSocket 연결이 종료되었습니다.")

async def generate_websocket_stream(message: str, user_id: int, session_id: str):
    """WebSocket용 실시간 스트림 생성"""
    try:
        if plandy_ai is None:
            yield json.dumps({"type": "error", "message": "Plandy AI 시스템이 초기화되지 않았습니다."})
            return
        
        # 초기 상태 전송
        yield json.dumps({"type": "status", "message": "AI가 응답을 생성하고 있습니다..."})
        
        # Plandy AI 시스템으로 실시간 스트림 처리
        from agents.nodes.supervisor_node import supervisor_node
        from agents.nodes.plan_node import plan_node
        from agents.nodes.worklife_node import worklife_node
        from agents.nodes.communication_node import communication_node
        
        # 사용자 입력 강화
        enhanced_input = f"""
        [시스템 지시사항]
        - 사용자 언어: 한국어
        - 사용자 시간대: Asia/Seoul
        - 사용자가 쓰는 언어로 응답해야 합니다
        - 해당 지역의 시간을 조회해야 합니다
        
        [사용자 입력]
        {message}
        """
        
        # 초기 상태 생성
        initial_state = plandy_ai.create_initial_state(enhanced_input, user_id)
        
        # 실시간 스트림 처리
        final_ai_response = ""
        current_state = initial_state
        
        # 1. Supervisor 노드 처리
        yield json.dumps({"type": "node_status", "node": "supervisor", "status": "processing", "message": "supervisor 처리 중..."})
        
        supervisor_result = supervisor_node(current_state)
        current_state.update(supervisor_result)
        
        yield json.dumps({"type": "node_status", "node": "supervisor", "status": "completed", "message": "supervisor 완료"})
        
        # 2. Plan 노드 처리
        yield json.dumps({"type": "node_status", "node": "plan_agent", "status": "processing", "message": "plan_agent 처리 중..."})
        
        plan_result = await plan_node(current_state)
        current_state.update(plan_result)
        
        if "ai_response" in plan_result and plan_result["ai_response"]:
            ai_response = plan_result["ai_response"]
            final_ai_response = ai_response
            yield json.dumps({"type": "ai_response", "node": "plan_agent", "response": ai_response})
        else:
            yield json.dumps({"type": "node_status", "node": "plan_agent", "status": "completed", "message": "plan_agent 완료 (응답 없음)"})
        
        # 3. WorkLife 노드 처리
        yield json.dumps({"type": "node_status", "node": "worklife_balance_agent", "status": "processing", "message": "worklife_balance_agent 처리 중..."})
        
        worklife_result = await worklife_node(current_state)
        current_state.update(worklife_result)
        
        if "ai_response" in worklife_result and worklife_result["ai_response"]:
            ai_response = worklife_result["ai_response"]
            if final_ai_response:
                final_ai_response += "\n\n" + ai_response
            else:
                final_ai_response = ai_response
            yield json.dumps({"type": "ai_response", "node": "worklife_balance_agent", "response": ai_response})
        else:
            yield json.dumps({"type": "node_status", "node": "worklife_balance_agent", "status": "completed", "message": "worklife_balance_agent 완료 (응답 없음)"})
        
        # 4. Communication 노드 처리
        yield json.dumps({"type": "node_status", "node": "communication_agent", "status": "processing", "message": "communication_agent 처리 중..."})
        
        communication_result = await communication_node(current_state)
        current_state.update(communication_result)
        
        if "ai_response" in communication_result and communication_result["ai_response"]:
            ai_response = communication_result["ai_response"]
            if final_ai_response:
                final_ai_response += "\n\n" + ai_response
            else:
                final_ai_response = ai_response
            yield json.dumps({"type": "ai_response", "node": "communication_agent", "response": ai_response})
        else:
            yield json.dumps({"type": "node_status", "node": "communication_agent", "status": "completed", "message": "communication_agent 완료 (응답 없음)"})
        
        # 최종 완료 응답
        yield json.dumps({"type": "complete", "final_response": final_ai_response, "session_id": session_id})
        
    except Exception as e:
        logger.error(f"WebSocket 채팅 처리 실패: {e}")
        yield json.dumps({"type": "error", "message": f"서버 오류: {str(e)}"})

@app.post("/chat")
async def chat(request: ChatRequest):
    """사용자 메시지 처리 (스트림 응답) - 기존 호환성 유지"""
    from fastapi.responses import StreamingResponse
    import asyncio
    
    return StreamingResponse(
        generate_stream_response(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache", 
            "Expires": "0",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "X-Accel-Buffering": "no",
            "Transfer-Encoding": "chunked"
        }
    )

@app.get("/schedules/{user_id}")
async def get_schedules(user_id: int):
    """사용자 일정 조회"""
    try:
        if plandy_ai is None:
            raise HTTPException(status_code=500, detail="Plandy AI 시스템이 초기화되지 않았습니다.")
        
        from tools import ScheduleTools
        schedule_tools = ScheduleTools()
        
        result = await schedule_tools.execute({
            "action": "list_schedules",
            "user_id": user_id
        })
        
        if result.get("status") == "success":
            return {
                "success": True,
                "schedules": result.get("schedules", []),
                "count": result.get("count", 0)
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "일정 조회 실패"))
            
    except Exception as e:
        logger.error(f"일정 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/schedules")
async def create_schedule(schedule_data: Dict[str, Any]):
    """새 일정 생성"""
    try:
        if plandy_ai is None:
            raise HTTPException(status_code=500, detail="Plandy AI 시스템이 초기화되지 않았습니다.")
        
        from tools import ScheduleTools
        schedule_tools = ScheduleTools()
        
        result = await schedule_tools.execute({
            "action": "save_schedule",
            **schedule_data
        })
        
        if result.get("status") == "success":
            return {
                "success": True,
                "schedule_id": result.get("schedule_id"),
                "message": result.get("message", "일정이 성공적으로 저장되었습니다.")
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "일정 저장 실패"))
            
    except Exception as e:
        logger.error(f"일정 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/time")
async def get_current_time(timezone: str = "Asia/Seoul"):
    """현재 시간 조회"""
    try:
        if plandy_ai is None:
            raise HTTPException(status_code=500, detail="Plandy AI 시스템이 초기화되지 않았습니다.")
        
        from tools import TimeTools
        time_tools = TimeTools()
        
        result = await time_tools.execute({
            "action": "now",
            "timezone": timezone,
            "format": "readable"
        })
        
        if result.get("status") == "success":
            return {
                "success": True,
                "time": result.get("readable_time"),
                "timezone": timezone
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "시간 조회 실패"))
            
    except Exception as e:
        logger.error(f"시간 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )
