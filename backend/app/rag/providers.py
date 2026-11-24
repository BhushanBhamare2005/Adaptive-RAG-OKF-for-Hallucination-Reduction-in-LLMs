from __future__ import annotations

import httpx

from app.core.config import settings


class OpenAICompatibleProvider:
    name = "openai_compatible"

    def __init__(self) -> None:
        self.refresh()

    def refresh(self) -> None:
        self.base_url = settings.llm_base_url.rstrip("/") if settings.llm_base_url else ""
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model

    def configured(self) -> bool:
        return bool(self.base_url and self.api_key and self.model)

    def health_check(self) -> dict:
        return (
            {"status": "configured", "provider": self.name, "model": self.model}
            if self.configured()
            else {"status": "not_configured", "provider": self.name, "model": self.model or None}
        )

    async def generate(self, prompt: str, temperature: float = 0.2, max_tokens: int = 1200) -> str:
        self.refresh()
        if not self.configured():
            raise RuntimeError("LLM provider is not configured.")
        headers = {
            "Authorization": "Bearer " + self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": min(max_tokens, 500),
        }
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise RuntimeError("LLM provider returned an unexpected response.") from error


class OllamaProvider:
    name = "ollama"

    def __init__(self) -> None:
        self.refresh()

    def refresh(self) -> None:
        self.base_url = (settings.llm_base_url or "http://127.0.0.1:11434").rstrip("/")
        self.model = settings.llm_model

    def configured(self) -> bool:
        return bool(self.base_url and self.model)

    def health_check(self) -> dict:
        return (
            {"status": "configured", "provider": self.name, "model": self.model}
            if self.configured()
            else {"status": "not_configured", "provider": self.name, "model": None}
        )

    async def generate(self, prompt: str, temperature: float = 0.2, max_tokens: int = 1200) -> str:
        self.refresh()
        if not self.configured():
            raise RuntimeError("Ollama provider is not configured.")
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "30m",
            "options": {
                "temperature": temperature,
                "num_predict": min(max_tokens, 500),
            },
        }
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
        response_text = data.get("response")
        if not isinstance(response_text, str):
            raise RuntimeError("Ollama returned an unexpected response.")
        return response_text


def build_llm_provider():
    return OllamaProvider() if settings.llm_provider.strip().lower() == "ollama" else OpenAICompatibleProvider()


llm_provider = build_llm_provider()


def configure_llm_provider(provider: str, base_url: str, api_key: str, model: str) -> object:
    global llm_provider
    settings.llm_provider = provider.strip().lower()
    settings.llm_base_url = base_url.rstrip("/") if base_url else ""
    settings.llm_model = model.strip()
    settings.llm_api_key = api_key if provider.strip().lower() == "openai_compatible" else ""
    llm_provider = build_llm_provider()
    return llm_provider


def get_llm_provider() -> object:
    global llm_provider
    if settings.llm_provider.strip().lower() == "ollama" and getattr(llm_provider, "name", "") != "ollama":
        llm_provider = build_llm_provider()
    elif settings.llm_provider.strip().lower() != "ollama" and getattr(llm_provider, "name", "") != "openai_compatible":
        llm_provider = build_llm_provider()
    llm_provider.refresh()
    return llm_provider
