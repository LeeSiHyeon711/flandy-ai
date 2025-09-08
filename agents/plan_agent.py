"""
PlanAgent - 일정 계획 수립

일정 생성, 최적화, 재조정을 담당하는 에이전트입니다.
Task와 ScheduleBlock 데이터를 관리하여 효율적인 일정을 수립합니다.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from .base_agent import BaseAgent, AgentStatus


class PlanAgent(BaseAgent):
    """
    일정 계획 수립 에이전트
    
    사용자의 작업과 일정을 분석하여 최적의 일정을 생성하고 관리합니다.
    """
    
    def __init__(self):
        super().__init__(name="PlanAgent", priority=7)
        self.logger = logging.getLogger("agent.PlanAgent")
    
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        일정 관련 작업을 처리합니다.
        
        Args:
            context (Dict[str, Any]): 처리할 컨텍스트 데이터
            
        Returns:
            Dict[str, Any]: 처리 결과
        """
        self.set_status(AgentStatus.PROCESSING)
        
        try:
            action = context.get("action", "schedule_plan")
            user_id = context.get("user_id")
            
            self.logger.info(f"Processing plan action: {action} for user: {user_id}")
            
            if action == "schedule_plan":
                result = await self._create_schedule(user_id, context.get("tasks", []))
            elif action == "reschedule":
                result = await self._reschedule_tasks(user_id, context.get("schedule_id"), context.get("reason"))
            elif action == "optimize_schedule":
                result = await self._optimize_schedule(user_id, context.get("schedule_id"))
            elif action == "add_task":
                result = await self._add_task_to_schedule(user_id, context.get("task"), context.get("schedule_id"))
            else:
                result = await self._create_schedule(user_id, context.get("tasks", []))
            
            return {
                "status": "success",
                "action": action,
                "user_id": user_id,
                "result": result,
                "processed_by": "PlanAgent"
            }
            
        except Exception as e:
            self.handle_error(e)
            return {
                "status": "error",
                "error": str(e),
                "processed_by": "PlanAgent"
            }
        finally:
            self.set_status(AgentStatus.IDLE)
    
    def can_handle(self, action: str) -> bool:
        """
        PlanAgent가 처리할 수 있는 액션인지 확인합니다.
        
        Args:
            action (str): 처리할 액션 타입
            
        Returns:
            bool: 처리 가능 여부
        """
        plan_actions = [
            "schedule_plan",
            "reschedule",
            "optimize_schedule",
            "add_task",
            "remove_task",
            "update_task",
            "time_block_analysis"
        ]
        return action in plan_actions
    
    def get_supported_actions(self) -> List[str]:
        """
        PlanAgent가 지원하는 액션 목록을 반환합니다.
        
        Returns:
            List[str]: 지원하는 액션 목록
        """
        return [
            "schedule_plan",
            "reschedule",
            "optimize_schedule",
            "add_task",
            "remove_task",
            "update_task",
            "time_block_analysis"
        ]
    
    async def _create_schedule(self, user_id: int, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        새로운 일정을 생성합니다.
        
        Args:
            user_id (int): 사용자 ID
            tasks (List[Dict[str, Any]]): 일정에 포함할 작업 목록
            
        Returns:
            Dict[str, Any]: 생성된 일정 정보
        """
        # 작업 우선순위 및 제약조건 분석
        prioritized_tasks = await self._prioritize_tasks(tasks)
        constraints = await self._get_user_constraints(user_id)
        
        # 시간 블록 할당
        schedule_blocks = await self._allocate_time_blocks(prioritized_tasks, constraints)
        
        # 일정 최적화
        optimized_schedule = await self._optimize_time_allocation(schedule_blocks)
        
        return {
            "schedule_id": f"schedule_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "blocks": optimized_schedule,
            "total_duration": sum(block["duration"] for block in optimized_schedule),
            "efficiency_score": await self._calculate_efficiency_score(optimized_schedule),
            "created_at": datetime.now().isoformat()
        }
    
    async def _reschedule_tasks(self, user_id: int, schedule_id: str, reason: str) -> Dict[str, Any]:
        """
        기존 일정을 재조정합니다.
        
        Args:
            user_id (int): 사용자 ID
            schedule_id (str): 재조정할 일정 ID
            reason (str): 재조정 사유
            
        Returns:
            Dict[str, Any]: 재조정된 일정 정보
        """
        # 기존 일정 조회
        current_schedule = await self._get_schedule(schedule_id)
        
        # 재조정 로직 적용
        if reason == "emergency":
            rescheduled = await self._emergency_reschedule(current_schedule)
        elif reason == "delay":
            rescheduled = await self._delay_reschedule(current_schedule)
        elif reason == "priority_change":
            rescheduled = await self._priority_reschedule(current_schedule)
        else:
            rescheduled = await self._general_reschedule(current_schedule)
        
        return {
            "schedule_id": schedule_id,
            "original_schedule": current_schedule,
            "rescheduled_schedule": rescheduled,
            "reason": reason,
            "changes": await self._analyze_schedule_changes(current_schedule, rescheduled),
            "updated_at": datetime.now().isoformat()
        }
    
    async def _optimize_schedule(self, user_id: int, schedule_id: str) -> Dict[str, Any]:
        """
        일정을 최적화합니다.
        
        Args:
            user_id (int): 사용자 ID
            schedule_id (str): 최적화할 일정 ID
            
        Returns:
            Dict[str, Any]: 최적화된 일정 정보
        """
        current_schedule = await self._get_schedule(schedule_id)
        user_preferences = await self._get_user_preferences(user_id)
        
        # 최적화 알고리즘 적용
        optimized = await self._apply_optimization_algorithm(current_schedule, user_preferences)
        
        return {
            "schedule_id": schedule_id,
            "original_schedule": current_schedule,
            "optimized_schedule": optimized,
            "improvements": await self._calculate_improvements(current_schedule, optimized),
            "optimized_at": datetime.now().isoformat()
        }
    
    async def _add_task_to_schedule(self, user_id: int, task: Dict[str, Any], schedule_id: str) -> Dict[str, Any]:
        """
        기존 일정에 새로운 작업을 추가합니다.
        
        Args:
            user_id (int): 사용자 ID
            task (Dict[str, Any]): 추가할 작업 정보
            schedule_id (str): 일정 ID
            
        Returns:
            Dict[str, Any]: 업데이트된 일정 정보
        """
        current_schedule = await self._get_schedule(schedule_id)
        
        # 작업을 적절한 시간대에 삽입
        updated_schedule = await self._insert_task_into_schedule(current_schedule, task)
        
        return {
            "schedule_id": schedule_id,
            "added_task": task,
            "updated_schedule": updated_schedule,
            "insertion_point": await self._find_insertion_point(current_schedule, task),
            "updated_at": datetime.now().isoformat()
        }
    
    async def _prioritize_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """작업들을 우선순위에 따라 정렬합니다."""
        # 우선순위 계산 로직 (마감일, 중요도, 예상 소요시간 등 고려)
        for task in tasks:
            task["priority_score"] = await self._calculate_task_priority(task)
        
        return sorted(tasks, key=lambda x: x["priority_score"], reverse=True)
    
    async def _get_user_constraints(self, user_id: int) -> Dict[str, Any]:
        """사용자의 제약조건을 조회합니다."""
        return {
            "working_hours": {"start": "09:00", "end": "18:00"},
            "break_times": ["12:00-13:00", "15:00-15:15"],
            "preferred_work_style": "focused_blocks",
            "max_continuous_work": 120  # 분
        }
    
    async def _allocate_time_blocks(self, tasks: List[Dict[str, Any]], constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """작업들을 시간 블록으로 할당합니다."""
        blocks = []
        current_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        for task in tasks:
            duration = task.get("estimated_duration", 60)  # 기본 60분
            block = {
                "task_id": task["id"],
                "title": task["title"],
                "start_time": current_time.isoformat(),
                "end_time": (current_time + timedelta(minutes=duration)).isoformat(),
                "duration": duration,
                "priority": task["priority_score"]
            }
            blocks.append(block)
            current_time += timedelta(minutes=duration + 15)  # 15분 휴식 시간
        
        return blocks
    
    async def _optimize_time_allocation(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """시간 할당을 최적화합니다."""
        # 실제 구현에서는 더 복잡한 최적화 알고리즘 사용
        return blocks
    
    async def _calculate_efficiency_score(self, schedule: List[Dict[str, Any]]) -> float:
        """일정의 효율성 점수를 계산합니다."""
        # 실제 구현에서는 다양한 요소를 고려한 점수 계산
        return 85.5
    
    async def _get_schedule(self, schedule_id: str) -> Dict[str, Any]:
        """일정 정보를 조회합니다."""
        # 실제 구현에서는 데이터베이스에서 조회
        return {"id": schedule_id, "blocks": []}
    
    async def _emergency_reschedule(self, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """긴급 상황에 대한 일정 재조정"""
        return schedule
    
    async def _delay_reschedule(self, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """지연에 대한 일정 재조정"""
        return schedule
    
    async def _priority_reschedule(self, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """우선순위 변경에 대한 일정 재조정"""
        return schedule
    
    async def _general_reschedule(self, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """일반적인 일정 재조정"""
        return schedule
    
    async def _analyze_schedule_changes(self, original: Dict[str, Any], updated: Dict[str, Any]) -> List[str]:
        """일정 변경사항을 분석합니다."""
        return ["시간 조정", "우선순위 변경"]
    
    async def _get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """사용자 선호도를 조회합니다."""
        return {
            "focus_time_preference": "morning",
            "break_frequency": 90,  # 분
            "work_style": "deep_work"
        }
    
    async def _apply_optimization_algorithm(self, schedule: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """최적화 알고리즘을 적용합니다."""
        return schedule
    
    async def _calculate_improvements(self, original: Dict[str, Any], optimized: Dict[str, Any]) -> Dict[str, Any]:
        """최적화 개선사항을 계산합니다."""
        return {
            "efficiency_gain": 12.5,
            "time_saved": 30,  # 분
            "stress_reduction": 8.2
        }
    
    async def _insert_task_into_schedule(self, schedule: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """일정에 작업을 삽입합니다."""
        return schedule
    
    async def _find_insertion_point(self, schedule: Dict[str, Any], task: Dict[str, Any]) -> str:
        """작업 삽입 지점을 찾습니다."""
        return "afternoon"
    
    async def _calculate_task_priority(self, task: Dict[str, Any]) -> float:
        """작업 우선순위를 계산합니다."""
        # 마감일, 중요도, 예상 소요시간 등을 고려한 점수 계산
        return 7.5
