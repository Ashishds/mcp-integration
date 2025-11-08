#!/usr/bin/env python3
"""
Setup and Configuration Script for Google Services MCP Integration
Guides users through OAuth2 authentication and application configuration.
"""

import os
import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from src.auth_manager import (
    check_authentication_status,
    generate_oauth_authorization_url,
    exchange_authorization_code_for_credentials,
    CREDENTIALS_PATH
)


def load_application_configuration():
    """
    Loads the application configuration from config.json file.
    
    Returns:
        dict: Configuration dictionary with Google service settings
    """
    try:
        config_file_path = Path('config.json')
        with open(config_file_path, 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        return {'google': {}}
    except json.JSONDecodeError:
        print('Warning: config.json contains invalid JSON. Creating new configuration.')
        return {'google': {}}


def save_application_configuration(configuration_data):
    """
    Saves the application configuration to config.json file.
    
    Args:
        configuration_data (dict): Configuration dictionary to save
    """
    config_file_path = Path('config.json')
    with open(config_file_path, 'w') as config_file:
        json.dump(configuration_data, config_file, indent=2)


def setup_google_services_integration():
    """
    Main setup function that guides users through:
    1. Creating credentials.json file
    2. OAuth2 authentication
    3. Application configuration
    """
    print('=' * 60)
    print('Google Services MCP Integration Setup')
    print('=' * 60 + '\n')
    
    # Step 1: Verify credentials.json exists
    print('Step 1: Google OAuth2 Credentials')
    print('-' * 60)
    if not os.path.exists(CREDENTIALS_PATH):
        print('credentials.json file not found.')
        print('\nTo create credentials.json:')
        print('1. Visit: https://console.cloud.google.com/apis/credentials')
        print('2. Create OAuth 2.0 Client ID credentials')
        print('3. Download the credentials file')
        print('4. Save it as credentials.json in the project root directory\n')
        
        user_input = input('Press Enter when credentials.json is ready, or "q" to quit: ')
        if user_input.lower() == 'q':
            print('Setup cancelled.')
            return
        
        if not os.path.exists(CREDENTIALS_PATH):
            print('\nError: credentials.json not found. Please create it first.')
            return
        print('✓ credentials.json found!\n')
    else:
        print('✓ credentials.json already exists\n')
    
    # Step 2: OAuth2 Authorization
    print('Step 2: OAuth2 Authorization')
    print('-' * 60)
    if check_authentication_status():
        print('✓ Authentication tokens found.')
        reauthorize = input('Do you want to re-authorize? (y/n): ')
        if reauthorize.lower() != 'y':
            print('Using existing authorization tokens.\n')
        else:
            perform_oauth_authentication()
    else:
        perform_oauth_authentication()
    
    # Step 3: Application Configuration
    print('Step 3: Application Configuration')
    print('-' * 60)
    app_config = load_application_configuration()
    
    if 'google' not in app_config:
        app_config['google'] = {}
    
    # Get spreadsheet ID (optional)
    spreadsheet_prompt = 'Enter your Google Spreadsheet ID (optional, press Enter to skip): '
    spreadsheet_id = input(spreadsheet_prompt).strip()
    if spreadsheet_id:
        app_config['google']['spreadsheetId'] = spreadsheet_id
        print(f'✓ Spreadsheet ID saved: {spreadsheet_id}')
    else:
        print('  Spreadsheet ID skipped (can be set per-operation)')
    
    # Get calendar ID (optional, defaults to 'primary')
    calendar_prompt = 'Enter Calendar ID (default: primary, press Enter for default): '
    calendar_id = input(calendar_prompt).strip()
    app_config['google']['calendarId'] = calendar_id or 'primary'
    print(f'✓ Calendar ID: {app_config["google"]["calendarId"]}')
    
    # Save configuration
    save_application_configuration(app_config)
    print('\n✓ Configuration saved successfully!')
    
    # Completion message
    print('\n' + '=' * 60)
    print('Setup Complete!')
    print('=' * 60)
    print('\nYour Google Services MCP integration is now configured.')
    print('You can start using the MCP server with Claude Desktop.')
    print('\nNext steps:')
    print('1. Configure Claude Desktop to use this MCP server')
    print('2. Restart Claude Desktop')
    print('3. Start using Google Services tools in Claude\n')


def perform_oauth_authentication():
    """
    Performs OAuth2 authentication flow.
    Guides user through browser-based authorization.
    """
    try:
        authorization_url = generate_oauth_authorization_url()
        print('\nTo authorize this application:')
        print('1. Open the following URL in your browser:')
        print(f'\n   {authorization_url}\n')
        print('2. Sign in with your Google account')
        print('3. Grant the requested permissions')
        print('4. After authorization, you will be redirected to a page')
        print('5. Copy the FULL URL from your browser address bar')
        
        redirect_url = input('\nPaste the full redirect URL here: ').strip()
        
        if not redirect_url:
            print('Error: No redirect URL provided.')
            return
        
        # Parse authorization code from redirect URL
        parsed_url = urlparse(redirect_url)
        url_query_params = parse_qs(parsed_url.query)
        auth_code = url_query_params.get('code', [None])[0]
        
        if not auth_code:
            print('Error: No authorization code found in the URL.')
            print('Please make sure you copied the complete URL from your browser.')
            return
        
        # Exchange authorization code for credentials
        exchange_authorization_code_for_credentials(auth_code)
        print('\n✓ Authorization successful! Tokens saved.')
        print('  You can now use Google Services APIs.\n')
    
    except FileNotFoundError:
        print('\nError: credentials.json not found.')
        print('Please create it first (see Step 1).\n')
    except Exception as error:
        print(f'\nError during authorization: {str(error)}')
        print('\nAlternative: You can also authorize by running the application,')
        print('which will automatically open a browser for authorization.\n')


if __name__ == '__main__':
    try:
        setup_google_services_integration()
    except KeyboardInterrupt:
        print('\n\nSetup cancelled by user.')
    except Exception as error:
        print(f'\nUnexpected error during setup: {str(error)}')
        import traceback
        traceback.print_exc()


# Maintain backward compatibility
def setup():
    """Backward compatibility wrapper for setup_google_services_integration"""
    setup_google_services_integration()

