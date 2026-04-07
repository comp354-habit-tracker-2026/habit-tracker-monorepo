# GPX Parser & Ski Metrics

Parses We Ski GPX session files, validates the data, and computes ski metrics.

## Folder Structure

```
weski_group3/
├── run.sh                          # run this to generate all output
├── data/                           # input .gpx files
├── sessions/                       # parsed JSON per session (auto-generated)
├── metrics_output/
│   └── all_sessions_metrics.json  # metrics for all sessions (auto-generated)
└── parser/
    ├── gpx_parser.py               # parses GPX → session JSON
    ├── metrics.py                  # computes ski metrics from session JSON
    ├── validation.py               # cleans GPS data (spike detection, interpolation)
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

## Code Flow

1. **`gpx_parser.py`** — entry point. For each `.gpx` file in `../data/`:
   - Parses the XML and creates a `ParsedSession` containing a list of `TrackPoint` objects (`lat`, `lon`, `ele`, `speed_mps`, `time`)
   - Infers `start_time`/`end_time` and geographic bounding box
   - Writes one `.json` file per session to `../sessions/`

2. **`validation.py`** — cleans each parsed session before metrics:
   - Validates coordinate ranges
   - Detects and removes GPS spikes (sudden implausible jumps)
   - Interpolates missing coordinates using linear time-based estimation

3. **`metrics.py`** — computes ski metrics from the cleaned session data:
   - Haversine distance calculation
   - Run counting via a state machine (`IDLE → RUN → LIFT`)
   - Accumulates: total distance, elevation gain, max speed, average speed, run count
   - Writes `all_sessions_metrics.json` to `../metrics_output/`

## Output Format

**Per-session JSON** (`sessions/*.json`):

```json
{
  "start_time": "2026-01-25T16:16:36+00:00",
  "end_time": "2026-01-25T21:30:00+00:00",
  "track_name": "Sommet Saint-Sauveur",
  "bounds": [45.88, -74.16, 45.90, -74.15],
  "points": [
    { "time": "2026-01-25T16:16:36+00:00", "lat": 45.881, "lon": -74.159, "ele": 213.0, "speed_mps": 1.08 }
  ]
}
```

**Consolidated metrics** (`metrics_output/all_sessions_metrics.json`):

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
