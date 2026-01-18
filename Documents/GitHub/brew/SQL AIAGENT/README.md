# SQL AI Agent

A powerful AI agent capable of interacting with MySQL databases using natural language. It leverages the **Model Context Protocol (MCP)** to securely and modularly expose database tools to the Large Language Model (LLM).

## Features

- **Web User Interface** (New!):
    - **Chat Interface**: Natural language chat with your data.
    - **Connection Manager**: Configure database credentials via a GUI.
    - **Model Settings**: Switch between Ollama and Google Gemini models.
- **Natural Language to SQL**: Ask questions in plain English and get results from your database.
- **MCP Architecture**: Uses the Model Context Protocol to separate the tool execution (Server) from the AI Client.
- **Ollama Integration**: Powered by local LLMs via Ollama (default: `llama3.2:latest`).
- **Secure Tools**: 
  - `query_all`: Run SELECT queries.
  - `query_one`: Fetch single rows.
  - `create_table`: Create new tables.
  - `insert_data` / `delete_rows`: Manage data.
  - `display_tables` / `display_columns`: Inspect schema.

## Architecture

```
graph LR
    User[User] -- "Browser UI" --> WebServer[FastAPI Server (server.py)]
    WebServer -- "API Calls" --> Agent[LangChain Agent]
    Agent -- "MCP Protocol" --> MCPServer[MCP Server (mcp_server.py)]
    MCPServer -- "SQL" --> DB[(MySQL Database)]
    DB -- "Results" --> MCPServer
    MCPServer -- "Results" --> Agent
    Agent -- "Response" --> WebServer
    WebServer -- "JSON" --> User
```

## Prerequisites

- **Python 3.10+**
- **MySQL Server** (running and accessible)
- **Ollama** (running with `llama3.2` model)
- **uv** (recommended for dependency management)

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/laiyungseng/SQL-AI-Agent.git
    cd SQL-AI-Agent
    ```

2.  Install dependencies:
    ```bash
    uv sync
    # OR
    pip install -r requirements.txt
    ```

3.  (Optional) Configure Environment:
    Create a `.env` file for any API keys (e.g., if switching to Google Gemini):
    ```env
    GOOGLE_API_KEY=your_key_here
    ```

## Usage

### 1. Web Interface (Recommended)

Start the web server:

```bash
uv run server.py
# OR
python server.py
```

Then open your browser to: **http://127.0.0.1:8000** (or `http://localhost:8000`)

**Using the UI:**
1.  Click **"Configure Connection"** to set your MySQL host, user, and password.
2.  Once connected, select a database from the dropdown.
3.  Start chatting! (e.g., "Show me all tables", "Count users in the users table").

### 2. CLI Mode

You can still run the CLI agent directly for testing (edit `main.py` to change the query):

```bash
uv run main.py
```

## Project Structure

- `server.py`: FastAPI Web Server (Backend for UI).
- `static/`: Frontend assets (HTML, CSS, JS).
    - `index.html`: Main UI.
    - `main.js`: UI Logic & API calls.
    - `style.css`: Styling.
- `main.py`: The LLM Client & Agent definition.
- `mcp_server.py`: The MCP Server. Exposes MySQL tools.
- `Tools/MySQL.py`: The core database logic.
- `db.cfg`: Database configuration file (created by UI).



## Recent Updates

### 1. Robust OpenRouter Integration
- **Unified Agent Architecture**: Refactored `llm_api.py` to use `langchain_openai.ChatOpenAI` for OpenRouter, ensuring consistent behavior with Local Ollama.
- **Dynamic Model Filtering**: Implemented logic to automatically filter out OpenRouter models that do not support "Function Calling" (Tools), preventing API errors.

### 2. Enhanced UI & Experience
- **Smart Model Selection**: Merged dropdown and input into a single **Searchable Input Box**. Users can type to search models or pick from the list.
- **Hot-Reload Configuration**: Server now detects changes to `.env` immediately. Updating your API key in the file and refreshing the page updates the UI instantly.
- **Transparent Settings**: The API Key is now visible in the settings box (masked as placeholders or value) to confirm it's loaded.

### 3. Developer Updates
- **CLI Usage**: Updated `main.py` to demonstrate correct agent invocation: `agent.ainvoke({"messages": [{"role": "user", "content": ...}]})`.
- **Validation**: Added `test_llm_api.py` for verification.

