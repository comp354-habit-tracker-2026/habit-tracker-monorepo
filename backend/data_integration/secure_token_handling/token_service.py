from datetime import datetime
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from sqlalchemy.orm import Session
from token_model import ProviderToken  # database model related

# --- GENERATE A FERNET KEY (USING TERMINAL) ----
# terminal: python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# terminal: export FERNET_KEY="generated key pasted here"
# -----------------------------------------------

# Load values from .env into environment variables
load_dotenv() # this is to keep the fernet key in local .env

FERNET_KEY = os.getenv("FERNET_KEY")  # FERNET_KEY is a secret key ---> os.getenv("FERNET_KEY") this loads value from local .env that contains the key

if not FERNET_KEY:  # if key is missing then stop the app
    raise ValueError("FERNET_KEY is missing. Set it before running the app.")

token_encryptor = Fernet(FERNET_KEY.encode()) # make an encryption tool which is used for encrypting tokens

# ------------ BELOW ARE METHODS TO ENCRYPT TOKEN AND MASK ------------
# Encryption is for safe storage in database -> we don't store the raw token in the database
# Masking is for safe display in responses or logs -> so the only visible part of the token is the last 4 characters

# Function that encrypts access token
# Returns an encrypted string that will be stored in the database instead of the raw token
def encrypt_access_token(access_token: str) -> str:
    return token_encryptor.encrypt(access_token.encode()).decode() # will be the one stored in database

# Function that hides all except the last 4 characters of the token
# Returns a masked string that hides the real full token
def mask_access_token(access_token: str) -> str:
    if len(access_token) <= 4:
        return "*" * len(access_token)
    else:
        return "*" * (len(access_token) - 4) + access_token[-4:]

# Function that gets the last 4 characters of the token
# Returns the last 4 characters or the whole token if it is shorter than 4
def get_token_last_4(access_token: str) -> str:
    if len(access_token) >= 4:
        return access_token[-4:]
    else:
        return access_token

# For now this is just a simple placeholder ---> RELATED TO AUDIT LOGGING WHICH IS RELATED TO FEATURE#38 
# Function that records token events
def record_token_event(token_action: str, user_id: int, provider_name: str):
    print(f"{token_action} | user_id={user_id} | provider_name={provider_name}")

# ------------ BELOW ARE METHODS RELATED TO THE DATABASE ------------
# Function that looks for an existing provider token in the database
# Returns the token record if found, otherwise returns None
def find_provider_token(database_session: Session, user_id: int, provider_name: str):
    return (database_session.query(ProviderToken).filter_by(user_id=user_id, provider_name=provider_name).first())

# Function that updates an existing provider token
# Returns the token action used for audit logging
def update_existing_provider_token(existing_provider_token, encrypted_access_token: str, token_last_4: str) -> str:
    existing_provider_token.encrypted_access_token = encrypted_access_token
    existing_provider_token.token_last_4 = token_last_4
    existing_provider_token.token_status = "ACTIVE"
    existing_provider_token.revoked_at = None
    return "ROTATE_TOKEN" #replace existing token with a new encrypted token for the same user and provider

# Function that inserts a new provider token in the database 
# Returns the token action used for audit logging
def create_new_provider_token(database_session: Session, user_id: int, provider_name: str, encrypted_access_token: str, token_last_4: str) -> str:
    new_provider_token = ProviderToken(user_id=user_id, provider_name=provider_name, encrypted_access_token=encrypted_access_token, 
            token_last_4=token_last_4, token_status="ACTIVE")
    database_session.add(new_provider_token)
    return "STORE_TOKEN"

# Function that builds a success response after saving a token
# Returns a dictionary that will be sent back to the route
def build_save_success_response(provider_name: str, access_token: str, token_action: str) -> dict:
    return {"success": True, "message": "Provider token saved securely", "provider_name": provider_name,
            "masked_access_token": mask_access_token(access_token), "token_action": token_action}

# Function that builds an error response
# Returns a dictionary with the error message
def build_error_response(provider_name: str, message: str) -> dict:
    return {"success": False, "message": message, "provider_name": provider_name}

# Function that saves a provider token securely
# Returns a dictionary that tells the route(in main.py) that the token was saved
def save_provider_token(database_session: Session, user_id: int, provider_name: str, access_token: str):
    try:
        encrypted_access_token = encrypt_access_token(access_token)  # encrypt raw token
    except Exception:
        return build_error_response(provider_name, "Encryption failed")

    token_last_4 = get_token_last_4(access_token)

    try:
        # Check if this user already has a token for this provider
        existing_provider_token = find_provider_token(database_session, user_id, provider_name)

        if existing_provider_token:  # update existing token
            token_action = update_existing_provider_token(existing_provider_token, encrypted_access_token, token_last_4)
        else:  # create a new one
            token_action = create_new_provider_token(database_session, user_id, provider_name, encrypted_access_token, token_last_4)

        database_session.commit()
        record_token_event(token_action, user_id, provider_name)

        return build_save_success_response(provider_name, access_token, token_action)

    except Exception:
        database_session.rollback()
        return build_error_response(provider_name, "Database save failed")

# Function that revokes a provider token
# Returns a dictionary that tells the route(in main.py) what happened after trying to revoke the token
def revoke_provider_token(database_session: Session, user_id: int, provider_name: str):
    try:
        # Find the token in the database
        existing_provider_token = find_provider_token(database_session, user_id, provider_name)

        # If token does not exist or is already revoked
        if not existing_provider_token or existing_provider_token.token_status == "REVOKED":
            return {"success": True, "message": "No active provider token to revoke", "provider_name": provider_name, "token_action": "REVOKE_TOKEN"}

        else:  # set token as revoked
            existing_provider_token.token_status = "REVOKED"
            existing_provider_token.revoked_at = datetime.now()
            database_session.commit()

            record_token_event("REVOKE_TOKEN", user_id, provider_name)

            return {"success": True, "message": "Provider token revoked successfully", "provider_name": provider_name, "token_action": "REVOKE_TOKEN"}

    except Exception:
        database_session.rollback()
        return build_error_response(provider_name, "Database revoke failed")