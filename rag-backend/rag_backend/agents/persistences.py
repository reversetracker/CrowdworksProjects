from langchain_openai import OpenAIEmbeddings

import directories
from langchain_extensions.embeddings import HyperClovaEmbeddings
from langchain_extensions.vectorstores.chroma import Chroma
from rag_backend.configs import settings

hyper_clova_embedding = HyperClovaEmbeddings(
    clovastudio_api_key=settings.clovastudio_api_key,
    apigw_api_key=settings.clovastudio_apigw_api_key,
)

openai_embedding = OpenAIEmbeddings()

disease_chroma = Chroma(
    persist_directory=str(directories.disease_chromadb),
    embedding_function=hyper_clova_embedding,
    collection_metadata={"hnsw:space": "cosine"},
)

insurance_chroma = Chroma(
    persist_directory=str(directories.insurance_chromadb),
    embedding_function=hyper_clova_embedding,
    collection_metadata={"hnsw:space": "cosine"},
)

coverage_limit_chroma = Chroma(
    persist_directory=str(directories.coverage_limit_chromadb),
    embedding_function=hyper_clova_embedding,
    collection_metadata={"hnsw:space": "cosine"},
)

# matrix 에서 정확한 이름으로 변경하기 위한 chroma db
collateral_name_chroma = Chroma(
    persist_directory=str(directories.matrix_collateral_name_chromadb),
    embedding_function=hyper_clova_embedding,
    collection_metadata={"hnsw:space": "cosine"},
)

disease_name_chroma = Chroma(
    persist_directory=str(directories.matrix_disease_name_chromadb),
    embedding_function=hyper_clova_embedding,
    collection_metadata={"hnsw:space": "cosine"},
)

insurance_requirements_chroma = Chroma(
    persist_directory=str(directories.insurance_requirements_chromadb),
    embedding_function=hyper_clova_embedding,
    collection_metadata={"hnsw:space": "cosine"},
)
