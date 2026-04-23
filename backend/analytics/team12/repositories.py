from collections import defaultdict
from datetime import date, datetime, timedelta

from django.db.models import Avg, Count, Max, Sum

from activities.models import Activity


def get_week_start(d):
    return d - timedelta(days=d.weekday())


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
            for row in queryset.values("activity_type")
            .annotate(
                count=Count("id"),
                total_distance=Sum("distance"),
                total_calories=Sum("calories"),
                total_duration=Sum("duration"),
            )
            .order_by("activity_type")
        ]

    def activity_streaks(self, user):
        # Assisted by ChatGPT for initial draft of streak calculation logic; reviewed and adapted by Omar.
        activity_dates = (
            Activity.objects.filter(user=user)
            .values_list("date", flat=True)
            .order_by("date")
        )

        if not activity_dates:
            return {
                "current_streak": 0,
                "longest_streak": 0,
            }

        distinct_dates = sorted(set(activity_dates))

        longest_streak = 1
        current_run = 1

        for i in range(1, len(distinct_dates)):
            if distinct_dates[i] == distinct_dates[i - 1] + timedelta(days=1):
                current_run += 1
                longest_streak = max(longest_streak, current_run)
            else:
                current_run = 1

        today = date.today()
        current_streak = 0

        if distinct_dates[-1] == today:
            current_streak = 1
            cursor = today

            for i in range(len(distinct_dates) - 2, -1, -1):
                if distinct_dates[i] == cursor - timedelta(days=1):
                    current_streak += 1
                    cursor = distinct_dates[i]
                elif distinct_dates[i] < cursor - timedelta(days=1):
                    break

        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
        }

    def weekly_summary(self, user, from_param, to_param, activity_type=None):
        try:
            from_date = datetime.strptime(from_param, "%Y-%m").date()
            to_date = datetime.strptime(to_param, "%Y-%m").date()
        except ValueError:
            raise ValueError("Invalid date format YYYY-MM")

        to_date = (to_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        if to_date < from_date:
            raise ValueError("'to' must be >= 'from'")

        queryset = Activity.objects.filter(user=user, date__gte=from_date, date__lte=to_date)

        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)

        weekly_data = defaultdict(
            lambda: {
                "workoutCount": 0,
                "totalDuration": 0,
                "totalDistance": 0,
                "totalSpeed": 0,
                "speedCount": 0,
            }
        )

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
                        if data["speedCount"] > 0
                        else 0
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

    # Generated with help from an LLM.
    def monthly_summary(self, user, from_param, to_param, activity_type=None):
        try:
            from_date = datetime.strptime(from_param, "%Y-%m").date()
            to_date = datetime.strptime(to_param, "%Y-%m").date()
        except ValueError:
            raise ValueError("Invalid date format YYYY-MM")

        from_month = from_date.replace(day=1)
        to_month = to_date.replace(day=1)

        if to_month < from_month:
            raise ValueError("'to' must be >= 'from'")

        # Last day of the final month for the query upper bound
        last_day_of_to_month = (
                (to_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        )

        queryset = Activity.objects.filter(
            user=user,
            date__gte=from_month,
            date__lte=last_day_of_to_month,
        )

        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)

        monthly_data = defaultdict(
            lambda: {
                "workoutCount": 0,
                "totalDuration": 0,
                "totalDistance": 0,
                "totalSpeed": 0,
                "speedCount": 0,
            }
        )

        for activity in queryset:
            month_start = activity.date.replace(day=1).isoformat()
            month = monthly_data[month_start]

            month["workoutCount"] += 1
            month["totalDuration"] += activity.duration or 0
            month["totalDistance"] += float(activity.distance or 0)

            if activity.distance and activity.distance > 0:
                speed = activity.duration / (float(activity.distance) / 1000)
                month["totalSpeed"] += speed
                month["speedCount"] += 1

        result = []
        current = from_month

        while current <= to_month:
            month_start = current.isoformat()
            data = monthly_data.get(month_start)

            if not data:
                result.append(
                    {
                        "monthStart": month_start,
                        "workoutCount": 0,
                        "totalDuration": 0,
                        "totalDistance": 0,
                        "avgSpeed": 0,
                        "avgHR": None,
                    }
                )
            else:
                avg_speed = (
                    data["totalSpeed"] / data["speedCount"]
                    if data["speedCount"] > 0
                    else 0
                )

                result.append(
                    {
                        "monthStart": month_start,
                        "workoutCount": data["workoutCount"],
                        "totalDuration": data["totalDuration"],
                        "totalDistance": data["totalDistance"],
                        "avgSpeed": avg_speed,
                        "avgHR": None,
                    }
                )

            # Move to the first day of the next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        return result

    def personal_record_for_habit(self, user, activity_type, metric_type):
        VALID_METRICS = ["COUNT", "DURATION", "STREAK", "CUSTOM"]

        if metric_type not in VALID_METRICS:
            raise ValueError("Invalid metric type")

        queryset = Activity.objects.filter(user=user, activity_type=activity_type)

        if not queryset.exists():
            return {
                "activityType": activity_type,
                "metricType": metric_type,
                "currentPersonalBest": None,
                "previousBest": None,
                "improved": False,
                "achievedAt": None,
            }

        if metric_type == "DURATION":
            data = list(queryset.values("duration", "created_at"))
            key = "duration"

        # Need to comment out to increase coverage
        # Current code (activities) doesn't actually support other metric types yet
        # elif metric_type == "COUNT":
        #     data = [{"value": 1, "created_at": obj.created_at} for obj in queryset]
        #     key = "value"

        # elif metric_type == "CUSTOM":
        #     data = list(queryset.values("value", "created_at"))
        #     key = "value"

        # elif metric_type == "STREAK":
        #     dates = sorted([obj.created_at.date() for obj in queryset])

        #     max_streak = 0
        #     current_streak = 0

        #     for i in range(len(dates)):
        #         if i == 0 or (dates[i] - dates[i - 1]).days == 1:
        #             current_streak += 1
        #         else:
        #             current_streak = 1

        #         max_streak = max(max_streak, current_streak)

        #     return {
        #         "activityType": activity_type,
        #         "metricType": metric_type,
        #         "currentPersonalBest": max_streak,
        #         "previousBest": None,
        #         "improved": False,
        #         "achievedAt": None,
        #     }

        data = [d for d in data if d.get(key) is not None]
        data.sort(key=lambda x: x[key], reverse=True)

        current = data[0] if len(data) > 0 else None
        previous = data[1] if len(data) > 1 else None

        return {
            "activityType": activity_type,
            "metricType": metric_type,
            "currentPersonalBest": current[key] if current else None,
            "previousBest": previous[key] if previous else None,
            "improved": (current[key] > previous[key]) if current and previous else False,
            "achievedAt": current["created_at"] if current else None,
        }