"""
HealthAgent - 건강 상태 모니터링

사용자의 건강 상태 및 습관 패턴을 분석하는 에이전트입니다.
HabitLog 데이터를 분석하여 건강 지표를 추적하고 개선 제안을 제공합니다.
"""

from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta
from .base_agent import BaseAgent, AgentStatus


class HealthAgent(BaseAgent):
    """
    건강 상태 모니터링 에이전트
    
    사용자의 습관 로그를 분석하고 건강 지표를 추적합니다.
    """
    
    def __init__(self):
        super().__init__(name="HealthAgent", priority=8)
        self.logger = logging.getLogger("agent.HealthAgent")
    
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        건강 관련 데이터를 분석하고 처리합니다.
        
        Args:
            context (Dict[str, Any]): 처리할 컨텍스트 데이터
            
        Returns:
            Dict[str, Any]: 처리 결과
        """
        self.set_status(AgentStatus.PROCESSING)
        
        try:
            action = context.get("action", "health_check")
            user_id = context.get("user_id")
            
            self.logger.info(f"Processing health action: {action} for user: {user_id}")
            
            if action == "health_check":
                result = await self._perform_health_check(user_id)
            elif action == "habit_analysis":
                result = await self._analyze_habits(user_id, context.get("date_range"))
            elif action == "health_monitoring":
                result = await self._monitor_health_metrics(user_id)
            else:
                result = await self._perform_health_check(user_id)
            
            return {
                "status": "success",
                "action": action,
                "user_id": user_id,
                "result": result,
                "processed_by": "HealthAgent"
            }
            
        except Exception as e:
            self.handle_error(e)
            return {
                "status": "error",
                "error": str(e),
                "processed_by": "HealthAgent"
            }
        finally:
            self.set_status(AgentStatus.IDLE)
    
    def can_handle(self, action: str) -> bool:
        """
        HealthAgent가 처리할 수 있는 액션인지 확인합니다.
        
        Args:
            action (str): 처리할 액션 타입
            
        Returns:
            bool: 처리 가능 여부
        """
        health_actions = [
            "health_check",
            "habit_analysis", 
            "health_monitoring",
            "stress_analysis",
            "sleep_analysis",
            "exercise_tracking"
        ]
        return action in health_actions
    
    def get_supported_actions(self) -> List[str]:
        """
        HealthAgent가 지원하는 액션 목록을 반환합니다.
        
        Returns:
            List[str]: 지원하는 액션 목록
        """
        return [
            "health_check",
            "habit_analysis",
            "health_monitoring", 
            "stress_analysis",
            "sleep_analysis",
            "exercise_tracking"
        ]
    
    async def _perform_health_check(self, user_id: int) -> Dict[str, Any]:
        """
        사용자의 전반적인 건강 상태를 체크합니다.
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            Dict[str, Any]: 건강 체크 결과
        """
        # 실제 구현에서는 HabitLog 모델에서 데이터를 조회
        # 여기서는 예시 데이터를 반환
        
        health_score = await self._calculate_health_score(user_id)
        recent_habits = await self._get_recent_habits(user_id, days=7)
        
        return {
            "health_score": health_score,
            "recent_habits": recent_habits,
            "recommendations": await self._generate_health_recommendations(user_id),
            "trends": await self._analyze_health_trends(user_id)
        }
    
    async def _analyze_habits(self, user_id: int, date_range: Dict[str, str] = None) -> Dict[str, Any]:
        """
        사용자의 습관 패턴을 분석합니다.
        
        Args:
            user_id (int): 사용자 ID
            date_range (Dict[str, str]): 분석할 날짜 범위
            
        Returns:
            Dict[str, Any]: 습관 분석 결과
        """
        if not date_range:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.fromisoformat(date_range["start"])
            end_date = datetime.fromisoformat(date_range["end"])
        
        # 습관 패턴 분석 로직
        habit_patterns = await self._get_habit_patterns(user_id, start_date, end_date)
        habit_frequency = await self._calculate_habit_frequency(user_id, start_date, end_date)
        
        return {
            "patterns": habit_patterns,
            "frequency": habit_frequency,
            "insights": await self._generate_habit_insights(habit_patterns),
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    
    async def _monitor_health_metrics(self, user_id: int) -> Dict[str, Any]:
        """
        건강 지표를 모니터링합니다.
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            Dict[str, Any]: 건강 지표 모니터링 결과
        """
        metrics = {
            "sleep_quality": await self._get_sleep_quality(user_id),
            "stress_level": await self._get_stress_level(user_id),
            "exercise_frequency": await self._get_exercise_frequency(user_id),
            "nutrition_score": await self._get_nutrition_score(user_id)
        }
        
        return {
            "metrics": metrics,
            "overall_score": sum(metrics.values()) / len(metrics),
            "alerts": await self._check_health_alerts(metrics)
        }
    
    async def _calculate_health_score(self, user_id: int) -> float:
        """건강 점수를 계산합니다."""
        # 실제 구현에서는 복잡한 알고리즘 사용
        return 75.5  # 예시 점수
    
    async def _get_recent_habits(self, user_id: int, days: int) -> List[Dict[str, Any]]:
        """최근 습관 데이터를 조회합니다."""
        # 실제 구현에서는 데이터베이스에서 조회
        return [
            {"habit": "coffee", "count": 3, "date": "2024-01-01"},
            {"habit": "exercise", "count": 1, "date": "2024-01-01"}
        ]
    
    async def _generate_health_recommendations(self, user_id: int) -> List[str]:
        """건강 개선 권장사항을 생성합니다."""
        return [
            "커피 섭취량을 줄여보세요",
            "규칙적인 운동을 시작해보세요",
            "충분한 수면을 취하세요"
        ]
    
    async def _analyze_health_trends(self, user_id: int) -> Dict[str, Any]:
        """건강 트렌드를 분석합니다."""
        return {
            "trend": "improving",
            "change_rate": 5.2,
            "period": "last_30_days"
        }
    
    async def _get_habit_patterns(self, user_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """습관 패턴을 분석합니다."""
        return {
            "most_frequent": "coffee",
            "time_patterns": {"morning": ["coffee", "exercise"], "evening": ["reading"]},
            "consistency_score": 0.8
        }
    
    async def _calculate_habit_frequency(self, user_id: int, start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """습관 빈도를 계산합니다."""
        return {
            "coffee": 2.5,  # 하루 평균 횟수
            "exercise": 0.8,
            "reading": 1.2
        }
    
    async def _generate_habit_insights(self, patterns: Dict[str, Any]) -> List[str]:
        """습관 인사이트를 생성합니다."""
        return [
            "아침에 커피를 자주 마시는 패턴이 보입니다",
            "운동 빈도가 점진적으로 증가하고 있습니다"
        ]
    
    async def _get_sleep_quality(self, user_id: int) -> float:
        """수면 품질 점수를 반환합니다."""
        return 7.5
    
    async def _get_stress_level(self, user_id: int) -> float:
        """스트레스 레벨을 반환합니다."""
        return 6.0
    
    async def _get_exercise_frequency(self, user_id: int) -> float:
        """운동 빈도 점수를 반환합니다."""
        return 6.5
    
    async def _get_nutrition_score(self, user_id: int) -> float:
        """영양 점수를 반환합니다."""
        return 7.0
    
    async def _check_health_alerts(self, metrics: Dict[str, float]) -> List[str]:
        """건강 알림을 확인합니다."""
        alerts = []
        if metrics["stress_level"] > 7.0:
            alerts.append("스트레스 레벨이 높습니다")
        if metrics["sleep_quality"] < 6.0:
            alerts.append("수면 품질이 낮습니다")
        return alerts
