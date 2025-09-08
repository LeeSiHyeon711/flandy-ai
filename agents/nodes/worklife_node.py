"""
WorkLife Node - 워라벨 균형 노드

LangGraph 기반의 워라벨 균형 관리 노드입니다.
"""

from typing import Dict, Any
import logging
import os
from datetime import datetime
from models import State, Task, WorkLifeBalanceData
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate


async def worklife_node(state: State) -> State:
    """
    워라벨 균형 관리 노드
    
    Args:
        state (State): 현재 상태
        
    Returns:
        State: 업데이트된 상태
    """
    print("\n\n============= WORKLIFE NODE ==============\n")
    
    logger = logging.getLogger("node.worklife")
    logger.info("WorkLife node processing started")
    
    try:
        # 현재 작업 확인
        current_task = state.get("current_task")
        if not current_task or current_task.agent != "worklife_balance_agent":
            logger.warning("WorkLife node called without proper task assignment")
            return state
        
        user_id = state.get("user_id", 1)
        user_request = state.get("user_request", "")
        
        # 워라벨 분석 수행
        worklife_analysis = await analyze_worklife_balance(user_id, user_request, state)
        
        # 워라벨 데이터 업데이트
        worklife_data = WorkLifeBalanceData(
            balance_score=worklife_analysis["balance_score"],
            work_hours=worklife_analysis["work_hours"],
            leisure_hours=worklife_analysis["leisure_hours"],
            stress_indicators=worklife_analysis["stress_indicators"],
            improvement_suggestions=worklife_analysis["improvement_suggestions"]
        )
        
        # 메시지 업데이트
        messages = state.get("messages", [])
        worklife_message = {
            "role": "assistant",
            "content": f"[WorkLife Agent] 워라벨 분석 완료: 균형 점수 {worklife_analysis['balance_score']}/100",
            "timestamp": datetime.now().isoformat(),
            "agent": "worklife_balance_agent"
        }
        messages.append(worklife_message)
        
        # 작업 완료 처리
        task_history = state.get("task_history", [])
        if task_history:
            task_history[-1].done = True
            task_history[-1].done_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # AI 추천 생성
        ai_recommendation = await generate_worklife_recommendation(worklife_analysis, state)
        
        # AI 응답 생성
        ai_response = f"워라벨 균형 분석이 완료되었습니다!\n\n"
        ai_response += f"⚖️ 균형 점수: {worklife_analysis.get('balance_score', 0)}/100\n"
        ai_response += f"💼 근무 시간: {worklife_analysis.get('work_hours', 0):.1f}시간/일\n"
        ai_response += f"🏠 개인 시간: {worklife_analysis.get('leisure_hours', 0):.1f}시간/일\n"
        ai_response += f"😴 휴식 시간: {worklife_analysis.get('rest_hours', 0):.1f}시간/일\n\n"
        ai_response += ai_recommendation
        
        logger.info("WorkLife node processing completed successfully")
        
        return {
            **state,
            "messages": messages,
            "worklife_data": worklife_data,
            "task_history": task_history,
            "ai_recommendation": ai_recommendation,
            "ai_response": ai_response,
            "system_status": "worklife_analysis_completed"
        }
        
    except Exception as e:
        logger.error(f"Error in worklife node: {str(e)}")
        error_messages = state.get("error_messages", [])
        error_messages.append(f"WorkLife node error: {str(e)}")
        
        return {
            **state,
            "error_messages": error_messages,
            "system_status": "error"
        }


