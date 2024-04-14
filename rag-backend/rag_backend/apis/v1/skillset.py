import json
import logging

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import JSONResponse

from rag_backend.agents import tools

router = APIRouter(prefix="/v1")

logger = logging.getLogger(__name__)


class Query(BaseModel):
    query: str | None = None
    disease_code: str | None = None
    rider: str | None = None


@router.post("/skillsets/disease", response_class=JSONResponse)
async def list_diseases(q: Query) -> JSONResponse:
    """질병 데이터베이스를 검색 한 뒤 결과를 반환합니다.

    Response:
        [
            {
                "KCD차수": "8",
                "대표질병대분류명": "신생물",
                "대표질병코드": "C22",
                "영문질병명": "Malignant neoplasm of liver and intrahepatic bile ducts",
                "유사질병명": "간내담관암, 간육종, 간암",
                "한글질병명": "간 및 간내 담관의 악성 신생물",
            },
            {
                "KCD차수": "9",
                "대표질병대분류명": "간암",
                "대표질병코드": "C22",
                "영문질병명": "Malignant neoplasm of liver and intrahepatic bile ducts",
                "유사질병명": "간내담관암, 간육종, 간암",
                "한글질병명": "간 및 간내 담관의 악성 신생물",
            }
        ]
    """
    documents = tools.SearchDiseaseTool().run(q.query)
    documents = json.loads(documents)
    return JSONResponse(content=documents)


@router.post("/skillsets/insurance", response_class=JSONResponse)
async def list_insurances(q: Query) -> JSONResponse:
    documents = tools.SearchInsuranceTool().run(q.query)
    documents = json.loads(documents)
    return JSONResponse(content=documents)


@router.post("/skillsets/criteria", response_class=JSONResponse)
async def list_conditions(q: Query) -> JSONResponse:
    content = {
        "criteria": [
            "결핵 완치 후 5년 미경과, 약제내성/속립성결핵 이라면 승인가능",
            "결핵 완치 후 5년 미경과, 비활동성결핵 이라면 승인 가능",
            "결핵 완치 안됨, 재발없음, 활동성/잠복결핵 이라면 승인 가능",
            "결핵 완치 안됨, 재발있음, 활동성/잠복결핵 이라면 승인 가능",
        ],
        "description": """
        아래에 사항들을 유저에게 물어보고 기준과 비교하여 판단 하시오!
        
        1) 결핵 완치여부
        2) 재발여부
        3) 치료종료 후 경과기간
        4) 결핵종류
        5) 약 복용기간
        """,
    }
    return JSONResponse(content=content)


@router.post("/skillsets/conditions", response_class=JSONResponse)
async def list_conditions(q: Query) -> JSONResponse:
    content = {
        "criteria": [
            "결핵 완치 후 5년 미경과, 약제내성/속립성결핵 이라면 승인가능",
            "결핵 완치 후 5년 미경과, 비활동성결핵 이라면 승인 가능",
            "결핵 완치 안됨, 재발없음, 활동성/잠복결핵 이라면 승인 가능",
            "결핵 완치 안됨, 재발있음, 활동성/잠복결핵 이라면 승인 가능",
        ],
        "description": """
        아래에 사항들을 유저에게 물어보고 기준과 비교하여 판단 하시오!

        1) 결핵 완치여부
        2) 재발여부
        3) 치료종료 후 경과기간
        4) 결핵종류
        5) 약 복용기간
        """,
    }
    return JSONResponse(content=content)
