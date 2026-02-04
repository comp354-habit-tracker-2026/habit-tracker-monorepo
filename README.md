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

## API
### Health check
`GET /health`

Response:
```json
{"status":"ok","service":"group-14-forecasting"}
