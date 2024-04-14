# Langchain Extensions 

## Overview

The Langchain Community module provides a comprehensive suite of extensions for handling various document formats. 
These extensions are designed to integrate seamlessly with the existing Langchain ecosystem, enhancing its capabilities to meet specific business and customer needs. The module includes custom file handlers and loaders for a wide range of document types, making it easier for developers to add and process documents in their applications.

## Installation

#### 1. pip
```bash
pip install --upgrade pip
pip install git+https://bitbucket.org/crowdworks_dev/langchain-extensions.git
```

#### 2. poetry
```bash
poetry add git+https://bitbucket.org/crowdworks_dev/langchain-extensions.git
```

## Features

### 1. language_models

#### 1.1 Hyperclova, Mixtral and etc..

langchain 과 100% 호환 되는 HyperClova 및 기타 모델입니다.
아래 Snippet 을 준비해 두었으니 참조 바랍니다.

```python
from langchain.schema import StrOutputParser
from langchain_community.llms.openai import OpenAI
from langchain_core.prompts import ChatPromptTemplate

from langchain_extensions.language_models import HyperClova

CLOVASTUDIO_API_KEY = "😝"

APIGW_API_KEY = "😝"

OPENAI_API_KEY = "😝"

prompt = ChatPromptTemplate.from_template("what is the city {person} is from?")

# Note: 대체해도 그대로 동작 가능!
# model = OpenAI(
#     api_key=OPENAI_API_KEY,
#     streaming=True,
# )

model = HyperClova(
    clovastudio_api_key=CLOVASTUDIO_API_KEY,
    apigw_api_key=APIGW_API_KEY,
)

chain = prompt | model | StrOutputParser()
invocation = chain.invoke({"person": "obama"})
print(invocation)
# AI(🤖): Obama is from Honolulu.


stream = chain.stream({"person": "obama"})
for s in stream:
    print(s, end="")
# AI(🤖): Obama is from Honolulu.
```


#### 1.2 History feature
당연하게도 히스토리 기능까지 모두 langchain 기능을 통합해서 사용 할 수 있습니다.
```python

runnable = prompt | mixtral | StrOutputParser()
chain = RunnableWithMessageHistory(
    runnable,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)
```
아래와 같이 히스토리 기록이 남게 됩니다.
```python
[
    HumanMessage(content="hi!", additional_kwargs={}, example=False),
    AIMessage(content="what`s up?", additional_kwargs={}, example=False),
    HumanMessage(content="I love you", additional_kwargs={}, example=False),
    AIMessage(content="what are you talking about?", additional_kwargs={}, example=False)
]
```

### 2. Knowledge Compiler
`langchain-extensions`는 SOTA에 근접한 여러 논문들을 바탕으로 개발한 `Knowledge Compiler` 를 지원합니다. 
- [https://arxiv.org/abs/2207.06300 현재 개발중인 Knowledge Compiler 논문 자료](https://arxiv.org/abs/2207.06300)
- [Re2G bitbucket for source code (under development..)](https://bitbucket.org/crowdworks_dev/re2g/src/master/)
- 추상화 된 Rerank feature 들을 언제든 새롭게 추가 및 변경이 가능하며 실제 사용 시 잘 작동하지 않는 Retrieval 부분들을 쉽게 보완 할 수 있습니다.
```python
from langchain_extensions.knowledge_compiler import KnowledgeCompiler

k_compiler = KnowledgeCompiler(prompt=prompt, retriever=retriever)

# 완전히 랭체인에 녹아든 knowledge compiler 사용 예시
# 향상 된 검색결과를 얻을 수 있습니다.
chain = k_compiler | model | StrOutputParser()
stream = chain.stream()

for token in stream:
    print(token, end="")

# AI(🤖): 와! 정보를 잘 주니 답변하기 너무 쉽다.
```


### 3. Mixin classes

#### 3.1 DefaultChromaFileHandler 
A versatile handler that supports adding documents from various formats, 
including CSV, PDF, Markdown, HTML, Word, and Excel, to the Chroma vector store. 
This handler leverages the document loaders to read files, extract content, 
and update document metadata before adding them to the vector store.

- 일반적인 langchain_community 의 Chroma 사용 시 아래와 같습니다.
```
from langchain_community.vectorstores import Chroma
```

- 하지만 해당 패키지를 설치 후 아래와 같이 사용 시 추가 확장 된 기능들을 이용 할 수 있습니다.
```
from langchain_extensions.vectorstores import Chroma

chroma = Chroma()

# 확장 된 chroma functions example 1
chroma.add_csv("path/to/csv/file.csv")

