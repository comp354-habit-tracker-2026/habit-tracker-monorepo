import pytest
from io import BytesIO
import importlib.util
from pathlib import Path
import sys
import types
from mapmyrun import upload_mapmyrun_data, build_activity_key, SQLiteRepository, sqlite3


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

"""
Tests for Feature #135 — upload_mapmyrun_data
Covers: normal uploads, duplicate detection (in-batch and cross-batch),
missing user_id, empty input, and partial failures.
"""
#Generated by Claude Sonnet 4.6
#Test data for feature #135 (Upload Vaildated, normalized data to DB, skip duplicates and give summary) 
# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clear_db(repo):  # pass repo as argument, forces repo to run first so the table exists before we delete
    """Wipe the activities table before every test so state doesn't bleed between runs."""
    conn = sqlite3.connect("test_activities.db")
    conn.execute("DELETE FROM activities")
    conn.commit()
    conn.close()

def print_db(label="", summary=None):
    """Print summary and all rows in the activities table."""
    print(f"\n{'='*90}")
    print(f"📋 DB State — {label}")
    print(f"{'='*90}")

    # Print summary if provided
    if summary:
        print(f"  ✅ Imported:   {summary['imported_count']}")
        print(f"  🔁 Duplicates: {summary['duplicate_count']}")
        print(f"  ❌ Failed:     {summary['failed_count']}")
        if summary['errors']:
            print(f"  ⚠️  Errors:    {summary['errors']}")
        print()

    # Print DB rows
    conn = sqlite3.connect("test_activities.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM activities")
    rows = cursor.fetchall()
    conn.close()

    print(f"  {'ID':<5} {'User':<10} {'Key':<35} {'Date':<15} {'Duration':<10} {'Distance'}")
    print(f"  {'-' * 85}")
    if rows:
        for row in rows:
            print(f"  {str(row[0]):<5} {str(row[1]):<10} {str(row[2]):<35} {str(row[3]):<15} {str(row[4]):<10} {row[5]}")
    else:
        print("  (empty)")
    print(f"{'='*90}\n")

@pytest.fixture()
def repo():
    return SQLiteRepository(db_name="test_activities.db")


ACTIVITY_A = {"date": "2024-01-10", "duration": 1800, "distance": 5.0}
ACTIVITY_B = {"date": "2024-01-11", "duration": 2400, "distance": 8.0}
ACTIVITY_C = {"date": "2024-01-12", "duration": 3000, "distance": 10.5}


# ---------------------------------------------------------------------------
# build_activity_key helper tests
# ---------------------------------------------------------------------------

class TestBuildActivityKey:

    def test_builds_pipe_separated_key(self):
        # Verifies that the activity key is correctly formatted as "date|duration|distance"
        # using pipe characters as separators between the three fields.
        key = build_activity_key(ACTIVITY_A)
        assert key == "2024-01-10|1800|5.0"

    def test_case_insensitive_field_lookup(self):
        # Verifies that the key builder works whether field names are lowercase ("date")
        # or Title-case ("Date"), since MapMyRun exports may vary in casing.
        titled = {"Date": "2024-01-10", "Duration": 1800, "Distance": 5.0}
        assert build_activity_key(titled) == build_activity_key(ACTIVITY_A)

    def test_missing_fields_produce_empty_segments(self):
        # Verifies that if an activity has no fields at all, the key still has
        # the correct format with empty segments ("||") instead of crashing.
        key = build_activity_key({})
        assert key == "||"


# ---------------------------------------------------------------------------
# SQLiteRepository helper tests
# ---------------------------------------------------------------------------

class TestSQLiteRepository:

    def test_new_activity_does_not_exist(self, repo):
        # Verifies that checking for an activity that was never saved returns False,
        # confirming the DB starts clean and exists() doesn't false-positive.
        assert repo.exists("user1", "some|key|here") is False

    def test_saved_activity_exists(self, repo):
        # Verifies that after saving an activity, exists() correctly returns True
        # for that same user and activity key combination.
        key = build_activity_key(ACTIVITY_A)
        repo.save("user1", ACTIVITY_A, key)
        assert repo.exists("user1", key) is True

    def test_activity_isolated_per_user(self, repo):
        # Verifies that an activity saved for user1 does NOT show up when checking
        # for user2 — each user's data is fully isolated in the DB.
        key = build_activity_key(ACTIVITY_A)
        repo.save("user1", ACTIVITY_A, key)
        assert repo.exists("user2", key) is False


# ---------------------------------------------------------------------------
# upload_mapmyrun_data — main feature tests
# ---------------------------------------------------------------------------

