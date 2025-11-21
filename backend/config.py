import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SQLALCHEMY_DATABASE_URI = "sqlite:///campus.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Google Calendar OAuth Configuration
# Load from environment variables
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:5000/api/calendar/callback")
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

# Validate required environment variables
if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    raise ValueError(
        "GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set as environment variables. "
        "Create a .env file in the backend directory with these values."
    )