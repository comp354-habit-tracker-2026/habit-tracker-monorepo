from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, Header
from database import Base, database_connection, open_database_session
from token_service import ProviderTokenManager
from database import Base, database_connection, open_database_session
from token_service import ProviderTokenManager
from token_model import ProviderToken
import os

# Load values from .env into environment variables
load_dotenv()  # this is to keep the test api key in local .env

# Install first libraries in the requirement.txt
# WHEN RUNNING TYPE IN TERMINAL:
# source venv/bin/activate
# python3 main.py OR python main.py
# -----------
# FOR SWAGGER UI:
# go to this http://127.0.0.1:8000/docs
# also the x-api-key in swagger is "group6-test-key"

# Only these providers are allowed
ALLOWED_PROVIDERS = {"strava", "mapmyrun", "weski", "mywhoosh"}

# Create database table when the app starts
Base.metadata.create_all(bind=database_connection)

# Create the FastAPI app
app = FastAPI(title="Provider Token API", description="API for saving, revoking, and retrieving provider tokens", version="1.0.0")

# Temporary API key check so only authorized users can use the token routes
TEST_API_KEY = os.getenv("TEST_API_KEY")  # saved in local .env

# Class for the request body when saving a provider token
class SaveProviderTokenRequest(BaseModel):  # pydantic library --> for data validation
    user_id: int
    provider_name: str
    access_token: str
    refresh_token: str | None = None
    access_token_expires_at: datetime | None = None

# Class for the request body when revoking a provider token
class RevokeProviderTokenRequest(BaseModel):
    user_id: int
    provider_name: str


class VerifyPermissionRequest(BaseModel):
    user_id: int
    provider_name: str
    scope: str


class VerifyProviderTokenRequest(BaseModel):
    user_id: int
    provider_name: str
    scope: str

# Function that checks if api_key is valid or not
# Returns 401 if the x-api-key value is wrong
def check_api_key(x_api_key: str = Header(default="")):
    if x_api_key != TEST_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

def normalize_provider_name(provider_name: str) -> str:
    normalized_provider_name = provider_name.strip().lower()

    if not normalized_provider_name:
        raise HTTPException(status_code=400, detail="provider_name is required")

    if normalized_provider_name not in ALLOWED_PROVIDERS:
        raise HTTPException(status_code=400, detail="provider_name is invalid")

    return normalized_provider_name

# Function that checks if the API is running
# Returns a message that it is running
@app.get("/", tags=["Provider Tokens"])
def root():
    return {"message": "Provider token API is running"}

# ---------------- BELOW ARE THE ROUTES TO SAVE AND REVOKE TOKEN ----------------

# Function that saves a provider token through the API
# Returns whatever the save_provider_token method returns
@app.post(
    "/provider-tokens/save",
    tags=["Provider Tokens"],
    summary="Save provider token"
)
def save_provider_token_route(request: SaveProviderTokenRequest, database_session: Session = Depends(open_database_session),
            _: None = Depends(check_api_key)):
    user_id = request.user_id
    provider_name = normalize_provider_name(request.provider_name)
    access_token = request.access_token.strip()
    refresh_token = request.refresh_token.strip() if request.refresh_token else None
    access_token_expires_at = request.access_token_expires_at

    # Check if provider_name is empty
    if not provider_name:
        raise HTTPException(status_code=400, detail="provider_name is required")

    # Check if access_token is empty
    if not access_token:
        raise HTTPException(status_code=400, detail="access_token is required")

    # Create an instance of the ProviderTokenManager with the database session
    token_manager = ProviderTokenManager(database_session)

    # Call the save_provider_token method of the token manager with the request data
    # Returns that method's result as the API response
    return token_manager.save_provider_token(user_id=user_id, provider_name=provider_name, access_token=access_token,
            refresh_token=refresh_token, access_token_expires_at=access_token_expires_at)

# Function that revokes a provider token through the API
# Returns whatever the revoke_provider_token method returns
@app.post(
    "/provider-tokens/revoke",
    tags=["Provider Tokens"],
    summary="Revoke provider token"
)
def revoke_provider_token_route(request: RevokeProviderTokenRequest, database_session: Session = Depends(open_database_session),
        _: None = Depends(check_api_key)):

    user_id = request.user_id
    provider_name = normalize_provider_name(request.provider_name)

    # Create an instance of the ProviderTokenManager with the database session
    token_manager = ProviderTokenManager(database_session)

    # Call the revoke_provider_token method of the token manager with the request data
    # Returns that method's result as the API response
    return token_manager.revoke_provider_token(
        user_id=user_id,
        provider_name=provider_name
    )

# Function that gets a valid provider token through the API
# Returns whatever the get_valid_provider_token method returns
@app.get( "/provider-tokens/{user_id}/{provider_name}", tags=["Provider Tokens"], summary="Get valid provider token")
def get_provider_token_route(user_id: int, provider_name: str, database_session: Session = Depends(open_database_session), _: None = Depends(check_api_key)):
    provider_name = normalize_provider_name(provider_name)

    # Create an instance of the ProviderTokenManager with the database session
    token_manager = ProviderTokenManager(database_session)

    # Call the get_valid_provider_token method of the token manager
    # Returns that method's result as the API response
    return token_manager.get_valid_provider_token(user_id=user_id, provider_name=provider_name)
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import Base, database_connection, open_database_session
from token_service import save_provider_token, revoke_provider_token
from fastapi import FastAPI, Depends, HTTPException, Header
import os

