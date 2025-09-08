"""
Communication Node - 사용자 소통 노드

LangGraph 기반의 사용자 소통 및 대화 노드입니다.
"""

from typing import Dict, Any
import logging
import os
import sys
import time
from datetime import datetime
from models import State, Task
from langchain_openai import ChatOpenAI


async def communication_node(state: State) -> State:
    """
    사용자 소통 노드
    
    Args:
        state (State): 현재 상태
        
    Returns:
        State: 업데이트된 상태
    """
    print("\n\n============= COMMUNICATION NODE ==============\n")
    
    logger = logging.getLogger("node.communication")
    logger.info("Communication node processing started")
    
    try:
        # 현재 작업 확인
        current_task = state.get("current_task")
        if not current_task or current_task.agent != "communication_agent":
            logger.warning("Communication node called without proper task assignment")
            return state
        
        user_id = state.get("user_id", 1)
        user_input = state.get("user_input", "")
        
        # 사용자 입력 분석 및 응답 생성
        communication_result = await process_user_communication(user_id, user_input, state)
        
        # 메시지 업데이트
        messages = state.get("messages", [])
        
        # 사용자 메시지 추가
        user_message = {
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id
        }
        messages.append(user_message)
        
        # AI 응답 추가
        ai_message = {
            "role": "assistant",
            "content": communication_result["response"],
            "timestamp": datetime.now().isoformat(),
            "agent": "communication_agent",
            "intent": communication_result["intent"],
            "confidence": communication_result["confidence"]
        }
        messages.append(ai_message)
        
        # 작업 완료 처리
        task_history = state.get("task_history", [])
        if task_history:
            task_history[-1].done = True
            task_history[-1].done_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # AI 추천 생성
        ai_recommendation = generate_communication_recommendation(communication_result, state)
        
        logger.info("Communication node processing completed successfully")
        
        return {
            **state,
            "messages": messages,
            "ai_response": communication_result["response"],
            "task_history": task_history,
            "ai_recommendation": ai_recommendation,
            "system_status": "communication_completed"
        }
        
    except Exception as e:
        logger.error(f"Error in communication node: {str(e)}")
        error_messages = state.get("error_messages", [])
        error_messages.append(f"Communication node error: {str(e)}")
        
        return {
            **state,
            "error_messages": error_messages,
            "system_status": "error"
        }


async def process_user_communication(user_id: int, user_input: str, state: State) -> Dict[str, Any]:
    """
    사용자 소통을 처리합니다.
    
    Args:
        user_id (int): 사용자 ID
        user_input (str): 사용자 입력
        state (State): 현재 상태
        
    Returns:
        Dict[str, Any]: 소통 처리 결과
    """
    # 의도 분석
    intent = analyze_user_intent(user_input)
    
    # 컨텍스트 분석
    context = analyze_conversation_context(state)
    
    # 응답 생성
    response = await generate_response(user_input, intent, context, state)
    
    return {
        "intent": intent["type"],
        "confidence": intent["confidence"],
        "response": response,
        "context_used": context
    }


def analyze_user_intent(user_input: str) -> Dict[str, Any]:
    """
    사용자 의도를 분석합니다.
    
    Args:
        user_input (str): 사용자 입력
        
    Returns:
        Dict[str, Any]: 의도 분석 결과
    """
    # 간단한 의도 분류 로직 (실제로는 더 정교한 NLP 모델 사용)
    intents = {
        "schedule_management": ["일정", "스케줄", "계획", "시간", "할일"],
        "health_concern": ["건강", "스트레스", "피로", "휴식", "운동"],
        "worklife_balance": ["워라벨", "균형", "업무", "개인시간", "휴가"],
        "feedback": ["피드백", "의견", "개선", "만족", "불만"],
        "general_inquiry": ["질문", "궁금", "알려줘", "도움", "어떻게"]
    }
    
    detected_intent = "general_inquiry"
    confidence = 0.5
    
    for intent_type, keywords in intents.items():
        for keyword in keywords:
            if keyword in user_input:
                detected_intent = intent_type
                confidence = 0.8
                break
    
    return {
        "type": detected_intent,
        "confidence": confidence,
        "keywords": [kw for kw in intents.get(detected_intent, []) if kw in user_input]
    }


