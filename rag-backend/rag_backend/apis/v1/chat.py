import logging

from fastapi import APIRouter
from langchain_core.prompts import SystemMessagePromptTemplate
from starlette.responses import PlainTextResponse
from starlette.responses import StreamingResponse

from rag_backend import agents
from rag_backend import schemas
from rag_backend.agents.prompts import gpt_prompt
from rag_backend.agents.tools import GetInsuranceAgeRestrictionDescriptionTool
from rag_backend.agents.tools import GetInsuranceEnrollmentCriteriaTool
from rag_backend.agents.tools import SearchDiseaseTool
from rag_backend.agents.tools import SearchInsuranceRequirementsTool
from rag_backend.agents.tools import SearchInsuranceTool

router = APIRouter(prefix="/v1")

logger = logging.getLogger(__name__)

llms = {
    "gpt": agents.gpt.build(),
    "clova": agents.clova.build(),
    "react": agents.react.build(),
}


@router.post("/chat/{model}/invoke", response_class=PlainTextResponse)
async def invoke(model: str, p: schemas.Prompt) -> PlainTextResponse:
    pass


@router.post("/chat/{model}/stream", response_class=StreamingResponse)
async def stream(model: str, p: schemas.Prompt) -> StreamingResponse:
    logger.error(f"Streaming response for [{model.upper()}]")
    logger.error(f"{p.session_id}: {p.message}]")
    agent = llms[model]

    async def generate():
        async for event in agent.astream_events(
            input={"input": p.message},
            config={"configurable": {"session_id": p.session_id}},
            version="v1",
        ):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    yield content
            elif kind == "on_tool_start":
                inputs = event["data"].get("input", {})
                if isinstance(inputs, dict):
                    params = ", ".join([f"{k}={v}" for k, v in inputs.items()])
                else:
                    params = str(inputs)
                yield "```"
                yield f"Planning tool: {event['name']}({params})"
                yield "```"
                yield "\n\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/chat/{model}/prompt", response_class=PlainTextResponse)
async def get_model_prompt(model: str) -> PlainTextResponse:
    logger.debug(f"Streaming response for [{model.upper()}]")

    search_disease_tool = SearchDiseaseTool()
    search_insurance_tool = SearchInsuranceTool()
    search_insurance_requirements_tool = SearchInsuranceRequirementsTool()
    get_insurance_enrollment_criteria_tool = GetInsuranceEnrollmentCriteriaTool()
    get_insurance_age_limit_description_tool = (
        GetInsuranceAgeRestrictionDescriptionTool()
    )

    tools = [
        search_disease_tool,
        search_insurance_tool,
        search_insurance_requirements_tool,
        get_insurance_enrollment_criteria_tool,
        get_insurance_age_limit_description_tool,
    ]

    answer = "Available tools:"
    answer += "\n\n"
    for tool in tools:

        answer += f"[{tool.name}]" + "\n"
        answer += tool.description + "\n"
        schema = tool.args_schema.schema()
        for key, value in schema["properties"].items():
            answer += f"{key}: {value['description']}\n"
        answer += "\n\n"

    answer += "Prompt:\n\n"
    for message in gpt_prompt.messages:
        if isinstance(message, SystemMessagePromptTemplate):
            answer += str(message.prompt.template) + "\n"
    return PlainTextResponse(answer)
