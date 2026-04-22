import os
import uuid
import pandas as pd
from pathlib import Path
from azure.storage.blob import BlobClient
from data_integration.data.mapmyrun_repository import save_mapmyrun_activities

SUPPORTED_EXTENSIONS = (".xlsx", ".xls")
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def validate_uploaded_file(file):

    if not file:
        return False, "No file provided."

    if not file.name:
        return False, "File must have a valid name."

    file_extension = Path(file.name).suffix.lower()

    if file_extension not in SUPPORTED_EXTENSIONS:
        return False, (
            f"Unsupported file type '{file_extension}'. "
            "Please upload a .xlsx or .xls file."
        )

    if file.size == 0:
        return False, "The uploaded file is empty."

    if file.size > MAX_FILE_SIZE_BYTES:
        return False, "File is too large. Maximum size is 10 MB."

    return True, None


def upload_file_to_blob(file, file_key):

    is_valid, error_message = validate_uploaded_file(file)
    if not is_valid:
        raise ValueError(error_message)

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING is not set.")

    container_name = "filestorage"

    extension = os.path.splitext(file.name)[1].lower()
    unique_name = f"{uuid.uuid4()}{extension}"

    blob_client = BlobClient.from_connection_string(
        conn_str=connection_string,
        container_name=container_name,
        blob_name=unique_name
    )

    file.seek(0)
    blob_client.upload_blob(file, overwrite=True)

    return {
        "file_key": file_key,
        "filename": file.name,
        "stored_as": unique_name,
        "content_type": getattr(file, "content_type", None),
        "size": file.size,
        "url": blob_client.url,
    }

