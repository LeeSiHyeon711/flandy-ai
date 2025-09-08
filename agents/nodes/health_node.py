"""
Health Node - 건강 모니터링 노드

LangGraph 기반의 건강 상태 모니터링 노드입니다.
"""

from typing import Dict, Any
import logging
import os
from datetime import datetime
from models import State, Task, HealthData
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate


async def health_node(state: State) -> State:
    """
    건강 상태 모니터링 노드
    
    Args:
        state (State): 현재 상태
        
    Returns:
        State: 업데이트된 상태
    """
    print("\n\n============= HEALTH NODE ==============\n")
    
    logger = logging.getLogger("node.health")
    logger.info("Health node processing started")
    
    try:
        # 현재 작업 확인
        current_task = state.get("current_task")
        if not current_task or current_task.agent != "health_agent":
            logger.warning("Health node called without proper task assignment")
            return state
        
        user_id = state.get("user_id", 1)
        user_request = state.get("user_request", "")
        
        # 건강 데이터 분석
        health_analysis = await analyze_health_data(user_id, user_request, state)
        
        # 건강 데이터 업데이트
        health_data = HealthData(
            health_score=health_analysis["health_score"],
            stress_level=health_analysis["stress_level"],
            sleep_quality=health_analysis["sleep_quality"],
            exercise_frequency=health_analysis["exercise_frequency"],
            habit_patterns=health_analysis["habit_patterns"],
            recommendations=health_analysis["recommendations"]
        )
        
        # 메시지 업데이트
        messages = state.get("messages", [])
        health_message = {
            "role": "assistant",
            "content": f"[Health Agent] 건강 분석 완료: 점수 {health_analysis['health_score']}/100",
            "timestamp": datetime.now().isoformat(),
            "agent": "health_agent"
        }
        messages.append(health_message)
        
        # 작업 완료 처리
        task_history = state.get("task_history", [])
        if task_history:
            task_history[-1].done = True
            task_history[-1].done_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # AI 추천 생성
        ai_recommendation = await generate_health_recommendation(health_analysis, state)
        
        # AI 응답 생성
        ai_response = f"건강 상태 분석이 완료되었습니다!\n\n"
        ai_response += f"🏥 건강 점수: {health_analysis['health_score']}/100\n"
        ai_response += f"😰 스트레스 수준: {health_analysis['stress_level']}/10\n"
        ai_response += f"😴 수면 품질: {health_analysis['sleep_quality']}/10\n"
        ai_response += f"🏃 운동 빈도: {health_analysis['exercise_frequency']}/주\n\n"
        ai_response += ai_recommendation
        
        # 다른 에이전트들에게 정보 전달을 위한 프롬프트 생성
        from services import prompt_service
        plan_prompt = prompt_service.generate_prompt(
            "health_agent", "plan_agent", health_analysis, state
        )
        worklife_prompt = prompt_service.generate_prompt(
            "health_agent", "worklife_balance_agent", health_analysis, state
        )
        
        logger.info("Health node processing completed successfully")
        
        return {
            **state,
            "messages": messages,
            "health_data": health_data,
            "task_history": task_history,
            "ai_recommendation": ai_recommendation,
            "ai_response": ai_response,
            "system_status": "health_analysis_completed",
            "context": {
                **state.get("context", {}),
                "health_to_plan_prompt": plan_prompt,
                "health_to_worklife_prompt": worklife_prompt
            }
        }
        
    except Exception as e:
        logger.error(f"Error in health node: {str(e)}")
        error_messages = state.get("error_messages", [])
        error_messages.append(f"Health node error: {str(e)}")
        
        return {
            **state,
            "error_messages": error_messages,
            "system_status": "error"
        }