def analyze_conversation_context(state: State) -> Dict[str, Any]:
    """
    대화 컨텍스트를 분석합니다.
    
    Args:
        state (State): 현재 상태
        
    Returns:
        Dict[str, Any]: 컨텍스트 분석 결과
    """
    messages = state.get("messages", [])
    
    context = {
        "conversation_length": len(messages),
        "recent_topics": [],
        "user_preferences": state.get("user_preferences", {}),
        "system_status": state.get("system_status", "idle")
    }
    
    # 최근 대화 주제 추출
    recent_messages = messages[-5:] if len(messages) > 5 else messages
    for message in recent_messages:
        if message.get("role") == "user":
            content = message.get("content", "")
            # 간단한 키워드 추출
            keywords = ["일정", "건강", "워라벨", "피드백", "도움"]
            for keyword in keywords:
                if keyword in content and keyword not in context["recent_topics"]:
                    context["recent_topics"].append(keyword)
    
    return context


async def generate_response(user_input: str, intent: Dict[str, Any], context: Dict[str, Any], state: State) -> str:
    """
    사용자 입력에 대한 응답을 생성합니다.
    
    Args:
        user_input (str): 사용자 입력
        intent (Dict[str, Any]): 의도 분석 결과
        context (Dict[str, Any]): 컨텍스트 정보
        state (State): 현재 상태
        
    Returns:
        str: 생성된 응답
    """
    intent_type = intent["type"]
    
    # 의도별 응답 생성
    if intent_type == "schedule_management":
        response = await generate_schedule_response(user_input, context, state)
    elif intent_type == "health_concern":
        response = generate_health_response(user_input, context, state)
    elif intent_type == "worklife_balance":
        response = generate_worklife_response(user_input, context, state)
    elif intent_type == "feedback":
        response = generate_feedback_response(user_input, context, state)
    else:
        response = await generate_general_response(user_input, context, state)
    
    return response


async def generate_schedule_response(user_input: str, context: Dict[str, Any], state: State) -> str:
    """일정 관리 관련 응답 생성 (진짜 streaming)"""
    try:
        from tools import TimeTools
        
        # TimeTools를 사용하여 현재 시간 정보 가져오기 (사용자 시간대 사용)
        time_tools = TimeTools()
        user_timezone = "Asia/Seoul"  # 기본값
        
        # state에서 시간대 정보 추출
        user_input = state.get("user_input", "")
        if "사용자 시간대:" in user_input:
            for line in user_input.split('\n'):
                if "사용자 시간대:" in line:
                    user_timezone = line.split("사용자 시간대:")[1].strip()
                    break
        
        time_result = await time_tools.execute({"action": "now", "timezone": user_timezone, "format": "readable"})
        current_time = time_result.get("readable_time", time_result.get("current_time", "현재 시간을 확인할 수 없습니다"))
        
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.7,
            streaming=True  # 진짜 streaming 활성화
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
        
        # 일정 조회 요청인지 확인하고 실제로 조회
        schedule_info = ""
        if any(keyword in user_input.lower() for keyword in ["일정", "스케줄", "뭐가", "있지", "확인", "조회"]):
            print("일정 조회 요청 감지 - ScheduleTools 사용 중...")
            from tools import ScheduleTools
            schedule_tools = ScheduleTools()
            schedule_result = await schedule_tools.execute({
                "action": "list_schedules", 
                "user_id": state.get("user_id", 1)
            })
            print(f"일정 조회 결과: {schedule_result}")
            
            if schedule_result.get("status") == "success":
                schedules = schedule_result.get("schedules", [])
                for schedule in schedules:
                    schedule_info += f"- {schedule.get('title', 'N/A')}: {schedule.get('start_time', 'N/A')}\n"
        
        prompt = f"""
        사용자가 '{user_input}'라고 말했습니다.
        현재 시간: {current_time}
        
        이전 대화 내용:
        {conversation_context}
        
        실제 일정 데이터:
        {schedule_info}
        
        현재 시간을 정확히 알려주고, 실제 일정 데이터를 바탕으로 일정 관리 전문가로서 도움이 되는 응답을 해주세요.
        """
        
        # 진짜 streaming으로 응답 생성
        full_response = ""
        print("AI 응답: ", end="", flush=True)
        
        async for chunk in llm.astream(prompt):
            if hasattr(chunk, 'content') and chunk.content:
                print(chunk.content, end="", flush=True)
                full_response += chunk.content
                time.sleep(0.02)  # 타이핑 효과
        
        print()  # 줄바꿈
        return full_response
        
    except Exception as e:
        return f"일정 관리에 대해 도움을 드리겠습니다. (API 오류: {str(e)})"


