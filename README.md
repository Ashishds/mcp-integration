# Google Workspace MCP Integration for Claude Desktop

A powerful Model Context Protocol (MCP) server that seamlessly integrates Claude Desktop with Google Workspace services. This project enables AI assistants to interact with Google Sheets, Gmail, and Google Calendar through a standardized MCP interface.

## ✨ Features

### 📊 Google Sheets
- Read data from spreadsheets
- Write and update cell values
- Append rows to sheets
- Get spreadsheet metadata

### 📧 Gmail
- List and search emails
- Get detailed email information
- Send emails
- Advanced email filtering

### 📅 Google Calendar
- List upcoming events
- Create new events
- Update existing events
- Delete events
- Get event details

### 💾 Database Support
- **PostgreSQL** integration via MCP
- **MongoDB** integration via MCP
- Full CRUD operations
- Query execution and data management

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Cloud Project with APIs enabled:
  - Google Sheets API
  - Gmail API
  - Google Calendar API
- Claude Desktop installed

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/claude-google-workspace-integration.git
   cd claude-google-workspace-integration
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google OAuth**
   - Download `credentials.json` from [Google Cloud Console](https://console.cloud.google.com/)
   - Place it in the project root directory
   - Run the setup script:
     ```bash
     python src/config_setup.py
     ```

4. **Configure the application**
   - Copy `config.example.json` to `config.json`
   - Fill in your configuration details

5. **Configure Claude Desktop**
   - Locate your Claude Desktop config file:
     - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
     - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
     - **Linux**: `~/.config/Claude/claude_desktop_config.json`
   - Add the MCP server configuration (see `claude_desktop_config.example.json`)
   - Update the file paths to match your installation
   - Restart Claude Desktop

## 📖 Usage

Once configured, you can interact with Google Workspace services through Claude Desktop:

### Google Sheets
- *"Read data from Sheet1!A1:B10 in my spreadsheet"*
- *"Write these values to my spreadsheet: [['Name', 'Age'], ['John', '30']]"*
- *"Append this row to Sheet1: ['Task', 'Description', 'Status']"*

### Gmail
- *"Show me my last 10 emails"*
- *"Search for emails from john@example.com"*
- *"Send an email to jane@example.com with subject 'Meeting' and body 'Let's meet tomorrow'"*

### Google Calendar
- *"List my upcoming calendar events"*
- *"Create a calendar event for tomorrow at 2pm titled 'Team Meeting'"*
- *"Update the event with ID xyz123 to change the time to 3pm"*

## 🏗️ Project Structure

```
.
├── src/
│   ├── main_server.py          # Main MCP server
│   ├── auth_manager.py         # OAuth2 authentication
│   ├── sheets_manager.py       # Google Sheets integration
│   ├── email_manager.py        # Gmail integration
│   ├── calendar_manager.py     # Calendar integration
│   ├── mongo_handler.py        # MongoDB operations
│   ├── mongo_server.py         # MongoDB MCP server
│   ├── postgres_handler.py     # PostgreSQL operations
│   ├── postgres_server.py      # PostgreSQL MCP server
│   ├── automation_agent.py     # Automation agent
│   └── config_setup.py         # Setup script
├── config.example.json         # Configuration template
├── claude_desktop_config.example.json  # Claude Desktop config template
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔧 Available MCP Tools

### Google Sheets (4 tools)
- `read_sheet` - Read data from a range
- `write_sheet` - Write data to a range
- `append_sheet` - Append rows to a sheet
- `get_sheet_info` - Get spreadsheet metadata

### Gmail (4 tools)
- `list_emails` - List emails from inbox
- `get_email_detail` - Get detailed email information
- `send_email` - Send an email
- `search_emails` - Search emails with query

### Google Calendar (5 tools)
- `list_calendar_events` - List upcoming events
- `create_calendar_event` - Create a new event
- `update_calendar_event` - Update an existing event
- `delete_calendar_event` - Delete an event
- `get_calendar_event` - Get event details

### Database Tools
- **PostgreSQL**: `execute_query`, `execute_write`, `run_custom_sql`, `list_tables`, `describe_table`, `get_table_count`
- **MongoDB**: `list_databases`, `list_collections`, `find_documents`, `insert_document`, `update_document`, `delete_document`, and more

## 🔒 Security

⚠️ **Important Security Notes**:
- Never commit `credentials.json`, `tokens.json`, or `config.json` to version control
- These files are already in `.gitignore`
- Keep your OAuth credentials secure
- Regularly rotate credentials if compromised

## 🐛 Troubleshooting

### Server Won't Start
- Verify Python is in your system PATH
- Check that the file path in Claude Desktop config is correct
- Ensure all dependencies are installed: `pip install -r requirements.txt`

### Tools Not Appearing
- Check Claude Desktop logs for errors
- Verify authentication: `tokens.json` exists and is valid
- Re-run setup: `python src/config_setup.py`
- Completely restart Claude Desktop

### Authentication Errors
- Re-authenticate: `python src/config_setup.py`
- Verify `credentials.json` is valid
- Check that all required APIs are enabled in Google Cloud Console

## 📝 License

This project is provided as-is for personal and educational use. Please ensure you comply with Google's API Terms of Service when using this integration.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 Acknowledgments

- Built with [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- Uses [Google APIs Client Library for Python](https://github.com/googleapis/google-api-python-client)
- Designed for integration with [Claude Desktop](https://claude.ai/desktop)

## 🆘 Support

If you encounter any issues:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review the [Google API documentation](https://developers.google.com/workspace)
3. Open an issue on GitHub with a detailed description

---

**Note**: This project is not affiliated with, endorsed by, or associated with Anthropic or Google. It is an independent integration project.
