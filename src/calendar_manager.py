"""
Google Calendar API Integration Module
Provides functions for managing calendar events via Google Calendar API.
"""

from googleapiclient.discovery import build
from datetime import datetime, timedelta
from src.auth_manager import obtain_google_credentials


def initialize_calendar_api_client():
    """
    Initializes and returns a Google Calendar API service client.
    
    Returns:
        Resource: Google Calendar API service object
    """
    api_credentials = obtain_google_credentials()
    return build('calendar', 'v3', credentials=api_credentials)


def retrieve_calendar_events(calendar_id='primary', max_results=10, start_time=None):
    """
    Retrieves a list of calendar events from a specified calendar.
    
    Args:
        calendar_id (str): Calendar identifier (default: 'primary')
        max_results (int): Maximum number of events to retrieve
        start_time (str): ISO 8601 formatted minimum start time (optional)
        
    Returns:
        dict: Result dictionary with 'success', 'events', and 'total' keys
    """
    try:
        calendar_client = initialize_calendar_api_client()
        
        # Set default start time to current UTC time if not provided
        if start_time is None:
            start_time = datetime.utcnow().isoformat() + 'Z'
        else:
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00')).isoformat() + 'Z'
        
        events_response = calendar_client.events().list(
            calendarId=calendar_id,
            timeMin=start_time,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        event_items = events_response.get('items', [])
        
        formatted_event_list = []
        for event_item in event_items:
            formatted_event_list.append({
                'id': event_item.get('id', ''),
                'summary': event_item.get('summary', ''),
                'description': event_item.get('description', ''),
                'start': event_item.get('start', {}).get('dateTime') or event_item.get('start', {}).get('date', ''),
                'end': event_item.get('end', {}).get('dateTime') or event_item.get('end', {}).get('date', ''),
                'location': event_item.get('location', ''),
                'attendees': [attendee.get('email', '') for attendee in event_item.get('attendees', [])],
                'status': event_item.get('status', '')
            })
        
        return {
            'success': True,
            'events': formatted_event_list,
            'total': len(formatted_event_list)
        }
    except Exception as error:
        return {
            'success': False,
            'error': str(error)
        }


def create_calendar_event(calendar_id='primary', event_details=None):
    """
    Creates a new calendar event in the specified calendar.
    
    Args:
        calendar_id (str): Calendar identifier (default: 'primary')
        event_details (dict): Event data dictionary with keys:
            - summary: Event title
            - description: Event description
            - start: Start time (ISO 8601 format)
            - end: End time (ISO 8601 format)
            - location: Event location (optional)
            - attendees: List of attendee email addresses (optional)
            - timeZone: Timezone (default: 'America/Los_Angeles')
        
    Returns:
        dict: Result dictionary with 'success', 'eventId', 'htmlLink', and 'event' keys
    """
    try:
        if event_details is None:
            event_details = {}
        
        calendar_client = initialize_calendar_api_client()
        
        new_event = {
            'summary': event_details.get('summary', ''),
            'description': event_details.get('description', ''),
            'start': {
                'dateTime': event_details.get('start', datetime.utcnow().isoformat() + 'Z'),
                'timeZone': event_details.get('timeZone', 'America/Los_Angeles')
            },
            'end': {
                'dateTime': event_details.get('end', (datetime.utcnow() + timedelta(hours=1)).isoformat() + 'Z'),
                'timeZone': event_details.get('timeZone', 'America/Los_Angeles')
            }
        }
        
        if event_details.get('location'):
            new_event['location'] = event_details['location']
        
        if event_details.get('attendees'):
            new_event['attendees'] = [{'email': email} for email in event_details['attendees']]
        
        created_event = calendar_client.events().insert(
            calendarId=calendar_id,
            body=new_event
        ).execute()
        
        return {
            'success': True,
            'eventId': created_event.get('id', ''),
            'htmlLink': created_event.get('htmlLink', ''),
            'event': {
                'id': created_event.get('id', ''),
                'summary': created_event.get('summary', ''),
                'start': created_event.get('start', {}).get('dateTime') or created_event.get('start', {}).get('date', ''),
                'end': created_event.get('end', {}).get('dateTime') or created_event.get('end', {}).get('date', '')
            }
        }
    except Exception as error:
        return {
            'success': False,
            'error': str(error)
        }


def modify_calendar_event(calendar_id='primary', event_id=None, event_updates=None):
    """
    Updates an existing calendar event with new information.
    
    Args:
        calendar_id (str): Calendar identifier (default: 'primary')
        event_id (str): Event identifier to update
        event_updates (dict): Dictionary of fields to update
        
    Returns:
        dict: Result dictionary with 'success', 'eventId', and 'htmlLink' keys
    """
    try:
        if event_updates is None:
            event_updates = {}
        if event_id is None:
            raise ValueError('event_id is required')
        
        calendar_client = initialize_calendar_api_client()
        
        # Retrieve existing event
        existing_event = calendar_client.events().get(calendarId=calendar_id, eventId=event_id).execute()
        
        # Update fields if provided
        if event_updates.get('summary'):
            existing_event['summary'] = event_updates['summary']
        if event_updates.get('description'):
            existing_event['description'] = event_updates['description']
        if event_updates.get('start'):
            existing_event['start'] = {
                'dateTime': event_updates['start'],
                'timeZone': event_updates.get('timeZone', 'America/Los_Angeles')
            }
        if event_updates.get('end'):
            existing_event['end'] = {
                'dateTime': event_updates['end'],
                'timeZone': event_updates.get('timeZone', 'America/Los_Angeles')
            }
        if event_updates.get('location'):
            existing_event['location'] = event_updates['location']
        if event_updates.get('attendees'):
            existing_event['attendees'] = [{'email': email} for email in event_updates['attendees']]
        
        # Save updated event
        updated_event = calendar_client.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=existing_event
        ).execute()
        
        return {
            'success': True,
            'eventId': updated_event.get('id', ''),
            'htmlLink': updated_event.get('htmlLink', '')
        }
    except Exception as error:
        return {
            'success': False,
            'error': str(error)
        }


