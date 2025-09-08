"""
Plandy AI Graph - LangGraph 기반 그래프 구조

에이전트들 간의 워크플로우를 정의하고 관리합니다.
"""

from typing import Dict, Any, List
import logging
from datetime import datetime
import os

# LangGraph 임포트 (실제 구현에서는 설치 필요)
try:
    from langgraph.graph import StateGraph, START, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("Warning: LangGraph not available. Using mock implementation.")

from models import State, Task
from agents.nodes import (
    health_node,
    plan_node,
    data_node,
    worklife_node,
    communication_node,
    supervisor_node,
    supervisor_router
)


class PlandyAIGraph:
    """
    Plandy AI 그래프 클래스
    
    LangGraph 기반의 에이전트 워크플로우를 관리합니다.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("graph.plandy_ai")
        self.graph = None
        self._build_graph()
    
    def _build_graph(self):
        """그래프를 구성합니다."""
        if LANGGRAPH_AVAILABLE:
            self._build_langgraph()
        else:
            self._build_mock_graph()
    
    def _build_langgraph(self):
        """LangGraph를 사용하여 그래프를 구성합니다."""
        try:
            # 상태 그래프 빌더 생성
            graph_builder = StateGraph(State)
            
            # 노드 추가
            graph_builder.add_node("supervisor", supervisor_node)
            graph_builder.add_node("health_agent", health_node)
            graph_builder.add_node("plan_agent", plan_node)
            graph_builder.add_node("data_agent", data_node)
            graph_builder.add_node("worklife_balance_agent", worklife_node)
            graph_builder.add_node("communication_agent", communication_node)
            
            # 엣지 추가
            graph_builder.add_edge(START, "supervisor")
            
            # Supervisor에서 다른 에이전트들로의 조건부 엣지
            graph_builder.add_conditional_edges(
                "supervisor",
                supervisor_router,
                {
                    "health_agent": "health_agent",
                    "plan_agent": "plan_agent",
                    "data_agent": "data_agent",
                    "worklife_balance_agent": "worklife_balance_agent",
                    "communication_agent": "communication_agent"
                }
            )
            
            # 에이전트들 간의 연결
            graph_builder.add_edge("health_agent", "plan_agent")
            graph_builder.add_edge("plan_agent", "worklife_balance_agent")
            graph_builder.add_edge("data_agent", "worklife_balance_agent")
            graph_builder.add_edge("worklife_balance_agent", "communication_agent")
            graph_builder.add_edge("communication_agent", END)
            
            # 그래프 컴파일
            self.graph = graph_builder.compile()
            
            self.logger.info("LangGraph-based graph built successfully")
            
        except Exception as e:
            self.logger.error(f"Error building LangGraph: {str(e)}")
            self._build_mock_graph()
    
    def _build_mock_graph(self):
        """LangGraph가 없을 때 사용하는 모의 그래프를 구성합니다."""
        self.logger.warning("Using mock graph implementation")
        self.graph = MockGraph()
    
    async def invoke(self, state: State) -> State:
        """
        그래프를 실행합니다.
        
        Args:
            state (State): 초기 상태
            
        Returns:
            State: 실행 결과 상태
        """
        try:
            self.logger.info("Starting graph execution")
            result = await self.graph.invoke(state)
            self.logger.info("Graph execution completed")
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing graph: {str(e)}")
            # 에러 상태 반환
            return {
                **state,
                "error_messages": [f"Graph execution error: {str(e)}"],
                "system_status": "error"
            }
    
    async def astream(self, state: State):
        """
        그래프를 stream 방식으로 실행합니다.
        
        Args:
            state (State): 초기 상태
            
        Yields:
            Dict[str, State]: 노드별 결과
        """
        try:
            self.logger.info("Starting graph execution (stream)")
            async for chunk in self.graph.astream(state):
                yield chunk
            self.logger.info("Graph execution completed (stream)")
            
        except Exception as e:
            self.logger.error(f"Error executing graph (stream): {str(e)}")
            yield {"error": {
                **state,
                "error_messages": [f"Graph execution error: {str(e)}"],
                "system_status": "error"
            }}
    
    def get_graph_info(self) -> Dict[str, Any]:
        """
        그래프 정보를 반환합니다.
        
        Returns:
            Dict[str, Any]: 그래프 정보
        """
        if LANGGRAPH_AVAILABLE and hasattr(self.graph, 'get_graph'):
            try:
                graph_info = self.graph.get_graph()
                return {
                    "type": "langgraph",
                    "nodes": list(graph_info.nodes.keys()),
                    "edges": [(edge.source, edge.target) for edge in graph_info.edges],
                    "available": True
                }
            except Exception as e:
                self.logger.error(f"Error getting graph info: {str(e)}")
        
        return {
            "type": "mock",
            "nodes": ["supervisor", "health_agent", "plan_agent", "data_agent", "worklife_balance_agent", "communication_agent"],
            "edges": [
                ("supervisor", "health_agent"),
                ("supervisor", "plan_agent"),
                ("supervisor", "data_agent"),
                ("supervisor", "worklife_balance_agent"),
                ("supervisor", "communication_agent"),
                ("health_agent", "plan_agent"),
                ("plan_agent", "worklife_balance_agent"),
                ("data_agent", "worklife_balance_agent"),
                ("worklife_balance_agent", "communication_agent")
            ],
            "available": True
        }
    
    def save_graph_diagram(self, file_path: str = None) -> str:
        """
        그래프 다이어그램을 저장합니다.
        
        Args:
            file_path (str): 저장할 파일 경로
            
        Returns:
            str: 저장된 파일 경로
        """
        if not file_path:
            file_path = f"plandy_ai_graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mmd"
        
        try:
            if LANGGRAPH_AVAILABLE and hasattr(self.graph, 'get_graph'):
                # Mermaid 다이어그램 생성
                mermaid_code = self.graph.get_graph().draw_mermaid()
            else:
                # 모의 Mermaid 다이어그램 생성
                mermaid_code = self._generate_mock_mermaid()
            
            # 파일 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(mermaid_code)
            
            self.logger.info(f"Graph diagram saved to: {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"Error saving graph diagram: {str(e)}")
            return ""
    
    def _generate_mock_mermaid(self) -> str:
        """모의 Mermaid 다이어그램을 생성합니다."""
        return """
