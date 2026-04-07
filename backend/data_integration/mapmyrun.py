import os
import uuid
from pathlib import Path
from azure.storage.blob import BlobClient
from dotenv import load_dotenv

load_dotenv()

SUPPORTED_EXTENSIONS = (".xlsx", ".xls")
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


#FEATURE : CHECK IF FILE IS OF VALID MIME TYPE AND VALID STORAGE SIZE

def validate_upload(file_path: str) -> tuple[bool, str | None]:

    path = Path(file_path)

    if not path.is_file():
        return False, f"File '{path.name}' not found. Please try uploading again."

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return False, (
            f"Unsupported file type '{path.suffix or '(none)'}'. "
            "Please upload a .xlsx or .xls file exported from MapMyRun."
        )

    size = os.path.getsize(file_path)
    if size == 0:
        return False, f"'{path.name}' is empty. Please re-export and try again."

    if size > MAX_FILE_SIZE_BYTES:
        return False, (
            f"'{path.name}' is {size / 1024 / 1024:.1f} MB, "
            "which exceeds the 10 MB limit. Try exporting a smaller date range."
        )

    return True, None

#FEATURE : UPLOAD FILE TO AZURE BLOB STORAGE AND RETURN URL OR ERROR MESSAGE

def upload_to_blob(file_path: str) -> tuple[bool, str]:
    is_valid, error = validate_upload(file_path)
    if not is_valid:
        return False, error

    try:
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not connection_string:
            return False, "AZURE_STORAGE_CONNECTION_STRING is not set."

        container_name = "filestorage"
        path = Path(file_path)

        unique_name = f"{uuid.uuid4()}{path.suffix}"

        blob_client = BlobClient.from_connection_string(
            conn_str=connection_string,
            container_name=container_name,
            blob_name=unique_name
        )

        with open(file_path, "rb") as data: blob_client.upload_blob(data, overwrite=True)

        print(f"✅ File uploaded successfully: {blob_client.url}")

        return True, blob_client.url

    except Exception as e:
        return False, f"Upload failed: {str(e)}"

