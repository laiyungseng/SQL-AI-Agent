# SQL AI Agent

A powerful AI agent capable of interacting with MySQL databases using natural language. It leverages the **Model Context Protocol (MCP)** to securely and modularly expose database tools to the Large Language Model (LLM).

## Features

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

```mermaid
graph LR
    User[User] -- "Questions" --> Client[Main Client (main.py)]
    Client -- "MCP Protocol (Stdio)" --> Server[MCP Server (mcp_server.py)]
    Server -- "SQL" --> DB[(MySQL Database)]
    DB -- "Results" --> Server
    Server -- "Results" --> Client
    Client -- "Natural Language Answer" --> User
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

3.  Configure Database:
    Create a `db.cfg` file in the root directory:
    ```ini
    [MySQL_Setting]
    host = localhost
    port = 3306
    user = your_user
    password = your_password
    database = your_database
    ```

4.  Configure Environment:
    Create a `.env` file for any API keys (e.g., if switching to Google Gemini):
    ```env
    GOOGLE_API_KEY=your_key_here
    ```

## Usage

Run the agent client:

```bash
uv run main.py
```

The agent will connect to the MCP server, initialize the connection to your database, and execute the hardcoded query (currently configured in `main.py`).

### Customizing Queries
Edit `main.py` to change the user prompt:

```python
output = await agent.ainvoke(
    {
        "messages": [{
            "role": "user", "content": "Your question here..."
        }]
    }
)
```

## Project Structure

- `main.py`: The LLM Client. Orchestrates the agent and connects to the MCP server.
- `mcp_server.py`: The MCP Server. Exposes MySQL tools.
- `Tools/MySQL.py`: The core database logic (Pure Python).
- `basemodel.py`: Pydantic models (if used).

## License

MIT
