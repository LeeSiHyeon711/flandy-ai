from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
import uvicorn
from main import PlandyAISystem
import logging

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

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """사용자 메시지 처리"""
    try:
        if plandy_ai is None:
            raise HTTPException(status_code=500, detail="Plandy AI 시스템이 초기화되지 않았습니다.")
        
        logger.info(f"채팅 요청 수신: {request.message}")
        
        # Plandy AI 시스템으로 요청 처리
        result = await plandy_ai.process_request(
            user_input=request.message,
            user_id=request.user_id
        )
        
        if result.get("success", False):
            return ChatResponse(
                success=True,
                message="요청이 성공적으로 처리되었습니다.",
                ai_response=result.get("ai_response", ""),
                session_id=request.session_id
            )
        else:
            return ChatResponse(
                success=False,
                message="요청 처리 중 오류가 발생했습니다.",
                ai_response="",
                session_id=request.session_id,
                error=result.get("error", "알 수 없는 오류")
            )
            
    except Exception as e:
        logger.error(f"채팅 처리 실패: {e}")
        return ChatResponse(
            success=False,
            message="서버 오류가 발생했습니다.",
            ai_response="",
            session_id=request.session_id,
            error=str(e)
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
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
