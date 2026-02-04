# Group 14 — Forecasting Engine

## Overview
This service provides short-term forecasts from historical activity data (e.g., distance per day).
It is designed to be called by other services (e.g., Analytics API / Goals) via HTTP.

## What this service does
- Accepts a time series of historical daily values for a target metric.
- Returns a forecast for the next N days.
- Provides a simple baseline method (repeat_last) and can be extended with more methods.

## What this service does NOT do
- Does not store data (no database).
- Does not authenticate users (handled elsewhere).
- Does not call external fitness APIs directly (handled by ingestion teams).

## API Endpoints

### Health Check
**GET /health**

Response:
```json
{
  "status": "ok",
  "service": "group-14-forecasting"
}
```
Forecast

POST /forecast
| Field        | Type   | Description                                      |
| ------------ | ------ | ------------------------------------------------ |
| user_id      | string | User identifier                                  |
| target       | string | One of: distance_km, duration_min, calories_kcal |
| horizon_days | int    | Number of future days to predict (1–30)          |
| history      | array  | List of past daily values                        |

Each history entry:
```json
{
  "date": "YYYY-MM-DD",
  "value": number
}
```
Minimum history length is 3 days.

Example Request:
```json
{
  "user_id": "u1",
  "target": "distance_km",
  "horizon_days": 7,
  "history": [
    { "date": "2026-02-01", "value": 4.2 },
    { "date": "2026-02-02", "value": 0.0 },
    { "date": "2026-02-03", "value": 3.1 }
  ]
}

```

Example Response
```json
{
  "user_id": "u1",
  "target": "distance_km",
  "horizon_days": 7,
  "method": "repeat_last",
  "forecast": [
    { "date": "2026-02-04", "value": 3.1 },
    { "date": "2026-02-05", "value": 3.1 }
  ],
  "summary": {
    "predicted_total": 21.7
  }
}

```

How to run locally windows powershell from this directory:

py -3.12 -m venv .venv

.\\.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt

python -m pytest -q .\tests

python -m uvicorn app.main:app --port 8014

then check:
http://127.0.0.1:8014/health
http://127.0.0.1:8014/docs

How to run a request in powershell:

first health check: 

curl.exe http://127.0.0.1:8014/health

how to send request in powershell:

<img width="646" height="375" alt="image" src="https://github.com/user-attachments/assets/a3bcac34-897d-4c74-810e-6869363b8de4" />








