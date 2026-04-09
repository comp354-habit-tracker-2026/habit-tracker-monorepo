from activity_model import Activity


def get_activities():

    raw_data = [
        {
            "activity_type": "Running",
            "duration": 45,
            "date": "2026-01-15",
            "distance": "7.5"
        },
        {
            "activity_type": "Cycling",
            "duration": 60,
            "date": "2026-01-15",
            "provider": "strava",
            "external_id": "strava_12345",
            "distance": "25.0"
        },
        {
            "activity_type": "Walking",
            "duration": 30,
            "date": "2026-01-16",
            "provider": "mapmyrun",
            "external_id": "mapmyrun_56789",
            "distance": "3.0"
        },
        {
            "activity_type": "Running",
            "duration": 50,
            "date": "2026-01-17",
            "provider": "strava",
            "external_id": "strava_67890",
            "distance": "10.0"
        }
    ]

    activities = []

    for item in raw_data:
        activity = Activity(
            distance=item["distance"],
            duration=item["duration"],
            date=item["date"],
            provider=item.get("provider"),
            external_id=item.get("external_id"),
            activity_type=item.get("activity_type")
        )
        activities.append(activity)

    return activities