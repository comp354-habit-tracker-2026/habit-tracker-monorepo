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