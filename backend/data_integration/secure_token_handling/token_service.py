from datetime import datetime
import os
import requests
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from sqlalchemy.orm import Session
from token_model import ProviderToken  # database model related
import logging

# --- GENERATE A FERNET KEY (USING TERMINAL) ----
# terminal: python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# terminal: export FERNET_KEY="generated key pasted here"
# -----------------------------------------------

# Load values from .env into environment variables
load_dotenv()  # this is to keep the fernet key and provider secrets in local .env
FERNET_KEY = os.getenv("FERNET_KEY")  # FERNET_KEY is a secret key ---> os.getenv("FERNET_KEY") loads the key from local .env
if not FERNET_KEY:  # if key is missing then stop the app
    raise ValueError("FERNET_KEY is missing. Set it before running the app.")

token_encryptor = Fernet(FERNET_KEY.encode())  # make an encryption tool which is used for encrypting tokens

# this is just to test if the refresh works since I dont have access yet to the real providers
USE_FAKE_REFRESH = os.getenv("USE_FAKE_REFRESH", "false").lower() == "true" # for testing refresh logic without actually calling the provider's refresh endpoint (set USE_FAKE_REFRESH=true in .env to use this) -> it will just generate a new fake token instead of calling the real refresh endpoint of the provider, but it will still go through the same database update and response flow as a real refresh would -> this is just for testing the refresh flow without needing valid provider credentials or waiting for the token to expire

# This class manages provider tokens using the database session
def _log_permission_check(user_id: int, provider_name: str, scope: str, caller_service: str, allowed: bool, reason: str):
    print({
        "timestamp": datetime.now().isoformat(),
        "caller_service": caller_service,
        "user_id": user_id,
        "provider_name": provider_name,
        "scope": scope,
        "allowed": allowed,
        "reason": reason
        # NOTE: no tokens or secrets logged here
    })


class ProviderTokenManager:
    # Constructor
    # Saves the current database session inside the object so all methods can use it
    def __init__(self, database_session: Session):
        self.database_session = database_session

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
    # Function that saves a provider token securely
    # Returns a dictionary that tells the route(in main.py) that the token was saved
    def save_provider_token(
        self,
        user_id: int,
        provider_name: str,
        access_token: str,
        refresh_token: str | None = None,
        access_token_expires_at=None
    ):
        try:
            encrypted_access_token = self.encrypt_token(access_token)
            encrypted_refresh_token = self.encrypt_token(refresh_token) if refresh_token else None
        except Exception as e:
            return self.build_error_response(provider_name, f"Encryption failed: {str(e)}")

        token_last_4 = self.get_token_last_4(access_token)

        try:
            existing_provider_token = self.find_provider_token(user_id, provider_name)

            if existing_provider_token:
                token_action = self.update_existing_provider_token(existing_provider_token=existing_provider_token,
                    encrypted_access_token=encrypted_access_token, encrypted_refresh_token=encrypted_refresh_token,
                    token_last_4=token_last_4, access_token_expires_at=access_token_expires_at
                )
            else:
                token_action = self.create_new_provider_token(
                    user_id=user_id,
                    provider_name=provider_name,
                    encrypted_access_token=encrypted_access_token,
                    encrypted_refresh_token=encrypted_refresh_token,
                    token_last_4=token_last_4,
                    access_token_expires_at=access_token_expires_at
                )

            self.database_session.commit()
            self.record_token_event(token_action, user_id, provider_name)

            return self.build_save_success_response(provider_name, access_token, token_action)

        except Exception as e:
            self.database_session.rollback()
            return self.build_error_response(provider_name, f"Database save failed: {str(e)}")

    # Function that checks if the access token is expired or about to expire within 5 minutes
    # Returns True if the token is expired or about to expire, otherwise returns False
    def is_access_token_expired(self, existing_provider_token) -> bool:
        if existing_provider_token.access_token_expires_at is None:
            return False

        return datetime.now() >= (
            existing_provider_token.access_token_expires_at - timedelta(minutes=5)
        )

