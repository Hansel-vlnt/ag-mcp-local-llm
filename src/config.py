import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
    default_model: str = os.getenv("DEFAULT_MODEL", "qwen2.5-coder:7b")
    request_timeout: float = float(os.getenv("REQUEST_TIMEOUT", "120.0"))
    default_num_ctx: int = int(os.getenv("DEFAULT_NUM_CTX", "8192"))


settings = Settings()
