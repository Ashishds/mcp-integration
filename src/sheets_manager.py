"""
Google Sheets API Integration Module
Provides functions for reading, writing, and managing Google Sheets data.
"""

from googleapiclient.discovery import build
from src.auth_manager import obtain_google_credentials


def initialize_sheets_api_client():
    """
    Initializes and returns a Google Sheets API service client.
    
    Returns:
        Resource: Google Sheets API service object
    """
    api_credentials = obtain_google_credentials()
    return build('sheets', 'v4', credentials=api_credentials)


def retrieve_sheet_range_data(spreadsheet_id, cell_range):
    """
    Retrieves data from a specific range in a Google Sheet.
    
    Args:
        spreadsheet_id (str): The unique identifier of the spreadsheet
        cell_range (str): The range to read (e.g., 'Sheet1!A1:B10')
        
    Returns:
        dict: Result dictionary with 'success', 'data', and 'range' keys
    """
    try:
        sheets_client = initialize_sheets_api_client()
        spreadsheet_service = sheets_client.spreadsheets()
        response = spreadsheet_service.values().get(
            spreadsheetId=spreadsheet_id,
            range=cell_range
        ).execute()
        
        cell_values = response.get('values', [])
        return {
            'success': True,
            'data': cell_values,
            'range': response.get('range', cell_range)
        }
    except Exception as error:
        return {
            'success': False,
            'error': str(error)
        }


def update_sheet_range_data(spreadsheet_id, cell_range, cell_values):
    """
    Writes data to a specific range in a Google Sheet.
    
    Args:
        spreadsheet_id (str): The unique identifier of the spreadsheet
        cell_range (str): The range to write to (e.g., 'Sheet1!A1:B10')
        cell_values (list): 2D array of values to write
        
    Returns:
        dict: Result dictionary with 'success', 'updatedCells', and 'updatedRange' keys
    """
    try:
        sheets_client = initialize_sheets_api_client()
        spreadsheet_service = sheets_client.spreadsheets()
        response = spreadsheet_service.values().update(
            spreadsheetId=spreadsheet_id,
            range=cell_range,
            valueInputOption='USER_ENTERED',
            body={'values': cell_values}
        ).execute()
        
        return {
            'success': True,
            'updatedCells': response.get('updatedCells', 0),
            'updatedRange': response.get('updatedRange', cell_range)
        }
    except Exception as error:
        return {
            'success': False,
            'error': str(error)
        }


def append_rows_to_sheet(spreadsheet_id, sheet_name, row_data):
    """
    Appends new rows to the end of a Google Sheet.
    
    Args:
        spreadsheet_id (str): The unique identifier of the spreadsheet
        sheet_name (str): The name of the sheet to append to
        row_data (list): 2D array of values to append
        
    Returns:
        dict: Result dictionary with 'success', 'updatedCells', and 'updatedRange' keys
    """
    try:
        sheets_client = initialize_sheets_api_client()
        spreadsheet_service = sheets_client.spreadsheets()
        response = spreadsheet_service.values().append(
            spreadsheetId=spreadsheet_id,
            range=sheet_name,
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body={'values': row_data}
        ).execute()
        
        update_info = response.get('updates', {})
        return {
            'success': True,
            'updatedCells': update_info.get('updatedCells', 0),
            'updatedRange': update_info.get('updatedRange', sheet_name)
        }
    except Exception as error:
        return {
            'success': False,
            'error': str(error)
        }


def fetch_spreadsheet_metadata(spreadsheet_id):
    """
    Retrieves metadata and structure information about a Google Sheet.
    
    Args:
        spreadsheet_id (str): The unique identifier of the spreadsheet
        
    Returns:
        dict: Result dictionary with 'success', 'title', and 'sheets' keys
    """
    try:
        sheets_client = initialize_sheets_api_client()
        spreadsheet_service = sheets_client.spreadsheets()
        response = spreadsheet_service.get(spreadsheetId=spreadsheet_id).execute()
        
        spreadsheet_properties = response.get('properties', {})
        worksheet_list = []
        
        for worksheet in response.get('sheets', []):
            worksheet_props = worksheet.get('properties', {})
            grid_config = worksheet_props.get('gridProperties', {})
            worksheet_list.append({
                'title': worksheet_props.get('title', ''),
                'sheetId': worksheet_props.get('sheetId', ''),
                'rowCount': grid_config.get('rowCount', 0),
                'columnCount': grid_config.get('columnCount', 0)
            })
        
        return {
            'success': True,
            'title': spreadsheet_properties.get('title', ''),
            'sheets': worksheet_list
        }
    except Exception as error:
        return {
            'success': False,
            'error': str(error)
        }


# Maintain backward compatibility with original function names
get_sheets_service = initialize_sheets_api_client
read_sheet_data = retrieve_sheet_range_data
write_sheet_data = update_sheet_range_data
append_sheet_data = append_rows_to_sheet
get_sheet_info = fetch_spreadsheet_metadata

