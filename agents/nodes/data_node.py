"""
Data Node - 데이터 분석 노드

LangGraph 기반의 데이터 수집 및 분석 노드입니다.
"""

from typing import Dict, Any
import logging
import os
from datetime import datetime
from models import State, Task, UserFeedback
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate


async def data_node(state: State) -> State:
    """
    데이터 분석 노드
    
    Args:
        state (State): 현재 상태
        
    Returns:
        State: 업데이트된 상태
    """
    print("\n\n============= DATA NODE ==============\n")
    
    logger = logging.getLogger("node.data")
    logger.info("Data node processing started")
    
    try:
        # 현재 작업 확인
        current_task = state.get("current_task")
        if not current_task or current_task.agent != "data_agent":
            logger.warning("Data node called without proper task assignment")
            return state
        
        user_id = state.get("user_id", 1)
        user_request = state.get("user_request", "")
        
        # 데이터 분석 수행
        data_analysis = perform_data_analysis(user_id, user_request, state)
        
        # 피드백 데이터 업데이트
        feedback_data = state.get("feedback_data", [])
        if data_analysis.get("new_feedback"):
            new_feedback = UserFeedback(
                feedback_id=data_analysis["new_feedback"]["feedback_id"],
                user_id=user_id,
                text=data_analysis["new_feedback"]["text"],
                rating=data_analysis["new_feedback"]["rating"],
                category=data_analysis["new_feedback"]["category"],
                sentiment=data_analysis["new_feedback"]["sentiment"]
            )
            feedback_data.append(new_feedback)
        
        # 메시지 업데이트
        messages = state.get("messages", [])
        data_message = {
            "role": "assistant",
            "content": f"[Data Agent] 데이터 분석 완료: {data_analysis['insights_count']}개 인사이트 생성",
            "timestamp": datetime.now().isoformat(),
            "agent": "data_agent"
        }
        messages.append(data_message)
        
        # 작업 완료 처리
        task_history = state.get("task_history", [])
        if task_history:
            task_history[-1].done = True
            task_history[-1].done_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # AI 추천 생성
        ai_recommendation = await generate_data_recommendation(data_analysis, state)
        
        # AI 응답 생성
        ai_response = f"데이터 분석이 완료되었습니다!\n\n"
        ai_response += f"📊 분석 결과: {data_analysis.get('analysis_type', '일반 분석')}\n"
        ai_response += f"📈 생산성 점수: {data_analysis.get('productivity_score', 0)}/100\n"
        ai_response += f"🎯 개선 영역: {len(data_analysis.get('improvement_areas', []))}개\n"
        ai_response += f"💡 인사이트: {len(data_analysis.get('insights', []))}개\n\n"
        ai_response += ai_recommendation
        
        logger.info("Data node processing completed successfully")
        
        return {
            **state,
            "messages": messages,
            "feedback_data": feedback_data,
            "task_history": task_history,
            "ai_recommendation": ai_recommendation,
            "ai_response": ai_response,
            "system_status": "data_analysis_completed"
        }
        
    except Exception as e:
        logger.error(f"Error in data node: {str(e)}")
        error_messages = state.get("error_messages", [])
        error_messages.append(f"Data node error: {str(e)}")
        
        return {
            **state,
            "error_messages": error_messages,
            "system_status": "error"
        }


def perform_data_analysis(user_id: int, user_request: str, state: State) -> Dict[str, Any]:
    """
    데이터 분석을 수행합니다.
    
    Args:
        user_id (int): 사용자 ID
        user_request (str): 사용자 요청
        state (State): 현재 상태
        
    Returns:
        Dict[str, Any]: 데이터 분석 결과
    """
    # 실제 구현에서는 사용자 데이터를 분석하고 패턴을 찾음
    # 여기서는 예시 분석 결과를 반환
    
    analysis = {
        "user_behavior_patterns": {
            "most_active_hours": [9, 10, 14, 15],
            "preferred_work_style": "focused_blocks",
            "break_patterns": "regular_breaks",
            "productivity_peaks": ["morning", "afternoon"]
        },
        "productivity_metrics": {
            "average_task_completion_rate": 0.85,
            "time_estimation_accuracy": 0.78,
            "focus_time_percentage": 0.72,
            "distraction_frequency": 0.15
        },
        "insights": [
            "오전 9-11시에 가장 높은 생산성을 보입니다",
            "점심 시간 후 1-2시간은 에너지가 낮아집니다",
            "깊은 작업 세션을 자주 유지하고 있습니다"
        ],
        "trends": {
            "productivity_trend": "improving",
            "workload_trend": "stable",
            "satisfaction_trend": "improving"
        },
        "insights_count": 3
    }
    
    # 사용자 요청에 따른 맞춤 분석
    if "패턴" in user_request or "pattern" in user_request.lower():
        analysis["insights"].append("규칙적인 작업 패턴을 유지하고 있습니다")
        analysis["insights_count"] += 1
    
    if "성과" in user_request or "performance" in user_request.lower():
        analysis["insights"].append("전반적인 성과가 개선되고 있습니다")
        analysis["insights_count"] += 1
    
    # 새로운 피드백이 있는 경우 처리
    if "피드백" in user_request or "feedback" in user_request.lower():
        analysis["new_feedback"] = {
            "feedback_id": f"feedback_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "text": "사용자 피드백이 수집되었습니다",
            "rating": 4.2,
            "category": "general",
            "sentiment": "positive"
        }
    
    return analysis


async def generate_data_recommendation(data_analysis: Dict[str, Any], state: State) -> str:
    """
    데이터 분석 결과를 바탕으로 AI 추천을 생성합니다.
    
    Args:
        data_analysis (Dict[str, Any]): 데이터 분석 결과
        state (State): 현재 상태
        
    Returns:
        str: AI 추천 메시지
    """
    try:
        from langchain_openai import ChatOpenAI
        import os
        
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.7,
            streaming=True  # 스트림 출력 활성화
        )
        
        prompt = f"""
        데이터 분석 결과를 바탕으로 개인화된 생산성 개선 방안을 생성해주세요.
        
        사용자 행동 패턴:
        {data_analysis['user_behavior_patterns']}
        
        생산성 지표:
        {data_analysis['productivity_metrics']}
        
        인사이트:
        {data_analysis['insights']}
        
        트렌드:
        {data_analysis['trends']}
        
        이 정보를 바탕으로 구체적이고 실행 가능한 생산성 개선 방안을 제시해주세요.
        """
        
        # 스트림 출력으로 응답 생성
        full_response = ""
        print("AI 응답: ", end="", flush=True)
        
        import time
        async for chunk in llm.astream(prompt):
            if hasattr(chunk, 'content') and chunk.content:
                print(chunk.content, end="", flush=True)
                full_response += chunk.content
                time.sleep(0.02)  # 타이핑 효과
        
        print()  # 줄바꿈
        return full_response
    except Exception as e:
        # 폴백: 기본 추천
        productivity_trend = data_analysis["trends"]["productivity_trend"]
        insights_count = data_analysis["insights_count"]
        
        if productivity_trend == "improving":
            recommendation = "생산성이 개선되고 있습니다. 현재 패턴을 유지하세요."
        elif productivity_trend == "stable":
            recommendation = "생산성이 안정적입니다. 새로운 도전을 시도해보세요."
        else:
            recommendation = "생산성 개선이 필요합니다. 작업 방식을 재검토해보세요."
        
        recommendation += f" {insights_count}개의 인사이트를 발견했습니다."
        
        return f"{recommendation} (API 오류: {str(e)})"
