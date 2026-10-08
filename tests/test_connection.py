import asyncio
import sys
from pathlib import Path

# Add project root to sys.path so tests can import src directly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.client import OllamaClient
from src.config import settings


async def run_diagnostics():
    print("=" * 60)
    print("   AG-MCP-LOCAL-LLM: DIAGNOSTIC & CONNECTION TEST")
    print("=" * 60)
    print(f"[1] Configuration Loaded:")
    print(f"    - OLLAMA_HOST     : {settings.ollama_host}")
    print(f"    - DEFAULT_MODEL   : {settings.default_model}")
    print(f"    - REQUEST_TIMEOUT : {settings.request_timeout}s")
    print(f"    - DEFAULT_NUM_CTX : {settings.default_num_ctx} tokens")
    print("-" * 60)

    client = OllamaClient()
    print("[2] Checking Ollama Connectivity...")
    status = await client.get_status()

    if not status.get("running"):
        print("[!] RESULT: Ollama is OFFLINE.")
        print(f"    Details: {status.get('error')}")
        print("\n--> Next Steps:")
        print("    1. Start Ollama (run 'ollama serve' in terminal or launch Ollama app).")
        print(f"    2. Pull your desired model (e.g. 'ollama pull {settings.default_model}').")
        print("    3. Re-run this test script.")
        print("=" * 60)
        return False

    print("[+] RESULT: Ollama is ONLINE!")
    print(f"    - Ollama Version  : {status.get('version')}")
    installed_models = status.get("installed_models", [])
    print(f"    - Installed Models: {len(installed_models)}")
    for model in installed_models:
        print(f"      * {model}")

    if not installed_models:
        print("\n[!] Warning: No models found in Ollama.")
        print(f"    Run 'ollama pull {settings.default_model}' to download a model.")
        print("=" * 60)
        return True

    target_model = settings.default_model
    if target_model not in installed_models and not any(target_model in m for m in installed_models):
        print(f"\n[!] Note: Default model '{target_model}' is not in installed models.")
        print(f"    Using the first available model '{installed_models[0]}' for ping test...")
        target_model = installed_models[0]

    print(f"\n[3] Testing Inference Ping on model '{target_model}'...")
    response = await client.generate(
        prompt="Reply with exactly 'PONG' and nothing else.",
        model=target_model,
        num_ctx=2048,
    )
    print(f"    Response: {response}")
    print("=" * 60)
    print("[+] All checks completed successfully!")
    return True


if __name__ == "__main__":
    asyncio.run(run_diagnostics())
