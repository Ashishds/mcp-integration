"""
Gmail API Integration Module
Provides functions for reading, sending, and searching emails via Gmail API.
"""

from googleapiclient.discovery import build
from base64 import urlsafe_b64decode, urlsafe_b64encode
from email.mime.text import MIMEText
from src.auth_manager import obtain_google_credentials


def initialize_gmail_api_client():
    """
    Initializes and returns a Gmail API service client.
    
    Returns:
        Resource: Gmail API service object
    """
    api_credentials = obtain_google_credentials()
    return build('gmail', 'v1', credentials=api_credentials)


def fetch_email_messages(max_results=10, search_query=''):
    """
    Retrieves a list of email messages from the user's Gmail inbox.
    
    Args:
        max_results (int): Maximum number of messages to retrieve
        search_query (str): Gmail search query string
        
    Returns:
        dict: Result dictionary with 'success', 'messages', and 'total' keys
    """
    try:
        gmail_client = initialize_gmail_api_client()
        response = gmail_client.users().messages().list(
            userId='me',
            maxResults=max_results,
            q=search_query
        ).execute()
        
        message_list = response.get('messages', [])
        detailed_messages = []
        
        for message_item in message_list:
            message_details = retrieve_email_message_details(message_item['id'])
            if message_details['success']:
                detailed_messages.append(message_details['data'])
        
        return {
            'success': True,
            'messages': detailed_messages,
            'total': response.get('resultSizeEstimate', 0)
        }
    except Exception as error:
        return {
            'success': False,
            'error': str(error)
        }


def retrieve_email_message_details(message_id):
    """
    Retrieves detailed information about a specific email message.
    
    Args:
        message_id (str): The Gmail message ID
        
    Returns:
        dict: Result dictionary with 'success' and 'data' keys
    """
    try:
        gmail_client = initialize_gmail_api_client()
        message = gmail_client.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        
        message_headers = message.get('payload', {}).get('headers', [])
        
        def extract_header_value(header_name):
            """Extracts a header value from message headers."""
            for header in message_headers:
                if header['name'].lower() == header_name.lower():
                    return header['value']
            return ''
        
        message_data = {
            'id': message['id'],
            'threadId': message.get('threadId', ''),
            'subject': extract_header_value('subject'),
            'from': extract_header_value('from'),
            'to': extract_header_value('to'),
            'date': extract_header_value('date'),
            'snippet': message.get('snippet', ''),
            'body': parse_email_body_content(message.get('payload', {}))
        }
        
        return {
            'success': True,
            'data': message_data
        }
    except Exception as error:
        return {
            'success': False,
            'error': str(error)
        }


def parse_email_body_content(payload):
    """
    Extracts and decodes the body content from an email message payload.
    
    Args:
        payload (dict): The message payload from Gmail API
        
    Returns:
        str: Decoded email body content
    """
    if not payload:
        return ''
    
    # Check for direct body data
    body_data = payload.get('body', {}).get('data')
    if body_data:
        return urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
    
    # Check multipart message parts
    message_parts = payload.get('parts', [])
    for part in message_parts:
        mime_type = part.get('mimeType')
        if mime_type == 'text/plain':
            part_body_data = part.get('body', {}).get('data')
            if part_body_data:
                return urlsafe_b64decode(part_body_data).decode('utf-8', errors='ignore')
        elif mime_type == 'text/html':
            part_body_data = part.get('body', {}).get('data')
            if part_body_data:
                return urlsafe_b64decode(part_body_data).decode('utf-8', errors='ignore')
    
    return ''


def compose_and_send_email(recipient_address, email_subject, email_body, use_html_format=False):
    """
    Composes and sends an email message via Gmail API.
    
    Args:
        recipient_address (str): Recipient email address
        email_subject (str): Email subject line
        email_body (str): Email body content
        use_html_format (bool): Whether the body is HTML formatted
        
    Returns:
        dict: Result dictionary with 'success', 'messageId', and 'threadId' keys
    """
    try:
        gmail_client = initialize_gmail_api_client()
        
        email_message = MIMEText(email_body, 'html' if use_html_format else 'plain')
        email_message['to'] = recipient_address
        email_message['subject'] = email_subject
        
        encoded_message = urlsafe_b64encode(email_message.as_bytes()).decode('utf-8')
        
        sent_message = gmail_client.users().messages().send(
            userId='me',
            body={'raw': encoded_message}
        ).execute()
        
        return {
            'success': True,
            'messageId': sent_message.get('id', ''),
            'threadId': sent_message.get('threadId', '')
        }
    except Exception as error:
        return {
            'success': False,
            'error': str(error)
        }


def search_email_messages(search_query):
    """
    Searches for email messages using a Gmail search query.
    
    Args:
        search_query (str): Gmail search query string
        
    Returns:
        dict: Result dictionary with 'success', 'messageIds', and 'total' keys
    """
    try:
        gmail_client = initialize_gmail_api_client()
        response = gmail_client.users().messages().list(
            userId='me',
            q=search_query,
            maxResults=50
        ).execute()
        
        message_list = response.get('messages', [])
        return {
            'success': True,
            'messageIds': [msg['id'] for msg in message_list],
            'total': response.get('resultSizeEstimate', 0)
        }
    except Exception as error:
        return {
            'success': False,
            'error': str(error)
        }


# Maintain backward compatibility with original function names
get_gmail_service = initialize_gmail_api_client
list_emails = fetch_email_messages
get_email_detail = retrieve_email_message_details
extract_body = parse_email_body_content
send_email = compose_and_send_email
search_emails = search_email_messages

