import asyncio
from operator import itemgetter
from typing import Sequence

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain_openai import ChatOpenAI

from rag_backend import conversation
from rag_backend.agents.prompts import gpt_prompt
from rag_backend.agents.retrievers import InsuranceAgeRestrictionRetriever
from rag_backend.agents.retrievers import format_by_newline
from rag_backend.agents.tools import GetInsuranceAgeRestrictionDescriptionTool
from rag_backend.agents.tools import GetInsuranceEnrollmentCriteriaDemoTool
from rag_backend.agents.tools import SearchDiseaseTool
from rag_backend.agents.tools import SearchInsuranceRequirementsTool
from rag_backend.agents.tools import SearchInsuranceTool
from rag_backend.configs import settings


def build():
    # llm
    llm = ChatOpenAI(model=settings.openai_model, temperature=1e-10, streaming=True)

    # tools
    search_disease_tool = SearchDiseaseTool()
    search_insurance_tool = SearchInsuranceTool()
    search_insurance_requirements_tool = SearchInsuranceRequirementsTool()
    get_insurance_enrollment_criteria_tool = GetInsuranceEnrollmentCriteriaDemoTool()
    get_insurance_age_restriction_tool = GetInsuranceAgeRestrictionDescriptionTool()

    tools = [
        search_disease_tool,
        search_insurance_tool,
        search_insurance_requirements_tool,
        get_insurance_enrollment_criteria_tool,
        get_insurance_age_restriction_tool,
    ]

    agent = create_openai_tools_agent(llm, tools, gpt_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    return RunnableWithMessageHistory(
        agent_executor,
        conversation.get_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )


def create_openai_tools_agent(
    llm: BaseLanguageModel, tools: Sequence[BaseTool], prompt: ChatPromptTemplate
) -> Runnable:
    missing_vars = {"agent_scratchpad"}.difference(prompt.input_variables)
    if missing_vars:
        raise ValueError(f"Prompt missing required variables: {missing_vars}")

    retriever = InsuranceAgeRestrictionRetriever()
    llm_with_tools = llm.bind(tools=[convert_to_openai_tool(tool) for tool in tools])

    agent = (
        RunnablePassthrough.assign(
            agent_scratchpad=lambda x: format_to_openai_tool_messages(
                x["intermediate_steps"]
            )
        )
        | {
            "input": itemgetter("input"),
            "context": itemgetter("input") | retriever | format_by_newline,
            "chat_history": itemgetter("chat_history"),
            "agent_scratchpad": itemgetter("agent_scratchpad"),
        }
        | prompt
        | llm_with_tools
        | OpenAIToolsAgentOutputParser()
    )
    return agent


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
