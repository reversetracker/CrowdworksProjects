"""NOT IMPLEMENTED."""

from fastapi import FastAPI
from starlette.responses import PlainTextResponse

from rag_backend.assemble.middleware import context_middleware
from rag_backend.assemble.middleware import cors_middleware
from rag_backend.assemble.middleware import session_context_id_middlewares

app = FastAPI(
    docs_url="/docs",
    middleware=[
        context_middleware,
        cors_middleware,
        session_context_id_middlewares,
    ],
)


@app.get("/", response_class=PlainTextResponse)
async def index():
    """Index Page of the API."""
    return "Hello, World!"
