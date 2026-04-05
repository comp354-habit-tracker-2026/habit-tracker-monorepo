# App-Filtered Goal Progress

This module implements support for app-filtered goal progress, allowing the system to compute progress and status based on activities from a specific source application.

In many real-world scenarios, users may track activities across multiple platforms (e.g., Strava, MapMyRun, MyWhoosh, We Ski). This feature enables more granular analysis by restricting computations to a single selected source application when required.

### Functionality

- When a `source_app` is provided, only activities originating from that application are included in progress calculations.
- When no filter is specified, the system falls back to using all available activities.
- The implementation ensures that filtering does not affect the correctness of the default (non-filtered) behavior.
- Edge cases such as missing or empty data for a selected application are handled gracefully.

### Design Overview

The feature is designed with modularity and separation of concerns:

- `app_filter.py`  
  Responsible for filtering activities based on the `source_app` field.

- `progress_by_app.py`  
  Applies filtering logic before delegating to the progress computation.

- `progress_calculator.py`  
  Contains the core logic for computing actual value, target value, and percent completion.

- `activity_model.py`  
  Defines the structure of activity data, including fields such as distance, duration, and source application.

- `goal_model.py`  
  Represents goal definitions, including target values and time ranges.

This modular approach ensures low coupling and makes the feature easy to extend or integrate with other components (e.g., sport filtering or analytics services).
