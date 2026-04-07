import os
import uuid
from pathlib import Path
from azure.storage.blob import BlobClient
from dotenv import load_dotenv

load_dotenv()
import pandas as pd
from datetime import datetime

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

# Feature #75 : normalization and validation of imported data
def validate_normalize_data(data):
    '''
    Parameters: data -> parsed data by MapMyRun data parser
    Returns: 
        Success: normalized_validated_data, None -> normalized/validated data, no error message
        Failure: None, error_msg -> no data, error message
    '''

    #convert data parameter to a Pandas Dataframe
    df = pd.DataFrame(data)

    #initialize empty dataframe for normalized and validated data
    normalized_validated_data = pd.DataFrame()

    # VALIDATION
    # Check for presence of data, duration, distance columns
    date_col = None
    duration_col = None
    distance_col = None
    
    #iterate through columns in dataset, search for required columns
    for col in df.columns:
        col_lower = col.lower()

        if 'date' in col_lower and not date_col:
            date_col = col
        elif 'duration' in col_lower and not duration_col:
            duration_col = col
        elif 'distance' in col_lower and not distance_col:
            distance_col = col

    #label missing columns
    missing = []
    if not date_col:
        missing.append('Date')
    if not duration_col:
        missing.append('Duration')
    if not distance_col:
        missing.append('Distance')
    
    #return error message labeling missing columns
    if missing:
        return None, f'Missing required fields from parsed MapMyRun dataset: {', '.join(missing)}'
    
    # VALIDATION
    # Search for invalid data in required columns, label + track invalid rows, convert to appropriate data type
    invalid_rows = []
    errors = []

    for i, row in df.iterrows():
        row_num = i + 2 #header is row number 1, first row with values is number 2

        #store required values
        date_val = row[date_col]
        duration_val = row[duration_col]
        distance_val = row[distance_col]

        #validate date value
        if pd.isna(date_val) or str(date_val).strip() == "":
            invalid_rows.append(i)
            errors.append(f'Row {i}: missing date')
        
        #validate duration
        if pd.isna(duration_val) or str(duration_val).strip() == "":
            invalid_rows.append(i)
            errors.append(f'Row {i}: missing duration')

        #validate distance
        if pd.isna(distance_val) or str(distance_val).strip() == "":
            invalid_rows.append(i)
            errors.append(f'Row {i}: missing distance')

    #drop invalid rows from dataset
    normalized_validated_data = df.drop(index=invalid_rows)

    
    return normalized_validated_data, None


