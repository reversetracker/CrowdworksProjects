FROM python:3.10.11-slim-buster

RUN apt-get update && apt-get install -y git

COPY requirements.txt /opt/rag-backend/requirements.txt
RUN pip install -r /opt/rag-backend/requirements.txt --no-cache-dir
RUN pip install pysqlite3-binary --no-cache-dir
RUN pip install numexpr

COPY ../.. /opt/rag-backend
WORKDIR /opt/rag-backend

RUN ls -l /opt/rag-backend

EXPOSE 80

CMD ["sh", "-c", "streamlit run streamlit_chatbot.py"]
