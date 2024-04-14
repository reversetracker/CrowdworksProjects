from langchain.schema import StrOutputParser
from langchain_community.llms.openai import OpenAI
from langchain_core.prompts import ChatPromptTemplate

from langchain_extensions.language_models import HyperClova

NAVER_CLOVA_API_KEY = "😝"

NAVER_INVOKE_URL = "😝"

OPENAI_API_KEY = "😝"

prompt = ChatPromptTemplate.from_template("what is the city {person} is from?")

# 대체해도 그대로 동작 가능!
# model = OpenAI(
#     api_key=OPENAI_API_KEY,
#     streaming=True,
# )

model = HyperClova(
    invoke_url=NAVER_INVOKE_URL,
    api_key=NAVER_CLOVA_API_KEY,
    streaming=True,
)

chain = prompt | model | StrOutputParser()

stream = chain.stream({"person": "obama"})

for s in stream:
    print(s, end="")
