from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional, Literal

Target = Literal["distance_km", "duration_min", "calories_kcal"]

class HistoryPoint(BaseModel):
    date: date
    value: float = Field(..., description="Value for target on this date")

class ForecastRequest(BaseModel):
    user_id: str
    target: Target
    horizon_days: int = Field(7, ge=1, le=30)
    history: List[HistoryPoint]

class ForecastPoint(BaseModel):
    date: date
    value: float
    low: Optional[float] = None
    high: Optional[float] = None

class ForecastResponse(BaseModel):
    user_id: str
    target: Target
    horizon_days: int
    method: str
    forecast: List[ForecastPoint]
    summary: dict
