"""
Google OAuth2 Authentication Module
Handles OAuth2 flow and credential management for Google API services.
"""

import os
import json
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Required OAuth2 scopes for Google APIs
OAUTH_SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar'
]

# File paths for credentials and tokens
_TOKEN_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'tokens.json')
_CREDENTIALS_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'credentials.json')

# Export paths for use in other modules
TOKEN_PATH = _TOKEN_FILE_PATH
CREDENTIALS_PATH = _CREDENTIALS_FILE_PATH


def obtain_google_credentials():
    """
    Obtains valid Google API credentials.
    
    Checks for existing tokens, refreshes if expired, or initiates
    OAuth2 flow if no valid credentials exist.
    
    Returns:
        Credentials: Valid Google API credentials object
        
    Raises:
        FileNotFoundError: If credentials.json is not found
    """
    credentials = None
    
    # Load existing tokens if available
    if os.path.exists(_TOKEN_FILE_PATH):
        credentials = Credentials.from_authorized_user_file(_TOKEN_FILE_PATH, OAUTH_SCOPES)
    
    # Validate and refresh credentials if needed
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            # Refresh expired credentials
            credentials.refresh(Request())
        else:
            # Start new OAuth2 flow
            if not os.path.exists(_CREDENTIALS_FILE_PATH):
                raise FileNotFoundError(
                    f'credentials.json not found at {_CREDENTIALS_FILE_PATH}. '
                    'Please create it with your OAuth2 credentials.'
                )
            
            oauth_flow = InstalledAppFlow.from_client_secrets_file(
                _CREDENTIALS_FILE_PATH, OAUTH_SCOPES)
            credentials = oauth_flow.run_local_server(port=0)
        
        # Save refreshed or new tokens
        persist_credentials_to_file(credentials)
    
    return credentials


def persist_credentials_to_file(credentials):
    """
    Saves OAuth2 credentials to a JSON file.
    
    Args:
        credentials (Credentials): Google API credentials object
    """
    with open(_TOKEN_FILE_PATH, 'w') as token_file:
        token_file.write(credentials.to_json())


def generate_oauth_authorization_url():
    """
    Generates an OAuth2 authorization URL for manual authentication.
    
    Returns:
        str: Authorization URL for user to visit
        
    Raises:
        FileNotFoundError: If credentials.json is not found
    """
    if not os.path.exists(_CREDENTIALS_FILE_PATH):
        raise FileNotFoundError('credentials.json not found')
    
    oauth_flow = InstalledAppFlow.from_client_secrets_file(
        _CREDENTIALS_FILE_PATH, OAUTH_SCOPES)
    authorization_url, _ = oauth_flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    return authorization_url


def exchange_authorization_code_for_credentials(auth_code):
    """
    Exchanges an authorization code for OAuth2 credentials.
    
    Args:
        auth_code (str): Authorization code from OAuth2 callback
        
    Returns:
        Credentials: Google API credentials object
    """
    oauth_flow = InstalledAppFlow.from_client_secrets_file(
        _CREDENTIALS_FILE_PATH, OAUTH_SCOPES)
    oauth_flow.fetch_token(code=auth_code)
    credentials = oauth_flow.credentials
    persist_credentials_to_file(credentials)
    return credentials


def check_authentication_status():
    """
    Checks if valid Google API credentials exist.
    
    Returns:
        bool: True if valid credentials exist, False otherwise
    """
    try:
        credentials = obtain_google_credentials()
        return credentials and credentials.valid
    except Exception:
        return False


# Maintain backward compatibility with original function names
get_credentials = obtain_google_credentials
save_token = persist_credentials_to_file
get_auth_url = generate_oauth_authorization_url
get_token_from_code = exchange_authorization_code_for_credentials
is_authorized = check_authentication_status

