from data_integration.models import MapMyRunActivity


def save_mapmyrun_activities(user_id, activities):
    existing_keys = set(
        MapMyRunActivity.objects
        .filter(user_id=user_id)
        .values_list("activity_key", flat=True)
    )

    saved_count = 0
    skipped_count = 0

    for activity in activities:
        activity_key = activity.get("activity_key")

        if activity_key in existing_keys:
            skipped_count += 1
            continue

        MapMyRunActivity.objects.create(
            user_id=user_id,
            activity_key=activity_key,
            workout_date=activity.get("workout_date"),
            activity_type=activity.get("activity_type"),
            calories_burned_kcal=activity.get("calories_burned_kcal"),
            distance_km=activity.get("distance_km"),
            workout_time_seconds=activity.get("workout_time_seconds"),
            avg_pace_min_per_km=activity.get("avg_pace_min_per_km"),
            max_pace_min_per_km=activity.get("max_pace_min_per_km"),
            avg_speed_kmh=activity.get("avg_speed_kmh"),
            max_speed_kmh=activity.get("max_speed_kmh"),
        )

        saved_count += 1
        existing_keys.add(activity_key)

    return {
        "saved_count": saved_count,
        "skipped_count": skipped_count,
    }