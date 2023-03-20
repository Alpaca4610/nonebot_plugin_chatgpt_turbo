from pydantic import Extra, BaseModel
from typing import Optional


class Config(BaseModel, extra=Extra.ignore):
    openai_api_key: Optional[str] = ""
    openai_model_name: Optional[str] = "gpt-3.5-turbo"
    openai_max_history_limit: Optional[int] = 5
    openai_http_proxy: Optional[str] = None
    enable_private_chat: bool = True


class ConfigError(Exception):
    pass
