"""
Plan Node - 일정 계획 노드

LangGraph 기반의 일정 계획 수립 노드입니다.
"""

from typing import Dict, Any
import logging
import re
import os
from datetime import datetime, timedelta
from models import State, Task, ScheduleData
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger("node.plan")


async def plan_node(state: State) -> State:
    """
    일정 계획 수립 노드
    
    Args:
        state (State): 현재 상태
        
    Returns:
        State: 업데이트된 상태
    """
    print("\n\n============= PLAN NODE ==============\n")
    
    logger.info("Plan node processing started")
    
    try:
        # 현재 작업 확인
        current_task = state.get("current_task")
        if not current_task or current_task.agent != "plan_agent":
            logger.warning("Plan node called without proper task assignment")
            return state
        
        user_id = state.get("user_id", 1)
        user_request = state.get("user_request", "")
        
        # 일정 계획 수립
        schedule_plan = await create_schedule_plan(user_id, user_request, state)
        
        # 일정 데이터 업데이트
        schedule_data = ScheduleData(
            schedule_id=schedule_plan["schedule_id"],
            tasks=schedule_plan["tasks"],
            time_blocks=schedule_plan["time_blocks"],
            constraints=schedule_plan["constraints"],
            efficiency_score=schedule_plan["efficiency_score"],
            conflicts=schedule_plan["conflicts"]
        )
        
        # 메시지 업데이트
        messages = state.get("messages", [])
        plan_message = {
            "role": "assistant",
            "content": f"[Plan Agent] 일정 계획 완료: {len(schedule_plan['time_blocks'])}개 블록 생성",
            "timestamp": datetime.now().isoformat(),
            "agent": "plan_agent"
        }
        messages.append(plan_message)
        
        # 작업 완료 처리
        task_history = state.get("task_history", [])
        if task_history:
            task_history[-1].done = True
            task_history[-1].done_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # AI 추천 생성
        ai_recommendation = await generate_plan_recommendation(schedule_plan, state)
        
        # AI 응답을 state에 추가
        ai_response = f"일정이 성공적으로 생성되었습니다!\n\n"
        ai_response += f"📅 일정: {schedule_plan['tasks'][0]['title']}\n"
        ai_response += f"⏰ 시간: {schedule_plan['tasks'][0]['deadline']}\n"
        ai_response += f"⏱️ 소요시간: {schedule_plan['tasks'][0]['duration']}분\n"
        ai_response += f"🎯 우선순위: {schedule_plan['tasks'][0]['priority']}/10\n\n"
        ai_response += ai_recommendation
        
        logger.info("Plan node processing completed successfully")
        
        return {
            **state,
            "messages": messages,
            "schedule_data": schedule_data,
            "task_history": task_history,
            "ai_recommendation": ai_recommendation,
            "ai_response": ai_response,
            "system_status": "schedule_plan_completed"
        }
        
    except Exception as e:
        logger.error(f"Error in plan node: {str(e)}")
        error_messages = state.get("error_messages", [])
        error_messages.append(f"Plan node error: {str(e)}")
        
        return {
            **state,
            "error_messages": error_messages,
            "system_status": "error"
        }