def parse_mapmyrun_file(uploaded_file):
    try:
        uploaded_file.seek(0)
        df = pd.read_excel(uploaded_file)

        required_columns = [
            "Workout Date",
            "Activity Type",
            "Calories Burned (kCal)",
            "Distance (km)",
            "Workout Time (seconds)",
            "Avg Pace (min/km)",
            "Max Pace (min/km)",
            "Avg Speed (km/h)",
            "Max Speed (km/h)",
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return None, f"Missing required columns: {', '.join(missing_columns)}"

        if df.empty:
            return None, "The uploaded MapMyRun file contains no activity rows."

        parsed_data = []

        for _, row in df.iterrows():
            parsed_data.append({
                "workout_date": pd.to_datetime(row["Workout Date"]).date() if pd.notna(row["Workout Date"]) else None,
                "activity_type": str(row["Activity Type"]).strip() if pd.notna(row["Activity Type"]) else None,
                "calories_burned_kcal": float(row["Calories Burned (kCal)"]) if pd.notna(row["Calories Burned (kCal)"]) else None,
                "distance_km": float(row["Distance (km)"]) if pd.notna(row["Distance (km)"]) else None,
                "workout_time_seconds": int(row["Workout Time (seconds)"]) if pd.notna(row["Workout Time (seconds)"]) else None,
                "avg_pace_min_per_km": float(row["Avg Pace (min/km)"]) if pd.notna(row["Avg Pace (min/km)"]) else None,
                "max_pace_min_per_km": float(row["Max Pace (min/km)"]) if pd.notna(row["Max Pace (min/km)"]) else None,
                "avg_speed_kmh": float(row["Avg Speed (km/h)"]) if pd.notna(row["Avg Speed (km/h)"]) else None,
                "max_speed_kmh": float(row["Max Speed (km/h)"]) if pd.notna(row["Max Speed (km/h)"]) else None,
            })

        return parsed_data, None

    except Exception as e:
        return None, f"Parsing failed: {str(e)}"


def validate_normalize_mapmyrun_data(parsed_data):

    if not parsed_data:
        return None, ["No parsed activity data was provided."]

    field_rules = {
        "workout_date": {
            "required": True,
            "converter": lambda v: v,
            "validator": None,
        },
        "activity_type": {
            "required": False,
            "converter": lambda v: str(v).strip() if v is not None else None,
            "validator": None,
        },
        "calories_burned_kcal": {
            "required": False,
            "converter": lambda v: float(v) if v is not None else None,
            "validator": lambda v: v is None or v >= 0,
            "error": "calories_burned_kcal cannot be negative",
        },
        "distance_km": {
            "required": True,
            "converter": float,
            "validator": lambda v: v >= 0,
            "error": "distance_km cannot be negative",
        },
        "workout_time_seconds": {
            "required": True,
            "converter": int,
            "validator": lambda v: v > 0,
            "error": "workout_time_seconds must be greater than 0",
        },
        "avg_pace_min_per_km": {
            "required": False,
            "converter": lambda v: float(v) if v is not None else None,
            "validator": lambda v: v is None or v >= 0,
            "error": "avg_pace_min_per_km cannot be negative",
        },
        "max_pace_min_per_km": {
            "required": False,
            "converter": lambda v: float(v) if v is not None else None,
            "validator": lambda v: v is None or v >= 0,
            "error": "max_pace_min_per_km cannot be negative",
        },
        "avg_speed_kmh": {
            "required": False,
            "converter": lambda v: float(v) if v is not None else None,
            "validator": lambda v: v is None or v >= 0,
            "error": "avg_speed_kmh cannot be negative",
        },
        "max_speed_kmh": {
            "required": False,
            "converter": lambda v: float(v) if v is not None else None,
            "validator": lambda v: v is None or v >= 0,
            "error": "max_speed_kmh cannot be negative",
        },
    }

    normalized_data = []
    errors = []

    for index, activity in enumerate(parsed_data, start=1):
        row_number = index + 1
        normalized_activity = {}
        row_has_error = False

        for field_name, rule in field_rules.items():
            raw_value = activity.get(field_name)

            is_missing = raw_value is None or str(raw_value).strip() == ""

            if rule["required"] and is_missing:
                errors.append(f"Row {row_number}: missing required field: {field_name}")
                row_has_error = True
                continue

            if is_missing:
                normalized_activity[field_name] = None
                continue

            try:
                normalized_value = rule["converter"](raw_value)
            except (ValueError, TypeError) as e:
                errors.append(f"Row {row_number}: invalid value for {field_name} - {str(e)}")
                row_has_error = True
                continue

            validator = rule.get("validator")
            if validator and not validator(normalized_value):
                errors.append(f"Row {row_number}: {rule['error']}")
                row_has_error = True
                continue

            normalized_activity[field_name] = normalized_value

        if not row_has_error:
            normalized_data.append(normalized_activity)

    if not normalized_data:
        return None, errors

    return normalized_data, errors


def process_mapmyrun_upload(uploaded_file, file_key, user_id):
    upload_result = upload_file_to_blob(uploaded_file, file_key)

    uploaded_file.seek(0)
    parsed_data, parse_error = parse_mapmyrun_file(uploaded_file)
    if parse_error:
        raise ValueError(parse_error)

    normalized_data, validation_errors = validate_normalize_mapmyrun_data(parsed_data)
    if normalized_data is None:
        raise ValueError("No valid MapMyRun activities found.")

    seen_keys = set()
    unique_data = []

    for activity in normalized_data:
        key = build_activity_key(activity)

        if key in seen_keys:
            continue  

        seen_keys.add(key)
        activity["activity_key"] = key
        unique_data.append(activity)

    saved_count = save_mapmyrun_activities(user_id, unique_data)

    return {
        "message": "File uploaded, parsed, normalized, and saved successfully.",
        "upload_result": upload_result,
        "parsed_count": len(parsed_data),
        "normalized_count": len(normalized_data),
        "saved_count": saved_count,
        "validation_errors": validation_errors,
        "normalized_preview": normalized_data[:5],
    }

def build_activity_key(activity: dict) -> str:
    date_val = str(activity.get("workout_date", "")).strip().lower()
    duration_val = str(activity.get("workout_time_seconds", "")).strip().lower()
    distance_val = str(activity.get("distance_km", "")).strip().lower()

    return f"{date_val}|{duration_val}|{distance_val}"