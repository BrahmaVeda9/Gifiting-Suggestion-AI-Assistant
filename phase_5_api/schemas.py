from pydantic import BaseModel
from typing import List, Optional

class ChatIntakeRequest(BaseModel):
    user_id: str
    recipient_id: str
    message: str
    current_context: Optional[dict] = {}

class ChatIntakeResponse(BaseModel):
    confidence_score: int
    extracted_data: dict
    reply_message: str

class StrategyRequest(BaseModel):
    context: dict

class NoteRequest(BaseModel):
    recipient_name: str
    strategy_name: str
    gift_idea: str
    context: dict
