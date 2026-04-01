from pydantic import BaseModel
from typing import List, Optional

class ExtractedGiftingData(BaseModel):
    budget: Optional[str] = None
    preference_type: Optional[str] = None  # Expected values: "wow" or "utility"
    frustrations: List[str] = []
    has_relationship_context: bool = False
