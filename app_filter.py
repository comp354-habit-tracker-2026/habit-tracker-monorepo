def filter_by_app(activities, provider=None):

    if provider is None:
        return activities

    filtered = []

    for activity in activities:
        if activity.provider == provider:
            filtered.append(activity)

    return filtered