from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: str = "dev"

    rdb_username: str = "crowdworks"
    rdb_password: str = "crowdworks"
    rdb_hostname: str = "crowdworks.com"
    rdb_db_name: str = "crowdworks"

    sqlalchemy_database_url: str = "sqlite+aiosqlite:////tmp/sqlite3.db"

    upload_workspace: str = "/tmp/upload_workspace"

    # open ai
    openai_model: str = "gpt-4"
    openai_api_key: str = "your-openai-api-key"

    # hyperclova
    clovastudio_api_key: str = "your-cloval-api-key"
    clovastudio_apigw_api_key: str = "your-apigw-api-key"
    clovastudio_invoke_url: str = "/testapp/v1/chat-completions/HCX-003"

    # fastapi
    backend_host: str = "localhost:8000"


settings = Settings()
