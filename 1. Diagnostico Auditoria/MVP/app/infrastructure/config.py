from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Kohem Chemicals MVP API"
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str = "sqlite+aiosqlite:///./kohem.db"
    # Motor de lenguaje opcional (DeepSeek, API compatible con OpenAI).
    # Si DEEPSEEK_API_KEY está vacía, el asistente usa el motor de reglas.
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    LLM_TIMEOUT_SECONDS: float = 20.0
    LLM_TEMPERATURE: float = 0.3
    # asistente: respuesta por plantilla (auditable).
    # conversacional: el modelo redacta con los datos calculados por el dominio.
    AI_MODE: str = "asistente"
    AI_HISTORY_MAX: int = 8
    # Orígenes permitidos para CORS, separados por coma.
    # En producción reemplazar por el dominio real del frontend.
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
