from pathlib import Path
from typing import Tuple, Type

from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class DatabaseSettings(BaseModel):
    db_name: str
    db_host: str
    db_port: str
    db_user: str
    db_password: str

class RedisSettings(BaseModel):
    host: str
    port: str


class TextSettings(BaseModel):
    size: int = Field(12)
    font: str = Field("Arial")


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        toml_file=Path(__name__).parent.resolve() / "config.toml"
    )

    database: DatabaseSettings
    redis: RedisSettings
    text: TextSettings | None = Field(TextSettings())


    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (TomlConfigSettingsSource(settings_cls),)

    @property
    def DATABASE_PATH(self) -> str:
        return f"postgresql+asyncpg://{self.database.db_user}:{self.database.db_password}@{self.database.db_host}:{self.database.db_port}/{self.database.db_name}"

    @property
    def DATABASE_PATH_SYNC(self) -> str:
        return f"postgresql+psycopg://{self.database.db_user}:{self.database.db_password}@{self.database.db_host}:{self.database.db_port}/{self.database.db_name}"