async def create_schedule_plan(user_id: int, user_request: str, state: State) -> Dict[str, Any]:
    """
    일정 계획을 생성합니다.
    
    Args:
        user_id (int): 사용자 ID
        user_request (str): 사용자 요청
        state (State): 현재 상태
        
    Returns:
        Dict[str, Any]: 일정 계획 결과
    """
    # ScheduleTools를 사용하여 실제 일정 생성
    from tools import ScheduleTools
    schedule_tools = ScheduleTools()
    
    schedule_id = f"schedule_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # AI가 사용자 요청을 분석하여 적절한 title과 description 생성
    from langchain_openai import ChatOpenAI
    import os
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.3
    )
    
    # 시스템 지시사항을 제거하고 순수한 사용자 요청만 추출
    pure_user_request = user_request
    if "[시스템 지시사항]" in user_request and "[사용자 입력]" in user_request:
        # [사용자 입력] 이후의 내용만 추출
        user_input_start = user_request.find("[사용자 입력]")
        if user_input_start != -1:
            pure_user_request = user_request[user_input_start + len("[사용자 입력]"):].strip()
    
    # AI가 일정 정보를 분석하여 적절한 title과 description 생성
    analysis_prompt = f"""
    사용자 요청: "{pure_user_request}"
    
    이 요청을 분석하여 일정을 생성할 때:
    1. title: 간단하고 명확한 제목 (예: "운동", "미팅", "프로젝트 작업")
    2. description: 사용자의 요청 내용을 자연스럽게 정리한 설명
    
    JSON 형식으로 응답해주세요:
    {{
        "title": "간단한 제목",
        "description": "사용자 요청을 자연스럽게 정리한 설명"
    }}
    """
    
    analysis_result = llm.invoke(analysis_prompt)
    analysis_text = analysis_result.content.strip()
    
    # JSON 파싱 시도
    try:
        import json
        # JSON 부분만 추출
        if "{" in analysis_text and "}" in analysis_text:
            json_start = analysis_text.find("{")
            json_end = analysis_text.rfind("}") + 1
            json_text = analysis_text[json_start:json_end]
            analysis_data = json.loads(json_text)
            title = analysis_data.get("title", "일정")
            description = analysis_data.get("description", user_request)
        else:
            title = "일정"
            description = user_request
    except:
        title = "일정"
        description = user_request
    
    # 사용자 요청을 바탕으로 일정 생성 (allocate 액션 사용)
    schedule_result = await schedule_tools.execute({
        "action": "allocate",
        "tasks": [
            {
                "id": "user_request_task",
                "title": title,
                "duration": 60,
                "priority": 8,
                "deadline": datetime.now().replace(hour=17, minute=0, second=0, microsecond=0).isoformat()
            }
        ],
        "constraints": {
            "working_hours": {"start": "09:00", "end": "18:00"},
            "break_times": ["12:00-13:00", "15:00-15:15"],
            "max_continuous_work": 120,
            "preferred_work_style": "focused_blocks"
        }
    })
    
    # 사용자 요청을 바탕으로 실제 일정 생성
    tasks = []
    
    # AI가 사용자 요청을 분석하여 시간과 소요시간 계산
    time_analysis_prompt = f"""
    사용자 요청: "{pure_user_request}"
    
    이 요청을 분석하여 일정 시간을 계산해주세요:
    1. 언제 시작할지 (예: "내일 같은 시간" = 내일 오후 7시, "오늘 3시" = 오늘 오후 3시)
    2. 얼마나 걸릴지 (예: "1시간", "30분", 기본값 60분)
    
    현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    
    JSON 형식으로 응답해주세요:
    {{
        "start_time": "YYYY-MM-DD HH:MM:SS",
        "duration_minutes": 60
    }}
    """
    
    time_analysis_result = llm.invoke(time_analysis_prompt)
    time_analysis_text = time_analysis_result.content.strip()
    
    # JSON 파싱 시도
    try:
        import json
        if "{" in time_analysis_text and "}" in time_analysis_text:
            json_start = time_analysis_text.find("{")
            json_end = time_analysis_text.rfind("}") + 1
            json_text = time_analysis_text[json_start:json_end]
            time_data = json.loads(json_text)
            parsed_time = datetime.fromisoformat(time_data.get("start_time", datetime.now().isoformat()))
            parsed_duration = time_data.get("duration_minutes", 60)
        else:
            parsed_time = datetime.now() + timedelta(hours=1)
            parsed_duration = 60
    except:
        parsed_time = datetime.now() + timedelta(hours=1)
        parsed_duration = 60
    
    print(f"사용자 요청: {pure_user_request}")
    print(f"AI가 계산한 시간: {parsed_time}")
    print(f"AI가 계산한 소요시간: {parsed_duration}분")
    
    # AI가 생성한 title과 description 사용
    tasks.append({
        "id": f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "title": title,
        "duration": parsed_duration,
        "priority": 6,
        "deadline": parsed_time.isoformat()
    })
    
    # 일정을 데이터베이스에 저장
    for task in tasks:
        save_result = await schedule_tools.execute({
            "action": "save_schedule",
            "user_id": user_id,
            "title": task["title"],
            "description": description,
            "start_time": parsed_time,
            "end_time": parsed_time + timedelta(minutes=task["duration"]),
            "duration": task["duration"],
            "priority": task["priority"]
        })
        logger.info(f"일정 저장 결과: {save_result}")
        
        # 사용자에게 일정 등록 완료 알림
        if save_result.get("status") == "success":
            print(f"\n✅ 일정이 성공적으로 등록되었습니다!")
            print(f"📅 제목: {task['title']}")
            print(f"⏰ 시간: {parsed_time.strftime('%Y-%m-%d %H:%M')}")
            print(f"⏱️ 소요시간: {task['duration']}분")
            print()
        else:
            print(f"\n❌ 일정 등록에 실패했습니다: {save_result.get('message', '알 수 없는 오류')}")
            print()
    
    # 일정 최적화 (optimize 액션 사용)
    optimization_result = await schedule_tools.execute({
        "action": "optimize",
        "schedule_id": schedule_id,
        "optimization_type": "efficiency"
    })
    
    # 제약조건
    constraints = {
        "working_hours": {"start": "09:00", "end": "18:00"},
        "break_times": ["12:15-13:15", "15:00-15:15"],
        "max_continuous_work": 120,  # 분
        "preferred_work_style": "focused_blocks"
    }
    
    # 효율성 점수 계산 (도구 결과 사용)
    efficiency_score = optimization_result.get("efficiency_score", 85)
    
    # 충돌 검사 (도구 결과 사용)
    conflicts = optimization_result.get("conflicts", [])
    
    return {
        "schedule_id": schedule_id,
        "tasks": tasks,
        "time_blocks": schedule_result.get("schedule_blocks", []),
        "constraints": constraints,
        "efficiency_score": schedule_result.get("efficiency_score", 85),
        "conflicts": [],
        "schedule_result": schedule_result,
        "optimization_result": optimization_result
    }


