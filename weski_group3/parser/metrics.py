import json
from pathlib import Path
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
from typing import List, Dict, Any, Optional

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the distance between two points using the Haversine formula.
    """
    R = 6371.0  # Radius of the Earth in kilometers

    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance * 1000  # convert to meters

def calculate_metrics(points: List[Dict[str, Any]], track_name: Optional[str]) -> Dict[str, Any]:
    """
    Calculates various metrics from a list of track points, including the number of runs.
    """

    total_distance_meters = 0.0
    total_elevation_gain = 0.0
    max_speed_mps = 0.0
    speeds_mps = []
    number_of_runs = 0

    # --- State Machine for Run Counting ---
    # States: 'IDLE', 'LIFT', 'RUN'
    current_state = 'IDLE' 
    
    # minimum speed in m/s to be considered skiing
    RUN_SPEED_THRESHOLD_MPS = 2.5 
    # vertical change in meters to confirm state change
    ELEVATION_CHANGE_THRESHOLD = 5 

    # Sort points by time to ensure correct order
    if not points:
        # Handle case with no points
        return {
            "track_name": track_name,
            "start_time": None,
            "total_elevation_gain_meters": 0,
            "total_distance_km": 0,
            "number_of_runs": 0,
            "total_time_seconds": 0,
            "average_speed_kmh": 0,
            "max_speed_kmh": 0
        }
        
    points.sort(key=lambda p: datetime.fromisoformat(p['time']))

    for i in range(1, len(points)):
        p1 = points[i-1]
        p2 = points[i]

        # ensure points have the necessary data
        if not all(k in p1 and p1[k] is not None and k in p2 and p2[k] is not None for k in ['lat', 'lon', 'ele', 'speed_mps']):
            continue

        # calculations for the current segment 
        segment_distance = calculate_distance(p1['lat'], p1['lon'], p2['lat'], p2['lon'])
        elevation_change = p2['ele'] - p1['ele']
        current_speed_mps = p2['speed_mps']

        # check if a run has started.
        if current_state in ['IDLE', 'LIFT']:
            # run starts if we are going downhill and fast enough.
            if elevation_change < -ELEVATION_CHANGE_THRESHOLD and current_speed_mps > RUN_SPEED_THRESHOLD_MPS:
                current_state = 'RUN'
                number_of_runs += 1 # new run has begun
        
        # If we are in a run, check if we've switched to a lift.
        elif current_state == 'RUN':
            
            if elevation_change > ELEVATION_CHANGE_THRESHOLD:
                current_state = 'LIFT'

        # accumulate other metrics
        total_distance_meters += segment_distance
        if elevation_change > 0:
            total_elevation_gain += elevation_change
        
        speeds_mps.append(current_speed_mps)
        if current_speed_mps > max_speed_mps:
            max_speed_mps = current_speed_mps

    start_time = datetime.fromisoformat(points[0]['time']) if points else None
    end_time = datetime.fromisoformat(points[-1]['time']) if points else None
    total_time_seconds = (end_time - start_time).total_seconds() if start_time and end_time else 0
    
    total_distance_km = total_distance_meters / 1000
    mps_to_kmh = 3.6
    average_speed_kmh = (sum(speeds_mps) / len(speeds_mps)) * mps_to_kmh if speeds_mps else 0.0
    max_speed_kmh = max_speed_mps * mps_to_kmh

    return {
        "track_name": track_name,
        "start_time": start_time.isoformat() if start_time else None,
        "total_elevation_gain_meters": total_elevation_gain,
        "total_distance_km": total_distance_km,
        "number_of_runs": number_of_runs,
        "total_time_seconds": total_time_seconds,
        "average_speed_kmh": average_speed_kmh,
        "max_speed_kmh": max_speed_kmh
    }

def process_sessions():
    """
    Processes all session JSON files and generates a single metrics file for all sessions.
    """
    
    sessions_dir = Path("../sessions")
    output_dir = Path("../metrics_output")
    output_dir.mkdir(exist_ok=True)

    if not sessions_dir.is_dir():
        print(f"Error: Could not find the sessions directory at '{sessions_dir.resolve()}'.")
        print("Please ensure the 'sessions' folder exists alongside the 'parser' folder.")
        return

    all_sessions_metrics = []
    session_id_counter = 0

    # Sort the files to ensure a consistent order for session IDs
    for session_file in sorted(sessions_dir.glob("*.json")):
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        points = session_data.get("points", [])
        track_name = session_data.get("track_name")


        metrics = calculate_metrics(points, track_name)
        
        metrics["session_id"] = session_id_counter
        
        
        all_sessions_metrics.append(metrics)
        
        print(f"Processed session {session_id_counter}: {session_file.name}")
        session_id_counter += 1

    if not all_sessions_metrics:
        print(f"No .json files found in the sessions directory: '{sessions_dir.resolve()}'")
        return

    output_file = output_dir / "all_sessions_metrics.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_sessions_metrics, f, indent=2)
        
    print(f"\nSuccessfully generated consolidated metrics file at: {output_file}")

if __name__ == "__main__":
    process_sessions()