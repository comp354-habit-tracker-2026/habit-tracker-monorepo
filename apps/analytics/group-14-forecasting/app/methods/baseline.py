from datetime import timedelta
from typing import List
from app.schemas import HistoryPoint, ForecastPoint

def repeat_last(history: List[HistoryPoint], horizon_days: int) -> List[ForecastPoint]:
    """
    Baseline forecast: repeat the last observed value for each future day.
    """
    if not history:
        return []

    last = history[-1]
    out: List[ForecastPoint] = []

    for i in range(1, horizon_days + 1):
        out.append(ForecastPoint(date=last.date + timedelta(days=i), value=last.value))

    return out