# 확장 된 chroma functions example 2  
with open("path/to/text/file.csv", "r") as f:
    file_bytes = f.read()
    chroma.add_csv(file_bytes)  
```

#### 3.2 Custom Functionality

- **Mixin classes**: 
An example class that demonstrates how to extend the Langchain module with custom file handling capabilities. 
This class is a mix-in that combines the features of Chroma with the DefaultChromaFileHandler, 
showcasing how to add documents from supported formats directly to a vector store for further processing or search capabilities.

- 아래는 실제 Default Chroma Mixin 이 구현 된 예시 입니다.
아래와 마찬가지로 `ChromaDefaultFileHandlerMixin` 을 원하는 Mixin class 로 변경 하시면
변경 및 확장 된 Chroma 를 자체적으로 Custom 하여 사용 할 수 있습니다.
```python
from langchain_community.vectorstores.chroma import Chroma as OriginalChroma

from langchain_extensions.mixins import ChromaDefaultFileHandlerMixin


class Chroma(OriginalChroma, ChromaDefaultFileHandlerMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

```

#### 3.3 Use apply()

- 별도의 조작 없이 apply 를 통해서 곧바로 mixin 된 객체를 사용 할 수 있습니다.

```
ChromaMixin = ChromaDefaultFileHandlerMixin.apply(Chroma)
chroma = ChromaMixin(persist_directory="/tmp/rag-chroma")

assert [
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
] == dir(chroma)
```

##### 3.4 Abstract classes

from langchain_extensions.mixins import AbcFileHandler
를 활용하여 자신만의 멋진 `File handler` 를 구축 할 수도 있습니다.
```python
import abc

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


```

### 4. Custom Embedding
OpenAI 의 임베딩을 사용하는 방식과 동일한 방식으로 Clova 및 다른 Custom Model 들의 임베딩 사용까지 지원합니다.

```python
from langchain_extensions.embeddings.naver import HyperClovaEmbeddings
from langchain_community.vectorstores import Chroma

API_KEY = "😝"

embedding = HyperClovaEmbeddings(api_key=API_KEY)
chroma = Chroma(embedding_function=embedding)
```

```python
# hyperclova embedding 을 사용하여 파일의 텍스트를 vectorize 합니다.
chroma.add_csv("path/to/csv/file.csv")

retriever = chroma.as_retriever(search_type="ip")
retriever.get_relevant_documents(query)[0]
```

```python
Document(page_content='Tonight. I call on the Senate to: Pass the Freedom to Vote Act. Pass the John Lewis Voting Rights Act. And while you’re at it, pass the Disclose Act so Americans can know who is funding our elections. \n\nTonight, I’d like to honor someone who has dedicated his life to serve this country: Justice Stephen Breyer—an Army veteran, Constitutional scholar, and retiring Justice of the United States Supreme Court. Justice Breyer, thank you for your service. \n\nOne of the most serious constitutional responsibilities a President has is nominating someone to serve on the United States Supreme Court. \n\nAnd I did that 4 days ago, when I nominated Circuit Court of Appeals Judge Ketanji Brown Jackson. One of our nation’s top legal minds, who will continue Justice Breyer’s legacy of excellence.', metadata={'source': '../../../state_of_the_union.txt'})
```

### 5. Papers 모듈화
#### 5.1 RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval

https://arxiv.org/abs/2401.18059
##### 5.1.1 RAPTOR 사용법
1. .env file 에 openai_api_key 를 넣어주세요.
2. 그 뒤 아래와 같이 사용하시면 됩니다.
```python
from bs4 import BeautifulSoup as Soup
from langchain_community.document_loaders.recursive_url_loader import RecursiveUrlLoader

from langchain_extensions.papers import raptor


def extractor(page):
    return Soup(page, "html.parser").text


url = "https://python.langchain.com/docs/expression_language/"

loader = RecursiveUrlLoader(url=url, max_depth=20, extractor=extractor)
docs = loader.load()

docs_texts = [d.page_content for d in docs]
very_long_text = "\n".join(docs_texts)
results = raptor.raptornize(very_long_text, level=1, n_levels=3)
print(results)
```

3. async 의 경우 `araptornize` 륄 사용하시면 됩니다.
```python
results = await raptor.araptornize(very_long_text, level=1, n_levels=3)
print(results)
```
## Contributing

Contributions to the Langchain Community module are welcome. Whether it's adding support for new document formats, enhancing existing functionality, or fixing bugs, your contributions help improve the module for everyone.

## License

해당 소스코드는 `(주)크라우드웍스`에 귀속되어 있습니다.
무단 배포 및 사용을 금합니다.
