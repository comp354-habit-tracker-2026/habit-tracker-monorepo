# Forecast API Contract

## Endpoint

POST /forecast

## Request

```json
{
  "userID": "123",
  "numOfDays": 5,
  "forecastType": "baseline"
}
```

## Response (Success)

```json
{
  "userID": "123",
  "forecastType": "baseline",
  "forecast": [
    { "date": "2026-04-01", "predictedValue": 5.0 }
  ],
  "metrics": {
    "mae": 0.0,
    "rmse": 0.0
  }
}
```

## Response (Error)

```json
{
  "error": "Invalid numOfDays",
  "status": 400
}
```


# Health Indicators API Contract

## Endpoint

POST /health-indicators

## Request

```json
{
  "user_id": "123",
  "from_date": "2026-04-01T00:00:00",
  "to_date": "2026-04-07T23:59:59",
  "window": "weekly",
  "target_workouts": 3,
  "alerts": []
}
```

## Response (Success)

```json
{
  "status": "success",
  "data": {
    "user_id": "123",
    "indicators": {
      "volume": {
        "total_volume": 180.0,
        "workout_count": 3,
        "interpretation": "Low to moderate workout volume (V = 180.0)"
      },
      "consistency": {
        "consistency_score": 75.0,
        "workouts_completed": 3,
        "target_workouts": 3,
        "interpretation": "Good: Strong consistency with minor irregularities (C = 75.0%)"
      }
    },
    "health_score": {
      "score": 78.0,
      "score_range": "Good",
      "explanation": "Health score computed from: volume, consistency, inactive. Final score = 78.0."
    },
    "inactivity": {
      "inactive": false,
      "days_since_last_activity": 1,
      "severity": "none",
      "message": "Last activity was 1 day(s) ago."
    },
    "alerts": [],
    "messages": [
      "Volume value is 180.0.",
      "Consistency value is 75.0.",
      "Inactive value is 0.",
      "Health score is 78.0.",
      "Score range: Good.",
      "Last activity was 1 day(s) ago."
    ]
  }
}
```

## Response (Error – invalid date range)

```json
{
  "status": "error",
  "message": "from_date must not be later than to_date"
}
```

## Response (Error – data service unavailable)

```json
{
  "status": "error",
  "message": "Activity data service unavailable: <reason>"
}
```
