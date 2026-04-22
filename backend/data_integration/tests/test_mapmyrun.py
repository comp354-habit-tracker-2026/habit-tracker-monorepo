import io
import json
from datetime import date
from io import BytesIO

import pandas as pd
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory

from data_integration.business import mapmyrun_service
from data_integration.business.mapmyrun_service import (
    MAX_FILE_SIZE_BYTES,
    build_activity_key,
    parse_mapmyrun_file,
    process_mapmyrun_upload,
    upload_file_to_blob,
    validate_normalize_mapmyrun_data,
    validate_uploaded_file,
)
from data_integration.data.mapmyrun_repository import save_mapmyrun_activities
from data_integration.models import MapMyRunActivity
from data_integration.presentation.mapmyrun_views import (
    get_mapmyrun_activities,
    upload_mapmyrun_file,
)


# =========================================================
# Helpers
# =========================================================

class FakeUploadFile(BytesIO):
    def __init__(
        self,
        content: bytes,
        name: str | None,
        content_type: str = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ):
        super().__init__(content)
        self.name = name
        self.size = len(content)
        self.content_type = content_type


class DummyBlobClient:
    def __init__(self):
        self.url = "https://fake.blob.core.windows.net/filestorage/fake-id.xlsx"
        self.upload_called = False
        self.upload_position = None

    def upload_blob(self, file_obj, overwrite=False):
        self.upload_called = True
        self.upload_position = file_obj.tell()


def make_valid_activity(**overrides):
    activity = {
        "workout_date": "2024-01-15",
        "activity_type": " Run ",
        "calories_burned_kcal": "450.5",
        "distance_km": "10.2",
        "workout_time_seconds": "3600",
        "avg_pace_min_per_km": "5.5",
        "max_pace_min_per_km": "4.8",
        "avg_speed_kmh": "10.9",
        "max_speed_kmh": "12.3",
    }
    activity.update(overrides)
    return activity


REQUIRED_COLUMNS = [
    "Workout Date",
    "Activity Type",
    "Calories Burned (kCal)",
    "Distance (km)",
    "Workout Time (seconds)",
    "Avg Pace (min/km)",
    "Max Pace (min/km)",
    "Avg Speed (km/h)",
    "Max Speed (km/h)",
]


def make_excel_file(rows):
    df = pd.DataFrame(rows, columns=REQUIRED_COLUMNS)
    file_obj = io.BytesIO()
    df.to_excel(file_obj, index=False)
    file_obj.seek(0)
    file_obj.name = "mapmyrun.xlsx"
    file_obj.size = len(file_obj.getvalue())
    file_obj.content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return file_obj


@pytest.fixture
def rf():
    return RequestFactory()


# =========================================================
# validate_uploaded_file tests
# =========================================================

def test_no_file():
    is_valid, error = validate_uploaded_file(None)
    assert is_valid is False
    assert error == "No file provided."


def test_missing_filename():
    file = FakeUploadFile(b"data", "")
    is_valid, error = validate_uploaded_file(file)
    assert is_valid is False
    assert error == "File must have a valid name."


def test_invalid_extension():
    file = FakeUploadFile(b"data", "file.txt")
    is_valid, error = validate_uploaded_file(file)
    assert is_valid is False
    assert "Unsupported file type" in error
    assert ".xlsx or .xls" in error


def test_valid_extensions_case_insensitive():
    for name in ["file.xlsx", "file.xls", "FILE.XLSX", "FILE.XLS"]:
        file = FakeUploadFile(b"data", name)
        is_valid, error = validate_uploaded_file(file)
        assert is_valid is True
        assert error is None


def test_empty_file():
    file = FakeUploadFile(b"", "file.xlsx")
    is_valid, error = validate_uploaded_file(file)
    assert is_valid is False
    assert error == "The uploaded file is empty."


def test_file_too_large():
    file = FakeUploadFile(b"x" * (MAX_FILE_SIZE_BYTES + 1), "file.xlsx")
    is_valid, error = validate_uploaded_file(file)
    assert is_valid is False
    assert error == "File is too large. Maximum size is 10 MB."


def test_file_at_max_size():
    file = FakeUploadFile(b"x" * MAX_FILE_SIZE_BYTES, "file.xlsx")
    is_valid, error = validate_uploaded_file(file)
    assert is_valid is True
    assert error is None


