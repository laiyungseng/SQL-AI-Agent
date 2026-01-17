from pydantic import BaseModel, Field

class DBConfig(BaseModel):
    host: str = Field(default='127.0.0.1', description='Database host address', examples='127.0.0.1')
    port: int = Field(..., description='Port Number in database config', examples=3306, ge=1, le=65535)
    user: str = Field(..., description='username in databasee', examples='root', min_length=1)
    password: str = Field(..., description='password set in database', min_length=1)
    database: str = Field(..., description='tables name', min_length=1)