# WeSki Group 3 — GPX Parser & Ski Metrics

Parses We Ski GPX session files and computes ski metrics (distance, speed, runs, elevation).

## Folder Structure

```
weski_group3/
├── run.sh                          # run this to generate all output
├── data/                           # input .gpx files
├── sessions/                       # parsed JSON per session (auto-generated)
├── metrics_output/
│   └── all_sessions_metrics.json  # refined metrics for all sessions (auto-generated)
└── parser/
    ├── gpx_parser.py               # parses GPX → session JSON
    ├── metrics.py                  # computes metrics from session JSON
    ├── models.py                   # TrackPoint and ParsedSession dataclasses
    └── requirements.txt
```

## How to Run

From the repo root (or anywhere):

```bash
./weski_group3/run.sh
```

This will generate:
- `weski_group3/sessions/*.json` — one file per GPX session
- `weski_group3/metrics_output/all_sessions_metrics.json` — metrics for all sessions

## Accessing the Data (for other teams)

The output file other teams should read is:

```
weski_group3/metrics_output/all_sessions_metrics.json
```

Each entry in the array represents one ski session:

```json
[
  {
    "session_id": 0,
    "track_name": "Sommet Saint-Sauveur",
    "start_time": "2026-01-25T16:16:36+00:00",
    "total_distance_km": 42.3,
    "total_elevation_gain_meters": 1850.0,
    "number_of_runs": 12,
    "total_time_seconds": 5899,
    "average_speed_kmh": 18.4,
    "max_speed_kmh": 67.2
  }
]
```

You do not need to run the parser yourself or import any of our code — just read the JSON file above.