async def analyze_worklife_balance(user_id: int, user_request: str, state: State) -> Dict[str, Any]:
    """
    워라벨 균형을 분석합니다.
    
    Args:
        user_id (int): 사용자 ID
        user_request (str): 사용자 요청
        state (State): 현재 상태
        
    Returns:
        Dict[str, Any]: 워라벨 분석 결과
    """
    # 실제 사용자의 일정 데이터를 기반으로 분석
    from tools import ScheduleTools
    from datetime import datetime, timedelta
    
    schedule_tools = ScheduleTools()
    
    # 사용자의 일정 데이터 가져오기
    schedule_result = await schedule_tools.execute({
        "action": "list_schedules",
        "user_id": user_id
    })
    
    if schedule_result.get("status") != "success":
        # 일정 데이터를 가져올 수 없는 경우 기본값
        return {
            "balance_score": 50.0,
            "work_hours": 0,
            "leisure_hours": 0,
            "stress_indicators": ["일정 데이터 부족"],
            "improvement_suggestions": ["일정을 등록하여 분석을 시작하세요"]
        }
    
    schedules = schedule_result.get("schedules", [])
    
    # 오늘 일정만 필터링
    today = datetime.now().date()
    today_schedules = []
    for schedule in schedules:
        start_time = schedule.get("start_time")
        if isinstance(start_time, datetime):
            if start_time.date() == today:
                today_schedules.append(schedule)
    
    # 업무/개인 시간 분류
    work_hours = 0
    personal_hours = 0
    work_schedules = []
    personal_schedules = []
    
    for schedule in today_schedules:
        title = schedule.get("title", "").lower()
        description = schedule.get("description", "").lower()
        
        # 업무 관련 키워드
        work_keywords = ["회의", "미팅", "프로젝트", "업무", "작업", "기획", "발표", "보고서"]
        # 개인 시간 관련 키워드
        personal_keywords = ["운동", "독서", "휴식", "취미", "가족", "친구", "여행", "영화"]
        
        is_work = any(keyword in title or keyword in description for keyword in work_keywords)
        is_personal = any(keyword in title or keyword in description for keyword in personal_keywords)
        
        # 실제 소요 시간 계산
        duration = 1.0  # 기본값
        
        # meta 데이터에서 실제 소요 시간 가져오기
        meta = schedule.get("meta", "{}")
        if isinstance(meta, str):
            try:
                import json
                meta_data = json.loads(meta)
                if "estimated_duration" in meta_data:
                    duration = meta_data["estimated_duration"] / 60.0  # 분을 시간으로 변환
            except:
                pass
        
        # deadline과 start_time으로 계산 (오늘 일정만)
        start_time = schedule.get("start_time")
        deadline = schedule.get("deadline")
        if start_time and deadline and isinstance(start_time, datetime) and isinstance(deadline, datetime):
            # 오늘 일정인 경우에만 시간 차이 계산
            if start_time.date() == today and deadline.date() == today:
                time_diff = deadline - start_time
                duration = time_diff.total_seconds() / 3600.0  # 초를 시간으로 변환
            else:
                # 오늘이 아닌 일정은 기본 1시간으로 설정
                duration = 1.0
        
        if is_work:
            work_schedules.append(schedule)
            work_hours += duration
        elif is_personal:
            personal_schedules.append(schedule)
            personal_hours += duration
        else:
            # 키워드가 없으면 제목으로 판단
            if any(keyword in title for keyword in ["회의", "미팅", "프로젝트"]):
                work_schedules.append(schedule)
                work_hours += duration
            else:
                personal_schedules.append(schedule)
                personal_hours += duration
    
    # 워라벨 점수 계산
    total_hours = work_hours + personal_hours
    if total_hours == 0:
        balance_score = 50.0  # 일정이 없으면 중간 점수
    else:
        # 업무:개인 = 8:8 이상이면 좋은 점수
        ideal_ratio = 8.0 / 8.0  # 1:1
        actual_ratio = work_hours / max(personal_hours, 0.1)  # 0으로 나누기 방지
        
        if actual_ratio <= 1.2:  # 1.2:1 이하면 좋음
            balance_score = 85.0
        elif actual_ratio <= 1.5:  # 1.5:1 이하면 보통
            balance_score = 70.0
        else:  # 그 이상이면 나쁨
            balance_score = 50.0
    
    # 스트레스 지표 분석
    stress_indicators = []
    if work_hours > 10:
        stress_indicators.append("과도한 업무 시간")
    if personal_hours < 2:
        stress_indicators.append("개인 시간 부족")
    if len(work_schedules) > 5:
        stress_indicators.append("업무 일정 과다")
    if not personal_schedules:
        stress_indicators.append("개인 활동 부재")
    
    # 개선 제안
    improvement_suggestions = []
    if work_hours > 8:
        improvement_suggestions.append("업무 시간을 8시간 이하로 조정하세요")
    if personal_hours < 4:
        improvement_suggestions.append("개인 시간을 더 확보하세요")
    if not any("운동" in s.get("title", "") for s in personal_schedules):
        improvement_suggestions.append("운동 시간을 추가하세요")
    if not any("휴식" in s.get("title", "") for s in personal_schedules):
        improvement_suggestions.append("휴식 시간을 확보하세요")
    
    analysis = {
        "balance_score": balance_score,
        "work_hours": work_hours,
        "leisure_hours": personal_hours,
        "work_schedules": work_schedules,
        "personal_schedules": personal_schedules,
        "stress_indicators": stress_indicators,
        "improvement_suggestions": improvement_suggestions
    }
    
    # 건강 데이터가 있는 경우 고려
    health_data = state.get("health_data")
    if health_data:
        if hasattr(health_data, 'stress_level') and health_data.stress_level > 7:
            analysis["balance_score"] -= 10
            analysis["stress_indicators"].append("건강 데이터 기반 스트레스 감지")
    
    return analysis


async def generate_worklife_recommendation(worklife_analysis: Dict[str, Any], state: State) -> str:
    """
    워라벨 분석 결과를 바탕으로 AI 추천을 생성합니다.
    
    Args:
        worklife_analysis (Dict[str, Any]): 워라벨 분석 결과
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
        워라벨 분석 결과를 바탕으로 개인화된 워라벨 균형 개선 방안을 생성해주세요.
        
        균형 점수: {worklife_analysis['balance_score']}/100
        업무 시간: {worklife_analysis['work_hours']}시간
        여가 시간: {worklife_analysis['leisure_hours']}시간
        
        스트레스 지표:
        {worklife_analysis['stress_indicators']}
        
        개선 제안:
        {worklife_analysis['improvement_suggestions']}
        
        이 정보를 바탕으로 구체적이고 실행 가능한 워라벨 균형 개선 방안을 제시해주세요.
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
        balance_score = worklife_analysis["balance_score"]
        work_hours = worklife_analysis["work_hours"]
        stress_indicators = worklife_analysis["stress_indicators"]
        
        if balance_score >= 80:
            recommendation = "워라벨 균형이 매우 좋습니다. 현재 패턴을 유지하세요."
        elif balance_score >= 60:
            recommendation = "워라벨 균형이 양호하지만 개선 여지가 있습니다."
        else:
            recommendation = "워라벨 균형 개선이 필요합니다. 업무와 개인 시간의 균형을 재조정하세요."
        
        if work_hours > 9:
            recommendation += " 업무 시간이 과도합니다."
        
        if len(stress_indicators) > 2:
            recommendation += " 스트레스 관리에 집중하세요."
        
        return f"{recommendation} (API 오류: {str(e)})"