# =========================================================
# upload_file_to_blob tests
# =========================================================

def test_upload_fails_invalid_file():
    file = FakeUploadFile(b"", "file.xlsx")

    with pytest.raises(ValueError, match="The uploaded file is empty."):
        upload_file_to_blob(file, "key-1")


def test_upload_missing_env(monkeypatch):
    monkeypatch.delenv("AZURE_STORAGE_CONNECTION_STRING", raising=False)

    file = FakeUploadFile(b"valid", "file.xlsx")

    with pytest.raises(ValueError, match="AZURE_STORAGE_CONNECTION_STRING is not set."):
        upload_file_to_blob(file, "key-2")


def test_upload_success(monkeypatch):
    monkeypatch.setenv("AZURE_STORAGE_CONNECTION_STRING", "fake-conn")
    dummy_client = DummyBlobClient()

    def fake_from_connection_string(conn_str, container_name, blob_name):
        return dummy_client

    monkeypatch.setattr(
        mapmyrun_service.BlobClient,
        "from_connection_string",
        fake_from_connection_string,
    )
    monkeypatch.setattr(mapmyrun_service.uuid, "uuid4", lambda: "fixed-id")

    file = FakeUploadFile(b"content", "file.xlsx")
    file.read()  # move pointer so we verify seek(0) happened

    result = upload_file_to_blob(file, "key-123")

    assert dummy_client.upload_called is True
    assert dummy_client.upload_position == 0
    assert result["file_key"] == "key-123"
    assert result["filename"] == "file.xlsx"
    assert result["stored_as"] == "fixed-id.xlsx"
    assert result["size"] == len(b"content")
    assert result["url"] == dummy_client.url


def test_upload_extension_preserved(monkeypatch):
    monkeypatch.setenv("AZURE_STORAGE_CONNECTION_STRING", "fake-conn")
    dummy_client = DummyBlobClient()

    def fake_from_connection_string(conn_str, container_name, blob_name):
        return dummy_client

    monkeypatch.setattr(
        mapmyrun_service.BlobClient,
        "from_connection_string",
        fake_from_connection_string,
    )
    monkeypatch.setattr(mapmyrun_service.uuid, "uuid4", lambda: "fixed-id")

    file = FakeUploadFile(b"content", "file.XLS")

    result = upload_file_to_blob(file, "key-999")

    assert result["stored_as"] == "fixed-id.xls"


# =========================================================
# validate_normalize_mapmyrun_data tests
# =========================================================

def test_no_parsed_activity_data_none():
    normalized, errors = validate_normalize_mapmyrun_data(None)
    assert normalized is None
    assert errors == ["No parsed activity data was provided."]


def test_no_parsed_activity_data_empty_list():
    normalized, errors = validate_normalize_mapmyrun_data([])
    assert normalized is None
    assert errors == ["No parsed activity data was provided."]


def test_valid_row_all_fields_normalized():
    normalized, errors = validate_normalize_mapmyrun_data([make_valid_activity()])

    assert errors == []
    assert normalized == [
        {
            "workout_date": "2024-01-15",
            "activity_type": "Run",
            "calories_burned_kcal": 450.5,
            "distance_km": 10.2,
            "workout_time_seconds": 3600,
            "avg_pace_min_per_km": 5.5,
            "max_pace_min_per_km": 4.8,
            "avg_speed_kmh": 10.9,
            "max_speed_kmh": 12.3,
        }
    ]


@pytest.mark.parametrize(
    "field,value",
    [
        ("activity_type", ""),
        ("calories_burned_kcal", None),
        ("avg_pace_min_per_km", "   "),
        ("max_pace_min_per_km", None),
        ("avg_speed_kmh", ""),
        ("max_speed_kmh", None),
    ],
)
def test_optional_fields_can_be_missing(field, value):
    normalized, errors = validate_normalize_mapmyrun_data(
        [make_valid_activity(**{field: value})]
    )

    assert errors == []
    assert normalized[0][field] is None


