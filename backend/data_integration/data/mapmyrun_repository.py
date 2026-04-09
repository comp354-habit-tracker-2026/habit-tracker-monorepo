from data_integration.models import MapMyRunActivity


def build_activity_key(activity: dict) -> str:
    date_val = str(activity.get("date", activity.get("Date", ""))).strip().lower()
    duration_val = str(activity.get("duration", activity.get("Duration", ""))).strip().lower()
    distance_val = str(activity.get("distance", activity.get("Distance", ""))).strip().lower()

    return f"{date_val}_{duration_val}_{distance_val}"


def save_mapmyrun_activities(user_id, normalized_data):
    if not normalized_data:
        return 0

    activities_to_create = []

    for activity in normalized_data:
        activities_to_create.append(
            MapMyRunActivity(
                user_id=user_id,
                activity_key=build_activity_key(activity),
                workout_date=activity["workout_date"],
                activity_type=activity.get("activity_type"),
                calories_burned_kcal=activity.get("calories_burned_kcal"),
                distance_km=activity["distance_km"],
                workout_time_seconds=activity["workout_time_seconds"],
                avg_pace_min_per_km=activity.get("avg_pace_min_per_km"),
                max_pace_min_per_km=activity.get("max_pace_min_per_km"),
                avg_speed_kmh=activity.get("avg_speed_kmh"),
                max_speed_kmh=activity.get("max_speed_kmh"),
            )
        )

    MapMyRunActivity.objects.bulk_create(activities_to_create)

    return len(activities_to_create)