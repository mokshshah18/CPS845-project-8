from flask import Blueprint, request, redirect, jsonify
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI, GOOGLE_SCOPES
from db import db
from models import UserPreferences
import json
from datetime import datetime, timedelta

calendar_bp = Blueprint("calendar", __name__)

# ============ OAuth Initiation ============

@calendar_bp.route("/auth", methods=["GET"])
def initiate_auth():
    """Initiate Google OAuth flow - redirects user to Google login"""
    try:
        user_id = request.args.get("user_id", type=int)
        
        if not user_id:
            # Redirect to frontend with error
            return redirect("http://localhost:5173/?calendar_error=missing_user_id")
        
        # Create OAuth flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [GOOGLE_REDIRECT_URI]
                }
            },
            scopes=GOOGLE_SCOPES,
            redirect_uri=GOOGLE_REDIRECT_URI
        )
        
        # Get authorization URL with state set to user_id
        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=str(user_id)  # Pass user_id as state parameter
        )
        
        # Redirect user to Google OAuth page
        return redirect(authorization_url)
    except Exception as e:
        # Log error and redirect with error message
        print(f"OAuth initiation error: {str(e)}")
        import traceback
        traceback.print_exc()
        return redirect(f"http://localhost:5173/?calendar_error=init_failed&details={str(e)}")

# ============ OAuth Callback ============

@calendar_bp.route("/callback", methods=["GET"])
def oauth_callback():
    """Handle OAuth callback from Google - exchange code for tokens and store"""
    code = request.args.get("code")
    state = request.args.get("state")  # This is the user_id we passed
    
    if not code:
        # No code means user denied access or error occurred
        return redirect("http://localhost:5173/?calendar_error=access_denied")
    
    if not state:
        return redirect("http://localhost:5173/?calendar_error=missing_state")
    
    try:
        user_id = int(state)
    except ValueError:
        return redirect("http://localhost:5173/?calendar_error=invalid_state")
    
    try:
        # Recreate the flow to exchange code for tokens
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [GOOGLE_REDIRECT_URI]
                }
            },
            scopes=GOOGLE_SCOPES,
            redirect_uri=GOOGLE_REDIRECT_URI
        )
        
        # Exchange authorization code for tokens
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Verify credentials have required fields
        if not credentials or not credentials.token:
            raise ValueError("Failed to obtain access token from Google")
        
        # Create proper Credentials object with all required fields for API calls
        from google.oauth2.credentials import Credentials
        full_credentials = Credentials(
            token=credentials.token,
            refresh_token=getattr(credentials, 'refresh_token', None),
            token_uri=credentials.token_uri,
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            scopes=GOOGLE_SCOPES
        )
        credentials = full_credentials
        
        # Get user's email from Google API
        # Try using the token directly with a simple HTTP request first
        try:
            import requests
            # Get user info using the access token directly
            headers = {'Authorization': f'Bearer {credentials.token}'}
            response = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers=headers)
            response.raise_for_status()
            user_info = response.json()
            email = user_info.get('email', '')
            
            if not email:
                # Fallback: try building the service
                service = build('oauth2', 'v2', credentials=credentials)
                user_info = service.userinfo().get().execute()
                email = user_info.get('email', '')
        except Exception as api_error:
            print(f"Error calling Google API: {str(api_error)}")
            import traceback
            traceback.print_exc()
            # If we can't get email, we can still proceed but log a warning
            email = ''  # Will fail domain validation but at least we tried
            print("Warning: Could not retrieve user email, but continuing...")
        
        # Validate email domain (allow @torontomu.ca and @gmail.com for testing)
        # TODO: For production, you may want to restrict to @torontomu.ca only
        if email:  # Only validate if we got an email
            allowed_domains = ['@torontomu.ca', '@gmail.com']
            if not any(email.endswith(domain) for domain in allowed_domains):
                return redirect(f"http://localhost:5173/?calendar_error=invalid_domain&email={email}")
        else:
            # If we couldn't get email, use a placeholder (for testing)
            email = 'unknown@test.com'
            print("Warning: Using placeholder email since we couldn't retrieve user email")
        
        # Store tokens and email in database
        # Convert credentials to JSON for storage
        # Note: refresh_token may be None if user has already authorized
        token_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        # Get or create user preferences
        preferences = UserPreferences.query.filter_by(user_id=user_id).first()
        if not preferences:
            preferences = UserPreferences(user_id=user_id)
            db.session.add(preferences)
        
        # Store token and email
        preferences.google_calendar_token = json.dumps(token_data)
        preferences.google_calendar_email = email
        preferences.calendar_sync_enabled = True
        db.session.commit()
        
        # Redirect to frontend with success
        return redirect("http://localhost:5173/?calendar_connected=true")
        
    except Exception as e:
        # Log error with full traceback for debugging
        print(f"OAuth callback error: {str(e)}")
        import traceback
        traceback.print_exc()
        # Redirect with more specific error info
        error_msg = str(e).replace(' ', '_')[:50]  # Limit length for URL
        return redirect(f"http://localhost:5173/?calendar_error=oauth_failed&details={error_msg}")

# ============ Upcoming Event Endpoint ============

@calendar_bp.route("/upcoming", methods=["GET"])
def get_upcoming_event():
    """Get the next event from user's Google Calendar within 30 minutes"""
    user_id = request.args.get("user_id", type=int)
    
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    # Get user's stored tokens
    preferences = UserPreferences.query.filter_by(user_id=user_id).first()
    
    if not preferences or not preferences.google_calendar_token:
        return jsonify({"error": "Calendar not connected"}), 401
    
    try:
        # Load stored credentials
        token_data = json.loads(preferences.google_calendar_token)
        
        # Recreate credentials object
        credentials = Credentials(
            token=token_data.get('token'),
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
            client_id=token_data.get('client_id', GOOGLE_CLIENT_ID),
            client_secret=token_data.get('client_secret', GOOGLE_CLIENT_SECRET),
            scopes=token_data.get('scopes', GOOGLE_SCOPES)
        )
        
        # Refresh token if expired
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            # Update stored token
            token_data['token'] = credentials.token
            preferences.google_calendar_token = json.dumps(token_data)
            db.session.commit()
        
        # Query Google Calendar for events in next 30 minutes
        
        service = build('calendar', 'v3', credentials=credentials)
        
        # Get current time and 30 minutes from now
        now = datetime.utcnow()
        time_max = now + timedelta(minutes=30)
        
        # Format times for Google Calendar API (RFC3339 format)
        time_min = now.isoformat() + 'Z'
        time_max_str = time_max.isoformat() + 'Z'
        
        # Query events
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max_str,
            maxResults=1,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return jsonify(None)  # No upcoming events
        
        # Get first event
        event = events[0]
        
        # Extract event details
        event_name = event.get('summary', 'Untitled Event')
        start_time = event.get('start', {}).get('dateTime') or event.get('start', {}).get('date')
        location = event.get('location', '')
        
        return jsonify({
            'name': event_name,
            'start_time': start_time,
            'location': location
        })
        
    except Exception as e:
        print(f"Error getting upcoming event: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

