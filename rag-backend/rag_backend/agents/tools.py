import json
import logging
import re
from typing import Optional, Type

from langchain.callbacks.manager import AsyncCallbackManagerForToolRun
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from rag_backend import predefined
from rag_backend.agents.persistences import (
    coverage_limit_chroma,
    disease_name_chroma,
    insurance_requirements_chroma,
)
from rag_backend.agents.persistences import disease_chroma, collateral_name_chroma
from rag_backend.agents.persistences import insurance_chroma

logger = logging.getLogger(__name__)


class SearchInsuranceRequirementsInput(BaseModel):
    disease_name: str = Field(description="보험 가입 때 등록 할 질병 명.")


class SearchInsuranceRequirementsTool(BaseTool):
    name: str = "search_insurance_requirements_tool"
    description: str = "보험 가입 시 필요한 서류를 조회 합니다."
    args_schema: Type[BaseModel] = SearchInsuranceRequirementsInput

    def _run(
        self,
        disease_name: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        documents = insurance_requirements_chroma.similarity_search(disease_name, k=3)
        metadata = [x.metadata for x in documents]
        return json.dumps(metadata, ensure_ascii=False, indent=2)

    async def _arun(
        self,
        disease_name: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        return self._run(disease_name)


class SearchDiseaseInput(BaseModel):
    query: str = Field(
        description=(
            "질병 이름 혹은 질병 증상등을 입력 합니다. "
            "'두통', '머리가 아파요' 혹은 '머리아픔' 같은 방식으로 입력 가능합니다."
        )
    )
    k: int = Field(
        description="검색 할 개수를 지정합니다. 기본값은 5 입니다.", default=5
    )


class SearchDiseaseTool(BaseTool):
    name: str = "search_disease_tool"
    description: str = (
        "질병 데이터베이스를 조회합니다. 유저가 질병에 대한 정보를 요청할 때 유용합니다."
    )
    args_schema: Type[BaseModel] = SearchDiseaseInput

    def _run(
        self,
        query: str,
        k: int = 5,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        if "폐" in query:
            query = query + ", 폐렴, 하부호흡기감염증"
        documents = disease_chroma.similarity_search(query, k=k)
        metadatas = [x.metadata for x in documents]
        return json.dumps(metadatas, ensure_ascii=False, indent=2)

    async def _arun(
        self,
        query: str,
        k: int = 5,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        return self._run(query, k=k, run_manager=run_manager)


class SearchInsuranceInput(BaseModel):
    query: str = Field(
        description="질병 이름 혹은 질병 증상등을 바탕으로 입력합니다. Ex) '암 보험', '해약환급금이 없는 무배당 암보험'"
    )


class SearchInsuranceTool(BaseTool):
    name: str = "search_insurance_tool"
    description: str = (
        "특약 종류, 보험 종류, 보험 코드, 보험금 및 보상금 정보를 얻을 수 있는 데이터베이스를 조회합니다. "
        "유저가 특약이나 보험 종류 및 가입금액에 대해서 물을때 유용합니다."
    )
    args_schema: Type[BaseModel] = SearchInsuranceInput

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        documents_1 = insurance_chroma.similarity_search(query, k=5)
        metadatas_1 = [x.metadata for x in documents_1]
        result_1 = json.dumps(metadatas_1, ensure_ascii=False, indent=2)
        documents_2 = coverage_limit_chroma.similarity_search(query, k=5)
        metadatas_2 = [x.metadata for x in documents_2]
        result_2 = json.dumps(metadatas_2, ensure_ascii=False, indent=2)
        result = result_1 + "\n\n" + result_2
        result += "\n\n\n"
        result += "[경고]: 보험 상품 유형 검색시, 사용자가 기본형, 해약환급금에 대해 선택하지 않았을 경우, 두개 다 보여 주시오."
        return result

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        return self._run(query)


class GetInsuranceEnrollmentCriteriaInput(BaseModel):
    disease_name: str = Field(description="환자가 앓고 있는 질병에 대한 질병 이름")
    collateral_name: str = Field(
        description="보험에 추가 할 담보명 example) 암, 질병입원, 15대입원수술"
    )


class GetInsuranceEnrollmentCriteriaTool(BaseTool):
    name: str = "get_insurance_enrollment_criteria_tool"
    description: str = (
        "보험이나 특약에 가입하고 싶을 때 어떤 조건을 충족해야 하는지 조회합니다. "
        "질병이 있는 환자가 보험이나 특약을 추가하고 싶은 경우에만 가능합니다. "
        "환자의 질병명과 담보명을 입력하면 가입 가능 여부를 알려줍니다."
    )
    args_schema: Type[BaseModel] = GetInsuranceEnrollmentCriteriaInput

    def _run(
        self,
        disease_name: str,
        collateral_name: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:

        disease_name = self.make_sure_disease_name(disease_name)
        collateral_name = self.make_sure_collateral_name(collateral_name)

        allowed_diseases = [
            "만성신우신염",
            "코로나19 합병증",
            "심근경색증",
            "폐렴, 기관지염",
        ]
        if disease_name not in allowed_diseases:
            return (
                "현재 지원되지 않는 질병 입니다."
                + "\n"
                + "지원 되는 질병명: "
                + ", ".join(allowed_diseases)
            )

        if run_manager:
            run_manager.on_text(
                f"```\n\n\n질병명: {disease_name}\n담보명: {collateral_name}\n\n\n```"
            )

        criteria_condition = self.get_criteria_condition(disease_name)
        criteria_description = self.get_criteria_from_matrix(
            disease_name, collateral_name
        )

        logger.info(f"chosen collateral name: {collateral_name}")
        logger.info(f"chosen criteria: {criteria_description}")

        answer = f"""
{criteria_description}

위 기준을 파악하기 위해서 물어봐야 할 필수 질문들:

{criteria_condition}

이미 답변이 된 부분은 답변을 같이 표기하시오.
"""
        return answer

    async def _arun(
        self,
        disease_name: str,
        collateral_name: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        return self._run(disease_name, collateral_name)

    def get_criteria_condition(self, disease_name: str) -> str | None:
        """아래와 같은 방식으로 유저에게 물어볼 질문을 반환합니다.
        1) 폐결핵 완치 여부\n2) 재발 여부\n3) 치료 종료 후 경과 기간
        """
        for x in predefined.essential_question.arguments:
            if x["병명"] == disease_name:
                return x["인수조건"]
        return None

    def make_sure_collateral_name(self, collateral: str) -> str:
        """가장 가까운 담보명으로 변환합니다."""
        collateral_names = collateral_name_chroma.similarity_search(collateral, k=1)
        return collateral_names[0].page_content

    def make_sure_disease_name(self, collateral: str) -> str:
        """가장 가까운 질병명으로 변환합니다."""
        disease_names = disease_name_chroma.similarity_search(collateral, k=1)
        return disease_names[0].page_content

    def get_criteria_from_matrix(self, disease_name: str, collateral_name: str) -> str:
        """질병 코드가 존재하는지 확인합니다."""
        args = predefined.disease_matrix.arguments

        # index 0 row 가 테이블의 header
        values = args[0].values()
        index = None
        for i, v in enumerate(values):
            if collateral_name in v:
                index = i

        if index is None:
            raise Exception("담보명이 존재하지 않습니다.")

        # Unnamed: 6 이 적용 기준
        # Unnamed: {index} 이 적용 기준 시 결과 (승인/거절)
        criteria = [
            f"{x['Unnamed: 6']} 인 경우 {x[f'Unnamed: {index}']}"
            for x in args
            if x.get("Unnamed: 1") == disease_name
        ]
        return "\n".join(criteria)


class GetInsuranceAgeRestrictionDescriptionInput(BaseModel):
    query: str = Field(
        description="질문을 입력하세요. ex) '남자 암 보험 나이제한은 몇세인가요?'"
    )


class GetInsuranceAgeRestrictionDescriptionTool(BaseTool):
    name: str = "get_insurance_age_restriction_tool"
    description: str = (
        "나이와 보험 및 특약의 조건을 조회합니다. 나이제한, 보험기간, 보험료 그리고 총 납입기간을 알 수 있습니다."
    )

    args_schema: Type[BaseModel] = GetInsuranceAgeRestrictionDescriptionInput

    def _run(
        self,
        query: str | None = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        condition = "주계약은 최소 만 15세 이상 이여야합니다."
        condition += "\n\n\n"
        condition += "보험에는 기본형과 해약환급금이 없는 유형이 있고 두가지는 매우 중요하므로 생략하지 마시오."
        condition += "\n\n\n"
        condition = """
## 기본형 남자 ##
보험기간: 90세 만기, 보험료 납입기간: 10년납, 기본형 남자: 75세
보험기간: 90세 만기, 보험료 납입기간: 15년납, 기본형 남자: 72세
보험기간: 90세 만기, 보험료 납입기간: 20년납, 기본형 남자: 68세
보험기간: 90세 만기, 보험료 납입기간: 25년납, 기본형 남자: 64세
보험기간: 90세 만기, 보험료 납입기간: 30년납, 기본형 남자: 60세
보험기간: 100세 만기, 보험료 납입기간: 10년납, 기본형 남자: 62세
보험기간: 100세 만기, 보험료 납입기간: 15년납, 기본형 남자: 60세
보험기간: 100세 만기, 보험료 납입기간: 20년납, 기본형 남자: 58세
보험기간: 100세 만기, 보험료 납입기간: 25년납, 기본형 남자: 55세
보험기간: 100세 만기, 보험료 납입기간: 30년납, 기본형 남자: 52세
보험기간: 종신, 보험료 납입기간: 10년납, 기본형 남자: 61세
보험기간: 종신, 보험료 납입기간: 15년납, 기본형 남자: 59세
보험기간: 종신, 보험료 납입기간: 20년납, 기본형 남자: 57세
보험기간: 종신, 보험료 납입기간: 25년납, 기본형 남자: 54세
보험기간: 종신, 보험료 납입기간: 30년납, 기본형 남자: 52세

## 기본형 여자 ##
보험기간: 90세 만기, 보험료 납입기간: 10년납, 기본형 여자: 75세
보험기간: 90세 만기, 보험료 납입기간: 15년납, 기본형 여자: 75세
보험기간: 90세 만기, 보험료 납입기간: 20년납, 기본형 여자: 70세
보험기간: 90세 만기, 보험료 납입기간: 25년납, 기본형 여자: 65세
보험기간: 90세 만기, 보험료 납입기간: 30년납, 기본형 여자: 60세
보험기간: 100세 만기, 보험료 납입기간: 10년납, 기본형 여자: 71세
보험기간: 100세 만기, 보험료 납입기간: 15년납, 기본형 여자: 69세
보험기간: 100세 만기, 보험료 납입기간: 20년납, 기본형 여자: 67세
보험기간: 100세 만기, 보험료 납입기간: 25년납, 기본형 여자: 64세
보험기간: 100세 만기, 보험료 납입기간: 30년납, 기본형 여자: 60세
보험기간: 종신, 보험료 납입기간: 10년납, 기본형 여자: 67세
보험기간: 종신, 보험료 납입기간: 15년납, 기본형 여자: 65세
보험기간: 종신, 보험료 납입기간: 20년납, 기본형 여자: 63세
보험기간: 종신, 보험료 납입기간: 25년납, 기본형 여자: 61세
보험기간: 종신, 보험료 납입기간: 30년납, 기본형 여자: 58세

## 해약 환급금이 없는 유형 남자 ##
보험기간: 90세 만기, 보험료 납입기간: 10년납, 해약환급금이 없는 유형 남자: 75세
보험기간: 90세 만기, 보험료 납입기간: 15년납, 해약환급금이 없는 유형 남자: 70세
보험기간: 90세 만기, 보험료 납입기간: 20년납, 해약환급금이 없는 유형 남자: 65세
보험기간: 90세 만기, 보험료 납입기간: 25년납, 해약환급금이 없는 유형 남자: 60세
보험기간: 90세 만기, 보험료 납입기간: 30년납, 해약환급금이 없는 유형 남자: 55세
보험기간: 100세 만기, 보험료 납입기간: 10년납, 해약환급금이 없는 유형 남자: 69 세
보험기간: 100세 만기, 보험료 납입기간: 15년납, 해약환급금이 없는 유형 남자: 64 세
보험기간: 100세 만기, 보험료 납입기간: 20년납, 해약환급금이 없는 유형 남자: 62 세
보험기간: 100세 만기, 보험료 납입기간: 25년납, 해약환급금이 없는 유형 남자: 59 세
보험기간: 100세 만기, 보험료 납입기간: 30년납, 해약환급금이 없는 유형 남자: 57 세
보험기간: 종신, 보험료 납입기간: 10년납, 해약환급금이 없는 유형 남자: 69 세 
보험기간: 종신, 보험료 납입기간: 15년납, 해약환급금이 없는 유형 남자: 64 세 
보험기간: 종신, 보험료 납입기간: 20년납, 해약환급금이 없는 유형 남자: 62 세 
보험기간: 종신, 보험료 납입기간: 25년납, 해약환급금이 없는 유형 남자: 59 세 
보험기간: 종신, 보험료 납입기간: 30년납, 해약환급금이 없는 유형 남자: 56 세  

## 해약 환급금이 없는 유형 여자 ##
보험기간: 90세 만기, 보험료 납입기간: 10년납, 해약환급금이 없는 유형 여자: 75세 
보험기간: 90세 만기, 보험료 납입기간: 15년납, 해약환급금이 없는 유형 여자: 70세 
보험기간: 90세 만기, 보험료 납입기간: 20년납, 해약환급금이 없는 유형 여자: 65세 
보험기간: 90세 만기, 보험료 납입기간: 25년납, 해약환급금이 없는 유형 여자: 60세 
보험기간: 90세 만기, 보험료 납입기간: 30년납, 해약환급금이 없는 유형 여자: 55세
보험기간: 100세 만기, 보험료 납입기간: 10년납, 해약환급금이 없는 유형 여자: 75 세
보험기간: 100세 만기, 보험료 납입기간: 15년납, 해약환급금이 없는 유형 여자: 72 세
보험기간: 100세 만기, 보험료 납입기간: 20년납, 해약환급금이 없는 유형 여자: 70 세
보험기간: 100세 만기, 보험료 납입기간: 25년납, 해약환급금이 없는 유형 여자: 65 세
보험기간: 100세 만기, 보험료 납입기간: 30년납, 해약환급금이 없는 유형 여자: 60 세
보험기간: 종신, 보험료 납입기간: 10년납, 해약환급금이 없는 유형 여자: 74 세  
보험기간: 종신, 보험료 납입기간: 15년납, 해약환급금이 없는 유형 여자: 70 세  
보험기간: 종신, 보험료 납입기간: 20년납, 해약환급금이 없는 유형 여자: 68 세  
보험기간: 종신, 보험료 납입기간: 25년납, 해약환급금이 없는 유형 여자: 65 세  
보험기간: 종신, 보험료 납입기간: 30년납, 해약환급금이 없는 유형 여자: 60 세  
"""
        llm = ChatOpenAI(temperature=0, streaming=True, callbacks=[])

        question = (
            f"{query}\n"
            f"# 조건은 아래와 같습니다. 질문에 답해주고 근거와 관련 정보를 상세히 제시해 주세요.."
            f"# 기본형과 해약환급금이 없는 유형 모두 포함하여 답변해 주세요."
            f"\n{condition}"
        )
        answer = llm.invoke(question)
        return answer.content + "\n이후에 function 및 tool 을 더이상 사용하지 마시오."

    async def _arun(
        self,
        query: str | None = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        return self._run(query)


class CompareNumberInput(BaseModel):
    number_1: str = Field(
        description="비교 할 대상 1: 1개월, 3일, 2 등등 모든 숫자가 포함 된 단위."
    )
    number_2: str = Field(
        description="비교 할 대상 2: 1개월, 3일, 2 등등 모든 숫자가 포함 된 단위."
    )


class CompareNumberTool(BaseTool):
    name: str = "compare_number_tool"
    description: str = "두 크기를 비교 합니다. 반드시 단위는 같아야 합니다."
    args_schema: Type[BaseModel] = CompareNumberInput

    def _run(
        self,
        number_1: str,
        number_2: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        # 정규식을 사용해 문자열에서 숫자 추출
        num1 = re.findall(r"\d+", number_1)
        num2 = re.findall(r"\d+", number_2)

        # 추출된 숫자가 있다면 정수로 변환, 비교를 위해
        if num1 and num2:
            num1 = int(num1[0])
            num2 = int(num2[0])

            # 대소 비교
            if num1 > num2:
                return f"{num1} > {num2}"
            elif num1 < num2:
                return f"{num1} < {num2}"
            else:
                return f"{num1} = {num2}"
        else:
            return "두 숫자를 비교 할 수 없습니다."

    async def _arun(
        self,
        number_1: str,
        number_2: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        return self._run(number_1, number_2)


class GetInsuranceEnrollmentCriteriaDemoInput(BaseModel):
    disease_name: str = Field(description="환자가 앓고 있는 질병에 대한 질병 이름")
    collateral_name: str = Field(
        description="보험에 추가 할 담보명 example) 암, 질병입원, 15대입원수술"
    )


class GetInsuranceEnrollmentCriteriaDemoTool(BaseTool):
    name: str = "get_insurance_enrollment_criteria_tool"
    description: str = (
        "보험이나 특약에 가입하고 싶을 때 어떤 조건을 충족해야 하는지 조회합니다. "
        "질병이 있는 환자가 보험이나 특약을 추가하고 싶은 경우에만 가능합니다. "
        "환자의 질병명과 담보명을 입력하면 가입 가능 여부를 알려줍니다."
    )
    args_schema: Type[BaseModel] = GetInsuranceEnrollmentCriteriaDemoInput

    def _run(
        self,
        disease_name: str,
        collateral_name: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:

        disease_name = self.make_sure_disease_name(disease_name)
        collateral_name = self.make_sure_collateral_name(collateral_name)

        allowed_diseases = [
            "만성신우신염",
            "코로나19 합병증",
            "심근경색증",
            "폐렴, 기관지염",
        ]
        if disease_name not in allowed_diseases:
            return (
                "현재 지원되지 않는 질병 입니다."
                + "\n"
                + "지원 되는 질병명: "
                + ", ".join(allowed_diseases)
            )

        allowed_collaterals = ["암", "소액사망", "질병입원"]
        if collateral_name not in allowed_collaterals:
            return (
                "현재 지원되지 않는 담보명 입니다."
                + "\n"
                + "지원 되는 담보명: "
                + ", ".join(allowed_collaterals)
            )

        if run_manager:
            run_manager.on_text(
                f"```\n\n\n질병명: {disease_name}\n담보명: {collateral_name}\n\n\n```"
            )

        descriptions = []
        count = 1
        for x in predefined.disease_matrix_2.arguments:
            if disease_name == x["대표질병명"]:
                descriptions.append(
                    f"{count}. {x['적용 기준']}일 경우 {x[collateral_name]} \n"
                )
                count += 1

        criteria_description = "\n".join(descriptions)
        criteria_condition = self.get_criteria_condition(disease_name)

        logger.info(f"chosen collateral name: {collateral_name}")
        logger.info(f"chosen criteria: {criteria_description}")

        answer = f"""
[상세 내역]
{criteria_description}

[상세 내역을 판단하기 위한 필수 질문 리스트]
{criteria_condition}

[지침사항]
1. 위 질문을 일단 유저에게 묻고 응답 결과를 기준과 비교하세요.
2. 이미 답변이 된 부분은 답변을 같이 표기하시오.
3. 답변이 판단 하기에 부족한 부분이 있으면 충족 할때까지 질문하시오.
4. 판단 결과를 말 할 때 상세 내역 중 일치하는 부분을 유저에게 보여주시오. ( 유저는 상세 내역을 모름 )
5. 중요: 상세 내역과 질문 리스트 기반으로만 답변 주세요.
"""
        return answer

    async def _arun(
        self,
        disease_name: str,
        collateral_name: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        return self._run(disease_name, collateral_name)

    def get_criteria_condition(self, disease_name: str) -> str | None:
        """아래와 같은 방식으로 유저에게 물어볼 질문을 반환합니다.
        1) 폐결핵 완치 여부\n2) 재발 여부\n3) 치료 종료 후 경과 기간
        """
        for x in predefined.essential_question.arguments:
            if x["병명"] == disease_name:
                return x["인수조건"]
        return None

    def make_sure_collateral_name(self, collateral: str) -> str:
        """가장 가까운 담보명으로 변환합니다."""
        collateral_names = collateral_name_chroma.similarity_search(collateral, k=1)
        return collateral_names[0].page_content

    def make_sure_disease_name(self, collateral: str) -> str:
        """가장 가까운 질병명으로 변환합니다."""
        disease_names = disease_name_chroma.similarity_search(collateral, k=1)
        return disease_names[0].page_content

    def get_criteria_from_matrix(self, disease_name: str, collateral_name: str) -> str:
        """질병 코드가 존재하는지 확인합니다."""
        args = predefined.disease_matrix.arguments

        # index 0 row 가 테이블의 header
        values = args[0].values()
        index = None
        for i, v in enumerate(values):
            if collateral_name in v:
                index = i

        if index is None:
            raise Exception("담보명이 존재하지 않습니다.")

        # Unnamed: 6 이 적용 기준
        # Unnamed: {index} 이 적용 기준 시 결과 (승인/거절)
        criteria = [
            f"{x['Unnamed: 6']} 인 경우 {x[f'Unnamed: {index}']}"
            for x in args
            if x.get("Unnamed: 1") == disease_name
        ]
        return "\n".join(criteria)