# ------------ BELOW ARE METHODS RELATED TO TOKEN REFRESH ------------
    # This chooses which provider refresh logic to run
    # Returns the new access token if refresh is successful, otherwise returns None
    def refresh_provider_access_token(self, existing_provider_token):
        provider_name = existing_provider_token.provider_name

        if provider_name == "strava":
            return self.refresh_strava_token(existing_provider_token)

        elif provider_name == "mapmyrun":
            return self.refresh_mapmyrun_token(existing_provider_token)

        elif provider_name == "weski":
            return self.refresh_weski_token(existing_provider_token)

        elif provider_name == "mywhoosh":
            return self.refresh_mywhoosh_token(existing_provider_token)

        else:
            return None

    # Function that refreshes a Strava access token using the refresh token
    # Returns the new access token if refresh is successful, otherwise returns None
    def refresh_strava_token(self, existing_provider_token):
        if not existing_provider_token.encrypted_refresh_token:
            return None

        try:
            refresh_token = self.decrypt_token(existing_provider_token.encrypted_refresh_token)

            # If fake refresh is enabled, simulate a successful refresh for testing
            if USE_FAKE_REFRESH:
                new_access_token = "new_fake_strava_token_9999"
                new_refresh_token = "new_fake_strava_refresh_9999"
                new_expiry = datetime.now() + timedelta(hours=1)

                existing_provider_token.encrypted_access_token = self.encrypt_token(new_access_token)
                existing_provider_token.encrypted_refresh_token = self.encrypt_token(new_refresh_token)
                existing_provider_token.token_last_4 = self.get_token_last_4(new_access_token)
                existing_provider_token.access_token_expires_at = new_expiry
                existing_provider_token.token_status = "ACTIVE"
                existing_provider_token.updated_at = datetime.now()
                existing_provider_token.revoked_at = None

                self.database_session.commit()
                self.database_session.refresh(existing_provider_token)

                self.record_token_event("REFRESH_TOKEN", existing_provider_token.user_id,
                                        existing_provider_token.provider_name)

                return new_access_token

            strava_client_id = os.getenv("STRAVA_CLIENT_ID")
            strava_client_secret = os.getenv("STRAVA_CLIENT_SECRET")

            if not strava_client_id or not strava_client_secret:
                return None

            response = requests.post(
                "https://www.strava.com/api/v3/oauth/token",
                data={
                    "client_id": strava_client_id,
                    "client_secret": strava_client_secret,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token
                },
                timeout=15
            )

            if response.status_code != 200:
                return None

            data = response.json()

            new_access_token = data.get("access_token")
            new_refresh_token = data.get("refresh_token")
            expires_at = data.get("expires_at")

            if not new_access_token or not new_refresh_token or not expires_at:
                return None

            new_expiry = datetime.fromtimestamp(expires_at)

            existing_provider_token.encrypted_access_token = self.encrypt_token(new_access_token)
            existing_provider_token.encrypted_refresh_token = self.encrypt_token(new_refresh_token)
            existing_provider_token.token_last_4 = self.get_token_last_4(new_access_token)
            existing_provider_token.access_token_expires_at = new_expiry
            existing_provider_token.token_status = "ACTIVE"
            existing_provider_token.updated_at = datetime.now()
            existing_provider_token.revoked_at = None

            self.database_session.commit()
            self.database_session.refresh(existing_provider_token)

            self.record_token_event("REFRESH_TOKEN", existing_provider_token.user_id,
                                    existing_provider_token.provider_name)

            return new_access_token

        except Exception:
            self.database_session.rollback()
            return None

    # Function that refreshes a MapMyRun access token using the refresh token
    # Returns the new access token if refresh is successful, otherwise returns None
    def refresh_mapmyrun_token(self, existing_provider_token):
        if not existing_provider_token.encrypted_refresh_token:
            return None

        try:
            refresh_token = self.decrypt_token(existing_provider_token.encrypted_refresh_token)
            if USE_FAKE_REFRESH:
                new_access_token = "new_fake_mapmyrun_token_8888"
                new_refresh_token = "new_fake_mapmyrun_refresh_8888"
                new_expiry = datetime.now() + timedelta(hours=1)

                existing_provider_token.encrypted_access_token = self.encrypt_token(new_access_token)
                existing_provider_token.encrypted_refresh_token = self.encrypt_token(new_refresh_token)
                existing_provider_token.token_last_4 = self.get_token_last_4(new_access_token)
                existing_provider_token.access_token_expires_at = new_expiry
                existing_provider_token.token_status = "ACTIVE"
                existing_provider_token.updated_at = datetime.now()
                existing_provider_token.revoked_at = None

                self.database_session.commit()
                self.database_session.refresh(existing_provider_token)

                self.record_token_event("REFRESH_TOKEN", existing_provider_token.user_id,
                                        existing_provider_token.provider_name)

                return new_access_token

            mapmyrun_client_id = os.getenv("MAPMYRUN_CLIENT_ID")
            mapmyrun_client_secret = os.getenv("MAPMYRUN_CLIENT_SECRET")

            if not mapmyrun_client_id or not mapmyrun_client_secret:
                return None

            response = requests.post(
                "https://api.mapmyfitness.com/v7.1/oauth2/access_token/",
                data={"grant_type": "refresh_token", "client_id": mapmyrun_client_id,
                    "client_secret": mapmyrun_client_secret, "refresh_token": refresh_token},
                timeout=15)

            if response.status_code != 200:
                return None

            data = response.json()

            new_access_token = data.get("access_token")
            new_refresh_token = data.get("refresh_token")
            expires_in = data.get("expires_in")

            if not new_access_token or not expires_in:
                return None

            new_expiry = datetime.now() + timedelta(seconds=expires_in)

            existing_provider_token.encrypted_access_token = self.encrypt_token(new_access_token)
            existing_provider_token.token_last_4 = self.get_token_last_4(new_access_token)
            existing_provider_token.access_token_expires_at = new_expiry
            existing_provider_token.token_status = "ACTIVE"
            existing_provider_token.updated_at = datetime.now()
            existing_provider_token.revoked_at = None

            if new_refresh_token:
                existing_provider_token.encrypted_refresh_token = self.encrypt_token(new_refresh_token)

            self.database_session.commit()
            self.database_session.refresh(existing_provider_token)

            self.record_token_event("REFRESH_TOKEN", existing_provider_token.user_id,
                                    existing_provider_token.provider_name)

            return new_access_token

        except Exception:
            self.database_session.rollback()
            return None

    # Function that refreshes a WeSki access token
    # Returns None for now because the real refresh flow is not implemented yet
    def refresh_weski_token(self, existing_provider_token):
        # TODO: replace with real WeSki refresh flow later if available (I CANT FIND THEIR DOCS FOR THIS)
        return None

    # Function that refreshes a MyWhoosh access token
    # Returns None for now because the real refresh flow is not implemented yet
    def refresh_mywhoosh_token(self, existing_provider_token):
        # TODO: replace with real MyWhoosh refresh flow later if available (I CANT FIND THEIR DOCS FOR THIS)
        return None

    # Function that gets a valid provider token for API calls
    # Returns a dictionary that tells the route(in main.py) whether the token is returned successfully or
    # if there was an error (like token not found, revoked, refresh failed, etc)
    def get_valid_provider_token(self, user_id: int, provider_name: str):
        existing_provider_token = self.find_provider_token(user_id, provider_name)

        if not existing_provider_token:
            return self.build_error_response(provider_name, "Provider token not found")

        try:
            if self.is_access_token_expired(existing_provider_token):
                refreshed_access_token = self.refresh_provider_access_token(existing_provider_token)

                if not refreshed_access_token:
                    return self.build_error_response(provider_name, "Token refresh failed")

                return {"success": True, "message": "Token refreshed successfully", "provider_name": provider_name,
                        "access_token": refreshed_access_token, "token_last_4": existing_provider_token.token_last_4}

            access_token = self.decrypt_token(existing_provider_token.encrypted_access_token)

            return {"success": True, "message": "Token returned successfully", "provider_name": provider_name,
                    "access_token": access_token, "token_last_4": existing_provider_token.token_last_4
            }

        except Exception:
            return self.build_error_response(provider_name, "Could not return token")

    # Function that revokes a provider token
    # Returns a dictionary that tells the route(in main.py) what happened after trying to revoke the token
    def revoke_provider_token(self, user_id: int, provider_name: str):
        try:
            # Find the token in the database
            existing_provider_token = self.find_provider_token(user_id, provider_name)

        # If token does not exist or is already revoked
        if not existing_provider_token or existing_provider_token.token_status == "REVOKED":
            return {"success": True, "message": "No active provider token to revoke", "provider_name": provider_name, "token_action": "REVOKE_TOKEN"}

            else:  # set token as revoked
                existing_provider_token.token_status = "REVOKED"
                existing_provider_token.revoked_at = datetime.now()
                existing_provider_token.updated_at = datetime.now()
                self.database_session.commit()

                self.record_token_event("REVOKE_TOKEN", user_id, provider_name)

                return {"success": True, "message": "Provider token revoked successfully", "provider_name": provider_name,
                        "token_action": "REVOKE_TOKEN"}

        except Exception:
            self.database_session.rollback()
            return self.build_error_response(provider_name, "Database revoke failed")


def verify_provider_token(database_session: Session, user_id: int, provider_name: str) -> dict:
    token = find_provider_token(database_session, user_id, provider_name)

    if not token or token.token_status != "ACTIVE":
        return {
            "allowed": False,
            "reason": "NO_ACTIVE_TOKEN",
            "user_id": user_id,
            "provider_name": provider_name
        }

    return {
        "allowed": True,
        "reason": "APPROVED",
        "user_id": user_id,
        "provider_name": provider_name
    }