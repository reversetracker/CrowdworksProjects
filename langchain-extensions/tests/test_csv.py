import pytest
from langchain_core.documents import Document
from pytest_mock import MockerFixture

import directories
from langchain_extensions.vectorstores.chroma import Chroma


@pytest.mark.asyncio
async def test_add_csv_with_filepath(mocker: MockerFixture):
    add_documents = mocker.patch(
        "langchain_extensions.vectorstores.chroma.Chroma.add_documents"
    )

    chroma = Chroma(persist_directory="/tmp/rag-chroma")

    documents = await chroma.add_csv(
        file_or_path=directories.csv_file.as_posix(),
        metadata={"author": "test author"},
    )

    assert add_documents.call_count == 1
    assert documents == [
        Document(
            page_content="John: Jack\nDoe: McGinnis\n120 jefferson st.: 220 hobo Av.\nRiverside: Phila\nNJ: PA\n08075: 09119",
            metadata={
                "source": "/Users/nelly/PycharmProjects/langchain-extensions/fixtures/upload_test_1.csv",
                "row": 0,
                "author": "test author",
            },
        ),
        Document(
            page_content='John: John "Da Man"\nDoe: Repici\n120 jefferson st.: 120 Jefferson St.\nRiverside: Riverside\nNJ: NJ\n08075: 08075',
            metadata={
                "source": "/Users/nelly/PycharmProjects/langchain-extensions/fixtures/upload_test_1.csv",
                "row": 1,
                "author": "test author",
            },
        ),
        Document(
            page_content='John: Stephen\nDoe: Tyler\n120 jefferson st.: 7452 Terrace "At the Plaza" road\nRiverside: SomeTown\nNJ: SD\n08075: 91234',
            metadata={
                "source": "/Users/nelly/PycharmProjects/langchain-extensions/fixtures/upload_test_1.csv",
                "row": 2,
                "author": "test author",
            },
        ),
        Document(
            page_content="John: \nDoe: Blankman\n120 jefferson st.: \nRiverside: SomeTown\nNJ: SD\n08075: 00298",
            metadata={
                "source": "/Users/nelly/PycharmProjects/langchain-extensions/fixtures/upload_test_1.csv",
                "row": 3,
                "author": "test author",
            },
        ),
        Document(
            page_content='John: Joan "the bone", Anne\nDoe: Jet\n120 jefferson st.: 9th, at Terrace plc\nRiverside: Desert City\nNJ: CO\n08075: 00123',
            metadata={
                "source": "/Users/nelly/PycharmProjects/langchain-extensions/fixtures/upload_test_1.csv",
                "row": 4,
                "author": "test author",
            },
        ),
    ]


@pytest.mark.asyncio
async def test_add_csv_with_bytes(mocker: MockerFixture):
    add_documents = mocker.patch(
        "langchain_extensions.vectorstores.chroma.Chroma.add_documents"
    )

    chroma = Chroma(persist_directory="/tmp/rag-chroma")

    with open(directories.csv_file, "rb") as f:
        csv_bytes = f.read()
        documents = await chroma.add_csv(
            file_or_path=csv_bytes,
            metadata={"author": "test author"},
        )

    assert add_documents.call_count == 1
    assert len(documents) == 5
