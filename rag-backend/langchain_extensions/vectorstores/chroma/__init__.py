from langchain_community.vectorstores.chroma import Chroma as OriginalChroma

from langchain_extensions.mixins import ChromaDefaultFileHandlerMixin


class Chroma(OriginalChroma, ChromaDefaultFileHandlerMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
