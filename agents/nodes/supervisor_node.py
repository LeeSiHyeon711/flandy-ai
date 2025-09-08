"""
Supervisor Node - 중앙 조정 노드

LangGraph 기반의 중앙 조정 및 작업 분배 노드입니다.
"""

from typing import Dict, Any
import logging
import os
from datetime import datetime
from models import State, Task
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate


def supervisor_node(state: State) -> State:
    """
    중앙 조정 노드
    
    Args:
        state (State): 현재 상태
        
    Returns:
        State: 업데이트된 상태
    """
    print("\n\n============= SUPERVISOR NODE ==============\n")
    
    logger = logging.getLogger("node.supervisor")
    logger.info("Supervisor node processing started")
    
    try:
        user_id = state.get("user_id", 1)
        user_request = state.get("user_request", "")
        user_input = state.get("user_input", "")
        
        # 작업 결정
        task_decision = decide_next_task(user_id, user_request, user_input, state)
        
        # 새로운 작업 생성
        new_task = Task(
            agent=task_decision["agent"],
            done=False,
            description=task_decision["description"],
            done_at="",
            priority=task_decision["priority"],
            user_id=user_id
        )
        
        # 작업 히스토리 업데이트
        task_history = state.get("task_history", [])
        task_history.append(new_task)
        
        # 메시지 업데이트
        messages = state.get("messages", [])
        supervisor_message = {
            "role": "assistant",
            "content": f"[Supervisor] 다음 작업 결정: {new_task.agent} - {new_task.description}",
            "timestamp": datetime.now().isoformat(),
            "agent": "supervisor"
        }
        messages.append(supervisor_message)
        
        # Supervisor 호출 횟수 업데이트
        supervisor_call_count = state.get("supervisor_call_count", 0) + 1
        
        logger.info(f"Supervisor decided next task: {new_task.agent}")
        
        return {
            **state,
            "messages": messages,
            "task_history": task_history,
            "current_task": new_task,
            "supervisor_call_count": supervisor_call_count,
            "system_status": "task_assigned"
        }
        
    except Exception as e:
        logger.error(f"Error in supervisor node: {str(e)}")
        error_messages = state.get("error_messages", [])
        error_messages.append(f"Supervisor node error: {str(e)}")
        
        return {
            **state,
            "error_messages": error_messages,
            "system_status": "error"
        }


def decide_next_task(user_id: int, user_request: str, user_input: str, state: State) -> Dict[str, Any]:
    """
    AI가 독립적으로 다음 작업을 결정합니다.
    
    Args:
        user_id (int): 사용자 ID
        user_request (str): 사용자 요청
        user_input (str): 사용자 입력
        state (State): 현재 상태
        
    Returns:
        Dict[str, Any]: 작업 결정 결과
    """
    # Supervisor 호출 횟수 확인
    supervisor_call_count = state.get("supervisor_call_count", 0)
    
    if supervisor_call_count > 3:
        return {
            "agent": "communication_agent",
            "description": "Supervisor 호출 횟수를 초과했으므로, 현재까지의 진행 상황을 사용자에게 보고합니다.",
            "priority": 1
        }
    
    try:
        # AI가 독립적으로 판단
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.3
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
        당신은 Plandy AI의 Supervisor Agent입니다.
        
        사용자 입력: {user_input}
        사용자 요청: {user_request}
        
        이전 대화 내용:
        {conversation_context}
        
        현재 상태:
        - Supervisor 호출 횟수: {supervisor_call_count}
        - 마지막 에이전트: {get_last_agent(state)}
        - 건강 데이터: {state.get('health_data')}
        - 일정 데이터: {state.get('schedule_data')}
        - 워라벨 데이터: {state.get('worklife_data')}
        
        사용 가능한 에이전트들:
        1. health_agent - 건강 상태 모니터링 및 분석
        2. plan_agent - 일정 계획 수립 및 최적화 (새로운 일정 생성/등록)
        3. data_agent - 데이터 분석 및 인사이트 생성
        4. worklife_balance_agent - 워라벨 균형 분석 및 개선
        5. communication_agent - 사용자 소통 및 일반 대화 (일정 조회, 질문 응답)
        
        **중요한 판단 기준:**
        - "일정 도와달라", "일정이 뭐가", "일정 확인" → communication_agent (조회/도움)
        - "일정 등록", "일정 추가", "면접 등록" → plan_agent (새로운 일정 생성)
        - "건강 상태", "건강 확인" → health_agent
        - "워라벨", "균형" → worklife_balance_agent
        - 일반적인 대화, 질문 → communication_agent
        
        사용자의 요청을 정확히 분석해서 가장 적절한 에이전트를 선택하세요.
        다음 형식으로 응답하세요:
        agent: [에이전트명]
        description: [작업 설명]
        priority: [우선순위 1-10]
        """
        
        response = llm.invoke(prompt)
        content = response.content
        
        # 응답 파싱
        lines = content.strip().split('\n')
        result = {}
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key == 'agent':
                    result['agent'] = value
                elif key == 'description':
                    result['description'] = value
                elif key == 'priority':
                    try:
                        result['priority'] = int(value)
                    except:
                        result['priority'] = 5
        
        # 기본값 설정
        if 'agent' not in result:
            result['agent'] = 'communication_agent'
        if 'description' not in result:
            result['description'] = '사용자 요청을 처리합니다.'
        if 'priority' not in result:
            result['priority'] = 5
            
        return result
        
    except Exception as e:
        # 폴백: 기본 로직
        return {
            "agent": "communication_agent",
            "description": "사용자 요청을 처리합니다.",
            "priority": 5
        }


def get_last_agent(state: State) -> str:
    """
    마지막으로 실행된 에이전트를 반환합니다.
    
    Args:
        state (State): 현재 상태
        
    Returns:
        str: 마지막 에이전트명
    """
    current_task = state.get("current_task")
    if current_task and hasattr(current_task, 'agent'):
        return current_task.agent
    return "none"


# 키워드 매칭 함수 제거 - AI가 독립적으로 판단


def get_last_agent(state: State) -> str:
    """마지막으로 실행된 에이전트를 반환합니다."""
    task_history = state.get("task_history", [])
    if task_history:
        return task_history[-1].agent
    return "none"


# 키워드 매칭 함수 제거 - AI가 독립적으로 판단


def supervisor_router(state: State) -> str:
    """
    Supervisor에서 다음 노드로 라우팅합니다.
    
    Args:
        state (State): 현재 상태
        
    Returns:
        str: 다음 노드 이름
    """
    current_task = state.get("current_task")
    if not current_task:
        return "communication_agent"
    
    return current_task.agent
