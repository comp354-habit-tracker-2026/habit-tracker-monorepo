from datetime import datetime
import uuid
from database import Base
from sqlalchemy import Column, Integer, String, DateTime

# This class represents a database table.
# Each row in this table stores one provider token for one user.
class ProviderToken(Base):
    __tablename__ = "PROVIDER_TOKENS"  # tablename in the database
    row_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4())) # unique id for each row
    user_id = Column(Integer, nullable=False)  #user_id of the user who owns the token
    provider_name = Column(String, nullable=False, index=True) #provider name(strava, mapmyrun, weski, mywhoosh)
    encrypted_access_token = Column(String, nullable=False) #encrypted version of the access token
    token_last_4 = Column(String, nullable=False) #last 4 characters of the token for safe display
    token_status = Column(String, nullable=False, default="ACTIVE") # current token status(ACTIVE or REVOKED)
    created_at = Column(DateTime, default=datetime.now) #when the token record was created
    revoked_at = Column(DateTime, nullable=True) #when the token was revoked
    