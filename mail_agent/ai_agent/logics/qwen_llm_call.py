import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=os.environ["HF_TOKEN"],
        )
    return _client


def generate(prompt: str, system_prompt: str | None = None, temperature: float = 0.3) -> str:
    """
    Single-turn text generation. Returns the raw text response.
    Raises on API failure — callers (nodes) catch and decide fallback behavior.
    """
    client = _get_client()
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    model = os.environ.get("QWEN_MODEL", DEFAULT_MODEL)

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return completion.choices[0].message.content