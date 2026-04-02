from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import Base, database_connection, open_database_session
from token_service import save_provider_token, revoke_provider_token, verify_provider_token
from token_model import ProviderToken
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


class VerifyPermissionRequest(BaseModel):
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


@app.post("/api/permissions/verify")
def verify_permission(
    request: VerifyPermissionRequest,
    database_session: Session = Depends(open_database_session),
    _: None = Depends(check_api_key)
):
    user_id = request.user_id
    provider_name = request.provider_name.strip().lower()

    if provider_name not in ALLOWED_PROVIDERS:
        raise HTTPException(status_code=400, detail="provider_name is invalid")

    consent = database_session.query(UserConsent).filter_by(
        user_id=user_id, provider_name=provider_name
    ).first()

    if not consent or consent.status != "ACTIVE":
        return {"allowed": False, "reason": "NO_CONSENT", "user_id": user_id, "provider_name": provider_name}

    token = database_session.query(ProviderToken).filter_by(
        user_id=user_id, provider_name=provider_name
    ).first()

    if not token or token.token_status != "ACTIVE":
        return {"allowed": False, "reason": "NO_ACTIVE_TOKEN", "user_id": user_id, "provider_name": provider_name}

    # Both checks passed
    return {"allowed": True, "reason": "APPROVED", "user_id": user_id, "provider_name": provider_name}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)



