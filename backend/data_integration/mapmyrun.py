import os
from pathlib import Path

SUPPORTED_EXTENSIONS = (".xlsx", ".xls")
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


#FEATURE : CHECK IF FILE IS OF VALID MIME TYPE AND VALID STORAGE SIZE

def validate_upload(file_path: str) -> tuple[bool, str | None]:
    """
    Validate a MapMyRun activity file.
    Returns (True, None) on success, or (False, error_message) on failure.
    """
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


