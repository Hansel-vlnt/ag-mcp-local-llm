import httpx
from typing import Any, Dict, List, Optional
from src.config import settings


class OllamaClient:
    def __init__(
        self,
        base_url: str = settings.ollama_host,
        timeout: float = settings.request_timeout,
        default_model: str = settings.default_model,
        default_num_ctx: int = settings.default_num_ctx,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.default_model = default_model
        self.default_num_ctx = default_num_ctx

    async def get_status(self) -> Dict[str, Any]:
        """Check Ollama service status, version, and list installed models."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                version_res = await client.get(f"{self.base_url}/api/version")
                version_data = version_res.json() if version_res.status_code == 200 else {}
                version = version_data.get("version", "unknown")

                tags_res = await client.get(f"{self.base_url}/api/tags")
                models: List[str] = []
                if tags_res.status_code == 200:
                    models = [m.get("name", "") for m in tags_res.json().get("models", [])]

                return {
                    "running": True,
                    "version": version,
                    "endpoint": self.base_url,
                    "default_model": self.default_model,
                    "installed_models": models,
                }
            except httpx.ConnectError:
                return {
                    "running": False,
                    "error": (
                        f"Cannot connect to Ollama at {self.base_url}. "
                        "Ensure Ollama is running (e.g. run 'ollama serve' or open Ollama app)."
                    ),
                    "installed_models": [],
                }
            except Exception as e:
                return {
                    "running": False,
                    "error": f"Ollama connection check failed: {str(e)}",
                    "installed_models": [],
                }

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        num_ctx: Optional[int] = None,
    ) -> str:
        """Send a prompt to Ollama and return the generated text response."""
        chosen_model = model.strip() if model and model.strip() else self.default_model
        ctx = num_ctx if num_ctx is not None else self.default_num_ctx

        payload: Dict[str, Any] = {
            "model": chosen_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_ctx": ctx,
            },
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(f"{self.base_url}/api/generate", json=payload)
                if response.status_code == 404:
                    return (
                        f"Error: Model '{chosen_model}' is not found in Ollama. "
                        f"Run 'ollama pull {chosen_model}' first."
                    )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "").strip()
            except httpx.ConnectError:
                return (
                    f"Connection Error: Could not reach Ollama at {self.base_url}. "
                    "Please verify that Ollama is active ('ollama serve')."
                )
            except httpx.TimeoutException:
                return (
                    f"Timeout Error: Request timed out after {self.timeout}s while generating response with model '{chosen_model}'."
                )
            except Exception as e:
                return f"Unexpected Ollama Error: {str(e)}"
