from local_activity_provider import get_activities
from app_filter import filter_by_app
from progress_calculator import calculate_progress


def main():

    activities = get_activities()

    # 按 provider 过滤（strava）
    strava_activities = filter_by_app(activities, "strava")

    result = calculate_progress(strava_activities, 50)

    print("Strava only:", result)

    # 不过滤（全部）
    all_activities = filter_by_app(activities)

    result_all = calculate_progress(all_activities, 50)

    print("All activities:", result_all)


if __name__ == "__main__":
    main()