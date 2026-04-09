from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from data_integration.business.mapmyrun_service import process_mapmyrun_upload
from data_integration.models import MapMyRunActivity


@csrf_exempt
@require_POST
# @login_required
def upload_mapmyrun_file(request, user_id):
    # if request.user.id != user_id:
    #     return JsonResponse(
    #         {"error": "You can only upload activities for your own account."},
    #         status=403
    #     )

    file_key = "file"
    uploaded_file = request.FILES.get(file_key)

    if not uploaded_file:
        return JsonResponse(
            {"error": f"No file provided under key '{file_key}'."},
            status=400
        )

    try:
        result = process_mapmyrun_upload(uploaded_file, file_key, user_id)

        return JsonResponse(
            {
                "message": "File uploaded successfully.",
                "result": result
            },
            status=201
        )

    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# @login_required
@require_GET
def get_mapmyrun_activities(request, user_id):
    # if request.user.id != user_id:
    #     return JsonResponse(
    #         {"error": "You can only view your own activities."},
    #         status=403
    #     )

    try:
        activities = MapMyRunActivity.objects.filter(user_id=user_id).order_by("-workout_date")

        data = [
            {
                "id": activity.id,
                "user_id": activity.user_id,
                "activity_key": activity.activity_key,
                "workout_date": activity.workout_date,
                "activity_type": activity.activity_type,
                "calories_burned_kcal": activity.calories_burned_kcal,
                "distance_km": activity.distance_km,
                "workout_time_seconds": activity.workout_time_seconds,
                "avg_pace_min_per_km": activity.avg_pace_min_per_km,
                "max_pace_min_per_km": activity.max_pace_min_per_km,
                "avg_speed_kmh": activity.avg_speed_kmh,
                "max_speed_kmh": activity.max_speed_kmh,
                "created_at": activity.created_at,
            }
            for activity in activities
        ]

        return JsonResponse(
            {
                "count": len(data),
                "activities": data
            },
            status=200
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)