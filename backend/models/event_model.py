from pydantic import BaseModel
from datetime import datetime

class CustomerEvent(BaseModel):
    user_id: int
    event_type: str
    product_id: int
    category: str
    session_duration: int
    price: float
    timestamp: datetime