@pytest.mark.parametrize(
    "field,value",
    [
        ("workout_date", ""),
        ("distance_km", None),
        ("workout_time_seconds", "   "),
    ],
)
def test_required_fields_missing(field, value):
    normalized, errors = validate_normalize_mapmyrun_data(
        [make_valid_activity(**{field: value})]
    )

    assert normalized is None
    assert f"Row 2: missing required field: {field}" in errors


@pytest.mark.parametrize(
    "field,value",
    [
        ("calories_burned_kcal", "abc"),
        ("distance_km", "abc"),
        ("workout_time_seconds", "abc"),
        ("avg_pace_min_per_km", "abc"),
        ("max_pace_min_per_km", "abc"),
        ("avg_speed_kmh", "abc"),
        ("max_speed_kmh", "abc"),
    ],
)
def test_invalid_numeric_conversion(field, value):
    normalized, errors = validate_normalize_mapmyrun_data(
        [make_valid_activity(**{field: value})]
    )

    assert normalized is None
    assert any(f"Row 2: invalid value for {field}" in error for error in errors)


@pytest.mark.parametrize(
    "field,value,error_text",
    [
        ("calories_burned_kcal", "-1", "calories_burned_kcal cannot be negative"),
        ("distance_km", "-1", "distance_km cannot be negative"),
        ("workout_time_seconds", "0", "workout_time_seconds must be greater than 0"),
        ("avg_pace_min_per_km", "-1", "avg_pace_min_per_km cannot be negative"),
        ("max_pace_min_per_km", "-1", "max_pace_min_per_km cannot be negative"),
        ("avg_speed_kmh", "-1", "avg_speed_kmh cannot be negative"),
        ("max_speed_kmh", "-1", "max_speed_kmh cannot be negative"),
    ],
)
def test_validator_failures(field, value, error_text):
    normalized, errors = validate_normalize_mapmyrun_data(
        [make_valid_activity(**{field: value})]
    )

    assert normalized is None
    assert f"Row 2: {error_text}" in errors


def test_invalid_rows_are_dropped_but_valid_rows_are_kept():
    parsed_data = [
        make_valid_activity(),
        make_valid_activity(distance_km="-5"),
        make_valid_activity(
            workout_date="2024-01-17",
            distance_km="3.0",
            workout_time_seconds="900",
        ),
    ]

    normalized, errors = validate_normalize_mapmyrun_data(parsed_data)

    assert len(normalized) == 2
    assert normalized[0]["distance_km"] == 10.2
    assert normalized[1]["distance_km"] == 3.0
    assert "Row 3: distance_km cannot be negative" in errors


def test_activity_type_non_string_is_stringified():
    normalized, errors = validate_normalize_mapmyrun_data(
        [make_valid_activity(activity_type=123)]
    )

    assert errors == []
    assert normalized[0]["activity_type"] == "123"


def test_type_error_conversion():
    parsed_data = [
        {
            "workout_date": "2024-01-15",
            "distance_km": object(),
            "workout_time_seconds": "1000",
        }
    ]

    normalized, errors = validate_normalize_mapmyrun_data(parsed_data)

    assert normalized is None
    assert any("invalid value for distance_km" in error for error in errors)


# =========================================================
# repository tests
# =========================================================

@pytest.mark.django_db
def test_save_mapmyrun_activities_saves_new_activities():
    activities = [
        {
            "activity_key": "2024-01-15|3600|10.2",
            "workout_date": date(2024, 1, 15),
            "activity_type": "Run",
            "calories_burned_kcal": 450.5,
            "distance_km": 10.2,
            "workout_time_seconds": 3600,
            "avg_pace_min_per_km": 5.5,
            "max_pace_min_per_km": 4.8,
            "avg_speed_kmh": 10.9,
            "max_speed_kmh": 12.3,
        }
    ]

    result = save_mapmyrun_activities(user_id=1, activities=activities)

    assert result["saved_count"] == 1
    assert result["skipped_count"] == 0
    assert MapMyRunActivity.objects.count() == 1

    saved = MapMyRunActivity.objects.first()
    assert saved.user_id == 1
    assert saved.activity_key == "2024-01-15|3600|10.2"
    assert saved.activity_type == "Run"
    assert saved.distance_km == 10.2