class TestUploadMapMyRunData:

    # --- Happy path ---

    def test_single_activity_imported(self, repo):
        # Verifies the basic happy path: uploading one new activity results in
        # imported_count=1 with no duplicates, failures, or errors.
        summary = upload_mapmyrun_data("user1", [ACTIVITY_A], repo)
        assert summary["imported_count"] == 1
        assert summary["duplicate_count"] == 0
        assert summary["failed_count"] == 0
        assert summary["errors"] == []
        print_db("test_single_activity_imported", summary)

    def test_multiple_unique_activities_all_imported(self, repo):
        # Verifies that uploading a batch of 3 completely different activities
        # results in all 3 being imported with zero duplicates.
        activities = [ACTIVITY_A, ACTIVITY_B, ACTIVITY_C]
        summary = upload_mapmyrun_data("user1", activities, repo)
        assert summary["imported_count"] == 3
        assert summary["duplicate_count"] == 0
        print_db("test_multiple_unique_activities_all_imported", summary)

    def test_data_actually_persists_in_db(self, repo):
        # Verifies that after uploading, the activity is physically stored in the DB
        # and can be found by exists() — not just counted in the summary.
        upload_mapmyrun_data("user1", [ACTIVITY_A], repo)
        summary = upload_mapmyrun_data("user1", [ACTIVITY_A], repo)
        key = build_activity_key(ACTIVITY_A)
        assert repo.exists("user1", key) is True
        print_db("test_data_actually_persists_in_db", summary)

    # --- Duplicate detection (same batch) ---

    def test_in_batch_duplicate_counted_once(self, repo):
        # Verifies that if the same activity appears twice in the same upload batch,
        # only the first one is imported and the second is counted as a duplicate.
        summary = upload_mapmyrun_data("user1", [ACTIVITY_A, ACTIVITY_A], repo)
        assert summary["imported_count"] == 1
        assert summary["duplicate_count"] == 1
        print_db("test_in_batch_duplicate_counted_once", summary)

    def test_three_identical_activities_only_one_imported(self, repo):
        # Verifies that if the same activity appears 3 times in one batch,
        # only 1 is imported and the remaining 2 are counted as duplicates.
        summary = upload_mapmyrun_data("user1", [ACTIVITY_A] * 3, repo)
        assert summary["imported_count"] == 1
        assert summary["duplicate_count"] == 2
        print_db("test_three_identical_activities_only_one_imported", summary)

    # --- Duplicate detection (cross-batch / already in DB) ---

    def test_second_upload_of_same_activity_is_duplicate(self, repo):
        # Verifies that uploading the same activity a second time (in a separate call)
        # is correctly detected as a duplicate using the DB — not just the in-memory set.
        upload_mapmyrun_data("user1", [ACTIVITY_A], repo)
        summary = upload_mapmyrun_data("user1", [ACTIVITY_A], repo)
        assert summary["imported_count"] == 0
        assert summary["duplicate_count"] == 1
        print_db("test_second_upload_of_same_activity_is_duplicate", summary)

    def test_duplicate_check_is_per_user(self, repo):
        # Verifies that the same activity uploaded by two different users is NOT
        # treated as a duplicate — each user has their own independent activity history.
        upload_mapmyrun_data("user1", [ACTIVITY_A], repo)
        summary = upload_mapmyrun_data("user2", [ACTIVITY_A], repo)
        assert summary["imported_count"] == 1
        assert summary["duplicate_count"] == 0
        print_db("test_duplicate_check_is_per_user", summary)

    def test_mixed_new_and_duplicate_activities(self, repo):
        # Verifies that in a batch containing one already-uploaded activity and one new one,
        # the duplicate is skipped and only the new activity is imported.
        upload_mapmyrun_data("user1", [ACTIVITY_A], repo)
        summary = upload_mapmyrun_data("user1", [ACTIVITY_A, ACTIVITY_B], repo)
        assert summary["imported_count"] == 1
        assert summary["duplicate_count"] == 1
        print_db("test_mixed_new_and_duplicate_activities", summary)

    # --- Edge cases: empty / missing input ---

    def test_empty_activity_list_returns_zero_counts(self, repo):
        # Verifies that passing an empty list doesn't crash and returns a clean
        # summary with all counts at zero and no errors.
        summary = upload_mapmyrun_data("user1", [], repo)
        assert summary["imported_count"] == 0
        assert summary["duplicate_count"] == 0
        assert summary["failed_count"] == 0
        assert summary["errors"] == []
        print_db("test_empty_activity_list_returns_zero_counts", summary)

    def test_missing_user_id_marks_all_as_failed(self, repo):
        # Verifies that passing an empty string as user_id causes all activities
        # to be marked as failed, and the error message mentions "user_id".
        activities = [ACTIVITY_A, ACTIVITY_B]
        summary = upload_mapmyrun_data("", activities, repo)
        assert summary["failed_count"] == len(activities)
        assert any("user_id" in e.lower() for e in summary["errors"])
        print_db("test_missing_user_id_marks_all_as_failed", summary)

    def test_none_user_id_marks_all_as_failed(self, repo):
        # Verifies that passing None as user_id (instead of an empty string)
        # also correctly marks the activity as failed without crashing.
        summary = upload_mapmyrun_data(None, [ACTIVITY_A], repo)
        assert summary["failed_count"] == 1
        print_db("test_none_user_id_marks_all_as_failed", summary)

    # --- Summary structure ---

    def test_summary_always_contains_required_keys(self, repo):
        # Verifies that the returned summary dictionary always contains all 4 expected keys:
        # imported_count, duplicate_count, failed_count, and errors — regardless of input.
        summary = upload_mapmyrun_data("user1", [ACTIVITY_A], repo)
        for key in ("imported_count", "duplicate_count", "failed_count", "errors"):
            assert key in summary
        print_db("test_summary_always_contains_required_keys", summary)

    def test_counts_add_up_to_total_activities(self, repo):
        # Verifies that imported + duplicate + failed always equals the total number
        # of activities submitted, so no activity is silently lost or double-counted.
        upload_mapmyrun_data("user1", [ACTIVITY_A], repo)   # pre-seed one duplicate
        activities = [ACTIVITY_A, ACTIVITY_B, ACTIVITY_C]
        summary = upload_mapmyrun_data("user1", activities, repo)
        total = summary["imported_count"] + summary["duplicate_count"] + summary["failed_count"]
        assert total == len(activities)
        print_db("test_counts_add_up_to_total_activities", summary)


