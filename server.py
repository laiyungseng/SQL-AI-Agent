from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager, AsyncExitStack
from pydantic import BaseModel
import sys
import os
import json
import configparser
from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client
from main import create_tools, load_dotenv
from llm_api import LLM_API, get_openrouter_model_list

load_dotenv()

# Pydantic Models
class ChatRequest(BaseModel):
    message: str
    provider: str = "local" # 'local' or 'openrouter'
    model: str = "llama3.2:latest"
    api_key: str = ""

class DBConfigRequest(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str

class APIKeyRequest(BaseModel):
    api_key: str
    provider: str
    model: str = "" # Optional, to save preferred model

# Global State for Prompt
SYSTEM_PROMPT = "You are a helpful assistant."

def load_system_prompt():
    global SYSTEM_PROMPT
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "llm_prompt_template", "prompt_template.json")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Assuming structure is [{"template": "..."}]
                if isinstance(data, list) and len(data) > 0 and 'template' in data[0]:
                    SYSTEM_PROMPT = data[0]['template']
        print(f"Loaded System Prompt (len={len(SYSTEM_PROMPT)})")
    except Exception as e:
        print(f"Error loading system prompt: {e}")

# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    load_system_prompt()
    
    # Connect to MCP Server
    server_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_server.py")
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_script],
        env=sys.modules['os'].environ.copy()
    )
    
    async with AsyncExitStack() as stack:
        print("Starting MCP Server...")
        try:
            read, write = await stack.enter_async_context(stdio_client(server_params))
            session = await stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            
            app.state.session = session
            app.state.tools = create_tools(session)
            print("MCP Server Connected and Tools Initialized.")
            
            yield
            
        except Exception as e:
            print(f"Error during lifecycle: {e}")
            raise e
        
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints

@app.get("/api/databases")
async def get_databases():
    if not hasattr(app.state, 'session'):
        raise HTTPException(status_code=503, detail="Server not initialized")
    
    try:
        result = await app.state.session.call_tool("check_databases", arguments={})
        result_text = result.content[0].text
        
        import ast
        try:
            data = ast.literal_eval(result_text)
            databases = []
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, tuple) and len(item) > 0:
                        databases.append(str(item[0]))
                    else:
                        databases.append(str(item))
            else:
                 databases = [] 
                 
            return {"databases": databases}
            
        except (ValueError, SyntaxError):
            return {"databases": [], "error": result_text}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/llm/models")
async def get_llm_models(provider: str = "local"):
    """
    Get available models for the specified provider.
    """
    if provider.lower() == "openrouter":
        # Get key from env if possible, as user might not pass it yet
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        # If blank, we might return empty or error.
        # But we can try fetching? OpenRouter needs key.
        if not api_key:
             return {"models": [], "error": "OpenRouter API Key not found in environment."}
        
        models = get_openrouter_model_list(api_key)
        # Verify if models is a list
        if isinstance(models, list):
             return {"models": models}
        else:
             return {"models": []}
             
    else:
        # Local / Ollama default
        return {"models": ["llama3.2:latest"]}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    if not hasattr(app.state, 'session'):
        raise HTTPException(status_code=503, detail="Server not initialized")

    # Determine API Key
    # Priority: Request -> Env
    api_key = request.api_key
    if not api_key:
        if request.provider.lower() == "openrouter":
            api_key = os.environ.get("OPENROUTER_API_KEY", "")
        # Google unused in this plan but kept logic style
    
    try:
        # Initialize LLM API
        # input is handled by agent invoke, not init? 
        # API signature: (service_provider, api_key, model_name, tools, template_prompt, temperature, max_retries)
        llm = LLM_API(
            service_provider=request.provider,
            api_key=api_key,
            model_name=request.model,
            tools=app.state.tools,
            template_prompt=SYSTEM_PROMPT,
            temperature=0, # Default to 0 for precision
            max_retries=2
        )
        
        agent = llm.run_llm()
        
        output = await agent.ainvoke({"messages": [{"role": "user", "content": request.message}]})
        
        # Format response
        messages = []
        if isinstance(output, dict) and 'messages' in output:
             for msg in output['messages']:
                if msg.type == 'ai':
                     messages.append({"role": "ai", "content": msg.content})
                elif msg.type == 'human':
                     messages.append({"role": "user", "content": msg.content})
        
        return {"response": messages[-1]['content'] if messages else "No response"}
    
    except Exception as e:
        print(f"Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/config/db")
async def update_db_config(config: DBConfigRequest):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, 'db.cfg')
        
        cfg = configparser.ConfigParser()
        cfg.read(config_path)
        if 'MySQL_Setting' not in cfg:
            cfg['MySQL_Setting'] = {}
            
        cfg['MySQL_Setting']['host'] = config.host
        cfg['MySQL_Setting']['port'] = str(config.port)
        cfg['MySQL_Setting']['user'] = config.user
        cfg['MySQL_Setting']['password'] = config.password
        cfg['MySQL_Setting']['database'] = config.database
        
        with open(config_path, 'w') as configfile:
            cfg.write(configfile)
            
        return {"status": "success", "message": "Database configuration updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config/db")
async def get_db_config():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, 'db.cfg')
        
        cfg = configparser.ConfigParser()
        cfg.read(config_path)
        
        if 'MySQL_Setting' in cfg:
            return {
                "host": cfg['MySQL_Setting'].get('host', ''),
                "port": int(cfg['MySQL_Setting'].get('port', 3306)),
                "user": cfg['MySQL_Setting'].get('user', ''),
                "password": cfg['MySQL_Setting'].get('password', ''),
                "database": cfg['MySQL_Setting'].get('database', '')
            }
        else:
            return {}
            
    except Exception as e:
        return {}

@app.post("/api/config/llm")
async def update_llm_config(request: APIKeyRequest):
    # Updates .env with keys AND preference
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(base_dir, '.env')
        
        # Read .env
        env_lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                env_lines = f.readlines()
        
        # Determine Key Name
        key_name = ""
        if request.provider.lower() == "openrouter":
            key_name = "OPENROUTER_API_KEY"
        elif request.provider.lower() == "google":
             key_name = "GOOGLE_API_KEY"
             
        env_vars = {}
        # Parse existing
        for line in env_lines:
            if '=' in line:
                k, v = line.split('=', 1)
                env_vars[k.strip()] = v.strip().strip('"').strip("'")
            
        # Update vars
        if key_name and request.api_key:
            env_vars[key_name] = request.api_key
            os.environ[key_name] = request.api_key
            
        env_vars["LLM_PROVIDER"] = request.provider
        if request.model:
            env_vars["LLM_MODEL"] = request.model
            
        # Write back
        with open(env_path, 'w') as f:
            for k, v in env_vars.items():
                f.write(f'{k}="{v}"\n')
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config/llm")
async def get_llm_config():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(base_dir, '.env')
        load_dotenv(env_path, override=True) # Force reload to get latest changes
        
        provider = os.environ.get("LLM_PROVIDER", "local")
        model = os.environ.get("LLM_MODEL", "llama3.2:latest")
        
        # We don't return API keys for security, or just masked?
        # User wants to see if they are set.
        openrouter_key = os.environ.get("OPENROUTER_API_KEY", "")
        key_length = len(openrouter_key)
        
        return {
            "provider": provider,
            "model": model,
            "has_openrouter_key": bool(openrouter_key),
            "key_length": key_length
        }
    except Exception as e:
        return {"provider": "local", "model": "llama3.2:latest"}

# Static Files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
