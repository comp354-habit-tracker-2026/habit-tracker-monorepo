def calculate_progress(activities, target_value):

    total_distance = 0

    for activity in activities:
        total_distance += float(activity.distance)

    if target_value == 0:
        percent = 0
    else:
        percent = (total_distance / target_value) * 100

    return {
        "actualValue": total_distance,
        "targetValue": target_value,
        "percentComplete": percent
    }