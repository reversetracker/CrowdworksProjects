from __future__ import annotations

import asyncio
import logging
import uuid
from typing import List

import httpx
from langchain_core.embeddings import Embeddings
from langchain_core.pydantic_v1 import BaseModel

logger = logging.getLogger(__name__)


class HyperClovaEmbeddings(BaseModel, Embeddings):

    host: str = "clovastudio.stream.ntruss.com"

    invoke_url: str = (
        "/testapp/v1/api-tools/embedding/clir-emb-dolphin/bce2e8a3e699451ba23f90f97c771adf"
    )

    # X-NCP-CLOVASTUDIO-API-KEY
    clovastudio_api_key: str

    # X-NCP-APIGW-API-KEY
    apigw_api_key: str

    def _send_request(self, text: str) -> dict:
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "X-NCP-CLOVASTUDIO-API-KEY": self.clovastudio_api_key,
            "X-NCP-APIGW-API-KEY": self.apigw_api_key,
            "X-NCP-CLOVASTUDIO-REQUEST-ID": str(uuid.uuid4()),
        }
        completion_request = {"text": text}
        url = f"https://{self.host}{self.invoke_url}"

        with httpx.Client() as client:
            response = client.post(url, json=completion_request, headers=headers)
        result = response.json()
        return result

    async def _send_request_async(self, text: str) -> dict:
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "X-NCP-CLOVASTUDIO-API-KEY": self.clovastudio_api_key,
            "X-NCP-APIGW-API-KEY": self.apigw_api_key,
            "X-NCP-CLOVASTUDIO-REQUEST-ID": str(uuid.uuid4()),
        }
        completion_request = {"text": text}
        url = f"https://{self.host}{self.invoke_url}"

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=completion_request, headers=headers)
        result = response.json()
        return result

    def _execute(self, completion_request: str) -> List[float]:
        res = self._send_request(completion_request)
        if res["status"]["code"] != "20000":
            raise ValueError(f"Error: {res['status']['code']}")
        return res["result"]["embedding"]

    async def _execute_async(self, completion_request: str) -> List[float]:
        res = await self._send_request_async(completion_request)
        if res["status"]["code"] != "20000":
            raise ValueError(f"Error: {res['status']['code']}")
        return res["result"]["embedding"]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._execute(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._execute(text)

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        return await asyncio.gather(*(self._execute_async(text) for text in texts))  # type: ignore

    async def aembed_query(self, text: str) -> List[float]:
        return await self._execute_async(text)
