# WeSki Group 3 — GPX Parser & Ski Metrics

Parses We Ski GPX session files, converts them to JSON, and computes per-session ski metrics.

## Folder Structure

```
weski_group3/
├── data/               # input .gpx files
├── sessions/           # parsed JSON files (auto-generated)
├── metrics_output/     # all_sessions_metrics.json (auto-generated)
└── parser/
    ├── gpx_parser.py   # parses GPX → ParsedSession JSON
    ├── metrics.py      # computes ski metrics from session JSON
    ├── models.py       # TrackPoint and ParsedSession dataclasses
    └── requirements.txt
```

## How to Run

```bash
cd weski_group3/parser
pip install -r requirements.txt
python3 gpx_parser.py
```

This will:
1. Parse every `.gpx` file in `../data/` → write one `.json` per session to `../sessions/`
2. Read all session JSONs → write `../metrics_output/all_sessions_metrics.json`

## Parsed Session Output (`sessions/*.json`)

```json
{
  "start_time": "2026-01-25T16:16:36+00:00",
  "end_time":   "2026-01-25T21:30:00+00:00",
  "track_name": "Sommet Saint-Sauveur",
  "bounds": [45.88, -74.16, 45.90, -74.15],
  "points": [
    { "time": "2026-01-25T16:16:36+00:00", "lat": 45.881, "lon": -74.159, "ele": 213.0, "speed_mps": 1.08 }
  ]
}
```

## Metrics Output (`metrics_output/all_sessions_metrics.json`)

```json
[
  {
    "session_id": 0,
    "track_name": "Sommet Saint-Sauveur",
    "start_time": "2026-01-25T16:16:36+00:00",
    "total_distance_km": 42.3,
    "total_elevation_gain_meters": 1850.0,
    "number_of_runs": 12,
    "total_time_seconds": 18864,
    "average_speed_kmh": 18.4,
    "max_speed_kmh": 67.2
  }
]
```

Runs are counted via a state machine (`IDLE → RUN → LIFT → RUN …`) triggered by downhill elevation change (> 5 m) and speed above 2.5 m/s.
