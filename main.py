import asyncio
import os
import sys
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

async def main():
    # Define connection parameters
    server_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_server.py")
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_script],
        env=None
    )

    # Connect to MCP server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Define wrapper functions for tools
            # We explicitly define them to ensure LangChain knows the schema (signatures).
            
            @tool
            async def query_all(query: str) -> str:
                """Executes a SQL query on a connected MySQL database and return all matching rows."""
                result = await session.call_tool("query_all", arguments={"query": query})
                return result.content[0].text

            @tool
            async def query_one(query: str) -> str:
                """Executes a SQL query on a connected MySQL database and return a single matching row."""
                result = await session.call_tool("query_one", arguments={"query": query})
                return result.content[0].text

            @tool
            async def create_table(query: str) -> str:
                """Executes a SQL CREATE TABLE statement."""
                result = await session.call_tool("create_table", arguments={"query": query})
                return result.content[0].text

            @tool
            async def display_tables() -> str:
                """Retrieves the list of table names from the currently connected MySQL database."""
                # Note: this tool takes no arguments in definition, calling it with empty args
                result = await session.call_tool("display_tables", arguments={})
                return result.content[0].text

            @tool
            async def display_columns(table: str) -> str:
                """Retrieves the column names from a specified table."""
                result = await session.call_tool("display_columns", arguments={"table": table})
                return result.content[0].text

            @tool
            async def insert_data(query: str) -> str:
                """Executes a SQL INSERT statement."""
                result = await session.call_tool("insert_data", arguments={"query": query})
                return result.content[0].text

            @tool
            async def delete_rows(query: str) -> str:
                """Executes a SQL DELETE statement."""
                result = await session.call_tool("delete_rows", arguments={"query": query})
                return result.content[0].text

            @tool
            async def check_databases() -> str:
                """Retrieves the list of available databases."""
                result = await session.call_tool("check_databases", arguments={})
                return result.content[0].text

            tools = [
                query_all, query_one, create_table, display_tables, 
                display_columns, insert_data, delete_rows, check_databases
            ]

            # Initialize Model
            model = ChatOllama(
                model='llama3.2:latest',
                temperature=0.0,
                max_retries=2
            )

            # Create Agent
            agent = create_react_agent(
                model=model,
                tools=tools,
                prompt='You are an helpful assistant that can use tools to solve issues.'
            )

            print("="*10 + " Starting Agent Execution " + "="*10)
            
            # Invoke Agent
            output = await agent.ainvoke(
                {
                    "messages": [{
                        "role": "user", "content": "please show me how many user are having SESSION_SCORE above 60 from logins table."
                    }]
                }
            )

            # Print Results
            for msg in output['messages']:
                if msg.type == 'human':
                    print("="*35+" HumanMessages "+"="*35)
                    print(f"User: {msg.content}")
                elif msg.type =='ai':
                    print("="*35+" AI Messages "+"="*35)
                    if msg.content == "":
                        for toolmsg in msg.tool_calls:
                            if toolmsg is not None:
                                print(f"Function Name: {toolmsg.get('type')}") # type usually is 'tool_call'?, name is in 'name'
                                print(f"Tool Name: {toolmsg.get('name')}")
                                print(f"Args: {toolmsg.get('args')}")
                    else:
                        print(f"AI response: {msg.content}")   
                    print(msg.usage_metadata)
                elif msg.type == 'tool':
                    print("="*35+" Tool Messages "+"="*35)
                    print(f"Tool Name: {msg.name}")
                    print(f"Tool_Call_id: {msg.tool_call_id}")
                    # Content might be large, truncate if needed or print all
                    print(f"Tool Response: {msg.content}")

if __name__ == "__main__":
    asyncio.run(main())
