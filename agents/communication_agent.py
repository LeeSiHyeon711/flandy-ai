"""
CommunicationAgent - 사용자 소통

사용자와의 자연스러운 소통을 담당하는 에이전트입니다.
채팅 인터페이스를 관리하고 상황별 맞춤형 응답을 제공합니다.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from .base_agent import BaseAgent, AgentStatus


class CommunicationAgent(BaseAgent):
    """
    사용자 소통 에이전트
    
    사용자와의 자연스러운 대화를 관리하고 상황에 맞는 응답을 제공합니다.
    """
    
    def __init__(self):
        super().__init__(name="CommunicationAgent", priority=4)
        self.logger = logging.getLogger("agent.CommunicationAgent")
        self.conversation_history = {}  # 사용자별 대화 히스토리
    
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        통신 관련 작업을 처리합니다.
        
        Args:
            context (Dict[str, Any]): 처리할 컨텍스트 데이터
            
        Returns:
            Dict[str, Any]: 처리 결과
        """
        self.set_status(AgentStatus.PROCESSING)
        
        try:
            action = context.get("action", "chat")
            user_id = context.get("user_id")
            message = context.get("message", "")
            
            self.logger.info(f"Processing communication action: {action} for user: {user_id}")
            
            if action == "chat":
                result = await self._handle_chat(user_id, message, context)
            elif action == "notification":
                result = await self._send_notification(user_id, context.get("notification_data"))
            elif action == "reminder":
                result = await self._send_reminder(user_id, context.get("reminder_data"))
            elif action == "feedback_collection":
                result = await self._collect_feedback(user_id, context.get("feedback_data"))
            elif action == "contextual_response":
                result = await self._generate_contextual_response(user_id, context)
            else:
                result = await self._handle_chat(user_id, message, context)
            
            return {
                "status": "success",
                "action": action,
                "user_id": user_id,
                "result": result,
                "processed_by": "CommunicationAgent"
            }
            
        except Exception as e:
            self.handle_error(e)
            return {
                "status": "error",
                "error": str(e),
                "processed_by": "CommunicationAgent"
            }
        finally:
            self.set_status(AgentStatus.IDLE)
    
    def can_handle(self, action: str) -> bool:
        """
        CommunicationAgent가 처리할 수 있는 액션인지 확인합니다.
        
        Args:
            action (str): 처리할 액션 타입
            
        Returns:
            bool: 처리 가능 여부
        """
        communication_actions = [
            "chat",
            "notification",
            "reminder",
            "feedback_collection",
            "contextual_response",
            "voice_interaction",
            "multimodal_communication"
        ]
        return action in communication_actions
    
    def get_supported_actions(self) -> List[str]:
        """
        CommunicationAgent가 지원하는 액션 목록을 반환합니다.
        
        Returns:
            List[str]: 지원하는 액션 목록
        """
        return [
            "chat",
            "notification",
            "reminder",
            "feedback_collection",
            "contextual_response",
            "voice_interaction",
            "multimodal_communication"
        ]
    
    async def _handle_chat(self, user_id: int, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        사용자와의 채팅을 처리합니다.
        
        Args:
            user_id (int): 사용자 ID
            message (str): 사용자 메시지
            context (Dict[str, Any]): 추가 컨텍스트
            
        Returns:
            Dict[str, Any]: 채팅 처리 결과
        """
        # 대화 히스토리 업데이트
        await self._update_conversation_history(user_id, message, "user")
        
        # 메시지 분석
        message_analysis = await self._analyze_message(message, context)
        
        # 의도 파악
        intent = await self._detect_intent(message, message_analysis)
        
        # 컨텍스트 기반 응답 생성
        response = await self._generate_response(user_id, message, intent, context)
        
        # 대화 히스토리 업데이트
        await self._update_conversation_history(user_id, response["text"], "assistant")
        
        return {
            "user_id": user_id,
            "message": message,
            "intent": intent,
            "response": response,
            "conversation_context": await self._get_conversation_context(user_id),
            "processed_at": datetime.now().isoformat()
        }
    
    async def _send_notification(self, user_id: int, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        사용자에게 알림을 전송합니다.
        
        Args:
            user_id (int): 사용자 ID
            notification_data (Dict[str, Any]): 알림 데이터
            
        Returns:
            Dict[str, Any]: 알림 전송 결과
        """
        notification_type = notification_data.get("type", "general")
        content = notification_data.get("content", "")
        priority = notification_data.get("priority", "normal")
        
        # 알림 메시지 생성
        message = await self._create_notification_message(notification_type, content, priority)
        
        # 전송 채널 결정
        channels = await self._determine_notification_channels(user_id, notification_type, priority)
        
        # 알림 전송
        delivery_results = await self._deliver_notification(user_id, message, channels)
        
        return {
            "user_id": user_id,
            "notification_type": notification_type,
            "message": message,
            "channels": channels,
            "delivery_results": delivery_results,
            "sent_at": datetime.now().isoformat()
        }
    
    async def _send_reminder(self, user_id: int, reminder_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        사용자에게 리마인더를 전송합니다.
        
        Args:
            user_id (int): 사용자 ID
            reminder_data (Dict[str, Any]): 리마인더 데이터
            
        Returns:
            Dict[str, Any]: 리마인더 전송 결과
        """
        reminder_type = reminder_data.get("type", "task")
        task_info = reminder_data.get("task_info", {})
        timing = reminder_data.get("timing", "now")
        
        # 리마인더 메시지 생성
        message = await self._create_reminder_message(reminder_type, task_info, timing)
        
        # 리마인더 전송
        delivery_result = await self._deliver_reminder(user_id, message, timing)
        
        return {
            "user_id": user_id,
            "reminder_type": reminder_type,
            "message": message,
            "timing": timing,
            "delivery_result": delivery_result,
            "sent_at": datetime.now().isoformat()
        }
    
    async def _collect_feedback(self, user_id: int, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        사용자 피드백을 수집합니다.
        
        Args:
            user_id (int): 사용자 ID
            feedback_data (Dict[str, Any]): 피드백 데이터
            
        Returns:
            Dict[str, Any]: 피드백 수집 결과
        """
        feedback_type = feedback_data.get("type", "general")
        questions = feedback_data.get("questions", [])
        context = feedback_data.get("context", {})
        
        # 피드백 요청 메시지 생성
        feedback_request = await self._create_feedback_request(feedback_type, questions, context)
        
        # 피드백 수집 방법 결정
        collection_method = await self._determine_feedback_collection_method(user_id, feedback_type)
        
        return {
            "user_id": user_id,
            "feedback_type": feedback_type,
            "feedback_request": feedback_request,
            "collection_method": collection_method,
            "questions": questions,
            "requested_at": datetime.now().isoformat()
        }
    
    async def _generate_contextual_response(self, user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        컨텍스트 기반 응답을 생성합니다.
        
        Args:
            user_id (int): 사용자 ID
            context (Dict[str, Any]): 컨텍스트 정보
            
        Returns:
            Dict[str, Any]: 컨텍스트 기반 응답
        """
        # 사용자 상태 분석
        user_state = await self._analyze_user_state(user_id, context)
        
        # 상황별 응답 생성
        response = await self._create_situational_response(user_state, context)
        
        # 개인화 적용
        personalized_response = await self._personalize_response(user_id, response, user_state)
        
        return {
            "user_id": user_id,
            "user_state": user_state,
            "response": personalized_response,
            "context_used": context,
            "generated_at": datetime.now().isoformat()
        }
    
    # 헬퍼 메서드들
    async def _update_conversation_history(self, user_id: int, message: str, sender: str) -> None:
        """대화 히스토리를 업데이트합니다."""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            "message": message,
            "sender": sender,
            "timestamp": datetime.now().isoformat()
        })
        
        # 히스토리 길이 제한 (최근 50개 메시지만 유지)
        if len(self.conversation_history[user_id]) > 50:
            self.conversation_history[user_id] = self.conversation_history[user_id][-50:]
    
    async def _analyze_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """메시지를 분석합니다."""
        return {
            "length": len(message),
            "sentiment": await self._analyze_sentiment(message),
            "keywords": await self._extract_keywords(message),
            "complexity": await self._assess_complexity(message),
            "urgency": await self._assess_urgency(message)
        }
    
    async def _detect_intent(self, message: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """메시지의 의도를 파악합니다."""
        # 간단한 의도 분류 로직 (실제로는 더 복잡한 NLP 모델 사용)
        intents = {
            "schedule_management": ["일정", "스케줄", "계획", "시간"],
            "task_management": ["할일", "작업", "업무", "태스크"],
            "health_concern": ["건강", "스트레스", "피로", "휴식"],
            "feedback": ["피드백", "의견", "개선", "만족"],
            "general_inquiry": ["질문", "궁금", "알려줘", "도움"]
        }
        
        detected_intent = "general_inquiry"
        confidence = 0.5
        
        for intent, keywords in intents.items():
            for keyword in keywords:
                if keyword in message:
                    detected_intent = intent
                    confidence = 0.8
                    break
        
        return {
            "intent": detected_intent,
            "confidence": confidence,
            "entities": await self._extract_entities(message)
        }
    
    async def _generate_response(self, user_id: int, message: str, intent: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """응답을 생성합니다."""
        intent_type = intent["intent"]
        
        if intent_type == "schedule_management":
            response_text = await self._generate_schedule_response(message, context)
        elif intent_type == "task_management":
            response_text = await self._generate_task_response(message, context)
        elif intent_type == "health_concern":
            response_text = await self._generate_health_response(message, context)
        elif intent_type == "feedback":
            response_text = await self._generate_feedback_response(message, context)
        else:
            response_text = await self._generate_general_response(message, context)
        
        return {
            "text": response_text,
            "intent": intent_type,
            "confidence": intent["confidence"],
            "suggestions": await self._generate_suggestions(intent_type, context)
        }
    
    async def _get_conversation_context(self, user_id: int) -> Dict[str, Any]:
        """대화 컨텍스트를 조회합니다."""
        if user_id not in self.conversation_history:
            return {"message_count": 0, "recent_topics": []}
        
        history = self.conversation_history[user_id]
        recent_topics = await self._extract_recent_topics(history[-10:])  # 최근 10개 메시지에서 주제 추출
        
        return {
            "message_count": len(history),
            "recent_topics": recent_topics,
            "conversation_length": len(history),
            "last_message_time": history[-1]["timestamp"] if history else None
        }
    
    async def _create_notification_message(self, notification_type: str, content: str, priority: str) -> str:
        """알림 메시지를 생성합니다."""
        priority_prefixes = {
            "high": "🚨 긴급: ",
            "normal": "📢 알림: ",
            "low": "💡 안내: "
        }
        
        prefix = priority_prefixes.get(priority, "📢 알림: ")
        return f"{prefix}{content}"
    
    async def _determine_notification_channels(self, user_id: int, notification_type: str, priority: str) -> List[str]:
        """알림 전송 채널을 결정합니다."""
        channels = ["in_app"]
        
        if priority == "high":
            channels.extend(["push", "email"])
        elif notification_type == "reminder":
            channels.append("push")
        
        return channels
    
    async def _deliver_notification(self, user_id: int, message: str, channels: List[str]) -> Dict[str, Any]:
        """알림을 전송합니다."""
        results = {}
        for channel in channels:
            results[channel] = {
                "status": "sent",
                "delivered_at": datetime.now().isoformat()
            }
        return results
    
    async def _create_reminder_message(self, reminder_type: str, task_info: Dict[str, Any], timing: str) -> str:
        """리마인더 메시지를 생성합니다."""
        if reminder_type == "task":
            task_name = task_info.get("name", "작업")
            return f"⏰ 리마인더: '{task_name}' 시간입니다!"
        elif reminder_type == "break":
            return "☕ 휴식 시간입니다. 잠시 쉬어가세요!"
        else:
            return "⏰ 리마인더: 예정된 시간입니다!"
    
    async def _deliver_reminder(self, user_id: int, message: str, timing: str) -> Dict[str, Any]:
        """리마인더를 전송합니다."""
        return {
            "status": "sent",
            "message": message,
            "delivered_at": datetime.now().isoformat()
        }
    
    async def _create_feedback_request(self, feedback_type: str, questions: List[str], context: Dict[str, Any]) -> str:
        """피드백 요청 메시지를 생성합니다."""
        if feedback_type == "satisfaction":
            return "💭 사용 경험에 대한 피드백을 들려주세요. 어떤 부분이 도움이 되었나요?"
        elif feedback_type == "improvement":
            return "🔧 개선하고 싶은 부분이 있다면 알려주세요!"
        else:
            return "💬 의견이나 제안이 있으시면 언제든 말씀해주세요!"
    
    async def _determine_feedback_collection_method(self, user_id: int, feedback_type: str) -> str:
        """피드백 수집 방법을 결정합니다."""
        if feedback_type == "satisfaction":
            return "rating_and_text"
        elif feedback_type == "improvement":
            return "text_input"
        else:
            return "conversational"
    
    async def _analyze_user_state(self, user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 상태를 분석합니다."""
        return {
            "current_activity": context.get("current_activity", "unknown"),
            "stress_level": context.get("stress_level", 5.0),
            "productivity_level": context.get("productivity_level", 7.0),
            "mood": context.get("mood", "neutral"),
            "time_of_day": datetime.now().hour
        }
    
    async def _create_situational_response(self, user_state: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """상황별 응답을 생성합니다."""
        time_of_day = user_state["time_of_day"]
        stress_level = user_state["stress_level"]
        
        if time_of_day < 9:
            greeting = "좋은 아침입니다! 오늘도 화이팅하세요! 🌅"
        elif time_of_day < 18:
            greeting = "안녕하세요! 오늘 하루는 어떠신가요? 😊"
        else:
            greeting = "수고하셨습니다! 휴식을 취하세요 🌙"
        
        if stress_level > 7:
            stress_message = "스트레스가 높아 보이시네요. 잠시 휴식을 취해보시는 것은 어떨까요?"
        else:
            stress_message = "오늘 컨디션이 좋아 보이시네요!"
        
        return {
            "greeting": greeting,
            "stress_message": stress_message,
            "suggestions": await self._get_situational_suggestions(user_state)
        }
    
    async def _personalize_response(self, user_id: int, response: Dict[str, Any], user_state: Dict[str, Any]) -> Dict[str, Any]:
        """응답을 개인화합니다."""
        # 사용자 선호도에 따른 개인화 로직
        personalized_response = response.copy()
        personalized_response["personalized"] = True
        return personalized_response
    
    # 추가 헬퍼 메서드들
    async def _analyze_sentiment(self, message: str) -> str:
        """메시지의 감정을 분석합니다."""
        positive_words = ["좋다", "만족", "도움", "감사"]
        negative_words = ["나쁘다", "불만", "문제", "어려움"]
        
        if any(word in message for word in positive_words):
            return "positive"
        elif any(word in message for word in negative_words):
            return "negative"
        else:
            return "neutral"
    
    async def _extract_keywords(self, message: str) -> List[str]:
        """메시지에서 키워드를 추출합니다."""
        # 간단한 키워드 추출 (실제로는 더 정교한 NLP 사용)
        keywords = []
        important_words = ["일정", "작업", "건강", "시간", "계획", "목표"]
        
        for word in important_words:
            if word in message:
                keywords.append(word)
        
        return keywords
    
    async def _assess_complexity(self, message: str) -> str:
        """메시지의 복잡도를 평가합니다."""
        if len(message) > 100:
            return "complex"
        elif len(message) > 50:
            return "medium"
        else:
            return "simple"
    
    async def _assess_urgency(self, message: str) -> str:
        """메시지의 긴급도를 평가합니다."""
        urgent_words = ["긴급", "빨리", "즉시", "지금"]
        if any(word in message for word in urgent_words):
            return "high"
        else:
            return "normal"
    
    async def _extract_entities(self, message: str) -> List[str]:
        """메시지에서 엔티티를 추출합니다."""
        # 간단한 엔티티 추출 (실제로는 NER 모델 사용)
        entities = []
        time_patterns = ["오늘", "내일", "다음주", "월요일"]
        
        for pattern in time_patterns:
            if pattern in message:
                entities.append(pattern)
        
        return entities
    
    async def _generate_schedule_response(self, message: str, context: Dict[str, Any]) -> str:
        """일정 관련 응답을 생성합니다."""
        return "일정 관리에 대해 도움을 드리겠습니다. 어떤 부분이 궁금하신가요?"
    
    async def _generate_task_response(self, message: str, context: Dict[str, Any]) -> str:
        """작업 관련 응답을 생성합니다."""
        return "작업 관리에 대해 도움을 드리겠습니다. 어떤 작업이 있으신가요?"
    
    async def _generate_health_response(self, message: str, context: Dict[str, Any]) -> str:
        """건강 관련 응답을 생성합니다."""
        return "건강 관리에 대해 도움을 드리겠습니다. 어떤 부분이 걱정되시나요?"
    
    async def _generate_feedback_response(self, message: str, context: Dict[str, Any]) -> str:
        """피드백 관련 응답을 생성합니다."""
        return "피드백을 주셔서 감사합니다. 더 나은 서비스를 위해 노력하겠습니다!"
    
    async def _generate_general_response(self, message: str, context: Dict[str, Any]) -> str:
        """일반적인 응답을 생성합니다."""
        return "안녕하세요! 무엇을 도와드릴까요?"
    
    async def _generate_suggestions(self, intent_type: str, context: Dict[str, Any]) -> List[str]:
        """제안사항을 생성합니다."""
        suggestions = {
            "schedule_management": ["일정 추가", "일정 수정", "일정 확인"],
            "task_management": ["작업 추가", "작업 완료", "작업 우선순위"],
            "health_concern": ["휴식 시간", "운동 계획", "스트레스 관리"],
            "feedback": ["만족도 평가", "개선 제안", "버그 신고"]
        }
        
        return suggestions.get(intent_type, ["도움말", "설정", "통계"])
    
    async def _extract_recent_topics(self, recent_messages: List[Dict[str, Any]]) -> List[str]:
        """최근 대화에서 주제를 추출합니다."""
        topics = []
        for message in recent_messages:
            if message["sender"] == "user":
                keywords = await self._extract_keywords(message["message"])
                topics.extend(keywords)
        
        return list(set(topics))  # 중복 제거
    
    async def _get_situational_suggestions(self, user_state: Dict[str, Any]) -> List[str]:
        """상황별 제안사항을 생성합니다."""
        suggestions = []
        
        if user_state["stress_level"] > 7:
            suggestions.append("명상이나 깊게 숨쉬기를 해보세요")
        
        if user_state["time_of_day"] < 12:
            suggestions.append("오전에 중요한 작업을 계획해보세요")
        elif user_state["time_of_day"] > 18:
            suggestions.append("저녁에는 휴식을 취하세요")
        
        return suggestions
