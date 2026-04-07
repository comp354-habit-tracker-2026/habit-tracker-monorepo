# Forecast API Contract

## Endpoint

POST /forecast

## Request

````json
{
  "userID": "123",
  "numOfDays": 5,
  "forecastType": "baseline"
}

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

{
  "error": "Invalid numOfDays",
  "status": 400
}


# Health Indicators API Contract

## Endpoint
POST /health-indicators


## Request

```json
{
  "userID": "123",
  "fromDate": "2026-04-01",
  "toDate": "2026-04-07",
  "window": "weekly"
}

{
  "userID": "123",
  "window": "weekly",
  "range": {
    "fromDate": "2026-04-01",
    "toDate": "2026-04-07"
  },
  "indicators": {
    "volume": {
      "totalDurationMinutes": 180,
      "totalDistanceKm": 12.4
    },
    "consistency": {
      "activeDays": 3,
      "totalDays": 7
    }
  },
  "healthScore": 78,
  "inactivity": {
    "inactive": false,
    "daysSinceLastActivity": 1,
    "severity": "none"
  },
  "explanations": [
    "You were active on 3 out of 7 days.",
    "Your weekly volume was 180 minutes.",
    "No inactivity alert was triggered for this time window."
  ]
}
{
  "error": "Invalid date range",
  "status": 400
}
````