# Install first libraries the in the requirement.txt
# WHEN RUNNING TYPE IN TERMINAL:
# source venv/bin/activate
# python3 main.py OR python main.py
#-----------
# FOR SWAGGER UI:
# go to this http://127.0.0.1:8000/docs
# also the x-api-key in swagger is "group6-test-key"

# Only these providers are allowed
ALLOWED_PROVIDERS = ["strava", "mapmyrun", "weski", "mywhoosh"]

# Create database table when the app starts
Base.metadata.create_all(bind=database_connection)

# Create the FastAPI app
app = FastAPI(title="Provider Token API")

# Temporary API key check so only authorized users can use the save and revoke routes
TEST_API_KEY = os.getenv("TEST_API_KEY") # saved on local .env

# Class for the request body when saving a provider token
class SaveProviderTokenRequest(BaseModel): # pydantic library --> for data validation https://docs.pydantic.dev/latest/#pydantic-examples
    user_id: int
    provider_name: str
    access_token: str

# Class for the request body when revoking a provider token
class RevokeProviderTokenRequest(BaseModel):
    user_id: int
    provider_name: str

# Function that checks if api_key is valid or not
def check_api_key(x_api_key: str = Header(default="")):
    if x_api_key != TEST_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

# Function that checks if the API is running
# Returns a message that it is running
@app.get("/")
def root():  # this only shows if you go to http://127.0.0.1:8000/
    return {"message": "Provider token API is running"}

# ---------------- BELOW ARE THE ROUTES TO SAVE AND REVOKE TOKEN -----------------
# Function that saves a provider token through the API
# Returns whatever the save_provider_token function returns
@app.post("/provider-tokens/save")
def save_provider_token_route(request: SaveProviderTokenRequest, database_session: Session = Depends(open_database_session), _: None = Depends(check_api_key)):
    user_id = request.user_id
    provider_name = request.provider_name.strip().lower()
    access_token = request.access_token.strip()

    # Check if provider_name is empty
    if not provider_name:
        raise HTTPException(status_code=400, detail="provider_name is required")

    # Check if access_token is empty
    if not access_token:
        raise HTTPException(status_code=400, detail="access_token is required")

    # Make sure provider is one of the 4 allowed providers
    if provider_name not in ALLOWED_PROVIDERS:
        raise HTTPException(status_code=400, detail="provider_name is invalid")

    # Call the save function from token_service.py
    return save_provider_token(database_session=database_session, user_id=user_id, provider_name=provider_name, access_token=access_token) # basically calls the method from token_service with request data and returns that function's result as the API response

# Function that revokes a provider token through the API
# Returns whatever the revoke_provider_token function returns
@app.post("/provider-tokens/revoke")
def revoke_provider_token_route(request: RevokeProviderTokenRequest, database_session: Session = Depends(open_database_session), _: None = Depends(check_api_key)):
    user_id = request.user_id
    provider_name = request.provider_name.strip().lower()

    # Check if provider_name is empty
    if not provider_name:
        raise HTTPException(status_code=400, detail="provider_name is required")

    # Make sure provider is one of the 4 allowed providers
    if provider_name not in ALLOWED_PROVIDERS:
        raise HTTPException(status_code=400, detail="provider_name is invalid")

    # Call the revoke function from provider_token_logic.py
    return revoke_provider_token(database_session=database_session, user_id=user_id, provider_name=provider_name)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


@app.post("/api/permissions/verify")
def verify_permission(
    request: VerifyPermissionRequest,
    database_session: Session = Depends(open_database_session),
    _: None = Depends(check_api_key),
    x_caller_service: str = Header(default="")
):
    user_id = request.user_id
    provider_name = normalize_provider_name(request.provider_name)

    # --- WAITING ON (#11) ---
    # consent = database_session.query(UserConsent).filter_by(
    #     user_id=user_id, provider_name=provider_name
    # ).first()
    # if not consent:
    #     return {"allowed": False, "reason": "CONSENT_NOT_FOUND", ...}
    # if consent.status == "REVOKED":
    #     return {"allowed": False, "reason": "CONSENT_REVOKED", ...}
    # if consent.expires_at and consent.expires_at < datetime.now():
    #     return {"allowed": False, "reason": "CONSENT_EXPIRED", ...}

    # --- WAITING ON USERS TABLE OWNER ---
    # if user.is_deleted:
    #     return {"allowed": False, "reason": "ACCOUNT_DELETED", ...}

    if not token or token.token_status != "ACTIVE":
        return {"allowed": False, "reason": "NO_ACTIVE_TOKEN", "user_id": user_id, "provider_name": provider_name}

    # Both checks passed
    return {"allowed": True, "reason": "APPROVED", "user_id": user_id, "provider_name": provider_name}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)