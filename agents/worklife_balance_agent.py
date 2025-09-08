"""
WorkLifeBalanceAgent - 워라벨 균형 관리

업무와 개인 시간의 균형을 관리하는 에이전트입니다.
BalanceScore를 계산하고 워라벨 개선 방안을 제시합니다.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from .base_agent import BaseAgent, AgentStatus


class WorkLifeBalanceAgent(BaseAgent):
    """
    워라벨 균형 관리 에이전트
    
    사용자의 업무와 개인 시간의 균형을 분석하고 개선 방안을 제시합니다.
    """
    
    def __init__(self):
        super().__init__(name="WorkLifeBalanceAgent", priority=5)
        self.logger = logging.getLogger("agent.WorkLifeBalanceAgent")
    
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        워라벨 관련 작업을 처리합니다.
        
        Args:
            context (Dict[str, Any]): 처리할 컨텍스트 데이터
            
        Returns:
            Dict[str, Any]: 처리 결과
        """
        self.set_status(AgentStatus.PROCESSING)
        
        try:
            action = context.get("action", "worklife_balance")
            user_id = context.get("user_id")
            
            self.logger.info(f"Processing worklife action: {action} for user: {user_id}")
            
            if action == "worklife_balance":
                result = await self._analyze_worklife_balance(user_id)
            elif action == "balance_analysis":
                result = await self._analyze_balance_score(user_id, context.get("period"))
            elif action == "balance_score":
                result = await self._calculate_balance_score(user_id)
            elif action == "improvement_suggestions":
                result = await self._generate_improvement_suggestions(user_id)
            elif action == "stress_monitoring":
                result = await self._monitor_stress_levels(user_id)
            else:
                result = await self._analyze_worklife_balance(user_id)
            
            return {
                "status": "success",
                "action": action,
                "user_id": user_id,
                "result": result,
                "processed_by": "WorkLifeBalanceAgent"
            }
            
        except Exception as e:
            self.handle_error(e)
            return {
                "status": "error",
                "error": str(e),
                "processed_by": "WorkLifeBalanceAgent"
            }
        finally:
            self.set_status(AgentStatus.IDLE)
    
    def can_handle(self, action: str) -> bool:
        """
        WorkLifeBalanceAgent가 처리할 수 있는 액션인지 확인합니다.
        
        Args:
            action (str): 처리할 액션 타입
            
        Returns:
            bool: 처리 가능 여부
        """
        balance_actions = [
            "worklife_balance",
            "balance_analysis",
            "balance_score",
            "improvement_suggestions",
            "stress_monitoring",
            "overtime_analysis",
            "leisure_time_tracking"
        ]
        return action in balance_actions
    
    def get_supported_actions(self) -> List[str]:
        """
        WorkLifeBalanceAgent가 지원하는 액션 목록을 반환합니다.
        
        Returns:
            List[str]: 지원하는 액션 목록
        """
        return [
            "worklife_balance",
            "balance_analysis",
            "balance_score",
            "improvement_suggestions",
            "stress_monitoring",
            "overtime_analysis",
            "leisure_time_tracking"
        ]
    
    async def _analyze_worklife_balance(self, user_id: int) -> Dict[str, Any]:
        """
        워라벨 균형을 종합적으로 분석합니다.
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            Dict[str, Any]: 워라벨 분석 결과
        """
        # 기본 지표 수집
        work_hours = await self._get_work_hours(user_id)
        leisure_hours = await self._get_leisure_hours(user_id)
        stress_level = await self._get_stress_level(user_id)
        satisfaction_score = await self._get_satisfaction_score(user_id)
        
        # 균형 점수 계산
        balance_score = await self._calculate_balance_score(user_id)
        
        # 분석 결과
        analysis = {
            "work_hours": work_hours,
            "leisure_hours": leisure_hours,
            "stress_level": stress_level,
            "satisfaction_score": satisfaction_score,
            "balance_score": balance_score,
            "work_leisure_ratio": work_hours / leisure_hours if leisure_hours > 0 else float('inf'),
            "balance_status": await self._determine_balance_status(balance_score),
            "trends": await self._analyze_balance_trends(user_id),
            "alerts": await self._check_balance_alerts(work_hours, stress_level, balance_score)
        }
        
        return {
            "user_id": user_id,
            "analysis": analysis,
            "recommendations": await self._generate_balance_recommendations(analysis),
            "analyzed_at": datetime.now().isoformat()
        }
    
    async def _analyze_balance_score(self, user_id: int, period: str = "weekly") -> Dict[str, Any]:
        """
        특정 기간의 균형 점수를 분석합니다.
        
        Args:
            user_id (int): 사용자 ID
            period (str): 분석 기간 (daily, weekly, monthly)
            
        Returns:
            Dict[str, Any]: 균형 점수 분석 결과
        """
        if period == "daily":
            scores = await self._get_daily_balance_scores(user_id, days=7)
        elif period == "weekly":
            scores = await self._get_weekly_balance_scores(user_id, weeks=4)
        elif period == "monthly":
            scores = await self._get_monthly_balance_scores(user_id, months=3)
        else:
            scores = await self._get_weekly_balance_scores(user_id, weeks=4)
        
        return {
            "user_id": user_id,
            "period": period,
            "scores": scores,
            "average_score": sum(scores) / len(scores) if scores else 0,
            "trend": await self._calculate_score_trend(scores),
            "variance": await self._calculate_score_variance(scores),
            "analyzed_at": datetime.now().isoformat()
        }
    
    async def _calculate_balance_score(self, user_id: int) -> float:
        """
        워라벨 균형 점수를 계산합니다.
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            float: 균형 점수 (0-100)
        """
        # 각 요소별 점수 계산
        work_satisfaction = await self._get_work_satisfaction_score(user_id)
        personal_time_score = await self._get_personal_time_score(user_id)
        stress_management_score = await self._get_stress_management_score(user_id)
        energy_level_score = await self._get_energy_level_score(user_id)
        relationship_score = await self._get_relationship_score(user_id)
        
        # 가중 평균으로 최종 점수 계산
        weights = {
            "work_satisfaction": 0.25,
            "personal_time": 0.25,
            "stress_management": 0.20,
            "energy_level": 0.15,
            "relationships": 0.15
        }
        
        balance_score = (
            work_satisfaction * weights["work_satisfaction"] +
            personal_time_score * weights["personal_time"] +
            stress_management_score * weights["stress_management"] +
            energy_level_score * weights["energy_level"] +
            relationship_score * weights["relationships"]
        )
        
        return round(balance_score, 2)
    
    async def _generate_improvement_suggestions(self, user_id: int) -> Dict[str, Any]:
        """
        워라벨 개선 제안을 생성합니다.
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            Dict[str, Any]: 개선 제안
        """
        current_balance = await self._analyze_worklife_balance(user_id)
        weak_areas = await self._identify_weak_areas(current_balance)
        
        suggestions = []
        
        for area in weak_areas:
            if area == "work_hours":
                suggestions.extend(await self._get_work_hours_suggestions(user_id))
            elif area == "stress_level":
                suggestions.extend(await self._get_stress_management_suggestions(user_id))
            elif area == "leisure_time":
                suggestions.extend(await self._get_leisure_time_suggestions(user_id))
            elif area == "energy_level":
                suggestions.extend(await self._get_energy_management_suggestions(user_id))
        
        return {
            "user_id": user_id,
            "current_balance_score": current_balance["analysis"]["balance_score"],
            "weak_areas": weak_areas,
            "suggestions": suggestions,
            "priority_actions": await self._prioritize_suggestions(suggestions),
            "expected_improvement": await self._estimate_improvement(suggestions),
            "generated_at": datetime.now().isoformat()
        }
    
    async def _monitor_stress_levels(self, user_id: int) -> Dict[str, Any]:
        """
        스트레스 레벨을 모니터링합니다.
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            Dict[str, Any]: 스트레스 모니터링 결과
        """
        current_stress = await self._get_current_stress_level(user_id)
        stress_history = await self._get_stress_history(user_id, days=7)
        stress_triggers = await self._identify_stress_triggers(user_id)
        
        return {
            "user_id": user_id,
            "current_stress_level": current_stress,
            "stress_history": stress_history,
            "stress_triggers": stress_triggers,
            "stress_trend": await self._analyze_stress_trend(stress_history),
            "alerts": await self._check_stress_alerts(current_stress, stress_history),
            "coping_strategies": await self._recommend_coping_strategies(current_stress, stress_triggers),
            "monitored_at": datetime.now().isoformat()
        }
    
    # 헬퍼 메서드들
    async def _get_work_hours(self, user_id: int) -> float:
        """일일 업무 시간을 조회합니다."""
        return 8.5  # 예시 값
    
    async def _get_leisure_hours(self, user_id: int) -> float:
        """일일 여가 시간을 조회합니다."""
        return 4.0  # 예시 값
    
    async def _get_stress_level(self, user_id: int) -> float:
        """현재 스트레스 레벨을 조회합니다."""
        return 6.5  # 10점 만점
    
    async def _get_satisfaction_score(self, user_id: int) -> float:
        """만족도 점수를 조회합니다."""
        return 7.2  # 10점 만점
    
    async def _determine_balance_status(self, balance_score: float) -> str:
        """균형 상태를 판단합니다."""
        if balance_score >= 80:
            return "excellent"
        elif balance_score >= 60:
            return "good"
        elif balance_score >= 40:
            return "fair"
        else:
            return "poor"
    
    async def _analyze_balance_trends(self, user_id: int) -> Dict[str, Any]:
        """균형 트렌드를 분석합니다."""
        return {
            "trend": "improving",
            "change_rate": 2.3,
            "volatility": "low"
        }
    
    async def _check_balance_alerts(self, work_hours: float, stress_level: float, balance_score: float) -> List[str]:
        """균형 관련 알림을 확인합니다."""
        alerts = []
        if work_hours > 10:
            alerts.append("업무 시간이 과도합니다")
        if stress_level > 7:
            alerts.append("스트레스 레벨이 높습니다")
        if balance_score < 50:
            alerts.append("워라벨 균형이 좋지 않습니다")
        return alerts
    
    async def _generate_balance_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """균형 개선 권장사항을 생성합니다."""
        recommendations = []
        
        if analysis["work_hours"] > 9:
            recommendations.append("업무 시간을 줄이고 휴식 시간을 늘리세요")
        
        if analysis["stress_level"] > 6:
            recommendations.append("스트레스 관리 기법을 도입하세요")
        
        if analysis["work_leisure_ratio"] > 2:
            recommendations.append("개인 시간을 더 확보하세요")
        
        return recommendations
    
    async def _get_daily_balance_scores(self, user_id: int, days: int) -> List[float]:
        """일일 균형 점수를 조회합니다."""
        return [75.2, 78.1, 72.5, 80.3, 76.8, 79.1, 77.4]  # 예시 데이터
    
    async def _get_weekly_balance_scores(self, user_id: int, weeks: int) -> List[float]:
        """주간 균형 점수를 조회합니다."""
        return [76.5, 78.2, 75.8, 79.1]  # 예시 데이터
    
    async def _get_monthly_balance_scores(self, user_id: int, months: int) -> List[float]:
        """월간 균형 점수를 조회합니다."""
        return [76.8, 78.5, 77.2]  # 예시 데이터
    
    async def _calculate_score_trend(self, scores: List[float]) -> str:
        """점수 트렌드를 계산합니다."""
        if len(scores) < 2:
            return "stable"
        
        recent_avg = sum(scores[-3:]) / len(scores[-3:])
        earlier_avg = sum(scores[:-3]) / len(scores[:-3]) if len(scores) > 3 else scores[0]
        
        if recent_avg > earlier_avg + 2:
            return "improving"
        elif recent_avg < earlier_avg - 2:
            return "declining"
        else:
            return "stable"
    
    async def _calculate_score_variance(self, scores: List[float]) -> float:
        """점수 분산을 계산합니다."""
        if len(scores) < 2:
            return 0.0
        
        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)
        return round(variance, 2)
    
    async def _get_work_satisfaction_score(self, user_id: int) -> float:
        """업무 만족도 점수를 조회합니다."""
        return 7.5
    
    async def _get_personal_time_score(self, user_id: int) -> float:
        """개인 시간 점수를 조회합니다."""
        return 6.8
    
    async def _get_stress_management_score(self, user_id: int) -> float:
        """스트레스 관리 점수를 조회합니다."""
        return 6.2
    
    async def _get_energy_level_score(self, user_id: int) -> float:
        """에너지 레벨 점수를 조회합니다."""
        return 7.1
    
    async def _get_relationship_score(self, user_id: int) -> float:
        """인간관계 점수를 조회합니다."""
        return 8.0
    
    async def _identify_weak_areas(self, balance_analysis: Dict[str, Any]) -> List[str]:
        """약한 영역을 식별합니다."""
        weak_areas = []
        analysis = balance_analysis["analysis"]
        
        if analysis["work_hours"] > 9:
            weak_areas.append("work_hours")
        if analysis["stress_level"] > 6:
            weak_areas.append("stress_level")
        if analysis["work_leisure_ratio"] > 2:
            weak_areas.append("leisure_time")
        if analysis["balance_score"] < 70:
            weak_areas.append("energy_level")
        
        return weak_areas
    
    async def _get_work_hours_suggestions(self, user_id: int) -> List[str]:
        """업무 시간 관련 제안을 생성합니다."""
        return [
            "업무 시간을 8시간으로 제한하세요",
            "점심 시간을 확실히 보장하세요",
            "야근을 최소화하세요"
        ]
    
    async def _get_stress_management_suggestions(self, user_id: int) -> List[str]:
        """스트레스 관리 제안을 생성합니다."""
        return [
            "명상이나 요가를 시작해보세요",
            "규칙적인 운동을 하세요",
            "충분한 수면을 취하세요"
        ]
    
    async def _get_leisure_time_suggestions(self, user_id: int) -> List[str]:
        """여가 시간 관련 제안을 생성합니다."""
        return [
            "취미 활동을 정기적으로 하세요",
            "가족이나 친구와의 시간을 늘리세요",
            "휴가를 정기적으로 계획하세요"
        ]
    
    async def _get_energy_management_suggestions(self, user_id: int) -> List[str]:
        """에너지 관리 제안을 생성합니다."""
        return [
            "규칙적인 식사를 하세요",
            "충분한 수면을 취하세요",
            "스트레스를 줄이는 활동을 하세요"
        ]
    
    async def _prioritize_suggestions(self, suggestions: List[str]) -> List[Dict[str, Any]]:
        """제안을 우선순위별로 정렬합니다."""
        return [
            {"suggestion": suggestion, "priority": i + 1, "impact": "high"}
            for i, suggestion in enumerate(suggestions[:3])
        ]
    
    async def _estimate_improvement(self, suggestions: List[str]) -> Dict[str, Any]:
        """개선 효과를 추정합니다."""
        return {
            "expected_score_increase": 8.5,
            "time_to_see_results": "2-4 weeks",
            "confidence_level": 0.75
        }
    
    async def _get_current_stress_level(self, user_id: int) -> float:
        """현재 스트레스 레벨을 조회합니다."""
        return 6.5
    
    async def _get_stress_history(self, user_id: int, days: int) -> List[Dict[str, Any]]:
        """스트레스 히스토리를 조회합니다."""
        return [
            {"date": "2024-01-01", "level": 6.2, "triggers": ["work_deadline"]},
            {"date": "2024-01-02", "level": 7.1, "triggers": ["meeting_overload"]},
            {"date": "2024-01-03", "level": 5.8, "triggers": []}
        ]
    
    async def _identify_stress_triggers(self, user_id: int) -> List[str]:
        """스트레스 유발 요인을 식별합니다."""
        return ["work_deadline", "meeting_overload", "overtime", "conflict"]
    
    async def _analyze_stress_trend(self, stress_history: List[Dict[str, Any]]) -> str:
        """스트레스 트렌드를 분석합니다."""
        return "stable"
    
    async def _check_stress_alerts(self, current_stress: float, stress_history: List[Dict[str, Any]]) -> List[str]:
        """스트레스 알림을 확인합니다."""
        alerts = []
        if current_stress > 7:
            alerts.append("스트레스 레벨이 높습니다")
        return alerts
    
    async def _recommend_coping_strategies(self, current_stress: float, stress_triggers: List[str]) -> List[str]:
        """대처 전략을 권장합니다."""
        return [
            "깊게 숨쉬기",
            "짧은 산책하기",
            "음악 듣기",
            "친구와 대화하기"
        ]
