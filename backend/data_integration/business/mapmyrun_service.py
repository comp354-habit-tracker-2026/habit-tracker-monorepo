import os
import uuid
from pathlib import Path
from azure.storage.blob import BlobClient

SUPPORTED_EXTENSIONS = (".xlsx", ".xls")
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def validate_uploaded_file(file):
    """
    Validates a Django uploaded file.

    Returns:
        (True, None) if valid
        (False, error_message) if invalid
    """

    if not file:
        return False, "No file provided."

    if not file.name:
        return False, "File must have a valid name."

    file_extension = Path(file.name).suffix.lower()

    if file_extension not in SUPPORTED_EXTENSIONS:
        return False, (
            f"Unsupported file type '{file_extension}'. "
            "Please upload a .xlsx or .xls file."
        )

    if file.size == 0:
        return False, "The uploaded file is empty."

    if file.size > MAX_FILE_SIZE_BYTES:
        return False, "File is too large. Maximum size is 10 MB."

    return True, None


def upload_file_to_blob(file, file_key):
    """
    file: InMemoryUploadedFile or TemporaryUploadedFile
    file_key: key used in form-data (e.g., 'file')

    Returns:
        dict with upload result or raises ValueError / Exception
    """

    is_valid, error_message = validate_uploaded_file(file)
    if not is_valid:
        raise ValueError(error_message)

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING is not set.")

    container_name = "filestorage"

    extension = os.path.splitext(file.name)[1].lower()
    unique_name = f"{uuid.uuid4()}{extension}"

    blob_client = BlobClient.from_connection_string(
        conn_str=connection_string,
        container_name=container_name,
        blob_name=unique_name
    )

    file.seek(0)
    blob_client.upload_blob(file, overwrite=True)

    return {
        "file_key": file_key,
        "filename": file.name,
        "stored_as": unique_name,
        "content_type": getattr(file, "content_type", None),
        "size": file.size,
        "url": blob_client.url,
    }