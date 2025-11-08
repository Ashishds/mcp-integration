#!/usr/bin/env python3
"""
MongoDB MCP Server for Claude Desktop
Provides MongoDB operations via Model Context Protocol
"""

import sys
import json
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server
import src.mongo_handler as mongo

def load_mongodb_configuration():
    """
    Loads MongoDB database configuration from config.json file.
    Tries multiple possible file locations.
    
    Returns:
        dict: Configuration dictionary with MongoDB settings
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
        return {'mongodb': {}}
    except Exception as config_error:
        # Return error info for debugging
        return {'mongodb': {}, 'error': str(config_error)}


# Load configuration at module level
mongodb_config = load_mongodb_configuration()
mongodb_connection_uri = mongodb_config.get('mongodb', {}).get('uri', '')

# Initialize MCP server instance
mongodb_mcp_server = Server("mongodb-integration-server")

@mongodb_mcp_server.list_tools()
async def list_mongodb_tools():
    """
    Returns a list of all available MongoDB MCP tools.
    
    Returns:
        list: List of Tool objects defining available MongoDB operations
    """
    return [
        Tool(
            name="list_databases",
            description="List all databases in MongoDB",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="list_collections",
            description="List all collections in a specific database",
            inputSchema={
                "type": "object",
                "properties": {
                    "database_name": {
                        "type": "string",
                        "description": "Name of the database"
                    }
                },
                "required": ["database_name"]
            }
        ),
        Tool(
            name="find_documents",
            description="Find documents in a collection. Supports query, limit, skip, and sort options.",
            inputSchema={
                "type": "object",
                "properties": {
                    "database_name": {"type": "string", "description": "Database name"},
                    "collection_name": {"type": "string", "description": "Collection name"},
                    "query": {
                        "type": "string",
                        "description": "MongoDB query filter (JSON string, e.g., '{\"name\": \"John\"}')"
                    },
                    "limit": {"type": "integer", "description": "Maximum number of documents to return (default: 100)"},
                    "skip": {"type": "integer", "description": "Number of documents to skip (default: 0)"},
                    "sort": {
                        "type": "string",
                        "description": "Sort criteria (JSON string, e.g., '{\"name\": 1}' for ascending)"
                    }
                },
                "required": ["database_name", "collection_name"]
            }
        ),
        Tool(
            name="insert_document",
            description="Insert a single document into a collection",
            inputSchema={
                "type": "object",
                "properties": {
                    "database_name": {"type": "string", "description": "Database name"},
                    "collection_name": {"type": "string", "description": "Collection name"},
                    "document": {
                        "type": "string",
                        "description": "Document to insert (JSON string, e.g., '{\"name\": \"John\", \"age\": 30}')"
                    }
                },
                "required": ["database_name", "collection_name", "document"]
            }
        ),
        Tool(
            name="insert_many_documents",
            description="Insert multiple documents into a collection",
            inputSchema={
                "type": "object",
                "properties": {
                    "database_name": {"type": "string", "description": "Database name"},
                    "collection_name": {"type": "string", "description": "Collection name"},
                    "documents": {
                        "type": "string",
                        "description": "Array of documents to insert (JSON string, e.g., '[{\"name\": \"John\"}, {\"name\": \"Jane\"}]')"
                    }
                },
                "required": ["database_name", "collection_name", "documents"]
            }
        ),
        Tool(
            name="update_document",
            description="Update a single document in a collection",
            inputSchema={
                "type": "object",
                "properties": {
                    "database_name": {"type": "string", "description": "Database name"},
                    "collection_name": {"type": "string", "description": "Collection name"},
                    "filter_query": {
                        "type": "string",
                        "description": "Filter query to find document (JSON string, e.g., '{\"_id\": \"...\"}')"
                    },
                    "update_data": {
                        "type": "string",
                        "description": "Update data (JSON string, e.g., '{\"name\": \"John Updated\"}')"
                    },
                    "upsert": {
                        "type": "boolean",
                        "description": "Create document if it doesn't exist (default: false)"
                    }
                },
                "required": ["database_name", "collection_name", "filter_query", "update_data"]
            }
        ),
        Tool(
            name="update_many_documents",
            description="Update multiple documents in a collection",
            inputSchema={
                "type": "object",
                "properties": {
                    "database_name": {"type": "string", "description": "Database name"},
                    "collection_name": {"type": "string", "description": "Collection name"},
                    "filter_query": {
                        "type": "string",
                        "description": "Filter query to find documents"
                    },
                    "update_data": {
                        "type": "string",
                        "description": "Update data for matching documents"
                    },
                    "upsert": {"type": "boolean", "description": "Create documents if they don't exist"}
                },
                "required": ["database_name", "collection_name", "filter_query", "update_data"]
            }
        ),
        Tool(
            name="delete_document",
            description="Delete a single document from a collection",
            inputSchema={
                "type": "object",
                "properties": {
                    "database_name": {"type": "string", "description": "Database name"},
                    "collection_name": {"type": "string", "description": "Collection name"},
                    "filter_query": {
                        "type": "string",
                        "description": "Filter query to find document to delete"
                    }
                },
                "required": ["database_name", "collection_name", "filter_query"]
            }
        ),
        Tool(
            name="delete_many_documents",
            description="Delete multiple documents from a collection",
            inputSchema={
                "type": "object",
                "properties": {
                    "database_name": {"type": "string", "description": "Database name"},
                    "collection_name": {"type": "string", "description": "Collection name"},
                    "filter_query": {
                        "type": "string",
                        "description": "Filter query to find documents to delete"
                    }
                },
                "required": ["database_name", "collection_name", "filter_query"]
            }
        ),
        Tool(
            name="count_documents",
            description="Count documents in a collection matching a query",
            inputSchema={
                "type": "object",
                "properties": {
                    "database_name": {"type": "string", "description": "Database name"},
                    "collection_name": {"type": "string", "description": "Collection name"},
                    "query": {
                        "type": "string",
                        "description": "Query filter (JSON string, optional)"
                    }
                },
                "required": ["database_name", "collection_name"]
            }
        ),
        Tool(
            name="aggregate",
            description="Run MongoDB aggregation pipeline",
            inputSchema={
                "type": "object",
                "properties": {
                    "database_name": {"type": "string", "description": "Database name"},
                    "collection_name": {"type": "string", "description": "Collection name"},
                    "pipeline": {
                        "type": "string",
                        "description": "Aggregation pipeline (JSON array string, e.g., '[{\"$match\": {...}}, {\"$group\": {...}}]')"
                    }
                },
                "required": ["database_name", "collection_name", "pipeline"]
            }
        )
    ]

@mongodb_mcp_server.call_tool()
async def execute_mongodb_tool(tool_name: str, tool_arguments: dict):
    """
    Executes a MongoDB MCP tool based on the tool name and provided arguments.
    
    Args:
        tool_name (str): Name of the MongoDB tool to execute
        tool_arguments (dict): Dictionary of arguments for the tool
        
    Returns:
        list: List of TextContent objects containing the tool execution result
    """
    try:
        # Reload config on each call to ensure we have the latest
        current_mongodb_config = load_mongodb_configuration()
        current_mongodb_uri = current_mongodb_config.get('mongodb', {}).get('uri', '')
        
        if not current_mongodb_uri:
            # Try to provide helpful error message
            config_file_path = Path(__file__).parent.parent / 'config.json'
            error_message = {
                "success": False,
                "error": "MongoDB URI not configured",
                "details": "Please add 'mongodb.uri' to config.json",
                "config_location": str(config_file_path),
                "config_exists": config_file_path.exists(),
                "config_keys": list(current_mongodb_config.keys())
            }
            if 'error' in current_mongodb_config:
                error_message["config_error"] = current_mongodb_config['error']
            return [TextContent(type="text", text=json.dumps(error_message, indent=2))]
        
        execution_result = None
        
        if tool_name == "list_databases":
            execution_result = mongo.list_databases(current_mongodb_uri)
        
        elif tool_name == "list_collections":
            database_name = tool_arguments.get("database_name")
            execution_result = mongo.list_collections(current_mongodb_uri, database_name)
        
        elif tool_name == "find_documents":
            database_name = tool_arguments.get("database_name")
            collection_name = tool_arguments.get("collection_name")
            query_filter = tool_arguments.get("query")
            result_limit = tool_arguments.get("limit", 100)
            result_skip = tool_arguments.get("skip", 0)
            sort_criteria = tool_arguments.get("sort")
            execution_result = mongo.find_documents(
                current_mongodb_uri, database_name, collection_name, 
                query_filter, result_limit, result_skip, sort_criteria
            )
        
        elif tool_name == "insert_document":
            database_name = tool_arguments.get("database_name")
            collection_name = tool_arguments.get("collection_name")
            document_data = tool_arguments.get("document")
            execution_result = mongo.insert_document(
                current_mongodb_uri, database_name, collection_name, document_data
            )
        
        elif tool_name == "insert_many_documents":
            database_name = tool_arguments.get("database_name")
            collection_name = tool_arguments.get("collection_name")
            documents_data = tool_arguments.get("documents")
            execution_result = mongo.insert_many_documents(
                current_mongodb_uri, database_name, collection_name, documents_data
            )
        
        elif tool_name == "update_document":
            database_name = tool_arguments.get("database_name")
            collection_name = tool_arguments.get("collection_name")
            filter_query = tool_arguments.get("filter_query")
            update_data = tool_arguments.get("update_data")
            upsert_flag = tool_arguments.get("upsert", False)
            execution_result = mongo.update_document(
                current_mongodb_uri, database_name, collection_name, 
                filter_query, update_data, upsert_flag
            )
        
        elif tool_name == "update_many_documents":
            database_name = tool_arguments.get("database_name")
            collection_name = tool_arguments.get("collection_name")
            filter_query = tool_arguments.get("filter_query")
            update_data = tool_arguments.get("update_data")
            upsert_flag = tool_arguments.get("upsert", False)
            execution_result = mongo.update_many_documents(
                current_mongodb_uri, database_name, collection_name, 
                filter_query, update_data, upsert_flag
            )
        
        elif tool_name == "delete_document":
            database_name = tool_arguments.get("database_name")
            collection_name = tool_arguments.get("collection_name")
            filter_query = tool_arguments.get("filter_query")
            execution_result = mongo.delete_document(
                current_mongodb_uri, database_name, collection_name, filter_query
            )
        
        elif tool_name == "delete_many_documents":
            database_name = tool_arguments.get("database_name")
            collection_name = tool_arguments.get("collection_name")
            filter_query = tool_arguments.get("filter_query")
            execution_result = mongo.delete_many_documents(
                current_mongodb_uri, database_name, collection_name, filter_query
            )
        
        elif tool_name == "count_documents":
            database_name = tool_arguments.get("database_name")
            collection_name = tool_arguments.get("collection_name")
            query_filter = tool_arguments.get("query")
            execution_result = mongo.count_documents(
                current_mongodb_uri, database_name, collection_name, query_filter
            )
        
        elif tool_name == "aggregate":
            database_name = tool_arguments.get("database_name")
            collection_name = tool_arguments.get("collection_name")
            aggregation_pipeline = tool_arguments.get("pipeline")
            execution_result = mongo.aggregate(
                current_mongodb_uri, database_name, collection_name, aggregation_pipeline
            )
        
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
    Main entry point for the MongoDB MCP server.
    Sets up stdio communication and runs the server.
    """
    async with stdio_server() as (read_stream, write_stream):
        await mongodb_mcp_server.run(
            read_stream,
            write_stream,
            mongodb_mcp_server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())

