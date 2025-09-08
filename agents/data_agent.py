"""
DataAgent - 데이터 수집 및 분석

사용자 데이터 수집 및 패턴 분석을 담당하는 에이전트입니다.
사용자 행동 패턴을 분석하고 데이터 기반 인사이트를 생성합니다.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from .base_agent import BaseAgent, AgentStatus


class DataAgent(BaseAgent):
    """
    데이터 수집 및 분석 에이전트
    
    사용자의 행동 패턴을 분석하고 데이터 기반 인사이트를 제공합니다.
    """
    
    def __init__(self):
        super().__init__(name="DataAgent", priority=6)
        self.logger = logging.getLogger("agent.DataAgent")
    
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        데이터 분석 관련 작업을 처리합니다.
        
        Args:
            context (Dict[str, Any]): 처리할 컨텍스트 데이터
            
        Returns:
            Dict[str, Any]: 처리 결과
        """
        self.set_status(AgentStatus.PROCESSING)
        
        try:
            action = context.get("action", "data_analysis")
            user_id = context.get("user_id")
            
            self.logger.info(f"Processing data action: {action} for user: {user_id}")
            
            if action == "data_analysis":
                result = await self._analyze_user_data(user_id, context.get("data_type"))
            elif action == "pattern_analysis":
                result = await self._analyze_patterns(user_id, context.get("pattern_type"))
            elif action == "insights":
                result = await self._generate_insights(user_id, context.get("insight_type"))
            elif action == "feedback_analysis":
                result = await self._analyze_feedback(user_id, context.get("feedback_data"))
            elif action == "performance_tracking":
                result = await self._track_performance(user_id, context.get("metrics"))
            else:
                result = await self._analyze_user_data(user_id)
            
            return {
                "status": "success",
                "action": action,
                "user_id": user_id,
                "result": result,
                "processed_by": "DataAgent"
            }
            
        except Exception as e:
            self.handle_error(e)
            return {
                "status": "error",
                "error": str(e),
                "processed_by": "DataAgent"
            }
        finally:
            self.set_status(AgentStatus.IDLE)
    
    def can_handle(self, action: str) -> bool:
        """
        DataAgent가 처리할 수 있는 액션인지 확인합니다.
        
        Args:
            action (str): 처리할 액션 타입
            
        Returns:
            bool: 처리 가능 여부
        """
        data_actions = [
            "data_analysis",
            "pattern_analysis",
            "insights",
            "feedback_analysis",
            "performance_tracking",
            "user_behavior_analysis",
            "trend_analysis"
        ]
        return action in data_actions
    
    def get_supported_actions(self) -> List[str]:
        """
        DataAgent가 지원하는 액션 목록을 반환합니다.
        
        Returns:
            List[str]: 지원하는 액션 목록
        """
        return [
            "data_analysis",
            "pattern_analysis",
            "insights",
            "feedback_analysis",
            "performance_tracking",
            "user_behavior_analysis",
            "trend_analysis"
        ]
    
    async def _analyze_user_data(self, user_id: int, data_type: str = "all") -> Dict[str, Any]:
        """
        사용자 데이터를 종합적으로 분석합니다.
        
        Args:
            user_id (int): 사용자 ID
            data_type (str): 분석할 데이터 타입
            
        Returns:
            Dict[str, Any]: 데이터 분석 결과
        """
        analysis_results = {}
        
        if data_type == "all" or data_type == "behavior":
            analysis_results["behavior"] = await self._analyze_user_behavior(user_id)
        
        if data_type == "all" or data_type == "productivity":
            analysis_results["productivity"] = await self._analyze_productivity(user_id)
        
        if data_type == "all" or data_type == "preferences":
            analysis_results["preferences"] = await self._analyze_user_preferences(user_id)
        
        if data_type == "all" or data_type == "trends":
            analysis_results["trends"] = await self._analyze_trends(user_id)
        
        return {
            "user_id": user_id,
            "analysis_type": data_type,
            "results": analysis_results,
            "summary": await self._generate_analysis_summary(analysis_results),
            "analyzed_at": datetime.now().isoformat()
        }
    
    async def _analyze_patterns(self, user_id: int, pattern_type: str = "all") -> Dict[str, Any]:
        """
        사용자 패턴을 분석합니다.
        
        Args:
            user_id (int): 사용자 ID
            pattern_type (str): 분석할 패턴 타입
            
        Returns:
            Dict[str, Any]: 패턴 분석 결과
        """
        patterns = {}
        
        if pattern_type == "all" or pattern_type == "time":
            patterns["time_patterns"] = await self._analyze_time_patterns(user_id)
        
        if pattern_type == "all" or pattern_type == "activity":
            patterns["activity_patterns"] = await self._analyze_activity_patterns(user_id)
        
        if pattern_type == "all" or pattern_type == "efficiency":
            patterns["efficiency_patterns"] = await self._analyze_efficiency_patterns(user_id)
        
        return {
            "user_id": user_id,
            "pattern_type": pattern_type,
            "patterns": patterns,
            "insights": await self._extract_pattern_insights(patterns),
            "analyzed_at": datetime.now().isoformat()
        }
    
    async def _generate_insights(self, user_id: int, insight_type: str = "all") -> Dict[str, Any]:
        """
        데이터 기반 인사이트를 생성합니다.
        
        Args:
            user_id (int): 사용자 ID
            insight_type (str): 생성할 인사이트 타입
            
        Returns:
            Dict[str, Any]: 생성된 인사이트
        """
        insights = []
        
        # 사용자 데이터 분석
        user_data = await self._analyze_user_data(user_id)
        patterns = await self._analyze_patterns(user_id)
        
        # 인사이트 생성 로직
        if insight_type == "all" or insight_type == "productivity":
            productivity_insights = await self._generate_productivity_insights(user_data, patterns)
            insights.extend(productivity_insights)
        
        if insight_type == "all" or insight_type == "wellness":
            wellness_insights = await self._generate_wellness_insights(user_data, patterns)
            insights.extend(wellness_insights)
        
        if insight_type == "all" or insight_type == "optimization":
            optimization_insights = await self._generate_optimization_insights(user_data, patterns)
            insights.extend(optimization_insights)
        
        return {
            "user_id": user_id,
            "insight_type": insight_type,
            "insights": insights,
            "confidence_scores": await self._calculate_insight_confidence(insights),
            "generated_at": datetime.now().isoformat()
        }
    
    async def _analyze_feedback(self, user_id: int, feedback_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        사용자 피드백을 분석합니다.
        
        Args:
            user_id (int): 사용자 ID
            feedback_data (List[Dict[str, Any]]): 피드백 데이터
            
        Returns:
            Dict[str, Any]: 피드백 분석 결과
        """
        sentiment_analysis = await self._analyze_sentiment(feedback_data)
        topic_analysis = await self._analyze_topics(feedback_data)
        satisfaction_score = await self._calculate_satisfaction_score(feedback_data)
        
        return {
            "user_id": user_id,
            "sentiment_analysis": sentiment_analysis,
            "topic_analysis": topic_analysis,
            "satisfaction_score": satisfaction_score,
            "recommendations": await self._generate_feedback_recommendations(sentiment_analysis, topic_analysis),
            "analyzed_at": datetime.now().isoformat()
        }
    
    async def _track_performance(self, user_id: int, metrics: List[str]) -> Dict[str, Any]:
        """
        사용자 성과를 추적합니다.
        
        Args:
            user_id (int): 사용자 ID
            metrics (List[str]): 추적할 메트릭 목록
            
        Returns:
            Dict[str, Any]: 성과 추적 결과
        """
        performance_data = {}
        
        for metric in metrics:
            if metric == "task_completion":
                performance_data["task_completion"] = await self._track_task_completion(user_id)
            elif metric == "time_management":
                performance_data["time_management"] = await self._track_time_management(user_id)
            elif metric == "goal_achievement":
                performance_data["goal_achievement"] = await self._track_goal_achievement(user_id)
            elif metric == "efficiency":
                performance_data["efficiency"] = await self._track_efficiency(user_id)
        
        return {
            "user_id": user_id,
            "metrics": metrics,
            "performance_data": performance_data,
            "trends": await self._analyze_performance_trends(performance_data),
            "tracked_at": datetime.now().isoformat()
        }
    
    # 헬퍼 메서드들
    async def _analyze_user_behavior(self, user_id: int) -> Dict[str, Any]:
        """사용자 행동 패턴을 분석합니다."""
        return {
            "most_active_hours": [9, 10, 14, 15],
            "preferred_work_style": "focused_blocks",
            "break_patterns": "regular_breaks",
            "productivity_peaks": ["morning", "afternoon"]
        }
    
    async def _analyze_productivity(self, user_id: int) -> Dict[str, Any]:
        """생산성을 분석합니다."""
        return {
            "average_task_completion_rate": 0.85,
            "time_estimation_accuracy": 0.78,
            "focus_time_percentage": 0.72,
            "distraction_frequency": 0.15
        }
    
    async def _analyze_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """사용자 선호도를 분석합니다."""
        return {
            "notification_preferences": "minimal",
            "work_environment": "quiet",
            "schedule_flexibility": "moderate",
            "collaboration_style": "independent"
        }
    
    async def _analyze_trends(self, user_id: int) -> Dict[str, Any]:
        """트렌드를 분석합니다."""
        return {
            "productivity_trend": "increasing",
            "workload_trend": "stable",
            "satisfaction_trend": "improving",
            "efficiency_trend": "fluctuating"
        }
    
    async def _generate_analysis_summary(self, analysis_results: Dict[str, Any]) -> str:
        """분석 결과 요약을 생성합니다."""
        return "사용자의 전반적인 생산성과 웰빙이 개선되고 있는 추세입니다."
    
    async def _analyze_time_patterns(self, user_id: int) -> Dict[str, Any]:
        """시간 패턴을 분석합니다."""
        return {
            "peak_productivity_hours": [9, 10, 14, 15],
            "low_energy_periods": [13, 16],
            "consistent_work_schedule": True,
            "weekend_work_pattern": "minimal"
        }
    
    async def _analyze_activity_patterns(self, user_id: int) -> Dict[str, Any]:
        """활동 패턴을 분석합니다."""
        return {
            "task_switching_frequency": "moderate",
            "deep_work_sessions": 3.2,  # 하루 평균
            "meeting_attendance": 0.6,  # 비율
            "break_consistency": 0.8
        }
    
    async def _analyze_efficiency_patterns(self, user_id: int) -> Dict[str, Any]:
        """효율성 패턴을 분석합니다."""
        return {
            "morning_efficiency": 0.85,
            "afternoon_efficiency": 0.78,
            "evening_efficiency": 0.65,
            "weekly_efficiency_trend": "stable"
        }
    
    async def _extract_pattern_insights(self, patterns: Dict[str, Any]) -> List[str]:
        """패턴에서 인사이트를 추출합니다."""
        return [
            "오전 시간대에 가장 높은 생산성을 보입니다",
            "점심 시간 후 1-2시간은 에너지가 낮아집니다",
            "깊은 작업 세션을 자주 유지하고 있습니다"
        ]
    
    async def _generate_productivity_insights(self, user_data: Dict[str, Any], patterns: Dict[str, Any]) -> List[str]:
        """생산성 인사이트를 생성합니다."""
        return [
            "오전 9-11시에 가장 중요한 작업을 배치하세요",
            "점심 후 2-3시에는 가벼운 작업을 권장합니다",
            "깊은 작업 시간을 더 늘리면 생산성이 향상될 것입니다"
        ]
    
    async def _generate_wellness_insights(self, user_data: Dict[str, Any], patterns: Dict[str, Any]) -> List[str]:
        """웰빙 인사이트를 생성합니다."""
        return [
            "규칙적인 휴식 시간을 유지하고 있습니다",
            "주말 업무 부담을 줄이는 것이 좋겠습니다",
            "스트레스 관리 기법을 도입해보세요"
        ]
    
    async def _generate_optimization_insights(self, user_data: Dict[str, Any], patterns: Dict[str, Any]) -> List[str]:
        """최적화 인사이트를 생성합니다."""
        return [
            "작업 전환 시간을 줄이면 효율성이 향상됩니다",
            "회의 시간을 30분으로 단축하는 것을 고려해보세요",
            "자동화 가능한 반복 작업을 식별했습니다"
        ]
    
    async def _calculate_insight_confidence(self, insights: List[str]) -> Dict[str, float]:
        """인사이트 신뢰도를 계산합니다."""
        return {insight: 0.85 for insight in insights}
    
    async def _analyze_sentiment(self, feedback_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """피드백 감정을 분석합니다."""
        return {
            "positive": 0.7,
            "neutral": 0.2,
            "negative": 0.1,
            "overall_sentiment": "positive"
        }
    
    async def _analyze_topics(self, feedback_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """피드백 주제를 분석합니다."""
        return {
            "schedule_management": 0.4,
            "notification_system": 0.3,
            "user_interface": 0.2,
            "performance": 0.1
        }
    
    async def _calculate_satisfaction_score(self, feedback_data: List[Dict[str, Any]]) -> float:
        """만족도 점수를 계산합니다."""
        return 4.2  # 5점 만점
    
    async def _generate_feedback_recommendations(self, sentiment: Dict[str, Any], topics: Dict[str, Any]) -> List[str]:
        """피드백 기반 권장사항을 생성합니다."""
        return [
            "일정 관리 기능을 개선하세요",
            "알림 시스템을 사용자 친화적으로 개선하세요"
        ]
    
    async def _track_task_completion(self, user_id: int) -> Dict[str, Any]:
        """작업 완료율을 추적합니다."""
        return {
            "completion_rate": 0.85,
            "on_time_rate": 0.78,
            "quality_score": 4.1
        }
    
    async def _track_time_management(self, user_id: int) -> Dict[str, Any]:
        """시간 관리를 추적합니다."""
        return {
            "estimated_vs_actual": 0.82,
            "schedule_adherence": 0.75,
            "time_waste_percentage": 0.12
        }
    
    async def _track_goal_achievement(self, user_id: int) -> Dict[str, Any]:
        """목표 달성을 추적합니다."""
        return {
            "daily_goals": 0.88,
            "weekly_goals": 0.72,
            "monthly_goals": 0.65
        }
    
    async def _track_efficiency(self, user_id: int) -> Dict[str, Any]:
        """효율성을 추적합니다."""
        return {
            "tasks_per_hour": 2.3,
            "focus_time_ratio": 0.68,
            "productivity_index": 0.81
        }
    
    async def _analyze_performance_trends(self, performance_data: Dict[str, Any]) -> Dict[str, str]:
        """성과 트렌드를 분석합니다."""
        return {
            "task_completion": "improving",
            "time_management": "stable",
            "goal_achievement": "improving",
            "efficiency": "fluctuating"
        }
