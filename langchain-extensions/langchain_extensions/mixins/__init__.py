import abc
import asyncio
import functools
import os
import tempfile
from typing import Callable

import aiofiles
from langchain_community.document_loaders import CSVLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_community.document_loaders import UnstructuredHTMLLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.document_loaders import UnstructuredPowerPointLoader
from langchain_community.document_loaders.base import BaseLoader
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.documents import Document


class BytesToFilepathAdaptive:
    def __init__(self, file_param_name: str, suffix: str = ""):
        self.file_param_name = file_param_name
        self.suffix = suffix

    def __call__(self, func: Callable):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError(
                "BytesToFileAdaptive decorator can only be applied to async functions."
            )

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            file_arg = kwargs.get(self.file_param_name)

            if not file_arg:
                raise ValueError(f"Parameter '{self.file_param_name}' is required.")

            if isinstance(file_arg, bytes):
                tmp_file_name = tempfile.mktemp(suffix=self.suffix)
                async with aiofiles.open(tmp_file_name, "wb") as tmp_file:
                    await tmp_file.write(file_arg)
                kwargs[self.file_param_name] = tmp_file_name
                result = await func(*args, **kwargs)
                os.remove(tmp_file_name)
                return result

            return await func(*args, **kwargs)

        return wrapper


class AbcFileHandler(abc.ABC):
    def add_csv(
        self,
        file_or_path: str | bytes,
        metadata: dict = None,
        collection: str = "default",
        segment: str = "default",
    ):
        raise NotImplementedError

    def add_pdf(
        self,
        file_or_path: str | bytes,
        metadata: dict = None,
        collection: str = "default",
        segment: str = "default",
    ):
        raise NotImplementedError

    def add_markdown(
        self,
        file_or_path: str | bytes,
        metadata: dict = None,
        collection: str = "default",
        segment: str = "default",
    ):
        raise NotImplementedError

    def add_json(
        self,
        file_or_path: str | bytes,
        metadata: dict = None,
        collection: str = "default",
        segment: str = "default",
    ):
        raise NotImplementedError

    def add_html(
        self,
        file_or_path: str | bytes,
        metadata: dict = None,
        collection: str = "default",
        segment: str = "default",
    ):
        raise NotImplementedError

    def add_ppt(
        self,
        file_or_path: str | bytes,
        metadata: dict = None,
        collection: str = "default",
        segment: str = "default",
    ):
        raise NotImplementedError

    def add_hangul(
        self,
        file_or_path: str | bytes,
        metadata: dict = None,
        collection: str = "default",
        segment: str = "default",
    ):
        raise NotImplementedError

    def add_word(
        self,
        file_or_path: str | bytes,
        metadata: dict = None,
        collection: str = "default",
        segment: str = "default",
    ):
        raise NotImplementedError

    def add_excel(
        self,
        file_or_path: str | bytes,
        metadata: dict = None,
        collection: str = "default",
        segment: str = "default",
    ):
        raise NotImplementedError


class ChromaDefaultFileHandlerMixin(AbcFileHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            from langchain_community.vectorstores.chroma import Chroma
        except ImportError:
            error_msg = (
                "Could not import Chroma from langchain_community.vectorstores.chroma.\n"
                "You can install following command `pip install langchain-community`."
            )
            raise ImportError(error_msg)

        if not isinstance(self, Chroma) and not any(
            issubclass(cls, Chroma) for cls in self.__class__.__bases__
        ):
            error_msg = (
                "ChromaDefaultFileHandlerMixin can only be used with Chroma class"
            )
            raise TypeError(error_msg)

    @BytesToFilepathAdaptive(file_param_name="file_or_path", suffix=".csv")
    async def add_csv(
        self,
        file_or_path: str | bytes,
        metadata: dict = None,
        collection: str = "default",
        segment: str = "default",
    ) -> list[Document]:
        loader = CSVLoader(file_path=file_or_path)
        documents = self._add_by_loader(loader=loader, metadata=metadata)
        return documents

    @BytesToFilepathAdaptive(file_param_name="file_or_path", suffix=".pdf")
    async def add_pdf(
        self,
        file_or_path: str | bytes,
        metadata: dict = None,
        collection: str = "default",
        segment: str = "default",
    ) -> list[Document]:
        loader = PyPDFLoader(file_path=file_or_path)
        documents = self._add_by_loader(loader=loader, metadata=metadata)
        return documents

    @BytesToFilepathAdaptive(file_param_name="file_or_path", suffix=".md")
    async def add_markdown(
        self,
        file_or_path: str | bytes,
        metadata: dict = None,
        collection: str = "default",
        segment: str = "default",
    ) -> list[Document]:
        loader = UnstructuredMarkdownLoader(file_path=file_or_path)
        documents = self._add_by_loader(loader=loader, metadata=metadata)
        return documents

    @BytesToFilepathAdaptive(file_param_name="file_or_path", suffix=".json")
    async def add_json(
        self,
        file_or_path: str | bytes,
        metadata: dict = None,
        collection: str = "default",
        segment: str = "default",
    ) -> list[Document]:
        loader = UnstructuredMarkdownLoader(file_path=file_or_path)
        documents = self._add_by_loader(loader=loader, metadata=metadata)
        return documents

    @BytesToFilepathAdaptive(file_param_name="file_or_path", suffix=".html")
    async def add_html(
        self,
        file_or_path: str | bytes,
        metadata: dict = None,
        collection: str = "default",
        segment: str = "default",
    ) -> list[Document]:
        loader = UnstructuredHTMLLoader(file_path=file_or_path)
        documents = self._add_by_loader(loader=loader, metadata=metadata)
        return documents

    @BytesToFilepathAdaptive(file_param_name="file_or_path", suffix=".ppt")
    async def add_ppt(
        self,
        file_or_path: str | bytes,
        metadata: dict = None,
        collection: str = "default",
        segment: str = "default",
    ) -> list[Document]:
        loader = UnstructuredPowerPointLoader(file_path=file_or_path)
        documents = self._add_by_loader(loader=loader, metadata=metadata)
        return documents

    async def add_hangul(
        self,
        file_or_path: str | bytes,
        metadata: dict = None,
        collection: str = "default",
        segment: str = "default",
    ):
        raise NotImplementedError

    @BytesToFilepathAdaptive(file_param_name="file_or_path", suffix=".docx")
    async def add_word(
        self,
        file_or_path: str | bytes,
        metadata: dict = None,
        collection: str = "default",
        segment: str = "default",
    ) -> list[Document]:
        loader = Docx2txtLoader(file_path=file_or_path)
        documents = self._add_by_loader(loader=loader, metadata=metadata)
        return documents

    @BytesToFilepathAdaptive(file_param_name="file_or_path", suffix=".xlsx")
    async def add_excel(
        self,
        file_or_path: str | bytes,
        metadata: dict = None,
        collection: str = "default",
        segment: str = "default",
    ) -> list[Document]:
        loader = UnstructuredExcelLoader(file_path=file_or_path, mode="elements")
        documents = self._add_by_loader(loader=loader, metadata=metadata)
        return documents

    def _add_by_loader(
        self, loader: BaseLoader, metadata: dict = None
    ) -> list[Document]:
        documents = loader.load()
        for document in documents:
            document.metadata.update(metadata or {})
        self.add_documents(documents=documents)
        return documents

    @staticmethod
    def apply(target: type):

        if not isinstance(target, type):
            raise TypeError("target must be a class.")

        if target not in [Chroma]:
            raise TypeError("target must be a Chroma class.")

        class VectorDBMixin(target, ChromaDefaultFileHandlerMixin):
            pass

        return VectorDBMixin
