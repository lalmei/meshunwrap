"""Configuration management for meshunwrap."""

from pydantic_settings import BaseSettings, SettingsConfigDict

from meshunwrap._version import get_version


class Config(BaseSettings):
    """Configuration class for loading environment variables.

    This class uses pydantic and pydantic-settings to define and load environment variables.
    It supports loading from .env and .env.prod files (lowest to highest priority),
    and uses field validators for data validation.
    """

    schema_version: str = "1.0.0"
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.dev", ".env.prod"),
        env_file_encoding="utf-8",
    )
    # Configurations for the application
    app_name: str = "meshunwrap"
    app_description: str = "UV unwrapping and figure reproduction for tube-like meshes"
    app_author: str = "Leandro G. Almeida"
    app_version: str = get_version()
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
