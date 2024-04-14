import pytest
from langchain_community.vectorstores.chroma import Chroma

from langchain_extensions.mixins import ChromaDefaultFileHandlerMixin


@pytest.mark.asyncio
async def test_apply():
    ChromaMixin = ChromaDefaultFileHandlerMixin.apply(Chroma)
    chroma = ChromaMixin(persist_directory="/tmp/rag-chroma")

    assert {
        "search",
        "asearch",
        "add_excel",
        "add_hangul",
        "add_html",
        "add_images",
        "add_json",
        "add_markdown",
        "add_pdf",
        "add_ppt",
        "add_word",
        "_add_by_loader",
    }.issubset(dir(chroma))
