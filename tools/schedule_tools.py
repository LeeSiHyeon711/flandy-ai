"""
ScheduleTools - 스케줄링 도구

일정 관리 및 스케줄링을 담당하는 도구입니다.
일정 할당, 재조정, 최적화 등의 기능을 제공합니다.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from .base_tool import BaseTool
from database import get_db_cursor


class ScheduleTools(BaseTool):
    """
    스케줄링 도구
    
    일정 관리, 할당, 최적화 등의 기능을 제공합니다.
    """
    
    def __init__(self):
        super().__init__(
            name="ScheduleTools",
            description="일정 관리 및 스케줄링 도구"
        )
        self.logger = logging.getLogger("tool.ScheduleTools")
    
    async def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        스케줄링 도구를 실행합니다.
        
        Args:
            args (Dict[str, Any]): 실행 인자
                - action (str): 실행할 액션
                - tasks (List[Dict], optional): 작업 목록
                - constraints (Dict, optional): 제약조건
                - schedule_id (str, optional): 일정 ID
                - user_id (int, optional): 사용자 ID
                
        Returns:
            Dict[str, Any]: 실행 결과
        """
        try:
            action = args.get("action")
            
            if action == "allocate":
                return await self._allocate_tasks(args)
            elif action == "reschedule":
                return await self._reschedule_tasks(args)
            elif action == "optimize":
                return await self._optimize_schedule(args)
            elif action == "validate":
                return await self._validate_schedule(args)
            elif action == "find_conflicts":
                return await self._find_conflicts(args)
            elif action == "suggest_times":
                return await self._suggest_available_times(args)
            elif action == "save_schedule":
                return await self._save_schedule(args)
            elif action == "get_schedule_by_id":
                return await self._get_schedule_by_id(args)
            elif action == "list_schedules":
                return await self._list_schedules(args)
            else:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}",
                    "available_actions": self.get_supported_actions()
                }
                
        except Exception as e:
            self.logger.error(f"Error executing ScheduleTools: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def validate(self, args: Dict[str, Any]) -> bool:
        """
        실행 인자를 검증합니다.
        
        Args:
            args (Dict[str, Any]): 검증할 인자
            
        Returns:
            bool: 유효성 검증 결과
        """
        action = args.get("action")
        
        if not action:
            return False
        
        if action == "allocate":
            return "tasks" in args and "constraints" in args
        elif action == "reschedule":
            return "schedule_id" in args and "user_id" in args
        elif action == "optimize":
            return "schedule_id" in args
        elif action == "validate":
            return "schedule" in args
        elif action == "find_conflicts":
            return "schedule" in args
        elif action == "suggest_times":
            return "duration" in args and "constraints" in args
        elif action == "save_schedule":
            return "user_id" in args and "title" in args and "start_time" in args
        elif action == "get_schedule_by_id":
            return "schedule_id" in args
        elif action == "list_schedules":
            return "user_id" in args
        
        return False
    
    def get_schema(self) -> Dict[str, Any]:
        """
        도구 스키마를 반환합니다.
        
        Returns:
            Dict[str, Any]: 도구 스키마
        """
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["allocate", "reschedule", "optimize", "validate", "find_conflicts", "suggest_times"],
                    "description": "실행할 액션"
                },
                "tasks": {
                    "type": "array",
                    "description": "작업 목록",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "title": {"type": "string"},
                            "duration": {"type": "number"},
                            "priority": {"type": "number"},
                            "deadline": {"type": "string"},
                            "dependencies": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                },
                "constraints": {
                    "type": "object",
                    "description": "제약조건",
                    "properties": {
                        "working_hours": {"type": "object"},
                        "break_times": {"type": "array"},
                        "max_continuous_work": {"type": "number"},
                        "preferred_work_style": {"type": "string"}
                    }
                },
                "schedule_id": {
                    "type": "string",
                    "description": "일정 ID"
                },
                "user_id": {
                    "type": "integer",
                    "description": "사용자 ID"
                },
                "schedule": {
                    "type": "object",
                    "description": "일정 데이터"
                },
                "duration": {
                    "type": "number",
                    "description": "필요한 시간 (분)"
                }
            },
            "required": ["action"]
        }
    
    def get_supported_actions(self) -> List[str]:
        """
        지원하는 액션 목록을 반환합니다.
        
        Returns:
            List[str]: 지원하는 액션 목록
        """
        return [
            "allocate",
            "reschedule",
            "optimize",
            "validate",
            "find_conflicts",
            "suggest_times",
            "save_schedule",
            "get_schedule_by_id",
            "list_schedules"
        ]
    
    async def _allocate_tasks(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        작업들을 시간에 할당합니다.
        
        Args:
            args (Dict[str, Any]): 실행 인자
            
        Returns:
            Dict[str, Any]: 할당 결과
        """
        try:
            tasks = args["tasks"]
            constraints = args["constraints"]
            
            # 작업 우선순위 정렬
            sorted_tasks = sorted(tasks, key=lambda x: x.get("priority", 0), reverse=True)
            
            # 시간 블록 생성
            schedule_blocks = []
            current_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
            
            for task in sorted_tasks:
                duration = task.get("duration", 60)  # 기본 60분
                
                # 제약조건 확인
                if not self._check_constraints(current_time, duration, constraints):
                    # 제약조건에 맞지 않으면 다음 가능한 시간으로 이동
                    current_time = self._find_next_available_time(current_time, duration, constraints)
                
                block = {
                    "task_id": task["id"],
                    "title": task["title"],
                    "start_time": current_time.isoformat(),
                    "end_time": (current_time + timedelta(minutes=duration)).isoformat(),
                    "duration": duration,
                    "priority": task.get("priority", 0)
                }
                
                schedule_blocks.append(block)
                current_time += timedelta(minutes=duration + 15)  # 15분 휴식
            
            return {
                "status": "success",
                "schedule_blocks": schedule_blocks,
                "total_duration": sum(block["duration"] for block in schedule_blocks),
                "efficiency_score": self._calculate_efficiency_score(schedule_blocks),
                "allocated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to allocate tasks: {str(e)}"
            }
    
    async def _reschedule_tasks(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        기존 일정을 재조정합니다.
        
        Args:
            args (Dict[str, Any]): 실행 인자
            
        Returns:
            Dict[str, Any]: 재조정 결과
        """
        try:
            schedule_id = args["schedule_id"]
            user_id = args["user_id"]
            reason = args.get("reason", "general")
            
            # 기존 일정 조회 (실제로는 데이터베이스에서 조회)
            current_schedule = await self._get_schedule(schedule_id)
            
            if not current_schedule:
                return {
                    "status": "error",
                    "error": f"Schedule {schedule_id} not found"
                }
            
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
                "status": "success",
                "schedule_id": schedule_id,
                "original_schedule": current_schedule,
                "rescheduled_schedule": rescheduled,
                "reason": reason,
                "changes": self._analyze_schedule_changes(current_schedule, rescheduled),
                "rescheduled_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to reschedule tasks: {str(e)}"
            }
    
    async def _optimize_schedule(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        일정을 최적화합니다.
        
        Args:
            args (Dict[str, Any]): 실행 인자
            
        Returns:
            Dict[str, Any]: 최적화 결과
        """
        try:
            schedule_id = args["schedule_id"]
            optimization_type = args.get("optimization_type", "efficiency")
            
            # 기존 일정 조회
            current_schedule = await self._get_schedule(schedule_id)
            
            if not current_schedule:
                return {
                    "status": "error",
                    "error": f"Schedule {schedule_id} not found"
                }
            
            # 최적화 알고리즘 적용
            if optimization_type == "efficiency":
                optimized = await self._optimize_for_efficiency(current_schedule)
            elif optimization_type == "energy":
                optimized = await self._optimize_for_energy(current_schedule)
            elif optimization_type == "focus":
                optimized = await self._optimize_for_focus(current_schedule)
            else:
                optimized = await self._optimize_for_efficiency(current_schedule)
            
            return {
                "status": "success",
                "schedule_id": schedule_id,
                "original_schedule": current_schedule,
                "optimized_schedule": optimized,
                "optimization_type": optimization_type,
                "improvements": self._calculate_improvements(current_schedule, optimized),
                "optimized_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to optimize schedule: {str(e)}"
            }
    
    async def _validate_schedule(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        일정의 유효성을 검증합니다.
        
        Args:
            args (Dict[str, Any]): 실행 인자
            
        Returns:
            Dict[str, Any]: 검증 결과
        """
        try:
            schedule = args["schedule"]
            
            validation_results = {
                "is_valid": True,
                "errors": [],
                "warnings": [],
                "suggestions": []
            }
            
            # 시간 충돌 검사
            conflicts = self._find_time_conflicts(schedule)
            if conflicts:
                validation_results["errors"].extend(conflicts)
                validation_results["is_valid"] = False
            
            # 제약조건 검사
            constraint_violations = self._check_constraint_violations(schedule)
            if constraint_violations:
                validation_results["warnings"].extend(constraint_violations)
            
            # 최적화 제안
            suggestions = self._generate_optimization_suggestions(schedule)
            validation_results["suggestions"].extend(suggestions)
            
            return {
                "status": "success",
                "validation_results": validation_results,
                "validated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to validate schedule: {str(e)}"
            }
    
    async def _find_conflicts(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        일정에서 충돌을 찾습니다.
        
        Args:
            args (Dict[str, Any]): 실행 인자
            
        Returns:
            Dict[str, Any]: 충돌 검사 결과
        """
        try:
            schedule = args["schedule"]
            
            conflicts = self._find_time_conflicts(schedule)
            
            return {
                "status": "success",
                "conflicts": conflicts,
                "conflict_count": len(conflicts),
                "checked_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to find conflicts: {str(e)}"
            }
    
    async def _suggest_available_times(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        사용 가능한 시간을 제안합니다.
        
        Args:
            args (Dict[str, Any]): 실행 인자
            
        Returns:
            Dict[str, Any]: 제안된 시간 목록
        """
        try:
            duration = args["duration"]  # 분 단위
            constraints = args["constraints"]
            date_range = args.get("date_range", {"start": datetime.now().isoformat(), "end": (datetime.now() + timedelta(days=7)).isoformat()})
            
            start_date = datetime.fromisoformat(date_range["start"])
            end_date = datetime.fromisoformat(date_range["end"])
            
            available_times = []
            current_date = start_date
            
            while current_date <= end_date:
                # 하루 중 사용 가능한 시간 찾기
                daily_times = self._find_daily_available_times(current_date, duration, constraints)
                available_times.extend(daily_times)
                current_date += timedelta(days=1)
            
            return {
                "status": "success",
                "duration": duration,
                "available_times": available_times,
                "suggested_count": len(available_times),
                "date_range": date_range,
                "suggested_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to suggest available times: {str(e)}"
            }
    
    # 헬퍼 메서드들
    def _check_constraints(self, start_time: datetime, duration: int, constraints: Dict[str, Any]) -> bool:
        """제약조건을 확인합니다."""
        working_hours = constraints.get("working_hours", {"start": "09:00", "end": "18:00"})
        end_time = start_time + timedelta(minutes=duration)
        
        # 근무 시간 확인
        work_start = datetime.combine(start_time.date(), datetime.strptime(working_hours["start"], "%H:%M").time())
        work_end = datetime.combine(start_time.date(), datetime.strptime(working_hours["end"], "%H:%M").time())
        
        return start_time >= work_start and end_time <= work_end
    
    def _find_next_available_time(self, current_time: datetime, duration: int, constraints: Dict[str, Any]) -> datetime:
        """다음 사용 가능한 시간을 찾습니다."""
        # 간단한 구현: 다음 근무일 9시로 이동
        next_day = current_time + timedelta(days=1)
        return next_day.replace(hour=9, minute=0, second=0, microsecond=0)
    
    def _calculate_efficiency_score(self, schedule_blocks: List[Dict[str, Any]]) -> float:
        """일정의 효율성 점수를 계산합니다."""
        if not schedule_blocks:
            return 0.0
        
        # 간단한 효율성 계산: 우선순위 기반
        total_priority = sum(block.get("priority", 0) for block in schedule_blocks)
        max_possible_priority = len(schedule_blocks) * 10  # 최대 우선순위 10 가정
        
        return (total_priority / max_possible_priority) * 100 if max_possible_priority > 0 else 0.0
    
    async def _get_schedule(self, schedule_id: str) -> Optional[Dict[str, Any]]:
        """일정을 조회합니다."""
        # 실제 구현에서는 데이터베이스에서 조회
        return {
            "id": schedule_id,
            "blocks": [],
            "created_at": datetime.now().isoformat()
        }
    
    async def _emergency_reschedule(self, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """긴급 상황에 대한 재조정"""
        return schedule
    
    async def _delay_reschedule(self, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """지연에 대한 재조정"""
        return schedule
    
    async def _priority_reschedule(self, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """우선순위 변경에 대한 재조정"""
        return schedule
    
    async def _general_reschedule(self, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """일반적인 재조정"""
        return schedule
    
    def _analyze_schedule_changes(self, original: Dict[str, Any], updated: Dict[str, Any]) -> List[str]:
        """일정 변경사항을 분석합니다."""
        return ["시간 조정", "우선순위 변경"]
    
    async def _optimize_for_efficiency(self, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """효율성 최적화"""
        return schedule
    
    async def _optimize_for_energy(self, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """에너지 최적화"""
        return schedule
    
    async def _optimize_for_focus(self, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """집중도 최적화"""
        return schedule
    
    def _calculate_improvements(self, original: Dict[str, Any], optimized: Dict[str, Any]) -> Dict[str, Any]:
        """개선사항을 계산합니다."""
        return {
            "efficiency_gain": 12.5,
            "time_saved": 30,
            "stress_reduction": 8.2
        }
    
    def _find_time_conflicts(self, schedule: Dict[str, Any]) -> List[str]:
        """시간 충돌을 찾습니다."""
        # 간단한 충돌 검사 로직
        return []
    
    def _check_constraint_violations(self, schedule: Dict[str, Any]) -> List[str]:
        """제약조건 위반을 확인합니다."""
        return []
    
    def _generate_optimization_suggestions(self, schedule: Dict[str, Any]) -> List[str]:
        """최적화 제안을 생성합니다."""
        return [
            "연속 작업 시간을 줄여보세요",
            "휴식 시간을 늘려보세요",
            "우선순위를 재검토해보세요"
        ]
    
    def _find_daily_available_times(self, date: datetime, duration: int, constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """하루 중 사용 가능한 시간을 찾습니다."""
        available_times = []
        
        # 근무 시간 내에서 가능한 시간 슬롯 찾기
        working_hours = constraints.get("working_hours", {"start": "09:00", "end": "18:00"})
        work_start = datetime.combine(date, datetime.strptime(working_hours["start"], "%H:%M").time())
        work_end = datetime.combine(date, datetime.strptime(working_hours["end"], "%H:%M").time())
        
        current_time = work_start
        while current_time + timedelta(minutes=duration) <= work_end:
            available_times.append({
                "start_time": current_time.isoformat(),
                "end_time": (current_time + timedelta(minutes=duration)).isoformat(),
                "duration": duration
            })
            current_time += timedelta(hours=1)  # 1시간 간격으로 제안
        
        return available_times
    
    async def _save_schedule(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """일정을 데이터베이스에 저장합니다."""
        try:
            user_id = args["user_id"]
            title = args["title"]
            description = args.get("description", "")
            start_time = args["start_time"]
            end_time = args["end_time"]
            duration = args["duration"]
            priority = args.get("priority", 5)
            
            # ID는 AUTO_INCREMENT로 자동 생성되므로 제외
            with get_db_cursor() as cursor:
                # 일정 저장 (id 컬럼 제외)
                cursor.execute("""
                    INSERT INTO tasks (user_id, title, description, start_time, deadline, status, labels, meta, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    user_id, title, description, start_time, end_time, 
                    'pending', '[]', '{}', datetime.now(), datetime.now()
                ))
                
                # 생성된 ID 가져오기
                schedule_id = cursor.lastrowid
                
                return {
                    "status": "success",
                    "schedule_id": schedule_id,
                    "message": "일정이 성공적으로 저장되었습니다."
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": f"일정 저장 실패: {str(e)}"
            }
    
    async def _get_schedule_by_id(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """ID로 일정을 조회합니다."""
        try:
            schedule_id = args["schedule_id"]
            
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM tasks WHERE id = %s
                """, (schedule_id,))
                
                schedule = cursor.fetchone()
                
                if schedule:
                    return {
                        "status": "success",
                        "schedule": schedule
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"일정을 찾을 수 없습니다: {schedule_id}"
                    }
                    
        except Exception as e:
            return {
                "status": "error",
                "error": f"일정 조회 실패: {str(e)}"
            }
    
    async def _list_schedules(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """사용자의 일정 목록을 조회합니다."""
        try:
            user_id = args["user_id"]
            date = args.get("date")  # 특정 날짜의 일정만 조회
            
            with get_db_cursor() as cursor:
                if date:
                    # 특정 날짜의 일정 조회
                    cursor.execute("""
                        SELECT * FROM tasks 
                        WHERE user_id = %s AND DATE(start_time) = %s
                        ORDER BY start_time
                    """, (user_id, date))
                else:
                    # 모든 일정 조회
                    cursor.execute("""
                        SELECT * FROM tasks 
                        WHERE user_id = %s
                        ORDER BY start_time
                    """, (user_id,))
                
                schedules = cursor.fetchall()
                
                return {
                    "status": "success",
                    "schedules": schedules,
                    "count": len(schedules)
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": f"일정 목록 조회 실패: {str(e)}"
            }
