"""
기본 에이전트 클래스

모든 AI 에이전트의 기본 클래스입니다.
에이전트의 공통 기능과 인터페이스를 정의합니다.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum
import logging
import asyncio
from datetime import datetime


class AgentStatus(Enum):
    """에이전트 상태 열거형"""
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    INITIALIZING = "initializing"
    CLEANUP = "cleanup"


class BaseAgent(ABC):
    """
    모든 AI 에이전트의 기본 클래스
    
    Attributes:
        name (str): 에이전트 이름
        status (AgentStatus): 현재 상태
        priority (int): 우선순위 (높을수록 우선)
        logger (logging.Logger): 로거 인스턴스
        created_at (datetime): 생성 시간
    """
    
    def __init__(self, name: str, priority: int = 1):
        """
        에이전트 초기화
        
        Args:
            name (str): 에이전트 이름
            priority (int): 우선순위 (기본값: 1)
        """
        self.name = name
        self.priority = priority
        self.status = AgentStatus.INITIALIZING
        self.created_at = datetime.now()
        
        # 로거 설정
        self.logger = logging.getLogger(f"agent.{name}")
        self.logger.setLevel(logging.INFO)
        
        # 에이전트 초기화
        self.initialize()
    
    @abstractmethod
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        에이전트가 주어진 컨텍스트를 처리합니다.
        
        Args:
            context (Dict[str, Any]): 처리할 컨텍스트 데이터
            
        Returns:
            Dict[str, Any]: 처리 결과
            
        Raises:
            NotImplementedError: 하위 클래스에서 구현해야 함
        """
        raise NotImplementedError("Subclasses must implement process method")
    
    @abstractmethod
    def can_handle(self, action: str) -> bool:
        """
        에이전트가 특정 액션을 처리할 수 있는지 확인합니다.
        
        Args:
            action (str): 처리할 액션 타입
            
        Returns:
            bool: 처리 가능 여부
            
        Raises:
            NotImplementedError: 하위 클래스에서 구현해야 함
        """
        raise NotImplementedError("Subclasses must implement can_handle method")
    
    def get_status(self) -> AgentStatus:
        """
        에이전트의 현재 상태를 반환합니다.
        
        Returns:
            AgentStatus: 현재 상태
        """
        return self.status
    
    def get_priority(self) -> int:
        """
        에이전트의 우선순위를 반환합니다.
        
        Returns:
            int: 우선순위
        """
        return self.priority
    
    def get_name(self) -> str:
        """
        에이전트 이름을 반환합니다.
        
        Returns:
            str: 에이전트 이름
        """
        return self.name
    
    def handle_error(self, error: Exception) -> None:
        """
        에이전트가 발생시킨 에러를 처리합니다.
        
        Args:
            error (Exception): 발생한 예외
        """
        self.status = AgentStatus.ERROR
        self.logger.error(f"Error in {self.name}: {str(error)}", exc_info=True)
    
    def initialize(self) -> None:
        """
        에이전트를 초기화합니다.
        하위 클래스에서 필요한 초기화 로직을 구현할 수 있습니다.
        """
        self.status = AgentStatus.IDLE
        self.logger.info(f"Agent {self.name} initialized successfully")
    
    def cleanup(self) -> None:
        """
        에이전트를 정리합니다.
        하위 클래스에서 필요한 정리 로직을 구현할 수 있습니다.
        """
        self.status = AgentStatus.CLEANUP
        self.logger.info(f"Agent {self.name} cleaned up successfully")
    
    def set_status(self, status: AgentStatus) -> None:
        """
        에이전트 상태를 설정합니다.
        
        Args:
            status (AgentStatus): 설정할 상태
        """
        self.status = status
        self.logger.debug(f"Agent {self.name} status changed to {status.value}")
    
    def get_info(self) -> Dict[str, Any]:
        """
        에이전트 정보를 반환합니다.
        
        Returns:
            Dict[str, Any]: 에이전트 정보
        """
        return {
            "name": self.name,
            "status": self.status.value,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "can_handle": self.get_supported_actions()
        }
    
    @abstractmethod
    def get_supported_actions(self) -> List[str]:
        """
        에이전트가 지원하는 액션 목록을 반환합니다.
        
        Returns:
            List[str]: 지원하는 액션 목록
            
        Raises:
            NotImplementedError: 하위 클래스에서 구현해야 함
        """
        raise NotImplementedError("Subclasses must implement get_supported_actions method")
    
    def __str__(self) -> str:
        """문자열 표현"""
        return f"{self.__class__.__name__}(name='{self.name}', status='{self.status.value}')"
    
    def __repr__(self) -> str:
        """객체 표현"""
        return f"{self.__class__.__name__}(name='{self.name}', priority={self.priority}, status='{self.status.value}')"
