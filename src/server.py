import json
import sys
from pathlib import Path
from typing import Optional

# Ensure project root is in sys.path so imports work when executed directly by MCP clients
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from mcp.server.mcpserver import MCPServer
except ImportError:
    from mcp.server.fastmcp import FastMCP as MCPServer

from src.client import OllamaClient
from src.config import settings

mcp = MCPServer(
    name="ag-mcp-local-llm",
    instructions="Offloads heavy computational prompts, code drafting, and local file analysis to local Ollama on GPU.",
)
ollama_client = OllamaClient()

MAX_FILE_BYTES = 15 * 1024 * 1024  # 15 MB safety guard for local text files
MAX_SAFE_CHARS = 28000             # ~8192 tokens safe single-pass threshold


@mcp.tool()
async def ask_local_llm(prompt: str, model: str = "", system: str = "") -> str:
    """Send a computational, summarization, or code drafting prompt to the local LLM.

    Args:
        prompt: The query or task instruction for the local model.
        model: Optional model name (e.g. 'qwen2.5-coder:7b'). Defaults to DEFAULT_MODEL in config.
        system: Optional system instruction or role definition for the local model.
    """
    if not prompt or not prompt.strip():
        return "Error: Prompt cannot be empty."

    result = await ollama_client.generate(
        prompt=prompt.strip(),
        model=model,
        system=system.strip() if system and system.strip() else None,
    )
    return result


@mcp.tool()
async def analyze_file_locally(
    file_path: str,
    instruction: str,
    model: str = "",
    start_line: int = 1,
    end_line: int = 0,
) -> str:
    """Read a local file directly on this machine and analyze it with the local LLM without uploading content to the cloud.

    Args:
        file_path: Absolute or relative path to the local text/code/log file.
        instruction: Specific analysis instruction (e.g. 'Find performance bottlenecks', 'Summarize error logs').
        model: Optional model name override.
        start_line: Starting line number to read (1-indexed, default 1).
        end_line: Ending line number to read (inclusive; 0 or omitted means read until end of file).
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

    lines = content.splitlines(keepends=True)
    total_lines = len(lines)

    actual_start_line = max(1, start_line)
    if end_line <= 0 or end_line > total_lines:
        actual_end_line = total_lines
    else:
        actual_end_line = max(actual_start_line, end_line)

    selected_lines = lines[actual_start_line - 1 : actual_end_line]
    sliced_content = "".join(selected_lines)

    warning_prefix = ""
    if len(sliced_content) > MAX_SAFE_CHARS:
        warning_prefix = (
            f"[Warning: Sliced content ({len(sliced_content)} chars) exceeds safe single-pass limit "
            f"~{MAX_SAFE_CHARS} chars (~8192 tokens). To prevent sliding context truncation in Ollama, "
            f"consider narrowing start_line and end_line.]\n\n"
        )

    # Instruction-Last pattern: places instruction after file content to avoid Ollama head-truncation
    prompt = (
        f"You are analyzing a local file.\n\n"
        f"File Path: {path.name}\n"
        f"Line Range: {actual_start_line} to {actual_end_line} (Total Lines: {total_lines})\n\n"
        f"--- File Content Begin ---\n"
        f"{sliced_content}\n"
        f"--- File Content End ---\n\n"
        f"Instruction: {instruction}\n\n"
        f"Provide your detailed analysis based strictly on the instruction above:"
    )

    result = await ollama_client.generate(prompt=prompt, model=model)
    return f"{warning_prefix}{result}" if warning_prefix else result


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
