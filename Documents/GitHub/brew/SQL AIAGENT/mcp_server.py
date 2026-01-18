from mcp.server.fastmcp import FastMCP
import Tools.MySQL as MySQL
import sys
import os

# Add current directory to path so it can find Tools
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

mcp = FastMCP("MySQL Server")

@mcp.tool()
def query_all(query: str) -> str:
    """Executes a SQL query on a connected MySQL database and return all matching rows."""
    return str(MySQL.query_all(query))

@mcp.tool()
def query_one(query: str) -> str:
    """Executes a SQL query on a connected MySQL database and return a single matching row."""
    return str(MySQL.query_one(query))

@mcp.tool()
def create_table(query: str) -> str:
    """Executes a SQL CREATE TABLE statement."""
    return str(MySQL.create_table(query))

@mcp.tool()
def display_tables() -> str:
    """Retrieves the list of table names."""
    return str(MySQL.display_tables())

@mcp.tool()
def display_columns(table: str) -> str:
    """Retrieves the column names from a specified table."""
    return str(MySQL.display_columns(table))

@mcp.tool()
def insert_data(query: str) -> str:
    """Executes a SQL INSERT statement."""
    return str(MySQL.insert_data(query))

@mcp.tool()
def delete_rows(query: str) -> str:
    """Executes a SQL DELETE statement."""
    return str(MySQL.delete_rows(query))

@mcp.tool()
def check_databases() -> str:
    """Retrieves the list of available databases."""
    return str(MySQL.check_databases())

if __name__ == "__main__":
    mcp.run()
