"""
Pydantic Models for Telegram Backup Manager
"""

from typing import Dict, Optional, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

class MessageType(Enum):
    """Tipos de mensagens para filtragem"""
    TEXT = "text"
    PHOTO = "photo"
    VIDEO = "video"
    DOCUMENT = "document"
    AUDIO = "audio"
    STICKER = "sticker"
    ANIMATION = "animation"

class RateLimitConfig(BaseModel):
    enabled: bool = True
    messages_per_second: float = Field(default=10.0, gt=0)

class BackupSettings(BaseModel):
    max_workers: int = Field(default=4, ge=1)
    batch_size: int = Field(default=100, ge=1)
    retry_delay: int = Field(default=5, ge=0)
    timeout: int = Field(default=30, ge=1)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)

class BackupFilters(BaseModel):
    media_only: bool = False
    photos: bool = True
    videos: bool = True
    documents: bool = False
    text_messages: bool = True

class BackupConfig(BaseModel):
    """Configuration model"""
    routes: Dict[str, str] = Field(default_factory=dict)
    filters: BackupFilters = Field(default_factory=BackupFilters)
    settings: BackupSettings = Field(default_factory=BackupSettings)

    @classmethod
    def default(cls) -> 'BackupConfig':
        """Compatibility method for tests"""
        return cls()

class BackupStats(BaseModel):
    """Statistics model"""
    total_routes: int = 0
    active_routes: int = 0
    processed_messages: int = 0
    last_message_id: int = 0
    last_update: Optional[datetime] = None
    errors_count: int = 0
    uptime_seconds: int = 0
