import asyncio
import collections

from langchain.agents import AgentExecutor
from langchain_community.chat_message_histories.in_memory import ChatMessageHistory
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain_extensions.language_models.naver import SkillsetHyperClova
from rag_backend.agents.parser import HyperclovaAgentOutputParser
from rag_backend.agents.prompts import clova_prompt


def build():
    clova_tools = []  # ignore tools here in clova
    llm = SkillsetHyperClova(
        clovastudio_api_key="NTA0MjU2MWZlZTcxNDJiY2gyE98rR/v9DrgLHwJkeRM8ZLJ8IqGbw++ZzZJZW86O",
        apigw_api_key="vzJneP0CpiUcwQc3nOdlBqoSFZljmq6NB6mr7fVd",
        invoke_url="/testapp/v1/skillsets/4cdq5l09/versions/52/final-answer",
    )
    llm_with_tools = llm.bind(tools=clova_tools)
    agent = (
        RunnablePassthrough()
        | clova_prompt
        | llm_with_tools
        | HyperclovaAgentOutputParser()
    )
    agent_executor = AgentExecutor(agent=agent, tools=clova_tools, verbose=True)

    session_histories = collections.defaultdict(ChatMessageHistory)

    def get_session_history(x: str):
        return session_histories[x]

    return RunnableWithMessageHistory(
        agent_executor,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )


async def main():
    agent = build()
    while True:
        message = input("Enter a message: ")
        async for event in agent.astream_events(
            input={"input": message},
            config={"configurable": {"session_id": "foo"}},
            version="v1",
        ):
            print(event)


if __name__ == "__main__":
    asyncio.run(main())
