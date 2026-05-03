from __future__ import annotations

import httpx


class LLMClientError(RuntimeError):
    pass


class LLMClient:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        api_style: str,
        timeout_seconds: float = 20.0,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.api_style = api_style
        self._owns_client = http_client is None
        self.http_client = http_client or httpx.Client(timeout=timeout_seconds)

    def complete(self, prompt: str) -> str:
        if self.api_style == "responses":
            return self._complete_responses(prompt)
        if self.api_style == "chat_completions":
            return self._complete_chat_completions(prompt)
        raise LLMClientError(f"Unsupported LLM api_style: {self.api_style}")

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _complete_chat_completions(self, prompt: str) -> str:
        response = self.http_client.post(
            f"{self.base_url}/chat/completions",
            headers=self._headers(),
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            },
        )
        self._raise_for_status(response)
        data = response.json()
        try:
            return str(data["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMClientError("Invalid chat_completions response shape") from exc

    def _complete_responses(self, prompt: str) -> str:
        response = self.http_client.post(
            f"{self.base_url}/responses",
            headers=self._headers(),
            json={"model": self.model, "input": prompt},
        )
        self._raise_for_status(response)
        data = response.json()
        if "output_text" in data:
            return str(data["output_text"])
        try:
            return str(data["output"][0]["content"][0]["text"])
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMClientError("Invalid responses response shape") from exc

    def _raise_for_status(self, response: httpx.Response) -> None:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise LLMClientError(f"LLM provider request failed: {response.status_code}") from exc

    def close(self) -> None:
        if self._owns_client:
            self.http_client.close()
