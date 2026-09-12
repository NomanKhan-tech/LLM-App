from enum import Enum

from pydantic import BaseModel


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class AnalyzeResponse(BaseModel):
    category: str
    priority: Priority
    sentiment: Sentiment
    response: str


class MessageAnalysis(BaseModel):
    category: str
    priority: Priority
    sentiment: Sentiment