@pytest.mark.django_db
def test_save_mapmyrun_activities_skips_existing_database_duplicates():
    MapMyRunActivity.objects.create(
        user_id=1,
        activity_key="2024-01-15|3600|10.2",
        workout_date=date(2024, 1, 15),
        activity_type="Run",
        calories_burned_kcal=450.5,
        distance_km=10.2,
        workout_time_seconds=3600,
        avg_pace_min_per_km=5.5,
        max_pace_min_per_km=4.8,
        avg_speed_kmh=10.9,
        max_speed_kmh=12.3,
    )

    activities = [
        {
            "activity_key": "2024-01-15|3600|10.2",
            "workout_date": date(2024, 1, 15),
            "activity_type": "Run",
            "calories_burned_kcal": 450.5,
            "distance_km": 10.2,
            "workout_time_seconds": 3600,
            "avg_pace_min_per_km": 5.5,
            "max_pace_min_per_km": 4.8,
            "avg_speed_kmh": 10.9,
            "max_speed_kmh": 12.3,
        }
    ]

    result = save_mapmyrun_activities(user_id=1, activities=activities)

    assert result["saved_count"] == 0
    assert result["skipped_count"] == 1
    assert MapMyRunActivity.objects.count() == 1


@pytest.mark.django_db
def test_save_mapmyrun_activities_skips_duplicate_within_same_input_batch():
    activities = [
        {
            "activity_key": "2024-01-15|3600|10.2",
            "workout_date": date(2024, 1, 15),
            "activity_type": "Run",
            "calories_burned_kcal": 450.5,
            "distance_km": 10.2,
            "workout_time_seconds": 3600,
            "avg_pace_min_per_km": 5.5,
            "max_pace_min_per_km": 4.8,
            "avg_speed_kmh": 10.9,
            "max_speed_kmh": 12.3,
        },
        {
            "activity_key": "2024-01-15|3600|10.2",
            "workout_date": date(2024, 1, 15),
            "activity_type": "Run",
            "calories_burned_kcal": 450.5,
            "distance_km": 10.2,
            "workout_time_seconds": 3600,
            "avg_pace_min_per_km": 5.5,
            "max_pace_min_per_km": 4.8,
            "avg_speed_kmh": 10.9,
            "max_speed_kmh": 12.3,
        },
    ]

    result = save_mapmyrun_activities(user_id=1, activities=activities)

    assert result["saved_count"] == 1
    assert result["skipped_count"] == 1
    assert MapMyRunActivity.objects.count() == 1


@pytest.mark.django_db
def test_save_mapmyrun_activities_duplicate_key_for_different_user_is_saved():
    MapMyRunActivity.objects.create(
        user_id=1,
        activity_key="2024-01-15|3600|10.2",
        workout_date=date(2024, 1, 15),
        activity_type="Run",
        calories_burned_kcal=450.5,
        distance_km=10.2,
        workout_time_seconds=3600,
        avg_pace_min_per_km=5.5,
        max_pace_min_per_km=4.8,
        avg_speed_kmh=10.9,
        max_speed_kmh=12.3,
    )

    activities = [
        {
            "activity_key": "2024-01-15|3600|10.2",
            "workout_date": date(2024, 1, 15),
            "activity_type": "Run",
            "calories_burned_kcal": 450.5,
            "distance_km": 10.2,
            "workout_time_seconds": 3600,
            "avg_pace_min_per_km": 5.5,
            "max_pace_min_per_km": 4.8,
            "avg_speed_kmh": 10.9,
            "max_speed_kmh": 12.3,
        }
    ]

    result = save_mapmyrun_activities(user_id=2, activities=activities)

    assert result["saved_count"] == 1
    assert result["skipped_count"] == 0
    assert MapMyRunActivity.objects.filter(activity_key="2024-01-15|3600|10.2").count() == 2


# =========================================================
# view tests
# =========================================================

