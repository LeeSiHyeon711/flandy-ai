"""
Plandy AI 시스템의 상태 모델

LangGraph 기반의 상태 관리를 위한 모델들을 정의합니다.
"""

from typing import List, Dict, Any, Optional, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from datetime import datetime


class Task(BaseModel):
    """작업 모델"""
    agent: Literal[
        "health_agent",
        "plan_agent", 
        "data_agent",
        "worklife_balance_agent",
        "communication_agent",
        "supervisor"
    ] = Field(
        ...,
        description="""
        작업을 수행하는 에이전트의 종류.
        - health_agent: 건강 상태 모니터링 및 습관 분석
        - plan_agent: 일정 계획 수립 및 최적화
        - data_agent: 데이터 수집 및 분석
        - worklife_balance_agent: 워라벨 균형 관리
        - communication_agent: 사용자 소통 및 대화
        - supervisor: 중앙 조정 및 작업 분배
        """
    )
    
    done: bool = Field(..., description="작업 완료 여부")
    description: str = Field(..., description="작업에 대한 설명")
    done_at: str = Field(..., description="작업 완료 시간")
    priority: int = Field(default=1, description="작업 우선순위")
    user_id: int = Field(..., description="사용자 ID")
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "agent": self.agent,
            "done": self.done,
            "description": self.description,
            "done_at": self.done_at,
            "priority": self.priority,
            "user_id": self.user_id
        }


class HealthData(BaseModel):
    """건강 데이터 모델"""
    health_score: float = Field(default=0.0, description="건강 점수")
    stress_level: float = Field(default=0.0, description="스트레스 레벨")
    sleep_quality: float = Field(default=0.0, description="수면 품질")
    exercise_frequency: float = Field(default=0.0, description="운동 빈도")
    habit_patterns: Dict[str, Any] = Field(default_factory=dict, description="습관 패턴")
    recommendations: List[str] = Field(default_factory=list, description="건강 권장사항")


class ScheduleData(BaseModel):
    """일정 데이터 모델"""
    schedule_id: str = Field(..., description="일정 ID")
    tasks: List[Dict[str, Any]] = Field(default_factory=list, description="작업 목록")
    time_blocks: List[Dict[str, Any]] = Field(default_factory=list, description="시간 블록")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="제약조건")
    efficiency_score: float = Field(default=0.0, description="효율성 점수")
    conflicts: List[str] = Field(default_factory=list, description="충돌 목록")


class WorkLifeBalanceData(BaseModel):
    """워라벨 데이터 모델"""
    balance_score: float = Field(default=0.0, description="균형 점수")
    work_hours: float = Field(default=0.0, description="업무 시간")
    leisure_hours: float = Field(default=0.0, description="여가 시간")
    stress_indicators: List[str] = Field(default_factory=list, description="스트레스 지표")
    improvement_suggestions: List[str] = Field(default_factory=list, description="개선 제안")


class UserFeedback(BaseModel):
    """사용자 피드백 모델"""
    feedback_id: str = Field(..., description="피드백 ID")
    user_id: int = Field(..., description="사용자 ID")
    text: str = Field(..., description="피드백 텍스트")
    rating: float = Field(default=0.0, description="평점")
    category: str = Field(default="general", description="카테고리")
    sentiment: str = Field(default="neutral", description="감정")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="타임스탬프")


class State(TypedDict):
    """시스템 전체 상태"""
    # 메시지 및 대화
    messages: List[Dict[str, Any]]
    user_input: str
    ai_response: str
    
    # 작업 관리
    task_history: List[Task]
    current_task: Optional[Task]
    supervisor_call_count: int
    
    # 사용자 정보
    user_id: int
    user_request: str
    user_preferences: Dict[str, Any]
    
    # 에이전트별 데이터
    health_data: Optional[HealthData]
    schedule_data: Optional[ScheduleData]
    worklife_data: Optional[WorkLifeBalanceData]
    feedback_data: List[UserFeedback]
    
    # 시스템 상태
    system_status: str
    error_messages: List[str]
    recommendations: List[str]
    
    # 컨텍스트 정보
    context: Dict[str, Any]
    session_id: str
    timestamp: str


class AgentContext(BaseModel):
    """에이전트 간 전달되는 컨텍스트 정보"""
    from_agent: str = Field(..., description="출발 에이전트")
    to_agent: str = Field(..., description="도착 에이전트")
    data_type: str = Field(..., description="데이터 타입")
    data: Dict[str, Any] = Field(..., description="전달할 데이터")
    priority: int = Field(default=1, description="우선순위")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="전달 시간")
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "data_type": self.data_type,
            "data": self.data,
            "priority": self.priority,
            "timestamp": self.timestamp
        }


class SystemMetrics(BaseModel):
    """시스템 메트릭 모델"""
    total_requests: int = Field(default=0, description="총 요청 수")
    successful_requests: int = Field(default=0, description="성공한 요청 수")
    failed_requests: int = Field(default=0, description="실패한 요청 수")
    average_response_time: float = Field(default=0.0, description="평균 응답 시간")
    agent_usage_count: Dict[str, int] = Field(default_factory=dict, description="에이전트 사용 횟수")
    last_updated: str = Field(default_factory=lambda: datetime.now().isoformat(), description="마지막 업데이트")
