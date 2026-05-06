from __future__ import annotations

import logging
import ssl
import time

import httpx

from app.llm.client_cache import llm_client_cache
from app.llm.metrics import llm_metrics


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
        timeout_seconds: float = 60.0,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.api_style = api_style
        self._owns_client = http_client is None
        self.timeout_seconds = timeout_seconds
        
        if http_client is None:
            # Create client with SSL verification and reasonable timeout
            timeout = httpx.Timeout(timeout_seconds, connect=10.0)
            self.http_client = httpx.Client(
                timeout=timeout,
                verify=True,  # Enable SSL verification
                http2=False,  # Disable HTTP/2 to avoid some SSL issues
            )
        else:
            self.http_client = http_client
            
        self._logger = logging.getLogger(__name__)

    def complete(self, prompt: str) -> str:
        start_time = time.time()
        prompt_length = len(prompt)

        # 检查客户端缓存
        cached_result = llm_client_cache.get(prompt, self.model, self.api_style)
        if cached_result is not None:
            self._logger.info(
                f"LLM cache hit: model={self.model}, prompt_length={prompt_length}, "
                f"response_length={len(cached_result)}"
            )
            llm_metrics.record_call(
                duration=0.0,
                success=True,
                cached=True,
                prompt_length=prompt_length,
                response_length=len(cached_result),
                model_name=self.model,
            )
            return cached_result

        try:
            if self.api_style == "responses":
                result = self._complete_responses(prompt)
            elif self.api_style == "chat_completions":
                result = self._complete_chat_completions(prompt)
            else:
                raise LLMClientError(f"Unsupported LLM api_style: {self.api_style}")

            duration = time.time() - start_time
            self._logger.info(
                f"LLM call completed: model={self.model}, prompt_length={prompt_length}, "
                f"response_length={len(result)}, duration={duration:.2f}s"
            )

            # 将结果存入缓存
            llm_client_cache.set(prompt, self.model, self.api_style, result)

            llm_metrics.record_call(
                duration=duration,
                success=True,
                prompt_length=prompt_length,
                response_length=len(result),
                model_name=self.model,
            )

            return result

        except httpx.TimeoutException as exc:
            duration = time.time() - start_time
            self._logger.error(
                f"LLM call timeout after {duration:.2f}s: model={self.model}, "
                f"prompt_length={prompt_length}"
            )
            llm_metrics.record_call(
                duration=duration,
                success=False,
                error_type="TimeoutException",
                error_message=str(exc),
                prompt_length=prompt_length,
                model_name=self.model,
            )
            raise

        except httpx.HTTPStatusError as exc:
            duration = time.time() - start_time
            self._logger.error(
                f"LLM call HTTP error after {duration:.2f}s: model={self.model}, "
                f"status={exc.response.status_code}"
            )
            llm_metrics.record_call(
                duration=duration,
                success=False,
                error_type="HTTPStatusError",
                error_message=f"HTTP {exc.response.status_code}: {exc.response.text[:200]}",
                prompt_length=prompt_length,
                model_name=self.model,
            )
            raise

        except httpx.NetworkError as exc:
            duration = time.time() - start_time
            error_msg = str(exc)
            # Check for SSL-related errors
            if "SSL" in error_msg or "EOF" in error_msg:
                self._logger.error(
                    f"LLM call SSL/Network error after {duration:.2f}s: model={self.model}, "
                    f"error={error_msg[:100]}"
                )
                llm_metrics.record_call(
                    duration=duration,
                    success=False,
                    error_type="SSLNetworkError",
                    error_message=error_msg[:200],
                    prompt_length=prompt_length,
                    model_name=self.model,
                )
                raise LLMClientError(f"SSL/Network error when calling LLM: {error_msg[:100]}") from exc
            else:
                self._logger.error(
                    f"LLM call network error after {duration:.2f}s: model={self.model}, "
                    f"error={error_msg}"
                )
                llm_metrics.record_call(
                    duration=duration,
                    success=False,
                    error_type="NetworkError",
                    error_message=error_msg[:200],
                    prompt_length=prompt_length,
                    model_name=self.model,
                )
                raise

        except Exception as exc:
            duration = time.time() - start_time
            self._logger.error(
                f"LLM call failed after {duration:.2f}s: model={self.model}, "
                f"prompt_length={prompt_length}, error={exc}"
            )
            llm_metrics.record_call(
                duration=duration,
                success=False,
                error_type=type(exc).__name__,
                error_message=str(exc)[:200],
                prompt_length=prompt_length,
                model_name=self.model,
            )
            raise

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
