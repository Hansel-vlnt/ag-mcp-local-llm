import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
    default_model: str = os.getenv("DEFAULT_MODEL", "qwen2.5-coder:7b")
    request_timeout: float = float(os.getenv("REQUEST_TIMEOUT", "120.0"))
    default_num_ctx: int = int(os.getenv("DEFAULT_NUM_CTX", "8192"))


settings = Settings()