async def analyze_health_data(user_id: int, user_request: str, state: State) -> Dict[str, Any]:
    """
    건강 데이터를 분석합니다.
    
    Args:
        user_id (int): 사용자 ID
        user_request (str): 사용자 요청
        state (State): 현재 상태
        
    Returns:
        Dict[str, Any]: 건강 분석 결과
    """
    # 실제 구현에서는 데이터베이스에서 건강 데이터를 조회하고 분석
    # 여기서는 예시 데이터를 반환
    
    analysis = {
        "health_score": 75.5,
        "stress_level": 6.2,
        "sleep_quality": 7.1,
        "exercise_frequency": 6.8,
        "habit_patterns": {
            "coffee_intake": 2.5,  # 하루 평균
            "exercise_days": 4,    # 주간 운동 일수
            "sleep_hours": 7.2,    # 평균 수면 시간
            "work_breaks": 3.1     # 하루 평균 휴식 횟수
        },
        "recommendations": [
            "커피 섭취량을 하루 2잔 이하로 줄이세요",
            "규칙적인 운동을 주 5회 이상 하세요",
            "충분한 수면을 위해 8시간 이상 주무세요",
            "업무 중 1시간마다 5분씩 휴식을 취하세요"
        ]
    }
    
    # 사용자 요청에 따른 맞춤 분석
    if "스트레스" in user_request or "stress" in user_request.lower():
        analysis["stress_level"] = 7.5
        analysis["recommendations"].append("스트레스 관리 기법을 도입하세요")
    
    if "운동" in user_request or "exercise" in user_request.lower():
        analysis["exercise_frequency"] = 5.2
        analysis["recommendations"].append("운동 빈도를 늘려보세요")
    
    return analysis


async def generate_health_recommendation(health_analysis: Dict[str, Any], state: State) -> str:
    """
    건강 분석 결과를 바탕으로 AI 추천을 생성합니다.
    
    Args:
        health_analysis (Dict[str, Any]): 건강 분석 결과
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
        
        # 이전 대화 내용 가져오기
        messages = state.get("messages", [])
        recent_messages = messages[-5:] if len(messages) > 5 else messages
        conversation_context = ""
        for msg in recent_messages:
            if msg.get("role") == "user":
                conversation_context += f"사용자: {msg.get('content', '')}\n"
            elif msg.get("role") == "assistant":
                conversation_context += f"AI: {msg.get('content', '')}\n"
        
        prompt = f"""
        당신은 Plandy AI의 Health Agent입니다.
        
        사용자 요청: {state.get('user_request', '')}
        
        이전 대화 내용:
        {conversation_context}
        
        건강 분석 결과:
        - 건강 점수: {health_analysis['health_score']}/100
        - 스트레스 레벨: {health_analysis['stress_level']}/10
        - 수면 품질: {health_analysis['sleep_quality']}/10
        - 운동 빈도: {health_analysis['exercise_frequency']}/10
        
        습관 패턴: {health_analysis['habit_patterns']}
        기존 권장사항: {health_analysis['recommendations']}
        
        사용자의 요청을 분석하고, 필요하다면 다른 에이전트들에게 도움이 되는 정보를 제공하세요.
        예를 들어:
        - Plan Agent에게: 건강 상태에 따른 일정 조정 권장사항
        - WorkLife Agent에게: 건강 상태에 따른 워라벨 균형 조정 방안
        
        이전 대화를 참고해서 구체적이고 실행 가능한 건강 개선 방안을 제시해주세요.
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
        health_score = health_analysis["health_score"]
        stress_level = health_analysis["stress_level"]
        
        if health_score >= 80:
            recommendation = "전반적인 건강 상태가 양호합니다. 현재 패턴을 유지하세요."
        elif health_score >= 60:
            recommendation = "건강 상태가 보통 수준입니다. 몇 가지 개선사항을 적용해보세요."
        else:
            recommendation = "건강 상태 개선이 필요합니다. 전문가 상담을 권장합니다."
        
        if stress_level > 7:
            recommendation += " 특히 스트레스 관리에 집중하세요."
        
        return f"{recommendation} (API 오류: {str(e)})"
