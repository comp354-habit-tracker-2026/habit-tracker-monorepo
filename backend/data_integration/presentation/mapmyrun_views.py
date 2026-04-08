from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from data_integration.business.mapmyrun_service import upload_file_to_blob


@csrf_exempt
@require_POST
def upload_mapmyrun_file(request):
    file_key = "file"
    uploaded_file = request.FILES.get(file_key)

    if not uploaded_file:
        return JsonResponse(
            {"error": f"No file provided under key '{file_key}'."},
            status=400
        )

    try:
        result = upload_file_to_blob(uploaded_file, file_key)

        return JsonResponse(
            {
                "message": "File uploaded successfully.",
                "result": result
            },
            status=201
        )

    except ValueError as e:
        return JsonResponse(
            {"error": str(e)},
            status=400
        )

    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500
        )