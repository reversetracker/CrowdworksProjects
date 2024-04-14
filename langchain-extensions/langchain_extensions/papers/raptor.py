import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Tuple, Union

import numpy as np
import pandas as pd
import umap
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sklearn.mixture import GaussianMixture


def global_cluster_embeddings(
    embeddings: np.ndarray,
    dim: int,
    n_neighbors: int = 0,
    metric: str = "cosine",
) -> np.ndarray:
    if not n_neighbors:
        n_neighbors = int((len(embeddings) - 1) ** 0.5)
    return umap.UMAP(
        n_neighbors=n_neighbors, n_components=dim, metric=metric
    ).fit_transform(embeddings)


def cluster_embeddings(
    embeddings: np.ndarray, dim: int, n_neighbors: int = 0, metric: str = "cosine"
) -> np.ndarray:
    if not n_neighbors:
        n_neighbors = int((len(embeddings) - 1) ** 0.5)
    return umap.UMAP(
        n_neighbors=n_neighbors, n_components=dim, metric=metric
    ).fit_transform(embeddings)


def get_optimal_clusters_n(
    embeddings: np.ndarray, max_clusters: int = 50, random_state: int = 42
) -> int:
    max_clusters = min(max_clusters, len(embeddings))
    n_clusters = np.arange(1, max_clusters)
    bics = []
    for n in n_clusters:
        gm = GaussianMixture(n_components=n, random_state=random_state)
        gm.fit(embeddings)
        bics.append(gm.bic(embeddings))
    return n_clusters[np.argmin(bics)]


def GMM_cluster(embeddings: np.ndarray, threshold: float, random_state: int = 0):
    n_clusters = get_optimal_clusters_n(embeddings)
    gm = GaussianMixture(n_components=n_clusters, random_state=random_state)
    gm.fit(embeddings)
    probs = gm.predict_proba(embeddings)
    labels = [np.where(prob > threshold)[0] for prob in probs]
    return labels, n_clusters


def perform_clustering(
    embeddings: np.ndarray,
    dim: int,
    threshold: float,
) -> List[np.ndarray]:
    if len(embeddings) <= dim + 1:
        return [np.array([0]) for _ in range(len(embeddings))]

    reduced_embeddings_global = cluster_embeddings(
        embeddings=embeddings, dim=dim, n_neighbors=0, metric="cosine"
    )
    global_clusters, n_global_clusters = GMM_cluster(
        reduced_embeddings_global, threshold
    )

    all_local_clusters = [np.array([]) for _ in range(len(embeddings))]
    total_clusters = 0

    for i in range(n_global_clusters):
        global_cluster_embeddings_ = embeddings[
            np.array([i in gc for gc in global_clusters])
        ]

        if len(global_cluster_embeddings_) == 0:
            continue

        if len(global_cluster_embeddings_) <= dim + 1:
            local_clusters = [np.array([0]) for _ in global_cluster_embeddings_]
            n_local_clusters = 1
        else:
            reduced_embeddings_local = cluster_embeddings(
                embeddings=global_cluster_embeddings_,
                dim=dim,
                n_neighbors=10,
                metric="cosine",
            )
            local_clusters, n_local_clusters = GMM_cluster(
                reduced_embeddings_local, threshold
            )

        for j in range(n_local_clusters):
            local_cluster_embeddings_ = global_cluster_embeddings_[
                np.array([j in lc for lc in local_clusters])
            ]
            indices = np.where(
                (embeddings == local_cluster_embeddings_[:, None]).all(-1)
            )[1]
            for idx in indices:
                all_local_clusters[idx] = np.append(
                    all_local_clusters[idx], j + total_clusters
                )

        total_clusters += n_local_clusters

    return all_local_clusters


def embed(texts: List[str]):
    embd = OpenAIEmbeddings()
    text_embeddings = embd.embed_documents(texts)
    text_embeddings_np = np.array(text_embeddings)
    return text_embeddings_np


def embed_cluster_texts(texts: List[str]):
    text_embeddings_np = embed(texts)
    cluster_labels = perform_clustering(text_embeddings_np, 10, 0.1)
    df = pd.DataFrame()
    df["text"] = texts
    df["embd"] = list(text_embeddings_np)
    df["cluster"] = cluster_labels
    return df


def fmt_txt(df: pd.DataFrame) -> str:
    unique_txt = df["text"].tolist()
    return "--- --- \n --- --- ".join(unique_txt)


def embed_cluster_summarize_texts(
    texts: List[str], level: int
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df_clusters = embed_cluster_texts(texts)
    expanded_list = []
    for index, row in df_clusters.iterrows():
        for cluster in row["cluster"]:
            expanded_list.append(
                {
                    "text": row["text"],
                    "embd": row["embd"],
                    "cluster": cluster,
                }
            )

    expanded_df = pd.DataFrame(expanded_list)
    all_clusters = expanded_df["cluster"].unique()

    print(f"--Generated {len(all_clusters)} clusters--")

    template = """
    언어 문서의 하위 집합이 있습니다.
    제공된 문서의 자세한 요약을 제공하십시오.

    문서:
    {context}
    """

    class StreamCallback(BaseCallbackHandler):
        def on_llm_new_token(self, token: str, **kwargs):
            print(token, end="", flush=True)

    model = ChatOpenAI(
        model="gpt-4-turbo-preview",
        temperature=0,
        streaming=True,
        callbacks=[StreamCallback()],
    )

    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model | StrOutputParser()

    summaries = []
    for i in all_clusters:
        df_cluster = expanded_df[expanded_df["cluster"] == i]
        formatted_txt = fmt_txt(df_cluster)
        summaries.append(chain.invoke({"context": formatted_txt}))

    df_summary = pd.DataFrame(
        {
            "summaries": summaries,
            "level": [level] * len(summaries),
            "cluster": list(all_clusters),
        }
    )
    return df_clusters, df_summary


def raptornize(
    texts_or_long_text: Union[str, List[str]], level: int = 1, n_levels: int = 3
) -> Dict[int, Tuple[pd.DataFrame, pd.DataFrame]]:

    if isinstance(texts_or_long_text, str):
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=2000, chunk_overlap=0
        )
        texts = text_splitter.split_text(texts_or_long_text)
    elif isinstance(texts_or_long_text, list):
        texts = texts_or_long_text
    else:
        raise ValueError("Input must be a string or list of strings.")

    results = {}
    df_clusters, df_summary = embed_cluster_summarize_texts(texts, level)
    results[level] = (df_clusters, df_summary)
    unique_clusters = df_summary["cluster"].nunique()
    if level < n_levels and unique_clusters > 1:
        new_texts = df_summary["summaries"].tolist()
        next_level_results = raptornize(new_texts, level + 1, n_levels)
        results.update(next_level_results)
    return results


async def araptornize(
    texts_or_long_text: Union[str, List[str]], level: int = 1, n_levels: int = 3
) -> Dict[int, Tuple[pd.DataFrame, pd.DataFrame]]:
    loop = asyncio.get_running_loop()

    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(
            executor, raptornize, texts_or_long_text, level, n_levels
        )
    return result
