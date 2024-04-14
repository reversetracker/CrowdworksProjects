import os
import uuid

import requests
import streamlit as st


host = os.getenv("BACKEND_HOST", "http://127.0.0.1:8000")


def streaming_response(message: str, session_id: str, model: str):
    url = f"{host}/v1/chat/{model}/stream"
    param = {"message": message, "session_id": session_id}

    with requests.post(url, json=param, stream=True, timeout=120) as r:
        for chunk in r.iter_content(chunk_size=1024, decode_unicode=True):
            yield chunk


st.set_page_config(page_title="미래에셋 챗봇 상담원", page_icon="🤖", layout="wide")

model = st.selectbox("Choose a model", ["gpt", "clova"])

st.title(f"{model}")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.chat_message("assistant"):
    st.markdown(
        "안녕하세요 미래에셋 챗봇 상담원 입니다. 아래와 같은 명령을 지원합니다."
    )
    # st.markdown(
    #     "1. 2009년 4월 10일생 남자가 헬스케어 건강보험의 가입하려고 하는데, 90세 만기일 때 보험료 납입기간의 종류를 알려줘."
    # )
    # st.markdown(
    #     "2. 사무직에 종사하는 40세 남자가 일반암을 1천만원 가입할건데, 고액암은 얼마까지 가입 가능한지 알려줘."
    # )
    # st.markdown(
    #     "3. 고객이 심장병을 걱정하고 있어서 해당 질환 관련된 보장을 받고 싶은데, 어떤 특약들을 가입하면 될지 알려줘."
    # )
    # st.markdown(
    #     "4. 66세 남자인데 헬스케어 건강보험 90세 만기를 가입하려고 할 때 납입기간 어떤 것들이 가능한지 알려줘."
    # )
    # st.markdown("5. 여자만 가입할 수 있는 특약들을 알려줘.")
    # st.markdown(
    #     "6. 작년 3월에 심근경색증 치료가 끝났고 재발은 없는 50세 여성인데 소액사망 인수가 가능할까?"
    # )
    # st.markdown("7. 심근경색증에 걸린 30세 여자인데 사망담보 가입이 가능할까?")
    # st.markdown(
    #     "8. 50세 남자가 코로나19 합병증으로 동네병원에서 통원치료 받았고, 입원치료도 했어요. 질병입원 가입 가능할까요?"
    # )
    # st.markdown("9. 신우신염에 걸린 30세 여자인데 질병입원 담보 가입이 가능할까?")
    # st.markdown(
    #     "10. 신우신염 완치되었고 치료 종료 6개월이 지났어요. 합병증은 없습니다. 소액사망 인수 가능할까요?"
    # )
    # st.markdown(
    #     "11. 코로나에 걸려서 치료를 받았었는데 필요한 서류는 어떤 것들이 있을까요??"
    # )
    # st.markdown("12. 헬스케어 건강보험에 부가 가능한 특약을 알려주세요.")
    # st.markdown("13. 72세 남성이 헬스케어 건강보험이 가입가능할까요?")
    # st.markdown("13. 72세 남성이 가입가능한 보험기간, 납입기간을 알려주세요.")
    # st.markdown(
    #     "14. 65세 여성인 경우 뇌혈관질환진단특약과 뇌혈관질환산정특례대상보장특약 가입금액 한도를 알려주세요."
    # )
    # st.markdown(
    #     "15. 헬스케어 건강보험의 암진단특약과 유사암진단특약 최대가입금액을 알려주세요."
    # )
    # st.markdown(
    #     "16. 23년 1월부터 폐렴, 기관지염을 복용중인 52세 남성이 가입가능한 담보를 알려주세요"
    # )
    # st.markdown(
    #     "17. ~~22년 4월부터 당뇨를 진단받은 여성, 당화혈색소 6.2, 합병증 없는 경우 사망급부 가입가능한가요?~~"
    # )
    # st.markdown(
    #     "18. 22년 4월부터 만성신우염 진단을 받는 여자 소액사망 가입 가능한가요?"
    # )
    # st.markdown(
    #     "19. 21년 2월 대장용종 제거한 이력이 있는 40세 남성의 경우 암진단, 입원급부 가입이 가능한가요?"
    # )
    # st.markdown(
    #     "20. 목디스크로 1년전 입원치료한 이력이 있는경우 입원,수술급부 가입이 가능한가요?"
    # )
    # st.markdown(
    #     "21. 허리가 삐끗하여 3년전 입원치료한 이력이 있는경우 입원,수술급부 가입이 가능한가요?"
    # )
    # st.markdown(
    #     "Note: 현재 추가 가능한 담보는 ```암, 소액사망, 질병입원``` 으로 제한됩니다."
    # )
    # st.markdown(
    #     "Note: 현재 심사 가능한 질병은 ```만성신우신염, 코로나19 합병증, 심근경색증, 폐렴, 기관지염``` 으로 제한됩니다."
    # )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What's up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        session_id = st.session_state.session_id
        response = st.write_stream(
            streaming_response(message=prompt, model=model, session_id=session_id),
        )
    st.session_state.messages.append({"role": "assistant", "content": response})
