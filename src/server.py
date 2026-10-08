import json
from pathlib import Path
from typing import Optional
from mcp.server.fastmcp import FastMCP

from src.client import OllamaClient
from src.config import settings

mcp = FastMCP("ag-mcp-local-llm")
ollama_client = OllamaClient()

MAX_FILE_BYTES = 15 * 1024 * 1024  # 15 MB safety guard for local text files


@mcp.tool()
async def ask_local_llm(prompt: str, model: str = "") -> str:
    """Send a computational, summarization, or code drafting prompt to the local LLM.

    Args:
        prompt: The query or task instruction for the local model.
        model: Optional model name (e.g. 'qwen2.5-coder:7b'). Defaults to DEFAULT_MODEL in config.
    """
    if not prompt or not prompt.strip():
        return "Error: Prompt cannot be empty."

    result = await ollama_client.generate(prompt=prompt.strip(), model=model)
    return result


@mcp.tool()
async def analyze_file_locally(file_path: str, instruction: str, model: str = "") -> str:
    """Read a local file directly on this machine and analyze it with the local LLM without uploading content to the cloud.

    Args:
        file_path: Absolute or relative path to the local text/code/log file.
        instruction: Specific analysis instruction (e.g. 'Find performance bottlenecks', 'Summarize error logs').
        model: Optional model name override.
    """
    path = Path(file_path).resolve()
    if not path.exists():
        return f"Error: File not found at path '{path}'."
    if not path.is_file():
        return f"Error: Path '{path}' is not a regular file."

    file_size = path.stat().st_size
    if file_size > MAX_FILE_BYTES:
        return (
            f"Error: File size ({file_size / (1024 * 1024):.2f} MB) exceeds maximum allowed size "
            f"({MAX_FILE_BYTES / (1024 * 1024):.0f} MB)."
        )

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return f"Error reading file '{path}': {str(e)}"

    prompt = (
        f"You are analyzing a local file.\n\n"
        f"File Path: {path.name}\n"
        f"Instruction: {instruction}\n\n"
        f"--- File Content Begin ---\n"
        f"{content}\n"
        f"--- File Content End ---\n\n"
        f"Provide your detailed analysis based strictly on the instruction above:"
    )

    result = await ollama_client.generate(prompt=prompt, model=model)
    return result


@mcp.tool()
async def check_local_llm_status() -> str:
    """Check Ollama service availability, version, default model, and list of installed models."""
    status = await ollama_client.get_status()
    if not status.get("running"):
        return f"Ollama Status: OFFLINE\nDetail: {status.get('error', 'Unknown error')}"

    models = status.get("installed_models", [])
    model_list_str = "\n".join(f"  - {m}" for m in models) if models else "  (None downloaded yet)"

    return (
        f"Ollama Status: ONLINE\n"
        f"Endpoint: {status.get('endpoint')}\n"
        f"Version: {status.get('version')}\n"
        f"Default Model: {status.get('default_model')}\n"
        f"Installed Models ({len(models)}):\n{model_list_str}"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
