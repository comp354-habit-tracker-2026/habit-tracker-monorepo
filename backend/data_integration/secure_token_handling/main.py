from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, Header


#class for the verification of tokens
class VerifyProviderTokenRequest(BaseModel):
    user_id: int
    provider_name: str
    scope: str

@app.post("/api/permissions/verify")
def verify_permission(
    request: VerifyProviderTokenRequest,
    database_session: Session = Depends(open_database_session),
    _: None = Depends(check_api_key),
    x_caller_service: str = Header(default="")
):
    user_id = request.user_id
    provider_name = normalize_provider_name(request.provider_name)

    token_manager = ProviderTokenManager(database_session)

    # Both checks passed
    return token_manager.verify_provider_token(
        user_id=user_id,
        provider_name=provider_name,
        scope=request.scope,
        caller_service=x_caller_service
    )
