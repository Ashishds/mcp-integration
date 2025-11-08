#!/usr/bin/env python3
"""
Model Context Protocol (MCP) Server for Google Services
Provides MCP tools for Google Sheets, Gmail, and Google Calendar integration.
Works with any MCP-compatible client via stdio protocol.
"""

import sys
import json
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server import Server
from mcp.types import Tool, TextContent
import src.sheets_manager as sheets_module
import src.email_manager as gmail_module
import src.calendar_manager as calendar_module


def load_application_configuration():
    """
    Loads the application configuration from config.json file.
    
    Returns:
        dict: Configuration dictionary, or default empty Google config if file not found
    """
    try:
        config_file_path = Path(__file__).parent.parent / 'config.json'
        with open(config_file_path, 'r') as config_file:
            return json.load(config_file)
    except Exception:
        return {'google': {}}


# Load configuration at module level
application_config = load_application_configuration()

# Initialize MCP server instance
mcp_server_instance = Server("google-services-integration-server")

@mcp_server_instance.list_tools()
async def list_available_tools():
    """
    Returns a list of all available MCP tools for Google Services.
    
    Returns:
        list: List of Tool objects defining available operations
    """
    return [
        Tool(
            name="read_sheet",
            description="Read data from a Google Sheet",
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheetId": {"type": "string", "description": "The ID of the spreadsheet"},
                    "range": {"type": "string", "description": "The range to read (e.g., 'Sheet1!A1:B10')"}
                },
                "required": ["spreadsheetId", "range"]
            }
        ),
        Tool(
            name="write_sheet",
            description="Write data to a Google Sheet",
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheetId": {"type": "string"},
                    "range": {"type": "string"},
                    "values": {
                        "type": "array",
                        "items": {"type": "array", "items": {"type": "string"}},
                        "description": "2D array of values to write"
                    }
                },
                "required": ["spreadsheetId", "range", "values"]
            }
        ),
        Tool(
            name="append_sheet",
            description="Append data to a Google Sheet",
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheetId": {"type": "string"},
                    "range": {"type": "string"},
                    "values": {
                        "type": "array",
                        "items": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "required": ["spreadsheetId", "range", "values"]
            }
        ),
        Tool(
            name="get_sheet_info",
            description="Get information about a Google Sheet",
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheetId": {"type": "string"}
                },
                "required": ["spreadsheetId"]
            }
        ),
        Tool(
            name="list_emails",
            description="List emails from Gmail",
            inputSchema={
                "type": "object",
                "properties": {
                    "maxResults": {"type": "integer", "description": "Maximum number of emails", "default": 10},
                    "query": {"type": "string", "description": "Gmail search query", "default": ""}
                }
            }
        ),
        Tool(
            name="get_email_detail",
            description="Get detailed information about a specific email",
            inputSchema={
                "type": "object",
                "properties": {
                    "messageId": {"type": "string", "description": "The Gmail message ID"}
                },
                "required": ["messageId"]
            }
        ),
        Tool(
            name="send_email",
            description="Send an email via Gmail",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body content"},
                    "isHtml": {"type": "boolean", "description": "Whether the body is HTML", "default": False}
                },
                "required": ["to", "subject", "body"]
            }
        ),
        Tool(
            name="search_emails",
            description="Search emails in Gmail",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Gmail search query"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="list_calendar_events",
            description="List upcoming calendar events",
            inputSchema={
                "type": "object",
                "properties": {
                    "calendarId": {"type": "string", "description": "Calendar ID (default: primary)", "default": "primary"},
                    "maxResults": {"type": "integer", "description": "Maximum number of events", "default": 10},
                    "timeMin": {"type": "string", "description": "Minimum time (ISO 8601 format)"}
                }
            }
        ),
        Tool(
            name="create_calendar_event",
            description="Create a new calendar event",
            inputSchema={
                "type": "object",
                "properties": {
                    "calendarId": {"type": "string", "default": "primary"},
                    "summary": {"type": "string", "description": "Event title"},
                    "description": {"type": "string", "description": "Event description"},
                    "start": {"type": "string", "description": "Start time (ISO 8601 format)"},
                    "end": {"type": "string", "description": "End time (ISO 8601 format)"},
                    "location": {"type": "string", "description": "Event location"},
                    "attendees": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Array of attendee email addresses"
                    },
                    "timeZone": {"type": "string", "default": "America/Los_Angeles"}
                },
                "required": ["summary", "start", "end"]
            }
        ),
        Tool(
            name="update_calendar_event",
            description="Update an existing calendar event",
            inputSchema={
                "type": "object",
                "properties": {
                    "calendarId": {"type": "string", "default": "primary"},
                    "eventId": {"type": "string", "description": "Event ID to update"},
                    "summary": {"type": "string"},
                    "description": {"type": "string"},
                    "start": {"type": "string"},
                    "end": {"type": "string"},
                    "location": {"type": "string"},
                    "attendees": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["eventId"]
            }
        ),
        Tool(
            name="delete_calendar_event",
            description="Delete a calendar event",
            inputSchema={
                "type": "object",
                "properties": {
                    "calendarId": {"type": "string", "default": "primary"},
                    "eventId": {"type": "string", "description": "Event ID to delete"}
                },
                "required": ["eventId"]
            }
        ),
        Tool(
            name="get_calendar_event",
            description="Get details of a specific calendar event",
            inputSchema={
                "type": "object",
                "properties": {
                    "calendarId": {"type": "string", "default": "primary"},
                    "eventId": {"type": "string", "description": "Event ID"}
                },
                "required": ["eventId"]
            }
        )
    ]

