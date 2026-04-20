from datetime import datetime
import uuid
from database import Base
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint

# This class represents a database table.
# Each row in this table stores one provider token for one user.
# Example providers: strava, mapmyrun, weski, mywhoosh
class ProviderToken(Base):
    __tablename__ = "PROVIDER_TOKENS"  # tablename in the database
    __table_args__ = (UniqueConstraint("user_id", "provider_name", name="unique_user_provider"),)
    row_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4())) # unique id for each row
    user_id = Column(Integer, nullable=False, index=True)  #user_id of the user who owns the token
    provider_name = Column(String, nullable=False, index=True) #provider name(strava, mapmyrun, weski, mywhoosh)

    encrypted_access_token = Column(String, nullable=False) #encrypted version of the access token
    encrypted_refresh_token = Column(String, nullable=True) #encrypted version of the refresh token (if the provider has one, otherwise null)

    token_last_4 = Column(String, nullable=False) #last 4 characters of the token for safe display
    token_status = Column(String, nullable=False, default="ACTIVE") # current token status(ACTIVE or REVOKED)

    #when the access token expires (if the provider gives an expiration time, otherwise null)
    access_token_expires_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.now) #when the token record was created
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now) #when the token record was last updated ->onupdate=datetime.now means it will automatically update this field to the current time whenever the record is updated
    revoked_at = Column(DateTime, nullable=True) #when the token was revoked