def calculate_efficiency_score(time_blocks: list, constraints: dict) -> float:
    """
    일정의 효율성 점수를 계산합니다.
    
    Args:
        time_blocks (list): 시간 블록 목록
        constraints (dict): 제약조건
        
    Returns:
        float: 효율성 점수 (0-100)
    """
    if not time_blocks:
        return 0.0
    
    # 우선순위 기반 점수 계산
    total_priority = sum(block.get("priority", 0) for block in time_blocks)
    max_possible_priority = len(time_blocks) * 10
    
    efficiency = (total_priority / max_possible_priority) * 100 if max_possible_priority > 0 else 0
    
    # 제약조건 위반 시 점수 감점
    working_hours = constraints.get("working_hours", {})
    work_start = datetime.strptime(working_hours.get("start", "09:00"), "%H:%M").time()
    work_end = datetime.strptime(working_hours.get("end", "18:00"), "%H:%M").time()
    
    for block in time_blocks:
        start_time = datetime.fromisoformat(block["start_time"]).time()
        end_time = datetime.fromisoformat(block["end_time"]).time()
        
        if start_time < work_start or end_time > work_end:
            efficiency -= 10  # 근무시간 외 작업 시 감점
    
    return max(0, min(100, efficiency))


def check_schedule_conflicts(time_blocks: list, constraints: dict) -> list:
    """
    일정 충돌을 검사합니다.
    
    Args:
        time_blocks (list): 시간 블록 목록
        constraints (dict): 제약조건
        
    Returns:
        list: 충돌 목록
    """
    conflicts = []
    
    # 시간 블록 간 충돌 검사
    for i, block1 in enumerate(time_blocks):
        for j, block2 in enumerate(time_blocks[i+1:], i+1):
            start1 = datetime.fromisoformat(block1["start_time"])
            end1 = datetime.fromisoformat(block1["end_time"])
            start2 = datetime.fromisoformat(block2["start_time"])
            end2 = datetime.fromisoformat(block2["end_time"])
            
            if start1 < end2 and start2 < end1:
                conflicts.append(f"시간 충돌: {block1['title']}과 {block2['title']}")
    
    # 제약조건 위반 검사
    max_continuous = constraints.get("max_continuous_work", 120)
    current_continuous = 0
    
    for block in time_blocks:
        duration = block["duration"]
        current_continuous += duration
        
        if current_continuous > max_continuous:
            conflicts.append(f"연속 작업 시간 초과: {current_continuous}분")
            current_continuous = 0
        else:
            current_continuous = 0  # 휴식 시간으로 리셋
    
    return conflicts




