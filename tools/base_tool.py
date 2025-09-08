"""
기본 도구 클래스

모든 도구의 기본 클래스입니다.
도구의 공통 기능과 인터페이스를 정의합니다.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime


class BaseTool(ABC):
    """
    모든 도구의 기본 클래스
    
    Attributes:
        name (str): 도구 이름
        description (str): 도구 설명
        logger (logging.Logger): 로거 인스턴스
        created_at (datetime): 생성 시간
        is_available (bool): 사용 가능 여부
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        도구 초기화
        
        Args:
            name (str): 도구 이름
            description (str): 도구 설명
        """
        self.name = name
        self.description = description
        self.created_at = datetime.now()
        self.is_available = True
        
        # 로거 설정
        self.logger = logging.getLogger(f"tool.{name}")
        self.logger.setLevel(logging.INFO)
        
        # 도구 초기화
        self.initialize()
    
    @abstractmethod
    async def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        도구를 실행합니다.
        
        Args:
            args (Dict[str, Any]): 실행에 필요한 인자들
            
        Returns:
            Dict[str, Any]: 실행 결과
            
        Raises:
            NotImplementedError: 하위 클래스에서 구현해야 함
        """
        raise NotImplementedError("Subclasses must implement execute method")
    
    @abstractmethod
    def validate(self, args: Dict[str, Any]) -> bool:
        """
        도구 실행에 필요한 인자들이 유효한지 검증합니다.
        
        Args:
            args (Dict[str, Any]): 검증할 인자들
            
        Returns:
            bool: 유효성 검증 결과
            
        Raises:
            NotImplementedError: 하위 클래스에서 구현해야 함
        """
        raise NotImplementedError("Subclasses must implement validate method")
    
    def get_description(self) -> str:
        """
        도구의 설명을 반환합니다.
        
        Returns:
            str: 도구 설명
        """
        return self.description
    
    def get_name(self) -> str:
        """
        도구 이름을 반환합니다.
        
        Returns:
            str: 도구 이름
        """
        return self.name
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        도구 실행에 필요한 인자 스키마를 반환합니다.
        
        Returns:
            Dict[str, Any]: 인자 스키마
            
        Raises:
            NotImplementedError: 하위 클래스에서 구현해야 함
        """
        raise NotImplementedError("Subclasses must implement get_schema method")
    
    def is_available(self) -> bool:
        """
        도구가 사용 가능한지 확인합니다.
        
        Returns:
            bool: 사용 가능 여부
        """
        return self.is_available
    
    def set_availability(self, available: bool) -> None:
        """
        도구의 사용 가능 여부를 설정합니다.
        
        Args:
            available (bool): 사용 가능 여부
        """
        self.is_available = available
        self.logger.info(f"Tool {self.name} availability set to {available}")
    
    def initialize(self) -> None:
        """
        도구를 초기화합니다.
        하위 클래스에서 필요한 초기화 로직을 구현할 수 있습니다.
        """
        self.logger.info(f"Tool {self.name} initialized successfully")
    
    def cleanup(self) -> None:
        """
        도구를 정리합니다.
        하위 클래스에서 필요한 정리 로직을 구현할 수 있습니다.
        """
        self.logger.info(f"Tool {self.name} cleaned up successfully")
    
    def get_info(self) -> Dict[str, Any]:
        """
        도구 정보를 반환합니다.
        
        Returns:
            Dict[str, Any]: 도구 정보
        """
        return {
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "is_available": self.is_available,
            "schema": self.get_schema()
        }
    
    def __str__(self) -> str:
        """문자열 표현"""
        return f"{self.__class__.__name__}(name='{self.name}', available={self.is_available})"
    
    def __repr__(self) -> str:
        """객체 표현"""
        return f"{self.__class__.__name__}(name='{self.name}', description='{self.description}')"
