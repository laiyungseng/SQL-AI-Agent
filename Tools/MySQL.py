import mysql.connector
from mysql.connector import Error
import configparser
import sys
import os
from typing import List, Tuple, Optional, Any, Union

# Add parent directory to path to allow imports if needed, though relative imports are better if this is a package.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def get_db_config():
    config = configparser.ConfigParser()
    # Read db.cfg from the current working directory or relative to this file
    # Trying CWD first then file dir
    if os.path.exists('db.cfg'):
        config.read('db.cfg')
    else:
        config.read(os.path.join(os.path.dirname(__file__), '..', 'db.cfg'))
    
    return config['MySQL_Setting']

def get_connection():
    settings = get_db_config()
    return mysql.connector.connect(
        host=settings.get('host', 'localhost'),
        port=settings.get('port', 3306),
        user=settings.get('user'),
        password=settings.get('password'),
        database=settings.get('database')
    )

def query_all(query: str) -> List[Tuple]:
    """
    Executes a SQL query on a connected MySQL database and return all matching rows.
    """
    connection = None
    cursor = None
    try:
        connection = get_connection() # Use helper if I defined it, or just get_connection
        cursor = connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    except Error as err:
        return [(f"Error: {err}",)]
    finally:
        if cursor: cursor.close()
        if connection: connection.close()

def query_one(query: str) -> Optional[Tuple]:
    """
    Executes a SQL query on a connected MySQL database and return a single matching row.
    """
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(query)
        return cursor.fetchone()
    except Error as err:
        return (f"Error: {err}",)
    finally:
        if cursor: cursor.close()
        if connection: connection.close()

def create_table(query: str) -> str:
    """
    Executes a SQL CREATE TABLE statement.
    """
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(query)
        return "Table created successfully"
    except Error as err:
        return f"Error: {err}"
    finally:
        if cursor: cursor.close()
        if connection: connection.close()

def display_tables() -> List[str]:
    """
    Retrieves the list of table names.
    """
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES;")
        results = cursor.fetchall()
        return [table[0] for table in results]
    except Error as err:
        return [f"Error: {err}"]
    finally:
        if cursor: cursor.close()
        if connection: connection.close()

def display_columns(table: str) -> List[str]:
    """
    Retrieves the column names from a specified table.
    """
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        # Use parameterized query or safe formatting? 
        # Table names cannot be parameterized in MySQL usually. 
        # We'll just trust the input for now as per original or do basic validation.
        cursor.execute(f"SELECT * FROM {table} LIMIT 0;")
        _ = cursor.fetchall()
        return [col[0] for col in cursor.description]
    except Error as err:
        return [f"Error: {err}"]
    finally:
        if cursor: cursor.close()
        if connection: connection.close()

def insert_data(query: str) -> str:
    """
    Executes a SQL INSERT statement.
    """
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        return f"{cursor.rowcount} row(s) inserted."
    except Error as err:
        return f"Error: {err}"
    finally:
        if cursor: cursor.close()
        if connection: connection.close()

def delete_rows(query: str) -> str:
    """
    Executes a SQL DELETE statement.
    """
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        return f"{cursor.rowcount} row(s) deleted"
    except Error as err:
        return f"Error: {err}"
    finally:
        if cursor: cursor.close()
        if connection: connection.close()

def check_databases() -> List[Tuple[str]]:
    """
    Retrieves the list of available databases.
    """
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES;")
        return cursor.fetchall()
    except Error as err:
        return [(f"Error: {err}",)]
    finally:
        if cursor: cursor.close()
        if connection: connection.close()
