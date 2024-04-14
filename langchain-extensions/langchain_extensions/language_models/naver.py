import json
import logging
import uuid
from typing import Any, Optional, List, Iterator, AsyncIterator, Dict

import httpx
from langchain_core.callbacks import AsyncCallbackManagerForLLMRun
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.messages import AIMessageChunk
from langchain_core.messages import BaseMessage
from langchain_core.messages import ChatMessage
from langchain_core.messages import HumanMessage
from langchain_core.messages import SystemMessage
from langchain_core.outputs import ChatGeneration
from langchain_core.outputs import ChatGenerationChunk
from langchain_core.outputs import ChatResult

logger = logging.getLogger(__name__)


class HyperClova(BaseChatModel):
    """A chat model that uses the Hyper Clova language model."""

    host: str = "https://clovastudio.stream.ntruss.com"

    """X-NCP-CLOVASTUDIO-API-KEY"""
    clovastudio_api_key: str

    """X-NCP-APIGW-API-KEY"""
    apigw_api_key: str

    invoke_url: str = "/testapp/v1/chat-completions/HCX-003"

    top_p: float = 0.8

    top_k: int = 0

    max_tokens: int = 256

    temperature: float = 0.5

    repeat_penalty: float = 5.0

    stop_before: List[str] = []

    include_ai_filters: bool = True

    seed: int = 0

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model."""
        return "hyperclova"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return a dictionary of identifying parameters."""
        return {
            "host": self.host,
            "clovastudio_api_key": self.clovastudio_api_key,
            "apigw_api_key": self.apigw_api_key,
            "invoke_url": self.invoke_url,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "repeat_penalty": self.repeat_penalty,
            "stop_before": self.stop_before,
            "include_ai_filters": self.include_ai_filters,
            "seed": self.seed,
        }

    @property
    def is_lc_serializable(cls) -> bool:
        """Return whether this class is serializable by Langchain."""
        return True

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Get the namespace of the langchain object."""
        return ["langchain", "llms", "hyper-clova"]

    @property
    def lc_attributes(self) -> Dict:
        """List of attribute names that should be included in the serialized kwargs.

        These attributes must be accepted by the constructor.
        """
        return self._identifying_params

    @property
    def endpoint(self) -> str:
        return self.host + self.invoke_url

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling OpenAI API."""
        return {
            "topP": self.top_p,
            "topK": self.top_k,
            "maxTokens": self.max_tokens,
            "temperature": self.temperature,
            "repeatPenalty": self.repeat_penalty,
            "stopBefore": self.stop_before,
            "includeAiFilters": self.include_ai_filters,
            "seed": self.seed,
        }

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate a response to the given prompt."""

        # TODO: Implement retry logic
        request_params = self._create_request_params(
            messages,
            stop,
            stream=False,
            **kwargs,
        )

        response = httpx.request(**request_params)
        response.raise_for_status()
        json_response = response.json()
        response_content = json_response["result"]["message"]["content"]

        message = AIMessage(content=response_content)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        clovastudio_request_id: str | None = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        """Stream a response to the given prompt."""
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")

        request_params = self._create_request_params(
            messages,
            stop,
            clovastudio_request_id=clovastudio_request_id,
            **kwargs,
        )
        with httpx.stream(**request_params) as response:
            for line in response.iter_lines():
                name, value = _decode(line)
                if name != "data":
                    # Ignore non-data lines
                    continue

                content = json.loads(value)
                if content.get("stopReason"):
                    continue

                message = content.get("message")
                if not message:
                    logger.debug(value)
                    continue

                message_chunk = AIMessageChunk(**message)
                chunk = ChatGenerationChunk(message=message_chunk)
                if run_manager:
                    run_manager.on_llm_new_token(token=chunk.text, chunk=chunk)
                yield chunk

    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        clovastudio_request_id: str | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")

        request_params = self._create_request_params(
            messages,
            stop,
            clovastudio_request_id=clovastudio_request_id,
            **kwargs,
        )
        async with httpx.AsyncClient() as client:
            async with client.stream(**request_params) as response:
                async for line in response.aiter_lines():
                    name, value = _decode(line)
                    if name != "data":
                        # Ignore non-data lines
                        continue

                    content = json.loads(value)
                    if content.get("stopReason"):
                        continue

                    message = content.get("message")
                    if not message:
                        logger.debug(value)
                        continue

                    message_chunk = AIMessageChunk(**message)
                    chunk = ChatGenerationChunk(message=message_chunk)
                    if run_manager:
                        await run_manager.on_llm_new_token(
                            token=chunk.text, chunk=chunk
                        )
                    yield chunk

    def _create_params(
        self, messages: List[BaseMessage], stop: Optional[List[str]]
    ) -> Dict[str, Any]:
        params = self._default_params
        params["messages"] = [_convert_message_to_dict(m) for m in messages]
        return params

    def _create_request_params(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]],
        clovastudio_request_id: str | None = None,
        stream: bool = True,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        headers = {
            "X-NCP-CLOVASTUDIO-API-KEY": self.clovastudio_api_key,
            "X-NCP-APIGW-API-KEY": self.apigw_api_key,
            "X-NCP-CLOVASTUDIO-REQUEST-ID": kwargs.get(
                "clovastudio_request_id", clovastudio_request_id or str(uuid.uuid4())
            ),
            "Content-Type": "application/json; charset=utf-8",
        }
        if stream:
            headers["Accept"] = "text/event-stream"
        return {
            "method": "POST",
            "url": self.endpoint,
            "headers": headers,
            "json": self._create_params(messages, stop),
            "timeout": 120,
        }


def _convert_message_to_dict(message: BaseMessage) -> dict:
    """Convert a LangChain message to a dictionary.

    Args:
        message: The LangChain message.

    Returns:
        The dictionary.
    """
    message_dict: Dict[str, Any]
    if isinstance(message, ChatMessage):
        message_dict = {"role": message.role, "content": message.content}
    elif isinstance(message, HumanMessage):
        message_dict = {"role": "user", "content": message.content}
    elif isinstance(message, AIMessage):
        message_dict = {"role": "assistant", "content": message.content}
    elif isinstance(message, SystemMessage):
        message_dict = {"role": "system", "content": message.content}
    else:
        raise TypeError(f"Got unknown type {message}")
    return message_dict


def _decode(line: str) -> tuple[Optional[str], Optional[str]]:
    if not line:
        return None, None
    name, value = line.split(":", maxsplit=1)
    return name, value
