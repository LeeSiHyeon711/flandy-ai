"""
SupervisorAgent - 중앙 조정자

전체 시스템의 중앙 조정 및 의사결정을 담당하는 에이전트입니다.
다른 에이전트들의 작업을 조율하고 우선순위를 결정합니다.
"""

from typing import Dict, Any, List
import asyncio
import logging
from .base_agent import BaseAgent, AgentStatus


class SupervisorAgent(BaseAgent):
    """
    중앙 조정자 에이전트
    
    다른 에이전트들을 관리하고 작업을 분배하는 핵심 에이전트입니다.
    """
    
    def __init__(self):
        super().__init__(name="SupervisorAgent", priority=10)
        self.agents = {}  # 등록된 에이전트들
        self.task_queue = asyncio.Queue()
        self.logger = logging.getLogger("agent.SupervisorAgent")
    
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        중앙 조정자로서 전체 시스템을 관리합니다.
        
        Args:
            context (Dict[str, Any]): 처리할 컨텍스트 데이터
            
        Returns:
            Dict[str, Any]: 처리 결과
        """
        self.set_status(AgentStatus.PROCESSING)
        
        try:
            # 1. 컨텍스트 분석
            action = context.get("action", "unknown")
            user_id = context.get("user_id")
            
            self.logger.info(f"Processing action: {action} for user: {user_id}")
            
            # 2. 적절한 에이전트 선택 및 작업 분배
            result = await self._delegate_task(context)
            
            # 3. 결과 통합 및 반환
            return {
                "status": "success",
                "action": action,
                "user_id": user_id,
                "result": result,
                "processed_by": "SupervisorAgent"
            }
            
        except Exception as e:
            self.handle_error(e)
            return {
                "status": "error",
                "error": str(e),
                "processed_by": "SupervisorAgent"
            }
        finally:
            self.set_status(AgentStatus.IDLE)
    
    def can_handle(self, action: str) -> bool:
        """
        SupervisorAgent는 모든 액션을 처리할 수 있습니다.
        
        Args:
            action (str): 처리할 액션 타입
            
        Returns:
            bool: 항상 True
        """
        return True
    
    def get_supported_actions(self) -> List[str]:
        """
        SupervisorAgent가 지원하는 액션 목록을 반환합니다.
        
        Returns:
            List[str]: 지원하는 액션 목록 (모든 액션)
        """
        return ["*"]  # 모든 액션 지원
    
    async def _delegate_task(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        작업을 적절한 에이전트에게 위임합니다.
        
        Args:
            context (Dict[str, Any]): 작업 컨텍스트
            
        Returns:
            Dict[str, Any]: 위임 결과
        """
        action = context.get("action")
        
        # 액션에 따른 에이전트 선택 로직
        if action in ["health_check", "habit_analysis", "health_monitoring"]:
            return await self._delegate_to_health_agent(context)
        elif action in ["schedule_plan", "reschedule", "optimize_schedule"]:
            return await self._delegate_to_plan_agent(context)
        elif action in ["data_analysis", "pattern_analysis", "insights"]:
            return await self._delegate_to_data_agent(context)
        elif action in ["worklife_balance", "balance_analysis", "balance_score"]:
            return await self._delegate_to_worklife_agent(context)
        elif action in ["chat", "communication", "notification"]:
            return await self._delegate_to_communication_agent(context)
        else:
            # 기본적으로 HealthAgent로 시작
            return await self._delegate_to_health_agent(context)
    
    async def _delegate_to_health_agent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """HealthAgent에게 작업 위임"""
        # 실제 구현에서는 HealthAgent 인스턴스를 호출
        return {"delegated_to": "HealthAgent", "context": context}
    
    async def _delegate_to_plan_agent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """PlanAgent에게 작업 위임"""
        return {"delegated_to": "PlanAgent", "context": context}
    
    async def _delegate_to_data_agent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """DataAgent에게 작업 위임"""
        return {"delegated_to": "DataAgent", "context": context}
    
    async def _delegate_to_worklife_agent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """WorkLifeBalanceAgent에게 작업 위임"""
        return {"delegated_to": "WorkLifeBalanceAgent", "context": context}
    
    async def _delegate_to_communication_agent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """CommunicationAgent에게 작업 위임"""
        return {"delegated_to": "CommunicationAgent", "context": context}
    
    def register_agent(self, agent: BaseAgent) -> None:
        """
        에이전트를 등록합니다.
        
        Args:
            agent (BaseAgent): 등록할 에이전트
        """
        self.agents[agent.get_name()] = agent
        self.logger.info(f"Agent {agent.get_name()} registered")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        등록된 모든 에이전트의 상태를 반환합니다.
        
        Returns:
            Dict[str, Any]: 에이전트 상태 정보
        """
        status = {}
        for name, agent in self.agents.items():
            status[name] = agent.get_info()
        return status