async def generate_plan_recommendation(schedule_plan: Dict[str, Any], state: State) -> str:
    """
    일정 계획 결과를 바탕으로 AI 추천을 생성합니다.
    
    Args:
        schedule_plan (Dict[str, Any]): 일정 계획 결과
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
            streaming=True  # 실시간 스트림 활성화
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
        
        # 다른 에이전트들의 데이터 가져오기
        health_data = state.get("health_data")
        worklife_data = state.get("worklife_data")
        
        prompt = f"""
        당신은 Plandy AI의 Plan Agent입니다.
        
        사용자 요청: {state.get('user_request', '')}
        
        이전 대화 내용:
        {conversation_context}
        
        일정 계획 결과:
        - 효율성 점수: {schedule_plan['efficiency_score']}/100
        - 충돌 개수: {len(schedule_plan['conflicts'])}
        - 시간 블록 수: {len(schedule_plan['time_blocks'])}
        
        시간 블록: {schedule_plan['time_blocks']}
        충돌 목록: {schedule_plan['conflicts']}
        제약조건: {schedule_plan['constraints']}
        
        다른 에이전트들의 데이터:
        - 건강 데이터: {health_data}
        - 워라벨 데이터: {worklife_data}
        
        사용자의 요청을 분석하고, 필요하다면 다른 에이전트들에게 도움이 되는 정보를 제공하세요.
        예를 들어:
        - Health Agent에게: 일정에 따른 건강 관리 권장사항
        - WorkLife Agent에게: 일정에 따른 워라벨 균형 조정 방안
        - Communication Agent에게: 일정 관련 사용자 응답 가이드
        
        이전 대화를 참고해서 구체적이고 실행 가능한 일정 개선 방안을 제시해주세요.
        """
        
        # 스트림 응답 생성 (API에서 실시간 처리)
        full_response = ""
        async for chunk in llm.astream(prompt):
            if hasattr(chunk, 'content') and chunk.content:
                full_response += chunk.content
        
        return full_response
    except Exception as e:
        # 폴백: 기본 추천
        efficiency_score = schedule_plan["efficiency_score"]
        conflicts = schedule_plan["conflicts"]
        
        if efficiency_score >= 80 and not conflicts:
            recommendation = "일정이 효율적으로 계획되었습니다. 현재 계획을 따르세요."
        elif efficiency_score >= 60:
            recommendation = "일정이 양호하지만 몇 가지 개선 여지가 있습니다."
        else:
            recommendation = "일정 최적화가 필요합니다. 우선순위를 재검토해보세요."
        
        if conflicts:
            recommendation += f" {len(conflicts)}개의 충돌이 발견되었습니다."
        
        return f"{recommendation} (API 오류: {str(e)})"