graph TD
    START([Start]) --> SUPERVISOR[Supervisor Agent]
    
    SUPERVISOR --> HEALTH{Health Agent}
    SUPERVISOR --> PLAN{Plan Agent}
    SUPERVISOR --> DATA{Data Agent}
    SUPERVISOR --> WORKLIFE{WorkLife Balance Agent}
    SUPERVISOR --> COMMUNICATION{Communication Agent}
    
    HEALTH --> PLAN
    PLAN --> WORKLIFE
    DATA --> WORKLIFE
    WORKLIFE --> COMMUNICATION
    
    COMMUNICATION --> END([End])
    
    classDef supervisor fill:#ff9999
    classDef health fill:#99ccff
    classDef plan fill:#99ff99
    classDef data fill:#ffcc99
    classDef worklife fill:#cc99ff
    classDef communication fill:#ffff99
    
    class SUPERVISOR supervisor
    class HEALTH health
    class PLAN plan
    class DATA data
    class WORKLIFE worklife
    class COMMUNICATION communication
        """


class MockGraph:
    """
    LangGraph가 없을 때 사용하는 모의 그래프 클래스
    """
    
    def __init__(self):
        self.logger = logging.getLogger("graph.mock")
    
    async def invoke(self, state: State) -> State:
        """
        모의 그래프 실행
        
        Args:
            state (State): 초기 상태
            
        Returns:
            State: 실행 결과 상태
        """
        self.logger.info("Executing mock graph")
        
        try:
            # Supervisor 노드 실행
            state = supervisor_node(state)
            
            # 현재 작업에 따라 적절한 에이전트 실행
            current_task = state.get("current_task")
            if current_task:
                agent = current_task.agent
                
                if agent == "health_agent":
                    state = await health_node(state)
                elif agent == "plan_agent":
                    state = await plan_node(state)
                elif agent == "data_agent":
                    state = await data_node(state)
                elif agent == "worklife_balance_agent":
                    state = await worklife_node(state)
                elif agent == "communication_agent":
                    state = await communication_node(state)
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error in mock graph execution: {str(e)}")
            return {
                **state,
                "error_messages": [f"Mock graph execution error: {str(e)}"],
                "system_status": "error"
            }
    
    async def astream(self, state: State):
        """
        Mock 그래프를 stream 방식으로 실행합니다.
        
        Args:
            state (State): 초기 상태
            
        Yields:
            Dict[str, State]: 노드별 결과
        """
        try:
            self.logger.info("Executing mock graph (stream)")
            
            # Supervisor 노드 실행
            state = supervisor_node(state)
            yield {"supervisor": state}
            
            # 현재 작업에 따라 적절한 에이전트 실행
            current_task = state.get("current_task")
            if current_task:
                agent = current_task.agent
                
                if agent == "health_agent":
                    state = await health_node(state)
                    yield {"health_agent": state}
                elif agent == "plan_agent":
                    state = await plan_node(state)
                    yield {"plan_agent": state}
                elif agent == "data_agent":
                    state = await data_node(state)
                    yield {"data_agent": state}
                elif agent == "worklife_balance_agent":
                    state = await worklife_node(state)
                    yield {"worklife_balance_agent": state}
                elif agent == "communication_agent":
                    state = await communication_node(state)
                    yield {"communication_agent": state}
            
        except Exception as e:
            self.logger.error(f"Error in mock graph stream execution: {str(e)}")
            yield {"error": state}


# 전역 그래프 인스턴스
plandy_ai_graph = PlandyAIGraph()
