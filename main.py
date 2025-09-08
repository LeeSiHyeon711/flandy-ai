"""
Plandy AI 에이전트 시스템 메인 실행 파일

LangGraph 기반의 새로운 아키텍처로 구현된 Plandy AI 시스템의 메인 진입점입니다.
"""

import asyncio
import logging
import os
import sys
import time
from typing import Dict, Any
from datetime import datetime
import uuid

# 환경 변수 로드
from dotenv import load_dotenv
load_dotenv()

from models import State, Task
from agents.graph import plandy_ai_graph
from services import prompt_service
from tools import TimeTools, ScheduleTools, FeedbackTools


class PlandyAISystem:
    """
    Plandy AI 시스템 메인 클래스
    
    LangGraph 기반의 에이전트 워크플로우를 관리합니다.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("PlandyAI")
        self.setup_logging()
        
        # 환경 변수 확인
        self.check_environment()
        
        # 도구들 초기화
        self.time_tools = TimeTools()
        self.schedule_tools = ScheduleTools()
        self.feedback_tools = FeedbackTools()
        
        # 그래프 정보 출력
        graph_info = plandy_ai_graph.get_graph_info()
        self.logger.info(f"Graph initialized: {graph_info['type']} with {len(graph_info['nodes'])} nodes")
        
        self.logger.info("Plandy AI 시스템이 초기화되었습니다.")
    
    def detect_user_language(self, user_input: str) -> str:
        """
        사용자 입력에서 언어를 감지합니다.
        
        Args:
            user_input (str): 사용자 입력
            
        Returns:
            str: 감지된 언어
        """
        # 한글 감지
        if any('\uac00' <= char <= '\ud7af' for char in user_input):
            return "한국어"
        
        # 일본어 감지
        if any('\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff' for char in user_input):
            return "일본어"
        
        # 중국어 감지
        if any('\u4e00' <= char <= '\u9fff' for char in user_input):
            return "중국어"
        
        # 기본값: 영어
        return "영어"
    
    def get_user_timezone(self, language: str) -> str:
        """
        언어에 따른 시간대를 반환합니다.
        
        Args:
            language (str): 사용자 언어
            
        Returns:
            str: 시간대
        """
        timezone_map = {
            "한국어": "Asia/Seoul",
            "일본어": "Asia/Tokyo", 
            "중국어": "Asia/Shanghai",
            "영어": "America/New_York"  # 기본값
        }
        return timezone_map.get(language, "UTC")
    
    def setup_logging(self):
        """로깅 설정"""
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        log_file = os.getenv('LOG_FILE', 'plandy_ai.log')
        
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def check_environment(self):
        """환경 변수 확인"""
        required_vars = ['OPENAI_API_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.logger.warning(f"필수 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
            self.logger.warning("env.example 파일을 참고하여 .env 파일을 생성하세요.")
        
        # OpenAI API 키 확인
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key and openai_key != 'your_openai_api_key_here':
            self.logger.info("OpenAI API 키가 설정되었습니다.")
        else:
            self.logger.warning("OpenAI API 키가 설정되지 않았습니다. 일부 기능이 제한될 수 있습니다.")
        
        # 선택적 환경 변수들
        optional_vars = {
            'TAVILY_API_KEY': '웹 검색 기능',
            'DATABASE_URL': '데이터베이스 기능',
            'REDIS_URL': '캐시/큐 기능'
        }
        
        for var, feature in optional_vars.items():
            if os.getenv(var):
                self.logger.info(f"{feature}이 활성화되었습니다.")
            else:
                self.logger.info(f"{feature}이 비활성화되었습니다. (선택사항)")
    
    def create_initial_state(self, user_input: str, user_id: int = 1) -> State:
        """
        초기 상태를 생성합니다.
        
        Args:
            user_input (str): 사용자 입력
            user_id (int): 사용자 ID
            
        Returns:
            State: 초기 상태
        """
        return State(
            messages=[],
            user_input=user_input,
            ai_response="",
            task_history=[],
            current_task=None,
            supervisor_call_count=0,
            user_id=user_id,
            user_request=user_input,
            user_preferences={},
            health_data=None,
            schedule_data=None,
            worklife_data=None,
            feedback_data=[],
            system_status="initialized",
            error_messages=[],
            recommendations=[],
            context={},
            session_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat()
        )
    
    async def process_request(self, user_input: str, user_id: int = 1) -> Dict[str, Any]:
        """
        사용자 요청을 처리합니다.
        
        Args:
            user_input (str): 사용자 입력
            user_id (int): 사용자 ID
            
        Returns:
            Dict[str, Any]: 처리 결과
        """
        try:
            self.logger.info(f"요청 처리 시작: {user_input[:50]}...")
            
            # 사용자 언어 감지 및 시간대 설정
            user_language = self.detect_user_language(user_input)
            user_timezone = self.get_user_timezone(user_language)
            
            # 사용자 입력에 언어 및 시간대 정보 추가
            enhanced_input = f"""
            [시스템 지시사항]
            - 사용자 언어: {user_language}
            - 사용자 시간대: {user_timezone}
            - 사용자가 쓰는 언어로 응답해야 합니다
            - 해당 지역의 시간을 조회해야 합니다
            
            [사용자 입력]
            {user_input}
            """
            
            # 초기 상태 생성
            initial_state = self.create_initial_state(enhanced_input, user_id)
            
            # 그래프 실행 (stream 방식)
            final_state = None
            async for chunk in plandy_ai_graph.astream(initial_state):
                # 각 노드의 결과를 실시간으로 출력
                for node_name, node_result in chunk.items():
                    if node_name == "supervisor":
                        print(f"\n============= SUPERVISOR NODE ==============")
                        current_task = node_result.get('current_task')
                        if current_task:
                            agent_name = getattr(current_task, 'agent', 'unknown')
                        else:
                            agent_name = 'unknown'
                        print(f"다음 작업: {agent_name}")
                    elif node_name == "health_agent":
                        print(f"\n============= HEALTH NODE ==============")
                        if "ai_response" in node_result:
                            print(f"건강 분석 결과:")
                            print(node_result["ai_response"])
                    elif node_name == "plan_agent":
                        print(f"\n============= PLAN NODE ==============")
                        if "ai_response" in node_result:
                            print(f"일정 계획 결과:")
                            print(node_result["ai_response"])
                        if "schedule_data" in node_result:
                            schedule_data = node_result["schedule_data"]
                            print(f"\n============= 저장된 일정 ==============")
                            if hasattr(schedule_data, 'schedule_id'):
                                print(f"일정 ID: {schedule_data.schedule_id}")
                            else:
                                print(f"일정 ID: N/A")
                            
                            if hasattr(schedule_data, 'tasks'):
                                print(f"작업 수: {len(schedule_data.tasks)}")
                                for task in schedule_data.tasks:
                                    if hasattr(task, 'title') and hasattr(task, 'deadline'):
                                        print(f"- {task.title}: {task.deadline}")
                                    else:
                                        print(f"- 작업 정보: {task}")
                            else:
                                print("작업 정보 없음")
                    elif node_name == "worklife_balance_agent":
                        print(f"\n============= WORKLIFE NODE ==============")
                        if "ai_response" in node_result:
                            print(f"워라벨 분석 결과:")
                            print(node_result["ai_response"])
                    elif node_name == "data_agent":
                        print(f"\n============= DATA NODE ==============")
                        if "ai_response" in node_result:
                            print(f"데이터 분석 결과:")
                            print(node_result["ai_response"])
                    elif node_name == "communication_agent":
                        print(f"\n============= COMMUNICATION NODE ==============")
                        if "ai_response" in node_result:
                            print(f"응답:")
                            print(node_result["ai_response"])
                
                final_state = node_result
            
            
            # 결과 정리
            result = {
                "status": "success",
                "user_input": user_input,
                "ai_response": final_state.get("ai_response", ""),
                "system_status": final_state.get("system_status", "completed"),
                "messages": final_state.get("messages", []),
                "recommendations": final_state.get("recommendations", []),
                "session_id": final_state.get("session_id", ""),
                "processed_at": datetime.now().isoformat()
            }
            
            # 에러가 있는 경우 추가
            if final_state.get("error_messages"):
                result["errors"] = final_state["error_messages"]
                result["status"] = "error"
            
            self.logger.info("요청 처리 완료")
            return result
            
        except Exception as e:
            self.logger.error(f"요청 처리 중 오류 발생: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "user_input": user_input,
                "processed_at": datetime.now().isoformat()
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """
        시스템 상태를 조회합니다.
        
        Returns:
            Dict[str, Any]: 시스템 상태 정보
        """
        graph_info = plandy_ai_graph.get_graph_info()
        
        return {
            "system_status": "running",
            "graph_info": graph_info,
            "tools": {
                "time_tools": self.time_tools.get_info(),
                "schedule_tools": self.schedule_tools.get_info(),
                "feedback_tools": self.feedback_tools.get_info()
            },
            "prompt_templates": prompt_service.get_available_prompts(),
            "uptime": datetime.now().isoformat()
        }
    
    async def shutdown(self):
        """시스템을 종료합니다."""
        self.logger.info("시스템 종료 중...")
        
        # 도구들 정리
        self.time_tools.cleanup()
        self.schedule_tools.cleanup()
        self.feedback_tools.cleanup()
        
        self.logger.info("시스템이 정상적으로 종료되었습니다.")


async def main():
    """메인 실행 함수"""
    # Plandy AI 시스템 초기화
    plandy_ai = PlandyAISystem()
    
    try:
        # 시스템 상태 확인
        status = await plandy_ai.get_system_status()
        print("=== Plandy AI 시스템 상태 ===")
        print(f"시스템 상태: {status['system_status']}")
        print(f"그래프 타입: {status['graph_info']['type']}")
        print(f"노드 수: {len(status['graph_info']['nodes'])}")
        print(f"엣지 수: {len(status['graph_info']['edges'])}")
        print(f"사용 가능한 도구 수: {len(status['tools'])}")
        print(f"프롬프트 템플릿 수: {len(status['prompt_templates'])}")
        print()
        
        # 그래프 다이어그램 저장
        diagram_path = plandy_ai_graph.save_graph_diagram()
        if diagram_path:
            print(f"그래프 다이어그램이 저장되었습니다: {diagram_path}")
        print()
        
        # 예제 요청들 처리 (주석 처리 - 불필요한 DB 저장 방지)
        # example_requests = [
        #     "오늘 건강 상태를 확인해주세요",
        #     "일정을 계획해주세요",
        #     "워라벨 균형을 분석해주세요",
        #     "안녕하세요! 오늘 일정을 도와주세요"
        # ]
        
        # print("=== 예제 요청 처리 ===")
        # for i, user_input in enumerate(example_requests, 1):
        #     print(f"\n--- 요청 {i}: {user_input} ---")
        #     result = await plandy_ai.process_request(user_input)
        #     
        #     if result.get('status') == 'success':
        #         print("✅ 요청이 성공적으로 처리되었습니다.")
        #     else:
        #         print(f"❌ 요청 처리 실패: {result.get('error', 'unknown error')}")
        #         if result.get('errors'):
        #             print(f"에러 목록: {result['errors']}")
        
        # print("\n=== 모든 예제 요청 처리 완료 ===")
        
        # 대화형 모드
        print("\n=== 대화형 모드 시작 ===")
        print("종료하려면 'quit', 'exit', 'q' 중 하나를 입력하세요.")
        
        while True:
            try:
                user_input = input("\n사용자: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("대화를 종료합니다.")
                    break
                
                if not user_input:
                    continue
                
                result = await plandy_ai.process_request(user_input)
                
                if result.get('status') == 'success':
                    print("✅ 요청이 성공적으로 처리되었습니다.")
                else:
                    print(f"❌ 요청 처리 실패: {result.get('error', 'unknown error')}")
                    if result.get('errors'):
                        print(f"에러 목록: {result['errors']}")
                    
            except KeyboardInterrupt:
                print("\n대화를 종료합니다.")
                break
            except Exception as e:
                print(f"대화 중 오류 발생: {str(e)}")
        
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"시스템 오류 발생: {str(e)}")
    finally:
        # 시스템 종료
        await plandy_ai.shutdown()


if __name__ == "__main__":
    # 비동기 메인 함수 실행
    asyncio.run(main())
