"""
Database models for Plandy AI
"""

from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Schedule:
    """일정 모델"""
    id: str
    user_id: int
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    duration: int  # 분 단위
    priority: int
    status: str  # pending, completed, cancelled
    created_at: datetime
    updated_at: datetime

@dataclass
class Task:
    """작업 모델"""
    id: str
    schedule_id: str
    title: str
    description: str
    duration: int  # 분 단위
    priority: int
    deadline: datetime
    status: str  # pending, in_progress, completed, cancelled
    created_at: datetime
    updated_at: datetime