def remove_calendar_event(calendar_id='primary', event_id=None):
    """
    Deletes a calendar event from the specified calendar.
    
    Args:
        calendar_id (str): Calendar identifier (default: 'primary')
        event_id (str): Event identifier to delete
        
    Returns:
        dict: Result dictionary with 'success' and 'message' keys
    """
    try:
        if event_id is None:
            raise ValueError('event_id is required')
        
        calendar_client = initialize_calendar_api_client()
        calendar_client.events().delete(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()
        
        return {
            'success': True,
            'message': 'Event deleted successfully'
        }
    except Exception as error:
        return {
            'success': False,
            'error': str(error)
        }


def fetch_calendar_event_details(calendar_id='primary', event_id=None):
    """
    Retrieves detailed information about a specific calendar event.
    
    Args:
        calendar_id (str): Calendar identifier (default: 'primary')
        event_id (str): Event identifier to retrieve
        
    Returns:
        dict: Result dictionary with 'success' and 'event' keys
    """
    try:
        if event_id is None:
            raise ValueError('event_id is required')
        
        calendar_client = initialize_calendar_api_client()
        event = calendar_client.events().get(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()
        
        return {
            'success': True,
            'event': {
                'id': event.get('id', ''),
                'summary': event.get('summary', ''),
                'description': event.get('description', ''),
                'start': event.get('start', {}).get('dateTime') or event.get('start', {}).get('date', ''),
                'end': event.get('end', {}).get('dateTime') or event.get('end', {}).get('date', ''),
                'location': event.get('location', ''),
                'attendees': [attendee.get('email', '') for attendee in event.get('attendees', [])],
                'status': event.get('status', '')
            }
        }
    except Exception as error:
        return {
            'success': False,
            'error': str(error)
        }


# Maintain backward compatibility with original function names
get_calendar_service = initialize_calendar_api_client
list_events = retrieve_calendar_events
create_event = create_calendar_event
update_event = modify_calendar_event
delete_event = remove_calendar_event
get_event = fetch_calendar_event_details