@pytest.mark.django_db
def test_upload_mapmyrun_file_missing_file(rf):
    request = rf.post("/fake-url/")
    request.FILES["wrong_key"] = SimpleUploadedFile(
        "file.xlsx",
        b"fake content",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    response = upload_mapmyrun_file(request, user_id=1)

    assert response.status_code == 400
    data = json.loads(response.content)
    assert data["error"] == "No file provided under key 'file'."


@pytest.mark.django_db
def test_upload_mapmyrun_file_success(rf, monkeypatch):
    uploaded_file = SimpleUploadedFile(
        "file.xlsx",
        b"fake content",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    def fake_process(file_obj, file_key, user_id):
        assert file_obj.name == "file.xlsx"
        assert file_key == "file"
        assert user_id == 5
        return {"saved_count": 2, "normalized_count": 2}

    monkeypatch.setattr(
        "data_integration.presentation.mapmyrun_views.process_mapmyrun_upload",
        fake_process,
    )

    request = rf.post("/fake-url/", {"file": uploaded_file})
    response = upload_mapmyrun_file(request, user_id=5)

    assert response.status_code == 201
    data = json.loads(response.content)
    assert data["message"] == "File uploaded successfully."
    assert data["result"]["saved_count"] == 2
    assert data["result"]["normalized_count"] == 2


@pytest.mark.django_db
def test_upload_mapmyrun_file_value_error_returns_400(rf, monkeypatch):
    uploaded_file = SimpleUploadedFile(
        "file.xlsx",
        b"fake content",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    def fake_process(file_obj, file_key, user_id):
        raise ValueError("Bad file content")

    monkeypatch.setattr(
        "data_integration.presentation.mapmyrun_views.process_mapmyrun_upload",
        fake_process,
    )

    request = rf.post("/fake-url/", {"file": uploaded_file})
    response = upload_mapmyrun_file(request, user_id=1)

    assert response.status_code == 400
    data = json.loads(response.content)
    assert data["error"] == "Bad file content"


@pytest.mark.django_db
def test_upload_mapmyrun_file_unexpected_error_returns_500(rf, monkeypatch):
    uploaded_file = SimpleUploadedFile(
        "file.xlsx",
        b"fake content",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    def fake_process(file_obj, file_key, user_id):
        raise Exception("Unexpected failure")

    monkeypatch.setattr(
        "data_integration.presentation.mapmyrun_views.process_mapmyrun_upload",
        fake_process,
    )

    request = rf.post("/fake-url/", {"file": uploaded_file})
    response = upload_mapmyrun_file(request, user_id=1)

    assert response.status_code == 500
    data = json.loads(response.content)
    assert data["error"] == "Unexpected failure"


@pytest.mark.django_db
def test_get_mapmyrun_activities_success_returns_only_requested_user(rf):
    MapMyRunActivity.objects.create(
        user_id=1,
        activity_key="a1",
        workout_date=date(2024, 1, 15),
        activity_type="Run",
        calories_burned_kcal=400,
        distance_km=8.0,
        workout_time_seconds=3000,
        avg_pace_min_per_km=6.0,
        max_pace_min_per_km=5.0,
        avg_speed_kmh=10.0,
        max_speed_kmh=12.0,
    )
    MapMyRunActivity.objects.create(
        user_id=1,
        activity_key="a2",
        workout_date=date(2024, 1, 20),
        activity_type="Walk",
        calories_burned_kcal=200,
        distance_km=4.0,
        workout_time_seconds=2000,
        avg_pace_min_per_km=7.0,
        max_pace_min_per_km=6.0,
        avg_speed_kmh=8.0,
        max_speed_kmh=9.0,
    )
    MapMyRunActivity.objects.create(
        user_id=2,
        activity_key="b1",
        workout_date=date(2024, 1, 21),
        activity_type="Bike",
        calories_burned_kcal=500,
        distance_km=20.0,
        workout_time_seconds=3600,
        avg_pace_min_per_km=None,
        max_pace_min_per_km=None,
        avg_speed_kmh=20.0,
        max_speed_kmh=25.0,
    )

    request = rf.get("/fake-url/")
    response = get_mapmyrun_activities(request, user_id=1)

    assert response.status_code == 200
    data = json.loads(response.content)

    assert data["count"] == 2
    assert len(data["activities"]) == 2
    assert data["activities"][0]["activity_key"] == "a2"
    assert data["activities"][1]["activity_key"] == "a1"

    for activity in data["activities"]:
        assert activity["user_id"] == 1


@pytest.mark.django_db
def test_get_mapmyrun_activities_empty_result(rf):
    request = rf.get("/fake-url/")
    response = get_mapmyrun_activities(request, user_id=999)

    assert response.status_code == 200
    data = json.loads(response.content)
    assert data["count"] == 0
    assert data["activities"] == []


@pytest.mark.django_db
def test_get_mapmyrun_activities_exception_returns_500(rf, monkeypatch):
    class BrokenManager:
        def filter(self, *args, **kwargs):
            raise Exception("Database exploded")

    monkeypatch.setattr(
        "data_integration.presentation.mapmyrun_views.MapMyRunActivity.objects",
        BrokenManager(),
    )

    request = rf.get("/fake-url/")
    response = get_mapmyrun_activities(request, user_id=1)

    assert response.status_code == 500
    data = json.loads(response.content)
    assert data["error"] == "Database exploded"


# =========================================================
# parse_mapmyrun_file tests
# =========================================================

def test_parse_mapmyrun_file_success():
    file_obj = make_excel_file(
        [
            [
                "2024-01-15",
                " Run ",
                450.5,
                10.2,
                3600,
                5.5,
                4.8,
                10.9,
                12.3,
            ]
        ]
    )

    parsed_data, error = parse_mapmyrun_file(file_obj)

    assert error is None
    assert len(parsed_data) == 1
    assert str(parsed_data[0]["workout_date"]) == "2024-01-15"
    assert parsed_data[0]["activity_type"] == "Run"
    assert parsed_data[0]["distance_km"] == 10.2
    assert parsed_data[0]["workout_time_seconds"] == 3600


def test_parse_mapmyrun_file_missing_required_columns():
    df = pd.DataFrame([{"Workout Date": "2024-01-15"}])
    file_obj = io.BytesIO()
    df.to_excel(file_obj, index=False)
    file_obj.seek(0)
    file_obj.name = "mapmyrun.xlsx"
    file_obj.size = len(file_obj.getvalue())

    parsed_data, error = parse_mapmyrun_file(file_obj)

    assert parsed_data is None
    assert "Missing required columns:" in error
    assert "Activity Type" in error


def test_parse_mapmyrun_file_empty_dataframe():
    df = pd.DataFrame(columns=REQUIRED_COLUMNS)
    file_obj = io.BytesIO()
    df.to_excel(file_obj, index=False)
    file_obj.seek(0)
    file_obj.name = "mapmyrun.xlsx"
    file_obj.size = len(file_obj.getvalue())

    parsed_data, error = parse_mapmyrun_file(file_obj)

    assert parsed_data is None
    assert error == "The uploaded MapMyRun file contains no activity rows."


def test_parse_mapmyrun_file_parsing_failure(monkeypatch):
    file_obj = io.BytesIO(b"not a real excel file")
    file_obj.name = "mapmyrun.xlsx"
    file_obj.size = len(file_obj.getvalue())

    def fake_read_excel(_):
        raise Exception("boom")

    monkeypatch.setattr(pd, "read_excel", fake_read_excel)

    parsed_data, error = parse_mapmyrun_file(file_obj)

    assert parsed_data is None
    assert error == "Parsing failed: boom"


# =========================================================
# build_activity_key tests
# =========================================================

def test_build_activity_key_normalizes_values():
    activity = {
        "workout_date": " 2024-01-15 ",
        "workout_time_seconds": " 3600 ",
        "distance_km": " 10.2 ",
    }

    key = build_activity_key(activity)

    assert key == "2024-01-15|3600|10.2"


def test_build_activity_key_handles_missing_values():
    activity = {}

    key = build_activity_key(activity)

    assert key == "||"


# =========================================================
# process_mapmyrun_upload tests
# =========================================================

def test_process_mapmyrun_upload_success(monkeypatch):
    uploaded_file = io.BytesIO(b"fake excel content")
    uploaded_file.name = "mapmyrun.xlsx"
    uploaded_file.size = len(uploaded_file.getvalue())
    uploaded_file.content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    fake_upload_result = {
        "file_key": "file",
        "filename": "mapmyrun.xlsx",
        "stored_as": "abc.xlsx",
        "content_type": uploaded_file.content_type,
        "size": uploaded_file.size,
        "url": "https://fake-url",
    }

    parsed_data = [
        {
            "workout_date": "2024-01-15",
            "activity_type": "Run",
            "calories_burned_kcal": 450.5,
            "distance_km": 10.2,
            "workout_time_seconds": 3600,
            "avg_pace_min_per_km": 5.5,
            "max_pace_min_per_km": 4.8,
            "avg_speed_kmh": 10.9,
            "max_speed_kmh": 12.3,
        },
        {
            "workout_date": "2024-01-15",
            "activity_type": "Run again",
            "calories_burned_kcal": 451.0,
            "distance_km": 10.2,
            "workout_time_seconds": 3600,
            "avg_pace_min_per_km": 5.4,
            "max_pace_min_per_km": 4.7,
            "avg_speed_kmh": 11.0,
            "max_speed_kmh": 12.4,
        },
        {
            "workout_date": "2024-01-16",
            "activity_type": "Walk",
            "calories_burned_kcal": 200.0,
            "distance_km": 3.0,
            "workout_time_seconds": 1800,
            "avg_pace_min_per_km": 10.0,
            "max_pace_min_per_km": 9.0,
            "avg_speed_kmh": 6.0,
            "max_speed_kmh": 7.0,
        },
    ]

    normalized_data = parsed_data[:]

    monkeypatch.setattr(
        "data_integration.business.mapmyrun_service.upload_file_to_blob",
        lambda uploaded_file, file_key: fake_upload_result,
    )
    monkeypatch.setattr(
        "data_integration.business.mapmyrun_service.parse_mapmyrun_file",
        lambda uploaded_file: (parsed_data, None),
    )
    monkeypatch.setattr(
        "data_integration.business.mapmyrun_service.validate_normalize_mapmyrun_data",
        lambda parsed: (normalized_data, []),
    )

    captured = {}

    def fake_save(user_id, unique_data):
        captured["user_id"] = user_id
        captured["unique_data"] = unique_data
        return 2

    monkeypatch.setattr(
        "data_integration.business.mapmyrun_service.save_mapmyrun_activities",
        fake_save,
    )

    result = process_mapmyrun_upload(uploaded_file, "file", 7)

    assert result["message"] == "File uploaded, parsed, normalized, and saved successfully."
    assert result["upload_result"]["stored_as"] == "abc.xlsx"
    assert result["parsed_count"] == 3
    assert result["normalized_count"] == 3
    assert result["saved_count"] == 2
    assert result["validation_errors"] == []
    assert len(result["normalized_preview"]) == 3

    assert captured["user_id"] == 7
    assert len(captured["unique_data"]) == 2
    assert captured["unique_data"][0]["activity_key"] == "2024-01-15|3600|10.2"
    assert captured["unique_data"][1]["activity_key"] == "2024-01-16|1800|3.0"


def test_process_mapmyrun_upload_parse_error(monkeypatch):
    uploaded_file = io.BytesIO(b"fake")
    uploaded_file.name = "mapmyrun.xlsx"
    uploaded_file.size = len(uploaded_file.getvalue())

    monkeypatch.setattr(
        "data_integration.business.mapmyrun_service.upload_file_to_blob",
        lambda uploaded_file, file_key: {"ok": True},
    )
    monkeypatch.setattr(
        "data_integration.business.mapmyrun_service.parse_mapmyrun_file",
        lambda uploaded_file: (None, "Parsing failed badly"),
    )

    with pytest.raises(ValueError, match="Parsing failed badly"):
        process_mapmyrun_upload(uploaded_file, "file", 1)


def test_process_mapmyrun_upload_no_valid_normalized_data(monkeypatch):
    uploaded_file = io.BytesIO(b"fake")
    uploaded_file.name = "mapmyrun.xlsx"
    uploaded_file.size = len(uploaded_file.getvalue())

    monkeypatch.setattr(
        "data_integration.business.mapmyrun_service.upload_file_to_blob",
        lambda uploaded_file, file_key: {"ok": True},
    )
    monkeypatch.setattr(
        "data_integration.business.mapmyrun_service.parse_mapmyrun_file",
        lambda uploaded_file: ([{"bad": "row"}], None),
    )
    monkeypatch.setattr(
        "data_integration.business.mapmyrun_service.validate_normalize_mapmyrun_data",
        lambda parsed: (None, ["error 1"]),
    )

    with pytest.raises(ValueError, match="No valid MapMyRun activities found."):
        process_mapmyrun_upload(uploaded_file, "file", 1)