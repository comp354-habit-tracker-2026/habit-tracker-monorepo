
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Location of the SQLite database file stored in this project folder 
DATABASE_URL = "sqlite:///./provider_tokens.db"

# Creates the connection to the database
database_connection = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}) # needed for SQLite with FastAPI

# Create a session maker
create_session = sessionmaker(bind=database_connection, autoflush=False, autocommit=False)

# Base is the parent class for all SQLAlchemy models-> so any model that inherits from Base becomes a database table model
Base = declarative_base()

# Creates a database session for each request
# and closes it after the request is finished
def open_database_session():
    database_session = create_session()
    try:
        yield database_session
    finally:
        database_session.close()