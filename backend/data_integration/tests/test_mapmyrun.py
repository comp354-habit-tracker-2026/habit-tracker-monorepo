import pytest
from io import BytesIO
import importlib.util
from pathlib import Path
import sys
import types


# ----------------------------
# Stub modules to avoid heavy imports
# ----------------------------

fake_repo_module = types.ModuleType("data_integration.data.mapmyrun_repository")
fake_repo_module.save_mapmyrun_activities = lambda user_id, activities: len(activities)

fake_data_package = types.ModuleType("data_integration.data")
fake_data_package.mapmyrun_repository = fake_repo_module

sys.modules["data_integration.data"] = fake_data_package
sys.modules["data_integration.data.mapmyrun_repository"] = fake_repo_module


# ----------------------------
# Load module with correct name (FIX FOR COVERAGE)
# ----------------------------

MODULE_PATH = Path(__file__).resolve().parents[1] / "business" / "mapmyrun_service.py"

spec = importlib.util.spec_from_file_location(
    "data_integration.business.mapmyrun_service",  # IMPORTANT
    MODULE_PATH
)

mapmyrun_service = importlib.util.module_from_spec(spec)

# Register module so coverage sees it
sys.modules["data_integration.business.mapmyrun_service"] = mapmyrun_service

spec.loader.exec_module(mapmyrun_service)


# Extract functions
MAX_FILE_SIZE_BYTES = mapmyrun_service.MAX_FILE_SIZE_BYTES
validate_uploaded_file = mapmyrun_service.validate_uploaded_file
upload_file_to_blob = mapmyrun_service.upload_file_to_blob


# ----------------------------
# Test helpers
# ----------------------------

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


# ----------------------------
# UNIT TESTS
# ----------------------------

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


# ----------------------------
# INTEGRATION TESTS
# ----------------------------

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

    monkeypatch.setattr(
        mapmyrun_service.uuid,
        "uuid4",
        lambda: "fixed-id"
    )

    file = FakeUploadFile(b"content", "file.xlsx")
    file.read()

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

    monkeypatch.setattr(
        mapmyrun_service.uuid,
        "uuid4",
        lambda: "fixed-id"
    )

    file = FakeUploadFile(b"content", "file.XLS")

    result = upload_file_to_blob(file, "key-999")

    assert result["stored_as"] == "fixed-id.xls"


# ------------------------
# Testing for normalization
# and validation (feature 75)
# ------------------------

# Test code developed with assistance from OpenAI's GPT-5.3 LLM 

from data_integration.business.mapmyrun_service import validate_normalize_mapmyrun_data


# ----------------------------
# Test helpers
# ----------------------------

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


# ----------------------------
# UNIT TESTS
# ----------------------------

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