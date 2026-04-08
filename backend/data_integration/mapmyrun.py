import os
import uuid
from pathlib import Path
import sqlite3
from azure.storage.blob import BlobClient
from dotenv import load_dotenv
import pandas as pd

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

#Upload MapMyrun Data Service (Feature #135)

class SQLiteRepository:
    #Simulate the app database for uploading
    def __init__(self, db_name="activities.db"):
        self.db_name = db_name
        self._create_table()
    #Open connection to SQLite database file
    def _connect(self):
        return sqlite3.connect(self.db_name)

    #Create the table if it doesn't already exist
    def _create_table(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                activity_key TEXT NOT NULL,
                date TEXT,
                duration INTEGER,
                distance REAL,
                UNIQUE(user_id, activity_key)
            )
        """)
        conn.commit()
        conn.close()

    #Checks if the activity already exists for the given user
    def exists(self, user_id: str, activity_key: str) -> bool:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM activities WHERE user_id = ? AND activity_key = ?",
            (user_id, activity_key)
        )
        result = cursor.fetchone()
        conn.close()
        return result is not None

    #Saves a non duplicate activity in the database
    def save(self, user_id: str, activity: dict, activity_key: str):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO activities (user_id, activity_key, date, duration, distance)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            activity_key,
            activity.get("date"),
            activity.get("duration"),
            activity.get("distance")
        ))
        conn.commit()
        conn.close()

#Helper for creation of the activity key for feature #135
def build_activity_key(activity: dict) -> str:
    date_val = str(activity.get("date", activity.get("Date", ""))).strip().lower()
    duration_val = str(activity.get("duration", activity.get("Duration", ""))).strip().lower()
    distance_val = str(activity.get("distance", activity.get("Distance", ""))).strip().lower()

    return f"{date_val}|{duration_val}|{distance_val}"

#Feature #135 take normalized activities, skip duplicates, give summary
def upload_mapmyrun_data(user_id: str, normalized_activities: list[dict], repository) -> dict:
    summary = {
        "imported_count": 0,
        "duplicate_count": 0,
        "failed_count": 0,
        "errors": [],
    }

    #If there are no user id, upload cannot continue
    if not user_id:
        summary["failed_count"] = len(normalized_activities)
        summary["errors"].append("Missing user_id.")
        return summary

    #If there are no normalized activities return empty summary
    if not normalized_activities:
        return summary

    #Tracks duplicates in the same upload batch
    duplicates = set()

    #Process each normalized activity one by one
    for index, activity in enumerate(normalized_activities, start=1):
        try:
            #make a copy to avoid modifying original data directly
            activity_copy = dict(activity)
            #Build a unique activity key
            activity_key = build_activity_key(activity_copy)

            #Skips any activity that was detected as a duplicate
            if activity_key in duplicates:
                summary["duplicate_count"] += 1
                continue
            #Skip the activity if it already exists in storage for current user
            if repository.exists(user_id, activity_key):
                summary["duplicate_count"] += 1
                continue
            
            #Link the activity to the current user before storing it
            activity_copy["user_id"] = user_id
            #Store/upload data
            repository.save(user_id, activity_copy, activity_key)

            #Add activity key to the duplicates pile so it is not repeated next time
            duplicates.add(activity_key)
            #Record successful import
            summary["imported_count"] += 1

        #In case failure occurs
        except Exception as e:
            summary["failed_count"] += 1
            summary["errors"].append(f"Activity {index}: {str(e)}")

    return summary
# Feature #137 : parse uploaded MapMyRun file from blob URL
def parse_mapmyrun_file(file_url: str):
    try:
        df = pd.read_excel(file_url)

        required_columns = [
            "Workout Date",
            "Workout Time (seconds)",
            "Distance (km)",
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return None, f"Missing required columns: {', '.join(missing_columns)}"

        if df.empty:
            return None, "The uploaded MapMyRun file contains no activity rows."
        
        parsed_data = df[required_columns].rename(
            columns={
                "Workout Date": "date",
                "Workout Time (seconds)": "duration",
                "Distance (km)": "distance",
            }
        ).to_dict(orient="records")
        
        return parsed_data, None

    except Exception as e:
        return None, f"Parsing failed: {str(e)}"