def generate_health_response(user_input: str, context: Dict[str, Any], state: State) -> str:
    """건강 관련 응답 생성"""
    return "건강 관리에 대해 도움을 드리겠습니다. 어떤 부분이 걱정되시나요?"


def generate_worklife_response(user_input: str, context: Dict[str, Any], state: State) -> str:
    """워라벨 관련 응답 생성"""
    return "워라벨 균형에 대해 도움을 드리겠습니다. 어떤 부분을 개선하고 싶으신가요?"


def generate_feedback_response(user_input: str, context: Dict[str, Any], state: State) -> str:
    """피드백 관련 응답 생성"""
    return "피드백을 주셔서 감사합니다. 더 나은 서비스를 위해 노력하겠습니다!"


async def generate_general_response(user_input: str, context: Dict[str, Any], state: State) -> str:
    """일반적인 응답 생성 (진짜 streaming)"""
    try:
        from tools import TimeTools
        
        # TimeTools를 사용하여 현재 시간 정보 가져오기 (사용자 시간대 사용)
        time_tools = TimeTools()
        user_timezone = "Asia/Seoul"  # 기본값
        
        # state에서 시간대 정보 추출
        user_input = state.get("user_input", "")
        if "사용자 시간대:" in user_input:
            for line in user_input.split('\n'):
                if "사용자 시간대:" in line:
                    user_timezone = line.split("사용자 시간대:")[1].strip()
                    break
        
        time_result = await time_tools.execute({"action": "now", "timezone": user_timezone, "format": "readable"})
        current_time = time_result.get("readable_time", time_result.get("current_time", "현재 시간을 확인할 수 없습니다"))
        
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.7,
            streaming=True  # 진짜 streaming 활성화
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
        
        # AI가 독립적으로 판단하도록 키워드 매칭 제거
        prompt = f"""
        당신은 Plandy AI의 Communication Agent입니다.
        
        사용자 입력: '{user_input}'
        현재 시간: {current_time}
        
        이전 대화 내용:
        {conversation_context}
        
        사용자의 요청을 분석하고, 필요하다면 다음 도구들을 사용할 수 있습니다:
        1. ScheduleTools - 일정 조회, 추가, 수정, 삭제
        2. TimeTools - 시간 관련 정보
        
        사용자의 요청을 분석해서:
        - 일정 조회가 필요하면 ScheduleTools의 list_schedules를 사용하세요
        - 일정 추가가 필요하면 ScheduleTools의 save_schedule을 사용하세요
        - 시간 정보가 필요하면 TimeTools를 사용하세요
        
        도구를 사용할 때는 실제로 호출하고, 결과를 바탕으로 응답하세요.
        도구 사용 후 결과를 바탕으로 친근하고 도움이 되는 응답을 해주세요.
        """
        
        # AI가 프롬프트를 통해 스스로 판단하도록 함
        # 키워드 매칭 제거 - AI가 독립적으로 판단
        
        # 도구 준비
        from tools import ScheduleTools, TimeTools
        
        schedule_tools = ScheduleTools()
        time_tools = TimeTools()
        
        # LangChain 도구로 변환
        from langchain.tools import Tool
        
        def schedule_list_tool(user_id: int = 1):
            """일정 목록을 조회합니다."""
            import asyncio
            return asyncio.run(schedule_tools.execute({"action": "list_schedules", "user_id": user_id}))
        
        def schedule_save_tool(title: str, description: str, start_time: str, end_time: str, user_id: int = 1):
            """일정을 저장합니다."""
            import asyncio
            from datetime import datetime
            return asyncio.run(schedule_tools.execute({
                "action": "save_schedule",
                "user_id": user_id,
                "title": title,
                "description": description,
                "start_time": datetime.fromisoformat(start_time),
                "end_time": datetime.fromisoformat(end_time),
                "duration": 60,
                "priority": 5
            }))
        
        def time_now_tool():
            """현재 시간을 조회합니다."""
            import asyncio
            user_timezone = "Asia/Seoul"  # 기본값
            user_input = state.get("user_input", "")
            if "사용자 시간대:" in user_input:
                for line in user_input.split('\n'):
                    if "사용자 시간대:" in line:
                        user_timezone = line.split("사용자 시간대:")[1].strip()
                        break
            return asyncio.run(time_tools.execute({"action": "now", "timezone": user_timezone, "format": "readable"}))
        
        tools = [
            Tool(name="schedule_list", description="일정 목록을 조회합니다", func=schedule_list_tool),
            Tool(name="schedule_save", description="일정을 저장합니다", func=schedule_save_tool),
            Tool(name="time_now", description="현재 시간을 조회합니다", func=time_now_tool)
        ]
        
        # 일정 조회 요청인지 확인하고 실제로 조회
        schedule_info = ""
        if any(keyword in user_input.lower() for keyword in ["일정", "스케줄", "뭐가", "있지", "확인", "조회"]):
            print("일정 조회 요청 감지 - ScheduleTools 사용 중...")
            schedule_result = await schedule_tools.execute({
                "action": "list_schedules", 
                "user_id": state.get("user_id", 1)
            })
            print(f"일정 조회 결과: {schedule_result}")
            
            if schedule_result.get("status") == "success":
                schedules = schedule_result.get("schedules", [])
                for schedule in schedules:
                    schedule_info += f"- {schedule.get('title', 'N/A')}: {schedule.get('start_time', 'N/A')}\n"
        
        # 프롬프트에 실제 일정 데이터 포함
        if schedule_info:
            prompt = f"""
            사용자가 '{user_input}'라고 물어봤습니다.
            현재 시간: {current_time}
            
            이전 대화 내용:
            {conversation_context}
            
            실제 일정 데이터:
            {schedule_info}
            
            실제 일정을 확인해서 친근하게 응답해주세요.
            """
        
        # 진짜 streaming으로 응답 생성
        full_response = ""
        print("AI 응답: ", end="", flush=True)
        
        async for chunk in llm.astream(prompt):
            if hasattr(chunk, 'content') and chunk.content:
                print(chunk.content, end="", flush=True)
                full_response += chunk.content
                time.sleep(0.02)  # 타이핑 효과
        
        print()  # 줄바꿈
        return full_response
        
    except Exception as e:
        return f"안녕하세요! 무엇을 도와드릴까요? (API 오류: {str(e)})"


def generate_communication_recommendation(communication_result: Dict[str, Any], state: State) -> str:
    """
    소통 결과를 바탕으로 AI 추천을 생성합니다.
    
    Args:
        communication_result (Dict[str, Any]): 소통 처리 결과
        state (State): 현재 상태
        
    Returns:
        str: AI 추천 메시지
    """
    intent = communication_result["intent"]
    confidence = communication_result["confidence"]
    
    if confidence > 0.8:
        recommendation = f"사용자의 의도({intent})가 명확하게 파악되었습니다."
    elif confidence > 0.5:
        recommendation = f"사용자의 의도({intent})를 어느 정도 파악했습니다."
    else:
        recommendation = "사용자의 의도를 명확히 파악하기 어렵습니다. 추가 정보가 필요할 수 있습니다."
    
    return recommendation
