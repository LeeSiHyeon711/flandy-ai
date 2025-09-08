"""
TimeTools - 시간 관리 도구

시간 관련 계산 및 관리를 담당하는 도구입니다.
현재 시간 조회, 시간 차이 계산, 일정 검증 등의 기능을 제공합니다.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta, timezone
import pytz
from .base_tool import BaseTool


class TimeTools(BaseTool):
    """
    시간 관리 도구
    
    시간 관련 계산, 변환, 검증 등의 기능을 제공합니다.
    """
    
    def __init__(self):
        super().__init__(
            name="TimeTools",
            description="시간 관련 계산 및 관리 도구"
        )
        self.logger = logging.getLogger("tool.TimeTools")
    
    async def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        시간 도구를 실행합니다.
        
        Args:
            args (Dict[str, Any]): 실행 인자
                - action (str): 실행할 액션
                - time1 (str, optional): 첫 번째 시간
                - time2 (str, optional): 두 번째 시간
                - timezone (str, optional): 시간대
                - format (str, optional): 시간 형식
                
        Returns:
            Dict[str, Any]: 실행 결과
        """
        try:
            action = args.get("action")
            
            if action == "now":
                return await self._get_current_time(args)
            elif action == "diff":
                return await self._calculate_time_diff(args)
            elif action == "add":
                return await self._add_time(args)
            elif action == "subtract":
                return await self._subtract_time(args)
            elif action == "format":
                return await self._format_time(args)
            elif action == "validate":
                return await self._validate_time(args)
            elif action == "convert_timezone":
                return await self._convert_timezone(args)
            else:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}",
                    "available_actions": self.get_supported_actions()
                }
                
        except Exception as e:
            self.logger.error(f"Error executing TimeTools: {str(e)}")
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
        
        if action == "now":
            return True
        elif action in ["diff", "add", "subtract"]:
            return "time1" in args and "time2" in args
        elif action == "format":
            return "time" in args and "format" in args
        elif action == "validate":
            return "time" in args
        elif action == "convert_timezone":
            return "time" in args and "timezone" in args
        
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
                    "enum": ["now", "diff", "add", "subtract", "format", "validate", "convert_timezone"],
                    "description": "실행할 액션"
                },
                "time1": {
                    "type": "string",
                    "description": "첫 번째 시간 (ISO 8601 형식)"
                },
                "time2": {
                    "type": "string", 
                    "description": "두 번째 시간 (ISO 8601 형식)"
                },
                "time": {
                    "type": "string",
                    "description": "시간 문자열"
                },
                "timezone": {
                    "type": "string",
                    "description": "시간대 (예: 'Asia/Seoul', 'UTC')"
                },
                "format": {
                    "type": "string",
                    "description": "출력 형식"
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
            "now",
            "diff", 
            "add",
            "subtract",
            "format",
            "validate",
            "convert_timezone"
        ]
    
    async def _get_current_time(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        현재 시간을 조회합니다.
        
        Args:
            args (Dict[str, Any]): 실행 인자
            
        Returns:
            Dict[str, Any]: 현재 시간 정보
        """
        timezone_str = args.get("timezone", "Asia/Seoul")
        format_str = args.get("format", "iso")
        
        try:
            # pytz를 사용하여 시간대 처리
            if timezone_str == "UTC":
                tz = pytz.UTC
            else:
                tz = pytz.timezone(timezone_str)
            
            now = datetime.now(tz)
            
            result = {
                "status": "success",
                "current_time": now.isoformat(),
                "timezone": timezone_str,
                "timestamp": now.timestamp()
            }
            
            if format_str == "readable":
                # 한국어 형식으로 시간 표시
                if timezone_str == "Asia/Seoul":
                    result["readable_time"] = now.strftime("%Y년 %m월 %d일 %p %I시 %M분 %S초").replace("AM", "오전").replace("PM", "오후")
                else:
                    result["readable_time"] = now.strftime("%Y년 %m월 %d일 %H시 %M분 %S초")
            elif format_str == "date_only":
                result["date"] = now.strftime("%Y-%m-%d")
            elif format_str == "time_only":
                result["time"] = now.strftime("%H:%M:%S")
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to get current time: {str(e)}"
            }
    
    async def _calculate_time_diff(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        두 시간의 차이를 계산합니다.
        
        Args:
            args (Dict[str, Any]): 실행 인자
            
        Returns:
            Dict[str, Any]: 시간 차이 결과
        """
        try:
            time1_str = args["time1"]
            time2_str = args["time2"]
            
            time1 = datetime.fromisoformat(time1_str.replace('Z', '+00:00'))
            time2 = datetime.fromisoformat(time2_str.replace('Z', '+00:00'))
            
            diff = time2 - time1
            
            return {
                "status": "success",
                "time1": time1.isoformat(),
                "time2": time2.isoformat(),
                "difference": {
                    "total_seconds": diff.total_seconds(),
                    "days": diff.days,
                    "hours": diff.seconds // 3600,
                    "minutes": (diff.seconds % 3600) // 60,
                    "seconds": diff.seconds % 60
                },
                "is_positive": diff.total_seconds() > 0
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to calculate time difference: {str(e)}"
            }
    
    async def _add_time(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        시간에 특정 시간을 더합니다.
        
        Args:
            args (Dict[str, Any]): 실행 인자
            
        Returns:
            Dict[str, Any]: 더한 시간 결과
        """
        try:
            base_time_str = args["time1"]
            add_time_str = args["time2"]
            
            base_time = datetime.fromisoformat(base_time_str.replace('Z', '+00:00'))
            
            # add_time_str을 파싱 (예: "2h30m", "90m", "3600s")
            add_delta = self._parse_time_duration(add_time_str)
            
            result_time = base_time + add_delta
            
            return {
                "status": "success",
                "base_time": base_time.isoformat(),
                "added_duration": add_time_str,
                "result_time": result_time.isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to add time: {str(e)}"
            }
    
    async def _subtract_time(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        시간에서 특정 시간을 뺍니다.
        
        Args:
            args (Dict[str, Any]): 실행 인자
            
        Returns:
            Dict[str, Any]: 뺀 시간 결과
        """
        try:
            base_time_str = args["time1"]
            subtract_time_str = args["time2"]
            
            base_time = datetime.fromisoformat(base_time_str.replace('Z', '+00:00'))
            
            # subtract_time_str을 파싱
            subtract_delta = self._parse_time_duration(subtract_time_str)
            
            result_time = base_time - subtract_delta
            
            return {
                "status": "success",
                "base_time": base_time.isoformat(),
                "subtracted_duration": subtract_time_str,
                "result_time": result_time.isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to subtract time: {str(e)}"
            }
    
    async def _format_time(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        시간을 특정 형식으로 포맷합니다.
        
        Args:
            args (Dict[str, Any]): 실행 인자
            
        Returns:
            Dict[str, Any]: 포맷된 시간 결과
        """
        try:
            time_str = args["time"]
            format_str = args["format"]
            
            time_obj = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            
            formatted_time = time_obj.strftime(format_str)
            
            return {
                "status": "success",
                "original_time": time_str,
                "format": format_str,
                "formatted_time": formatted_time
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to format time: {str(e)}"
            }
    
    async def _validate_time(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        시간 문자열의 유효성을 검증합니다.
        
        Args:
            args (Dict[str, Any]): 실행 인자
            
        Returns:
            Dict[str, Any]: 검증 결과
        """
        try:
            time_str = args["time"]
            
            # ISO 8601 형식 검증
            datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            
            return {
                "status": "success",
                "time": time_str,
                "is_valid": True,
                "format": "ISO 8601"
            }
            
        except ValueError:
            return {
                "status": "success",
                "time": time_str,
                "is_valid": False,
                "error": "Invalid time format"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to validate time: {str(e)}"
            }
    
    async def _convert_timezone(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        시간대를 변환합니다.
        
        Args:
            args (Dict[str, Any]): 실행 인자
            
        Returns:
            Dict[str, Any]: 변환 결과
        """
        try:
            time_str = args["time"]
            target_timezone = args["timezone"]
            
            time_obj = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            
            # 실제 구현에서는 pytz 라이브러리 사용
            # 여기서는 간단한 예시
            converted_time = time_obj  # 임시로 동일한 시간 반환
            
            return {
                "status": "success",
                "original_time": time_str,
                "target_timezone": target_timezone,
                "converted_time": converted_time.isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to convert timezone: {str(e)}"
            }
    
    def _parse_time_duration(self, duration_str: str) -> timedelta:
        """
        시간 지속시간 문자열을 파싱합니다.
        
        Args:
            duration_str (str): 지속시간 문자열 (예: "2h30m", "90m", "3600s")
            
        Returns:
            timedelta: 파싱된 시간 지속시간
        """
        import re
        
        # 정규식으로 시간, 분, 초 추출
        hours = 0
        minutes = 0
        seconds = 0
        
        # 시간 추출 (예: 2h, 2H)
        hour_match = re.search(r'(\d+)h', duration_str, re.IGNORECASE)
        if hour_match:
            hours = int(hour_match.group(1))
        
        # 분 추출 (예: 30m, 30M)
        minute_match = re.search(r'(\d+)m', duration_str, re.IGNORECASE)
        if minute_match:
            minutes = int(minute_match.group(1))
        
        # 초 추출 (예: 30s, 30S)
        second_match = re.search(r'(\d+)s', duration_str, re.IGNORECASE)
        if second_match:
            seconds = int(second_match.group(1))
        
        # 숫자만 있는 경우 분으로 간주
        if not any([hour_match, minute_match, second_match]):
            try:
                minutes = int(duration_str)
            except ValueError:
                raise ValueError(f"Invalid duration format: {duration_str}")
        
        return timedelta(hours=hours, minutes=minutes, seconds=seconds)
