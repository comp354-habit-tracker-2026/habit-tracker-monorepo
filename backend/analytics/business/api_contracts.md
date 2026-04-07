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

