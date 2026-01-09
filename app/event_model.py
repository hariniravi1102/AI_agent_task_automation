from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
import uuid

class Event(BaseModel):
    event_id: str = str(uuid.uuid4())
    event_type: str
    source: str
    payload: Dict[str, Any]
    timestamp: datetime = datetime.utcnow()
