# GPX Parser

Parses We Ski GPX session files and writes the extracted data to JSON.

## Folder Structure

```
weski_group3/
├── data/        # input GPX files
├── sessions/      # generated JSON files (created automatically)
└── parser/
    ├── gpx_parser.py   # main parser logic
    ├── models.py       # TrackPoint and ParsedSession dataclasses
    └── requirements.txt
```

## How to Run

From inside the `parser/` folder:

```bash
cd weski_group3/parser
python3 gpx_parser.py
```

This will parse every `.gpx` file in `../data/` and write one `.json` file per session to `../sessions/`.

## Code Flow

1. **`parse_gpx(path)`** — entry point. Reads a GPX file, parses the XML, and returns a `ParsedSession`.
2. For each `<trkpt>` element, a **`TrackPoint`** is created with `lat`, `lon`, `ele`, `speed_mps`, and `time`.
3. **`_infer_time_bounds`** — scans all points to find the session `start_time` and `end_time`.
4. **`_compute_bounds`** — scans all points to find the geographic bounding box `(min_lat, min_lon, max_lat, max_lon)`.
5. The result is a **`ParsedSession`** containing the track name, time bounds, geo bounds, and the full list of points.
6. The `__main__` block serializes each session to JSON using a recursive `to_dict` converter that handles dataclasses and datetimes.

## Output Format

Each JSON file looks like:

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
