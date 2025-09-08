"""
Prompt Service - 프롬프트 관리 서비스

에이전트 간 정보 전달을 위한 프롬프트 시스템을 관리합니다.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from models import State, AgentContext


class PromptService:
    """
    프롬프트 관리 서비스
    
    에이전트 간 정보 전달을 위한 프롬프트를 생성하고 관리합니다.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("service.prompt")
        self.prompt_templates = self._initialize_prompt_templates()
    
    def _initialize_prompt_templates(self) -> Dict[str, str]:
        """프롬프트 템플릿을 초기화합니다."""
        return {
            "health_to_plan": """
            건강 분석 결과를 바탕으로 일정 계획에 반영할 정보:
            
            건강 점수: {health_score}/100
            스트레스 레벨: {stress_level}/10
            수면 품질: {sleep_quality}/10
            운동 빈도: {exercise_frequency}/10
            
            주요 습관 패턴:
            - 커피 섭취: {coffee_intake}회/일
            - 운동 일수: {exercise_days}일/주
            - 평균 수면: {sleep_hours}시간
            - 업무 휴식: {work_breaks}회/일
            
            권장사항:
            {recommendations}
            
            이 정보를 바탕으로 사용자의 건강 상태를 고려한 일정을 계획해주세요.
            """,
            
            "plan_to_worklife": """
            일정 계획 결과를 바탕으로 워라벨 분석에 반영할 정보:
            
            일정 ID: {schedule_id}
            총 작업 시간: {total_work_hours}시간
            효율성 점수: {efficiency_score}/100
            충돌 개수: {conflict_count}개
            
            시간 블록 정보:
            {time_blocks}
            
            제약조건:
            - 근무 시간: {working_hours}
            - 휴식 시간: {break_times}
            - 최대 연속 작업: {max_continuous_work}분
            
            이 정보를 바탕으로 워라벨 균형을 분석해주세요.
            """,
            
            "worklife_to_communication": """
            워라벨 분석 결과를 바탕으로 사용자 소통에 반영할 정보:
            
            균형 점수: {balance_score}/100
            업무 시간: {work_hours}시간
            여가 시간: {leisure_hours}시간
            
            스트레스 지표:
            {stress_indicators}
            
            개선 제안:
            {improvement_suggestions}
            
            이 정보를 바탕으로 사용자에게 워라벨 균형에 대한 조언을 제공해주세요.
            """,
            
            "data_to_supervisor": """
            데이터 분석 결과를 바탕으로 시스템 개선에 반영할 정보:
            
            사용자 행동 패턴:
            - 가장 활발한 시간: {active_hours}
            - 선호하는 작업 스타일: {work_style}
            - 휴식 패턴: {break_patterns}
            - 생산성 피크: {productivity_peaks}
            
            생산성 지표:
            - 작업 완료율: {completion_rate}%
            - 시간 추정 정확도: {estimation_accuracy}%
            - 집중 시간 비율: {focus_ratio}%
            - 산만함 빈도: {distraction_frequency}%
            
            인사이트:
            {insights}
            
            트렌드:
            - 생산성: {productivity_trend}
            - 업무량: {workload_trend}
            - 만족도: {satisfaction_trend}
            
            이 정보를 바탕으로 시스템 개선 방향을 결정해주세요.
            """,
            
            "supervisor_to_all": """
            Supervisor의 작업 지시사항:
            
            현재 사용자 요청: {user_request}
            시스템 상태: {system_status}
            우선순위: {priority}
            
            작업 지시:
            {task_description}
            
            참고할 이전 결과:
            {previous_results}
            
            이 지시사항에 따라 작업을 수행해주세요.
            """,
            
            "communication_to_supervisor": """
            사용자 소통 결과를 바탕으로 다음 작업 결정에 반영할 정보:
            
            사용자 의도: {intent}
            의도 신뢰도: {confidence}
            사용자 응답: {user_response}
            
            대화 컨텍스트:
            - 대화 길이: {conversation_length}
            - 최근 주제: {recent_topics}
            - 사용자 선호도: {user_preferences}
            
            이 정보를 바탕으로 다음 작업을 결정해주세요.
            """
        }
    
    def generate_prompt(self, from_agent: str, to_agent: str, data: Dict[str, Any], state: State) -> str:
        """
        에이전트 간 정보 전달을 위한 프롬프트를 생성합니다.
        
        Args:
            from_agent (str): 출발 에이전트
            to_agent (str): 도착 에이전트
            data (Dict[str, Any]): 전달할 데이터
            state (State): 현재 상태
            
        Returns:
            str: 생성된 프롬프트
        """
        try:
            # 프롬프트 키 생성
            prompt_key = f"{from_agent}_to_{to_agent}"
            
            if prompt_key not in self.prompt_templates:
                self.logger.warning(f"No prompt template found for {prompt_key}")
                return self._generate_default_prompt(from_agent, to_agent, data, state)
            
            # 템플릿 가져오기
            template = self.prompt_templates[prompt_key]
            
            # 데이터 포맷팅
            formatted_data = self._format_data_for_prompt(data, state)
            
            # 프롬프트 생성
            prompt = template.format(**formatted_data)
            
            self.logger.info(f"Generated prompt from {from_agent} to {to_agent}")
            return prompt
            
        except Exception as e:
            self.logger.error(f"Error generating prompt: {str(e)}")
            return self._generate_default_prompt(from_agent, to_agent, data, state)
    
    def _format_data_for_prompt(self, data: Dict[str, Any], state: State) -> Dict[str, Any]:
        """
        프롬프트용 데이터를 포맷팅합니다.
        
        Args:
            data (Dict[str, Any]): 원본 데이터
            state (State): 현재 상태
            
        Returns:
            Dict[str, Any]: 포맷팅된 데이터
        """
        formatted = data.copy()
        
        # 리스트를 문자열로 변환
        for key, value in formatted.items():
            if isinstance(value, list):
                if isinstance(value[0], str):
                    formatted[key] = "\n".join(f"- {item}" for item in value)
                else:
                    formatted[key] = "\n".join(f"- {str(item)}" for item in value)
            elif isinstance(value, dict):
                formatted[key] = "\n".join(f"- {k}: {v}" for k, v in value.items())
        
        # 상태 정보 추가
        formatted.update({
            "user_request": state.get("user_request", ""),
            "system_status": state.get("system_status", "idle"),
            "timestamp": datetime.now().isoformat()
        })
        
        return formatted
    
    def _generate_default_prompt(self, from_agent: str, to_agent: str, data: Dict[str, Any], state: State) -> str:
        """
        기본 프롬프트를 생성합니다.
        
        Args:
            from_agent (str): 출발 에이전트
            to_agent (str): 도착 에이전트
            data (Dict[str, Any]): 전달할 데이터
            state (State): 현재 상태
            
        Returns:
            str: 기본 프롬프트
        """
        # 이전 대화 내용 가져오기
        messages = state.get("messages", [])
        recent_messages = messages[-3:] if len(messages) > 3 else messages
        conversation_context = ""
        for msg in recent_messages:
            if msg.get("role") == "user":
                conversation_context += f"사용자: {msg.get('content', '')}\n"
            elif msg.get("role") == "assistant":
                conversation_context += f"AI: {msg.get('content', '')}\n"
        
        return f"""
        {from_agent}에서 {to_agent}로 전달되는 정보:
        
        사용자 요청: {state.get('user_request', '')}
        
        이전 대화 내용:
        {conversation_context}
        
        전달 데이터: {data}
        전달 시간: {datetime.now().isoformat()}
        
        이 정보를 바탕으로 적절한 작업을 수행해주세요.
        """
    
    def create_agent_context(self, from_agent: str, to_agent: str, data: Dict[str, Any], priority: int = 1) -> AgentContext:
        """
        에이전트 컨텍스트를 생성합니다.
        
        Args:
            from_agent (str): 출발 에이전트
            to_agent (str): 도착 에이전트
            data (Dict[str, Any]): 전달할 데이터
            priority (int): 우선순위
            
        Returns:
            AgentContext: 에이전트 컨텍스트
        """
        return AgentContext(
            from_agent=from_agent,
            to_agent=to_agent,
            data_type="information_transfer",
            data=data,
            priority=priority
        )
    
    def get_available_prompts(self) -> List[str]:
        """
        사용 가능한 프롬프트 목록을 반환합니다.
        
        Returns:
            List[str]: 프롬프트 키 목록
        """
        return list(self.prompt_templates.keys())
    
    def add_custom_prompt(self, key: str, template: str) -> None:
        """
        사용자 정의 프롬프트를 추가합니다.
        
        Args:
            key (str): 프롬프트 키
            template (str): 프롬프트 템플릿
        """
        self.prompt_templates[key] = template
        self.logger.info(f"Added custom prompt: {key}")
    
    def update_prompt(self, key: str, template: str) -> None:
        """
        기존 프롬프트를 업데이트합니다.
        
        Args:
            key (str): 프롬프트 키
            template (str): 새로운 프롬프트 템플릿
        """
        if key in self.prompt_templates:
            self.prompt_templates[key] = template
            self.logger.info(f"Updated prompt: {key}")
        else:
            self.logger.warning(f"Prompt not found: {key}")
    
    def delete_prompt(self, key: str) -> None:
        """
        프롬프트를 삭제합니다.
        
        Args:
            key (str): 삭제할 프롬프트 키
        """
        if key in self.prompt_templates:
            del self.prompt_templates[key]
            self.logger.info(f"Deleted prompt: {key}")
        else:
            self.logger.warning(f"Prompt not found: {key}")


# 전역 프롬프트 서비스 인스턴스
prompt_service = PromptService()
