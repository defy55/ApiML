from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, List, Literal
from pydantic import BaseModel

BASE_DIR = Path(__file__).parent.parent


class Setting(BaseSettings):
    api_v1_prefix: str = "/api_ds"

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    MODE: Literal["DEV", "TEST", "PROD"]
    db_echo: bool = False
    # db_echo: bool = True

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    TEST_POSTGRES_DB: str
    TEST_POSTGRES_USER: str
    TEST_POSTGRES_PASSWORD: str
    TEST_POSTGRES_HOST: str
    TEST_POSTGRES_PORT: str

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def TEST_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.TEST_POSTGRES_USER}:{self.TEST_POSTGRES_PASSWORD}@{self.TEST_POSTGRES_HOST}:{self.TEST_POSTGRES_PORT}/{self.TEST_POSTGRES_DB}"

    SECRET_KEY: str
    ALGORITHM: str

    # CORS_ORIGINS: List[str]
    CORS_HEADERS: List[str]
    CORS_METHODS: List[str]


settings = Setting()


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = settings.ALGORITHM
    access_token_expire_minutes: int = 90
    refresh_token_expire_days: int = 15


auth_settings = AuthJWT()