@mcp_server_instance.call_tool()
async def execute_mcp_tool(tool_name: str, tool_arguments: dict):
    """
    Executes an MCP tool based on the tool name and provided arguments.
    
    Args:
        tool_name (str): Name of the tool to execute
        tool_arguments (dict): Dictionary of arguments for the tool
        
    Returns:
        list: List of TextContent objects containing the tool execution result
    """
    try:
        # Reload configuration to get latest settings
        current_config = load_application_configuration()
        google_config = current_config.get("google", {})
        
        execution_result = None
        
        # Google Sheets operations
        if tool_name == "read_sheet":
            spreadsheet_id = tool_arguments.get("spreadsheetId") or google_config.get("spreadsheetId")
            execution_result = sheets_module.retrieve_sheet_range_data(spreadsheet_id, tool_arguments["range"])
        
        elif tool_name == "write_sheet":
            spreadsheet_id = tool_arguments.get("spreadsheetId") or google_config.get("spreadsheetId")
            execution_result = sheets_module.update_sheet_range_data(
                spreadsheet_id, tool_arguments["range"], tool_arguments["values"]
            )
        
        elif tool_name == "append_sheet":
            spreadsheet_id = tool_arguments.get("spreadsheetId") or google_config.get("spreadsheetId")
            execution_result = sheets_module.append_rows_to_sheet(
                spreadsheet_id, tool_arguments["range"], tool_arguments["values"]
            )
        
        elif tool_name == "get_sheet_info":
            spreadsheet_id = tool_arguments.get("spreadsheetId") or google_config.get("spreadsheetId")
            execution_result = sheets_module.fetch_spreadsheet_metadata(spreadsheet_id)
        
        # Gmail operations
        elif tool_name == "list_emails":
            execution_result = gmail_module.fetch_email_messages(
                tool_arguments.get("maxResults", 10), tool_arguments.get("query", "")
            )
        
        elif tool_name == "get_email_detail":
            execution_result = gmail_module.retrieve_email_message_details(tool_arguments["messageId"])
        
        elif tool_name == "send_email":
            execution_result = gmail_module.compose_and_send_email(
                tool_arguments["to"],
                tool_arguments["subject"],
                tool_arguments["body"],
                tool_arguments.get("isHtml", False)
            )
        
        elif tool_name == "search_emails":
            execution_result = gmail_module.search_email_messages(tool_arguments["query"])
        
        # Google Calendar operations
        elif tool_name == "list_calendar_events":
            execution_result = calendar_module.retrieve_calendar_events(
                tool_arguments.get("calendarId") or google_config.get("calendarId", "primary"),
                tool_arguments.get("maxResults", 10),
                tool_arguments.get("timeMin")
            )
        
        elif tool_name == "create_calendar_event":
            execution_result = calendar_module.create_calendar_event(
                tool_arguments.get("calendarId") or google_config.get("calendarId", "primary"),
                {
                    "summary": tool_arguments["summary"],
                    "description": tool_arguments.get("description", ""),
                    "start": tool_arguments["start"],
                    "end": tool_arguments["end"],
                    "location": tool_arguments.get("location", ""),
                    "attendees": tool_arguments.get("attendees", []),
                    "timeZone": tool_arguments.get("timeZone", "America/Los_Angeles")
                }
            )
        
        elif tool_name == "update_calendar_event":
            execution_result = calendar_module.modify_calendar_event(
                tool_arguments.get("calendarId") or google_config.get("calendarId", "primary"),
                tool_arguments["eventId"],
                {
                    "summary": tool_arguments.get("summary"),
                    "description": tool_arguments.get("description"),
                    "start": tool_arguments.get("start"),
                    "end": tool_arguments.get("end"),
                    "location": tool_arguments.get("location"),
                    "attendees": tool_arguments.get("attendees"),
                    "timeZone": tool_arguments.get("timeZone", "America/Los_Angeles")
                }
            )
        
        elif tool_name == "delete_calendar_event":
            execution_result = calendar_module.remove_calendar_event(
                tool_arguments.get("calendarId") or google_config.get("calendarId", "primary"),
                tool_arguments["eventId"]
            )
        
        elif tool_name == "get_calendar_event":
            execution_result = calendar_module.fetch_calendar_event_details(
                tool_arguments.get("calendarId") or google_config.get("calendarId", "primary"),
                tool_arguments["eventId"]
            )
        
        else:
            execution_result = {"success": False, "error": f"Unknown tool: {tool_name}"}
        
        return [TextContent(type="text", text=json.dumps(execution_result, indent=2))]
    
    except Exception as error:
        error_response = {"success": False, "error": str(error)}
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]


async def main():
    """
    Main entry point for the MCP server.
    Sets up stdio communication and runs the server.
    """
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server_instance.run(
            read_stream,
            write_stream,
            mcp_server_instance.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
