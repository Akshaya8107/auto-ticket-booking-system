from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator

CATEGORIES = ["Network", "Hardware", "Access", "Performance"]
SUBCATEGORIES = ["Wi-Fi", "Projector", "Forgot Password", "Slow Computer"]
STATES = ["New", "In progress", "On hold", "Resolved", "Closed"]
DEPENDENCIES = {
    "Network": ["Wi-Fi"],
    "Hardware": ["Projector"],
    "Access": ["Forgot Password"],
    "Performance": ["Slow Computer"],
}

class TicketCreate(BaseModel):
    caller_name: str = Field(min_length=1, max_length=120)
    caller_email: str
    short_description: str = Field(min_length=1, max_length=500)
    description: str = Field(default="", max_length=5000)
    state: str = "New"
    assigned_group: Optional[str] = None
    assigned_to: Optional[str] = None

    @field_validator("caller_email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("caller_email must be a valid email address")
        return value

class TicketUpdate(BaseModel):
    caller_name: Optional[str] = None
    caller_email: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    state: Optional[str] = None
    assigned_group: Optional[str] = None
    assigned_to: Optional[str] = None

class Ticket(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    number: str
    caller_name: str
    caller_email: str
    category: Optional[str]
    subcategory: Optional[str]
    short_description: str
    description: str
    state: str
    assigned_group: Optional[str]
    assigned_to: Optional[str]
    created_at: datetime
    updated_at: datetime

class ClassificationResult(BaseModel):
    category: Optional[str]
    subcategory: Optional[str]
    matched_keywords: list[str] = []
    confidence: float
    reason: str

class AIRequest(BaseModel):
    short_description: str
    description: str = ""

class AIResponse(BaseModel):
    provider: str
    category: Optional[str]
    subcategory: Optional[str]
    explanation: str
    confidence: float
