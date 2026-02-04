from fastapi import FastAPI, HTTPException
from app.schemas import ForecastRequest, ForecastResponse
from .methods.baseline import repeat_last

app = FastAPI(
    title="Group 14 - Forecasting Engine",
    version="0.1.0"
)

@app.get("/health")
def health():
    return {"status": "ok", "service": "group-14-forecasting"}

@app.post("/forecast", response_model=ForecastResponse)
def forecast(req: ForecastRequest):
    if len(req.history) < 3:
        raise HTTPException(status_code=400, detail="Need at least 3 historical points")

    fc = repeat_last(req.history, req.horizon_days)

    return ForecastResponse(
        user_id=req.user_id,
        target=req.target,
        horizon_days=req.horizon_days,
        method="repeat_last",
        forecast=fc,
        summary={"predicted_total": sum(p.value for p in fc)}
    )
