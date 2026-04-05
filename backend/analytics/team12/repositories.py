from django.db.models import Avg, Count, Max, Sum

from activities.models import Activity


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
