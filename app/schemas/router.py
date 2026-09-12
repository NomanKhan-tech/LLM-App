from enum import Enum

from pydantic import BaseModel


class Intent(str, Enum):
    SIMPLE = "simple"
    TOOL = "tool"
    KNOWLEDGE = "knowledge"


class IntentResponse(BaseModel):
    intent: Intent
