from django.db.models import Avg, Count, Max, Sum
from collections import defaultdict
from datetime import datetime, timedelta

from activities.models import Activity

def get_week_start(date):
    return date - timedelta(days=date.weekday())


class Team12AnalyticsRepository:
    def activity_statistics(self, user):
        queryset = Activity.objects.filter(user=user)
        return {
            "total_distance": queryset.aggregate(value=Sum("distance"))["value"] or 0,
            "total_calories": queryset.aggregate(value=Sum("calories"))["value"] or 0,
            "average_duration": queryset.aggregate(value=Avg("duration"))["value"] or 0,
            "activity_count": queryset.count(),
        }

    def personal_records(self, user):
        queryset = Activity.objects.filter(user=user)
        records = queryset.aggregate(
            best_distance=Max("distance"),
            best_duration=Max("duration"),
            best_calories=Max("calories"),
        )
        return {
            "best_distance": float(records["best_distance"]) if records["best_distance"] is not None else 0,
            "best_duration": records["best_duration"] or 0,
            "best_calories": records["best_calories"] or 0,
        }

    def activity_type_breakdown(self, user):
        queryset = Activity.objects.filter(user=user)
        return [
            {
                "activity_type": row["activity_type"],
                "activity_count": row["count"],
                "total_distance": row["total_distance"] or 0,
                "total_calories": row["total_calories"] or 0,
                "total_duration": row["total_duration"] or 0,
            }
            for row in queryset.values("activity_type").annotate(
                count=Count("id"),
                total_distance=Sum("distance"),
                total_calories=Sum("calories"),
                total_duration=Sum("duration"),
            ).order_by("activity_type")
        ]

    def weekly_summary(self, user, from_param, to_param, activity_type=None):
        try:
            from_date = datetime.strptime(from_param, "%Y-%m").date()
            to_date = datetime.strptime(to_param, "%Y-%m").date()
        except ValueError:
            raise ValueError("Invalid date format YYYY-MM")

        to_date = (to_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        if to_date < from_date:
            raise ValueError("'to' must be >= 'from'")

        queryset = Activity.objects.filter(
            user=user,
            date__gte=from_date,
            date__lte=to_date
        )

        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)

        weekly_data = defaultdict(lambda: {
            "workoutCount": 0,
            "totalDuration": 0,
            "totalDistance": 0,
            "totalSpeed": 0,
            "speedCount": 0,
        })

        for activity in queryset:
            week_start = get_week_start(activity.date).isoformat()
            week = weekly_data[week_start]

            week["workoutCount"] += 1
            week["totalDuration"] += activity.duration or 0
            week["totalDistance"] += float(activity.distance or 0)

            if activity.distance and activity.distance > 0:
                speed = activity.duration / (float(activity.distance) / 1000)
                week["totalSpeed"] += speed
                week["speedCount"] += 1

        result = []
        current = from_date
        seen_weeks = set()

        while current <= to_date:
            week_start = get_week_start(current).isoformat()

            if week_start not in seen_weeks:
                data = weekly_data.get(week_start)

                if not data:
                    result.append({
                        "weekStart": week_start,
                        "workoutCount": 0,
                        "totalDuration": 0,
                        "totalDistance": 0,
                        "avgSpeed": 0,
                        "avgHR": None,
                    })
                else:
                    avg_speed = (
                        data["totalSpeed"] / data["speedCount"]
                        if data["speedCount"] > 0 else 0
                    )

                    result.append({
                        "weekStart": week_start,
                        "workoutCount": data["workoutCount"],
                        "totalDuration": data["totalDuration"],
                        "totalDistance": data["totalDistance"],
                        "avgSpeed": avg_speed,
                        "avgHR": None,
                    })

                seen_weeks.add(week_start)

            current += timedelta(days=7)

        return result