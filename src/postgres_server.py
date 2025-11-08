#!/usr/bin/env python3
"""
PostgreSQL MCP Server for Claude Desktop
Provides database operations via Model Context Protocol
"""

import sys
import json
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server
import src.postgres_handler as db

def load_postgresql_configuration():
    """
    Loads PostgreSQL database configuration from config.json file.
    Tries multiple possible file locations.
    
    Returns:
        dict: Configuration dictionary with PostgreSQL settings
    """
    try:
        # Try multiple possible paths
        possible_config_paths = [
            Path(__file__).parent.parent / 'config.json',  # Standard location
            Path.cwd() / 'config.json',  # Current working directory
            Path.home() / 'mcplatestv1' / 'config.json',  # Alternative location
        ]
        
        for config_file_path in possible_config_paths:
            if config_file_path.exists():
                with open(config_file_path, 'r') as config_file:
                    return json.load(config_file)
        
        # If no config file found, return empty dict
        return {'database': {}}
    except Exception as config_error:
        # Return error info for debugging
        return {'database': {}, 'error': str(config_error)}


# Load configuration at module level
postgresql_config = load_postgresql_configuration()
postgresql_connection_url = postgresql_config.get('database', {}).get('url', '')

# Initialize MCP server instance
postgresql_mcp_server = Server("postgresql-integration-server")

@postgresql_mcp_server.list_tools()
async def list_postgresql_tools():
    """
    Returns a list of all available PostgreSQL MCP tools.
    
    Returns:
        list: List of Tool objects defining available PostgreSQL operations
    """
    return [
        Tool(
            name="execute_query",
            description="Execute a SELECT query and return results. Use for reading data from tables.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL SELECT query to execute"
                    },
                    "params": {
                        "type": "array",
                        "description": "Optional query parameters for parameterized queries",
                        "items": {"type": "string"}
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="execute_write",
            description="Execute INSERT, UPDATE, or DELETE queries. Use for modifying data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL INSERT, UPDATE, or DELETE query"
                    },
                    "params": {
                        "type": "array",
                        "description": "Optional query parameters",
                        "items": {"type": "string"}
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="run_custom_sql",
            description="Execute any SQL query (SELECT, INSERT, UPDATE, DELETE, etc.). Automatically handles query type.",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "Any SQL query to execute"
                    },
                    "params": {
                        "type": "array",
                        "description": "Optional query parameters",
                        "items": {"type": "string"}
                    }
                },
                "required": ["sql"]
            }
        ),
        Tool(
            name="list_tables",
            description="List all tables in the database with their schemas",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="describe_table",
            description="Get detailed schema information for a specific table including columns, types, and constraints",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table to describe"
                    }
                },
                "required": ["table_name"]
            }
        ),
        Tool(
            name="get_table_count",
            description="Get the total number of rows in a table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table"
                    }
                },
                "required": ["table_name"]
            }
        )
    ]

@postgresql_mcp_server.call_tool()
async def execute_postgresql_tool(tool_name: str, tool_arguments: dict):
    """
    Executes a PostgreSQL MCP tool based on the tool name and provided arguments.
    
    Args:
        tool_name (str): Name of the PostgreSQL tool to execute
        tool_arguments (dict): Dictionary of arguments for the tool
        
    Returns:
        list: List of TextContent objects containing the tool execution result
    """
    try:
        # Reload config on each call to ensure we have the latest
        current_postgresql_config = load_postgresql_configuration()
        current_db_url = current_postgresql_config.get('database', {}).get('url', '')
        
        if not current_db_url:
            # Try to provide helpful error message
            config_file_path = Path(__file__).parent.parent / 'config.json'
            error_message = {
                "success": False,
                "error": "Database URL not configured",
                "details": "Please add 'database.url' to config.json",
                "config_location": str(config_file_path),
                "config_exists": config_file_path.exists(),
                "config_keys": list(current_postgresql_config.keys())
            }
            if 'error' in current_postgresql_config:
                error_message["config_error"] = current_postgresql_config['error']
            return [TextContent(type="text", text=json.dumps(error_message, indent=2))]
        
        execution_result = None
        
        if tool_name == "execute_query":
            sql_query = tool_arguments.get("query")
            query_params = tool_arguments.get("params")
            execution_result = db.execute_query(current_db_url, sql_query, query_params)
        
        elif tool_name == "execute_write":
            sql_query = tool_arguments.get("query")
            query_params = tool_arguments.get("params")
            execution_result = db.execute_write(current_db_url, sql_query, query_params)
        
        elif tool_name == "run_custom_sql":
            sql_statement = tool_arguments.get("sql")
            sql_params = tool_arguments.get("params")
            execution_result = db.run_custom_sql(current_db_url, sql_statement, sql_params)
        
        elif tool_name == "list_tables":
            execution_result = db.list_tables(current_db_url)
        
        elif tool_name == "describe_table":
            table_name = tool_arguments.get("table_name")
            execution_result = db.describe_table(current_db_url, table_name)
        
        elif tool_name == "get_table_count":
            table_name = tool_arguments.get("table_name")
            execution_result = db.get_table_count(current_db_url, table_name)
        
        else:
            execution_result = {"success": False, "error": f"Unknown tool: {tool_name}"}
        
        return [TextContent(type="text", text=json.dumps(execution_result, indent=2, default=str))]
    
    except Exception as error:
        error_response = {"success": False, "error": str(error)}
        return [TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]


async def main():
    """
    Main entry point for the PostgreSQL MCP server.
    Sets up stdio communication and runs the server.
    """
    async with stdio_server() as (read_stream, write_stream):
        await postgresql_mcp_server.run(
            read_stream,
            write_stream,
            postgresql_mcp_server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())

