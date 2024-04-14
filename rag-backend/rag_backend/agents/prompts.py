from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import HumanMessagePromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import SystemMessagePromptTemplate

gpt_prompt = ChatPromptTemplate(
    input_variables=["agent_scratchpad", "chat_history", "context", "input"],
    messages=[
        SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                input_variables=[],
                template="당신은 미래에셋 보험회사의 보험 상담사입니다.",
            )
        ),
        SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                input_variables=[],
                template="당신은 도구를 활용하여 미래에셋 데이터베이스에 접근 할 수 있고 해당 내용을 바탕으로 고객에게 설명합니다.",
            )
        ),
        SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                input_variables=[],
                template="답변할 때, 도구에서 얻은 정보를 마크다운 형식으로 작성 하되 함부로 web 주소를 노출하면 절대 안됩니다.",
            )
        ),
        SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                input_variables=[],
                template="답변시 상세한 이유를 반드시 상대방에게 알려야 합니다.",
            )
        ),
        SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                input_variables=[],
                template="답변시 tool 을 사용하여 얻은 정보만 이용해서 답변하세요.",
            )
        ),
        SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                input_variables=[],
                template="가입 가능한 보험 및 담보를 질문하면 search_insurance_tool 을 사용 하세요..",
            )
        ),
        SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                input_variables=[],
                template="'코로나19' 와 '코로나19 합병증' 은 다르므로 반드시 구분하시오.",
            )
        ),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        HumanMessagePromptTemplate(
            prompt=PromptTemplate(
                input_variables=["input", "context"],
                template="{input}\n{context}",
            )
        ),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ],
)

clova_prompt = ChatPromptTemplate(
    input_variables=["input", "chat_history"],
    messages=[
        SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                input_variables=[],
                template="당신은 미래에셋보험 상담을 도와주는 챗봇입니다.",
            )
        ),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        HumanMessagePromptTemplate(
            prompt=PromptTemplate(input_variables=["input"], template="{input}")
        ),
    ],
)
