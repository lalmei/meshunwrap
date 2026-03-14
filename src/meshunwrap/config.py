"""Configuration management for meshunwrap."""

from pydantic import BaseModel


class Config(BaseModel):
    """Configuration model for meshunwrap."""

    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
