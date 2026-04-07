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
# habit-tracker-monorepo

## Stale PR Labeler

This repo uses an automated GitHub Action to manage stale pull requests.

### How it works
Pull requests with no activity (comments, commits, or reviews) for **14 days**
are automatically labeled as `stale` and the author is notified via a comment.
The stale label is removed if the PR becomes active again.

### Exemption Label
If a PR should **not** be marked as stale (e.g. it's intentionally on hold),
add the `do-not-stale` label to it. The action will skip that PR entirely.

## Code owners PR Review Assignment
This repo contains a `CODEOWNERS` file that assigns groups to a PR when it is created.
Reviewers can be set by a group to protect their features from breaking during shared file merges.

### How it works
When a pull request is created, codeowner group(s) are automatically assigned to review the pull request.
The groups are relevant to files changed in the pull request.
The pull request must receive a review from a member of the assigned group(s) before it can be closed.

### How to add a codeowner
Ownership of a folder or a file can be set by adding a line inside the `CODEOWNERS` file.
A single line in the `CODEOWNERS` file can target either a (set of) file(s) or a folder.

The `CODEOWNERS` file has some assignments prepared that need specifications on file and folder names, placeholdered by `{...}`.
Otherwise, teams can specify other files and folders by themselves using documentation provided below.

Team names are simply `Group-xx` for groups 1-4 and `group-xx` for groups 5-27.
Do be mindful of capitalization when assigning ownership.
The lines for assigning codeowners are as follows:

#### Folder ownership:
`/{path}/{from}/{root}/{folder}/ @comp354-habit-tracker-2026/{team}`

#### File ownership:
`/{path}/{from}/{root}/{file}.{ext} @comp354-habit-tracker-2026/{team}` for single files.

`/{path}/{from}/{root}/*.{ext} @comp354-habit-tracker-2026/{team}` for all files of the same extension.

#### Multiple team ownership:
`/{path}/{from}/{root}/{folder}/ @comp354-habit-tracker-2026/{team1} @comp354-habit-tracker-2026/{team2}`
for a folder shared between 2 groups. This can also be done with files.
Setting ownership through multiple lines will not add but override ownership.
This will require a review from those 2 (or more) groups.

Further documentation can be found [here](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners).

## PR Labeling Automation

This repository uses multiple GitHub Actions to automatically label pull requests.

### How it works
- **Path-based labels** are applied based on changed files (for example, `frontend/` or `backend/`). The workflow is defined in [`.github/workflows/labeler.yml`](.github/workflows/labeler.yml), and the matching rules are configured in [`.github/labeler.yml`](.github/labeler.yml).
- **PR size labels** (`XS`, `S`, `M`, `L`, `XL`) are added based on the number of lines changed. This workflow is defined in [`.github/workflows/pr-size-labeler.yml`](.github/workflows/pr-size-labeler.yml).

### Purpose
- Helps reviewers quickly understand the scope of a PR
- Improves organization and review efficiency
- Makes it clearer which workflow/config to update when labeling rules need to change
