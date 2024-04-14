import asyncio

from langchain import hub
from langchain.agents import AgentExecutor
from langchain.agents import create_react_agent
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

from rag_backend import conversation
from rag_backend.agents.tools import (
    SearchDiseaseTool,
    SearchInsuranceTool,
    GetInsuranceEnrollmentCriteriaTool,
    GetInsuranceAgeRestrictionDescriptionTool,
    CompareNumberTool,
)


def build():
    search_disease_tool = SearchDiseaseTool()
    search_insurance_tool = SearchInsuranceTool()
    check_rider_eligibility_tool = GetInsuranceEnrollmentCriteriaTool()
    check_insurance_age_limit_tool = GetInsuranceAgeRestrictionDescriptionTool()
    compare_number_tool = CompareNumberTool()

    prompt = hub.pull("hwchase17/react")
    prompt.template = "Respond it in korean.\n" + prompt.template

    llm = ChatOpenAI(temperature=0, streaming=True, callbacks=[])
    tools = [
        search_disease_tool,
        search_insurance_tool,
        check_rider_eligibility_tool,
        check_insurance_age_limit_tool,
        compare_number_tool,
    ]
    agent = create_react_agent(llm, tools, prompt=prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

    return RunnableWithMessageHistory(
        agent_executor,
        conversation.get_history,
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
