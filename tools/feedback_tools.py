"""
FeedbackTools - 피드백 도구

사용자 피드백 수집 및 분석을 담당하는 도구입니다.
피드백 데이터를 수집하고 분석하여 개선점을 도출합니다.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from .base_tool import BaseTool


class FeedbackTools(BaseTool):
    """
    피드백 도구
    
    사용자 피드백 수집, 분석, 처리 등의 기능을 제공합니다.
    """
    
    def __init__(self):
        super().__init__(
            name="FeedbackTools",
            description="사용자 피드백 수집 및 분석 도구"
        )
        self.logger = logging.getLogger("tool.FeedbackTools")
    
    async def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        피드백 도구를 실행합니다.
        
        Args:
            args (Dict[str, Any]): 실행 인자
                - action (str): 실행할 액션
                - feedback_data (Dict, optional): 피드백 데이터
                - user_id (int, optional): 사용자 ID
                - feedback_type (str, optional): 피드백 타입
                
        Returns:
            Dict[str, Any]: 실행 결과
        """
        try:
            action = args.get("action")
            
            if action == "collect":
                return await self._collect_feedback(args)
            elif action == "analyze":
                return await self._analyze_feedback(args)
            elif action == "categorize":
                return await self._categorize_feedback(args)
            elif action == "sentiment_analysis":
                return await self._analyze_sentiment(args)
            elif action == "generate_insights":
                return await self._generate_feedback_insights(args)
            elif action == "track_trends":
                return await self._track_feedback_trends(args)
            else:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}",
                    "available_actions": self.get_supported_actions()
                }
                
        except Exception as e:
            self.logger.error(f"Error executing FeedbackTools: {str(e)}")
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
        
        if action == "collect":
            return "feedback_data" in args and "user_id" in args
        elif action in ["analyze", "categorize", "sentiment_analysis"]:
            return "feedback_data" in args
        elif action == "generate_insights":
            return "user_id" in args
        elif action == "track_trends":
            return "user_id" in args and "period" in args
        
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
                    "enum": ["collect", "analyze", "categorize", "sentiment_analysis", "generate_insights", "track_trends"],
                    "description": "실행할 액션"
                },
                "feedback_data": {
                    "type": "object",
                    "description": "피드백 데이터",
                    "properties": {
                        "text": {"type": "string"},
                        "rating": {"type": "number"},
                        "category": {"type": "string"},
                        "timestamp": {"type": "string"}
                    }
                },
                "user_id": {
                    "type": "integer",
                    "description": "사용자 ID"
                },
                "feedback_type": {
                    "type": "string",
                    "description": "피드백 타입"
                },
                "period": {
                    "type": "string",
                    "description": "분석 기간"
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
            "collect",
            "analyze",
            "categorize",
            "sentiment_analysis",
            "generate_insights",
            "track_trends"
        ]
    
    async def _collect_feedback(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        피드백을 수집합니다.
        
        Args:
            args (Dict[str, Any]): 실행 인자
            
        Returns:
            Dict[str, Any]: 피드백 수집 결과
        """
        try:
            feedback_data = args["feedback_data"]
            user_id = args["user_id"]
            feedback_type = args.get("feedback_type", "general")
            
            # 피드백 데이터 검증 및 정규화
            normalized_feedback = self._normalize_feedback_data(feedback_data)
            
            # 피드백 저장 (실제로는 데이터베이스에 저장)
            feedback_id = await self._save_feedback(user_id, normalized_feedback, feedback_type)
            
            return {
                "status": "success",
                "feedback_id": feedback_id,
                "user_id": user_id,
                "feedback_type": feedback_type,
                "collected_data": normalized_feedback,
                "collected_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to collect feedback: {str(e)}"
            }
    
    async def _analyze_feedback(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        피드백을 분석합니다.
        
        Args:
            args (Dict[str, Any]): 실행 인자
            
        Returns:
            Dict[str, Any]: 피드백 분석 결과
        """
        try:
            feedback_data = args["feedback_data"]
            
            # 기본 분석 수행
            analysis = {
                "word_count": len(feedback_data.get("text", "").split()),
                "character_count": len(feedback_data.get("text", "")),
                "has_rating": "rating" in feedback_data,
                "rating_value": feedback_data.get("rating"),
                "category": feedback_data.get("category", "uncategorized")
            }
            
            # 감정 분석
            sentiment = await self._analyze_sentiment(args)
            analysis["sentiment"] = sentiment.get("result", {})
            
            # 키워드 추출
            keywords = self._extract_keywords(feedback_data.get("text", ""))
            analysis["keywords"] = keywords
            
            return {
                "status": "success",
                "analysis": analysis,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to analyze feedback: {str(e)}"
            }
    
    async def _categorize_feedback(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        피드백을 카테고리별로 분류합니다.
        
        Args:
            args (Dict[str, Any]): 실행 인자
            
        Returns:
            Dict[str, Any]: 카테고리 분류 결과
        """
        try:
            feedback_data = args["feedback_data"]
            text = feedback_data.get("text", "")
            
            # 카테고리 분류 로직
            category = self._classify_feedback_category(text)
            subcategory = self._classify_feedback_subcategory(text, category)
            priority = self._determine_feedback_priority(text, category)
            
            return {
                "status": "success",
                "category": category,
                "subcategory": subcategory,
                "priority": priority,
                "confidence": self._calculate_classification_confidence(text, category),
                "categorized_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to categorize feedback: {str(e)}"
            }
    
    async def _analyze_sentiment(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        피드백의 감정을 분석합니다.
        
        Args:
            args (Dict[str, Any]): 실행 인자
            
        Returns:
            Dict[str, Any]: 감정 분석 결과
        """
        try:
            feedback_data = args["feedback_data"]
            text = feedback_data.get("text", "")
            
            # 간단한 감정 분석 (실제로는 더 정교한 NLP 모델 사용)
            sentiment_score = self._calculate_sentiment_score(text)
            sentiment_label = self._get_sentiment_label(sentiment_score)
            
            # 감정 키워드 추출
            emotion_keywords = self._extract_emotion_keywords(text)
            
            return {
                "status": "success",
                "result": {
                    "sentiment_score": sentiment_score,
                    "sentiment_label": sentiment_label,
                    "emotion_keywords": emotion_keywords,
                    "confidence": abs(sentiment_score)  # 절댓값으로 신뢰도 계산
                },
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to analyze sentiment: {str(e)}"
            }
    
    async def _generate_feedback_insights(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        피드백에서 인사이트를 생성합니다.
        
        Args:
            args (Dict[str, Any]): 실행 인자
            
        Returns:
            Dict[str, Any]: 인사이트 생성 결과
        """
        try:
            user_id = args["user_id"]
            period = args.get("period", "30d")
            
            # 사용자의 피드백 히스토리 조회
            feedback_history = await self._get_user_feedback_history(user_id, period)
            
            # 인사이트 생성
            insights = {
                "satisfaction_trend": self._analyze_satisfaction_trend(feedback_history),
                "common_issues": self._identify_common_issues(feedback_history),
                "improvement_areas": self._identify_improvement_areas(feedback_history),
                "positive_aspects": self._identify_positive_aspects(feedback_history),
                "recommendations": self._generate_recommendations(feedback_history)
            }
            
            return {
                "status": "success",
                "user_id": user_id,
                "period": period,
                "insights": insights,
                "feedback_count": len(feedback_history),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to generate feedback insights: {str(e)}"
            }
    
    async def _track_feedback_trends(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        피드백 트렌드를 추적합니다.
        
        Args:
            args (Dict[str, Any]): 실행 인자
            
        Returns:
            Dict[str, Any]: 트렌드 추적 결과
        """
        try:
            user_id = args["user_id"]
            period = args["period"]
            
            # 피드백 트렌드 데이터 조회
            trend_data = await self._get_feedback_trend_data(user_id, period)
            
            # 트렌드 분석
            trends = {
                "satisfaction_trend": self._calculate_satisfaction_trend(trend_data),
                "volume_trend": self._calculate_volume_trend(trend_data),
                "category_trends": self._calculate_category_trends(trend_data),
                "sentiment_trend": self._calculate_sentiment_trend(trend_data)
            }
            
            return {
                "status": "success",
                "user_id": user_id,
                "period": period,
                "trends": trends,
                "tracked_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to track feedback trends: {str(e)}"
            }
    
    # 헬퍼 메서드들
    def _normalize_feedback_data(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """피드백 데이터를 정규화합니다."""
        normalized = feedback_data.copy()
        
        # 텍스트 정규화
        if "text" in normalized:
            normalized["text"] = normalized["text"].strip()
        
        # 타임스탬프 추가
        if "timestamp" not in normalized:
            normalized["timestamp"] = datetime.now().isoformat()
        
        # 기본 카테고리 설정
        if "category" not in normalized:
            normalized["category"] = "general"
        
        return normalized
    
    async def _save_feedback(self, user_id: int, feedback_data: Dict[str, Any], feedback_type: str) -> str:
        """피드백을 저장합니다."""
        # 실제 구현에서는 데이터베이스에 저장
        feedback_id = f"feedback_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return feedback_id
    
    def _extract_keywords(self, text: str) -> List[str]:
        """텍스트에서 키워드를 추출합니다."""
        # 간단한 키워드 추출 (실제로는 더 정교한 NLP 사용)
        important_words = ["일정", "작업", "건강", "시간", "계획", "목표", "만족", "문제", "개선"]
        keywords = []
        
        for word in important_words:
            if word in text:
                keywords.append(word)
        
        return keywords
    
    def _classify_feedback_category(self, text: str) -> str:
        """피드백 카테고리를 분류합니다."""
        categories = {
            "schedule": ["일정", "스케줄", "계획", "시간"],
            "task": ["할일", "작업", "업무", "태스크"],
            "health": ["건강", "스트레스", "피로", "휴식"],
            "ui": ["인터페이스", "화면", "디자인", "사용법"],
            "performance": ["속도", "성능", "느림", "빠름"],
            "bug": ["오류", "버그", "문제", "에러"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return "general"
    
    def _classify_feedback_subcategory(self, text: str, category: str) -> str:
        """피드백 하위 카테고리를 분류합니다."""
        subcategories = {
            "schedule": ["생성", "수정", "삭제", "확인"],
            "task": ["추가", "완료", "우선순위", "상태"],
            "health": ["모니터링", "분석", "권장", "경고"]
        }
        
        category_keywords = subcategories.get(category, [])
        for subcategory in category_keywords:
            if subcategory in text:
                return subcategory
        
        return "general"
    
    def _determine_feedback_priority(self, text: str, category: str) -> str:
        """피드백 우선순위를 결정합니다."""
        high_priority_keywords = ["긴급", "중요", "빨리", "즉시", "버그", "오류"]
        
        if any(keyword in text for keyword in high_priority_keywords):
            return "high"
        elif category in ["bug", "performance"]:
            return "medium"
        else:
            return "low"
    
    def _calculate_classification_confidence(self, text: str, category: str) -> float:
        """분류 신뢰도를 계산합니다."""
        # 간단한 신뢰도 계산
        return 0.8 if category != "general" else 0.5
    
    def _calculate_sentiment_score(self, text: str) -> float:
        """감정 점수를 계산합니다."""
        positive_words = ["좋다", "만족", "도움", "감사", "훌륭", "완벽"]
        negative_words = ["나쁘다", "불만", "문제", "어려움", "느림", "오류"]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count + negative_count == 0:
            return 0.0
        
        return (positive_count - negative_count) / (positive_count + negative_count)
    
    def _get_sentiment_label(self, sentiment_score: float) -> str:
        """감정 점수에 따른 라벨을 반환합니다."""
        if sentiment_score > 0.2:
            return "positive"
        elif sentiment_score < -0.2:
            return "negative"
        else:
            return "neutral"
    
    def _extract_emotion_keywords(self, text: str) -> List[str]:
        """감정 키워드를 추출합니다."""
        emotion_keywords = {
            "happy": ["기쁘", "행복", "만족", "좋다"],
            "sad": ["슬프", "우울", "실망", "나쁘다"],
            "angry": ["화나", "짜증", "불만", "분노"],
            "excited": ["신나", "기대", "흥미", "재미"]
        }
        
        found_emotions = []
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in text for keyword in keywords):
                found_emotions.append(emotion)
        
        return found_emotions
    
    async def _get_user_feedback_history(self, user_id: int, period: str) -> List[Dict[str, Any]]:
        """사용자의 피드백 히스토리를 조회합니다."""
        # 실제 구현에서는 데이터베이스에서 조회
        return [
            {
                "id": "feedback_1",
                "text": "일정 관리가 잘 되고 있어요",
                "rating": 4.5,
                "category": "schedule",
                "timestamp": "2024-01-01T10:00:00"
            },
            {
                "id": "feedback_2", 
                "text": "알림이 너무 자주 와요",
                "rating": 2.0,
                "category": "notification",
                "timestamp": "2024-01-02T14:30:00"
            }
        ]
    
    def _analyze_satisfaction_trend(self, feedback_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """만족도 트렌드를 분석합니다."""
        if not feedback_history:
            return {"trend": "no_data", "average_rating": 0.0}
        
        ratings = [f.get("rating", 0) for f in feedback_history if f.get("rating")]
        if not ratings:
            return {"trend": "no_ratings", "average_rating": 0.0}
        
        average_rating = sum(ratings) / len(ratings)
        
        # 간단한 트렌드 계산
        if len(ratings) >= 2:
            recent_avg = sum(ratings[-3:]) / len(ratings[-3:])
            earlier_avg = sum(ratings[:-3]) / len(ratings[:-3]) if len(ratings) > 3 else ratings[0]
            
            if recent_avg > earlier_avg + 0.5:
                trend = "improving"
            elif recent_avg < earlier_avg - 0.5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "trend": trend,
            "average_rating": round(average_rating, 2),
            "rating_count": len(ratings)
        }
    
    def _identify_common_issues(self, feedback_history: List[Dict[str, Any]]) -> List[str]:
        """공통 이슈를 식별합니다."""
        issue_keywords = ["문제", "오류", "버그", "느림", "어려움", "불편"]
        common_issues = []
        
        for feedback in feedback_history:
            text = feedback.get("text", "")
            for keyword in issue_keywords:
                if keyword in text and keyword not in common_issues:
                    common_issues.append(keyword)
        
        return common_issues
    
    def _identify_improvement_areas(self, feedback_history: List[Dict[str, Any]]) -> List[str]:
        """개선 영역을 식별합니다."""
        improvement_keywords = ["개선", "향상", "더", "추가", "바꿔", "수정"]
        improvement_areas = []
        
        for feedback in feedback_history:
            text = feedback.get("text", "")
            for keyword in improvement_keywords:
                if keyword in text and keyword not in improvement_areas:
                    improvement_areas.append(keyword)
        
        return improvement_areas
    
    def _identify_positive_aspects(self, feedback_history: List[Dict[str, Any]]) -> List[str]:
        """긍정적인 측면을 식별합니다."""
        positive_keywords = ["좋다", "만족", "도움", "감사", "훌륭", "완벽"]
        positive_aspects = []
        
        for feedback in feedback_history:
            text = feedback.get("text", "")
            for keyword in positive_keywords:
                if keyword in text and keyword not in positive_aspects:
                    positive_aspects.append(keyword)
        
        return positive_aspects
    
    def _generate_recommendations(self, feedback_history: List[Dict[str, Any]]) -> List[str]:
        """개선 권장사항을 생성합니다."""
        recommendations = []
        
        # 만족도 기반 권장사항
        satisfaction_trend = self._analyze_satisfaction_trend(feedback_history)
        if satisfaction_trend["average_rating"] < 3.0:
            recommendations.append("사용자 만족도 개선이 필요합니다")
        
        # 공통 이슈 기반 권장사항
        common_issues = self._identify_common_issues(feedback_history)
        if "느림" in common_issues:
            recommendations.append("성능 최적화가 필요합니다")
        if "어려움" in common_issues:
            recommendations.append("사용자 인터페이스 개선이 필요합니다")
        
        return recommendations
    
    async def _get_feedback_trend_data(self, user_id: int, period: str) -> List[Dict[str, Any]]:
        """피드백 트렌드 데이터를 조회합니다."""
        # 실제 구현에서는 데이터베이스에서 조회
        return []
    
    def _calculate_satisfaction_trend(self, trend_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """만족도 트렌드를 계산합니다."""
        return {"trend": "stable", "change_rate": 0.0}
    
    def _calculate_volume_trend(self, trend_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """피드백 볼륨 트렌드를 계산합니다."""
        return {"trend": "stable", "change_rate": 0.0}
    
    def _calculate_category_trends(self, trend_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """카테고리별 트렌드를 계산합니다."""
        return {"schedule": "stable", "task": "stable", "health": "stable"}
    
    def _calculate_sentiment_trend(self, trend_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """감정 트렌드를 계산합니다."""
        return {"trend": "stable", "change_rate": 0.0}
